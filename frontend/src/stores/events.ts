import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { SecurityEvent, EventSearchForm, PageResponse } from '@/types'
import { getEventList, getEventDetail, updateEventStatus } from '@/services/events'

export const useEventsStore = defineStore('events', () => {
  // 状态
  const events = ref<SecurityEvent[]>([])
  const currentEvent = ref<SecurityEvent | null>(null)
  const loading = ref(false)
  const total = ref(0)
  const currentPage = ref(1)
  const pageSize = ref(20)
  
  // 搜索表单
  const searchForm = ref<EventSearchForm>({
    threatType: '',
    severityLevel: '',
    status: '',
    sourceIp: '',
    dateRange: undefined,
    keyword: ''
  })

  // 计算属性
  const hasEvents = computed(() => events.value.length > 0)
  const pendingEventsCount = computed(() => 
    events.value.filter(event => event.status === 'pending').length
  )
  
  // 获取事件列表
  const fetchEvents = async (page = 1) => {
    try {
      loading.value = true
      currentPage.value = page
      
      const params = {
        page,
        size: pageSize.value,
        ...searchForm.value,
        startTime: searchForm.value.dateRange?.[0],
        endTime: searchForm.value.dateRange?.[1]
      }
      
      // 清理空值
      Object.keys(params).forEach(key => {
        if (params[key] === '' || params[key] === undefined) {
          delete params[key]
        }
      })
      
      const data = await getEventList(params)
      events.value = data.list
      total.value = data.total
    } catch (error) {
      console.error('获取事件列表失败:', error)
    } finally {
      loading.value = false
    }
  }

  // 获取事件详情
  const fetchEventDetail = async (eventId: string) => {
    try {
      loading.value = true
      const data = await getEventDetail(eventId)
      currentEvent.value = data
      return data
    } catch (error) {
      console.error('获取事件详情失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 更新事件状态
  const updateStatus = async (eventId: string, status: string) => {
    try {
      await updateEventStatus(eventId, status as any)
      
      // 更新本地状态
      const eventIndex = events.value.findIndex(event => event.id === eventId)
      if (eventIndex !== -1) {
        events.value[eventIndex].status = status as any
      }
      
      if (currentEvent.value && currentEvent.value.id === eventId) {
        currentEvent.value.status = status as any
      }
    } catch (error) {
      console.error('更新事件状态失败:', error)
      throw error
    }
  }

  // 搜索事件
  const searchEvents = async () => {
    currentPage.value = 1
    await fetchEvents(1)
  }

  // 重置搜索
  const resetSearch = () => {
    searchForm.value = {
      threatType: '',
      severityLevel: '',
      status: '',
      sourceIp: '',
      dateRange: undefined,
      keyword: ''
    }
    searchEvents()
  }

  // 刷新当前页
  const refreshEvents = () => {
    fetchEvents(currentPage.value)
  }

  return {
    // 状态
    events,
    currentEvent,
    loading,
    total,
    currentPage,
    pageSize,
    searchForm,
    
    // 计算属性
    hasEvents,
    pendingEventsCount,
    
    // 方法
    fetchEvents,
    fetchEventDetail,
    updateStatus,
    searchEvents,
    resetSearch,
    refreshEvents
  }
}) 