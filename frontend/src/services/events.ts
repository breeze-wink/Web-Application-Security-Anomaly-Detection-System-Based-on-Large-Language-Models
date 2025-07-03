import api from './api'
import type { 
  SecurityEvent, 
  EventSearchForm, 
  PageResponse,
  EventStatus 
} from '@/types'

// 获取事件列表
export function getEventList(params: {
  page?: number
  size?: number
  threatType?: string
  severityLevel?: string
  status?: string
  sourceIp?: string
  startTime?: string
  endTime?: string
  keyword?: string
}) {
  return api.get<PageResponse<SecurityEvent>>('/v1/events', { params })
}

// 获取事件详情
export function getEventDetail(eventId: string) {
  return api.get<SecurityEvent>(`/v1/events/${eventId}`)
}

// 更新事件状态
export function updateEventStatus(eventId: string, status: EventStatus) {
  return api.put(`/v1/events/${eventId}/status`, { status })
}

// 批量处理事件
export function batchProcessEvents(eventIds: string[], action: string) {
  return api.post('/v1/events/batch', {
    eventIds,
    action
  })
}

// 删除事件
export function deleteEvent(eventId: string) {
  return api.delete(`/v1/events/${eventId}`)
}

// 批量删除事件
export function batchDeleteEvents(eventIds: string[]) {
  return api.delete('/v1/events/batch', {
    data: { eventIds }
  })
} 