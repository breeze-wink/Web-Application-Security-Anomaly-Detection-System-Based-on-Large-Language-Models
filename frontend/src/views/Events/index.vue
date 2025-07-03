<template>
  <div class="events-page">
    <div class="page-header">
      <h1 class="title">事件管理</h1>
      <div class="actions">
        <el-button type="primary" @click="refreshEvents">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </div>

    <!-- 搜索表单 -->
    <el-card class="search-card">
      <el-form :model="searchForm" :inline="true">
        <el-form-item label="威胁类型">
          <el-select v-model="searchForm.threatType" placeholder="请选择威胁类型">
            <el-option label="全部" value="" />
            <el-option label="SQL注入" value="sql_injection" />
            <el-option label="XSS攻击" value="xss" />
            <el-option label="命令注入" value="command_injection" />
            <el-option label="路径遍历" value="path_traversal" />
            <el-option label="暴力破解" value="brute_force" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>

        <el-form-item label="威胁级别">
          <el-select v-model="searchForm.severityLevel" placeholder="请选择威胁级别">
            <el-option label="全部" value="" />
            <el-option label="低" value="low" />
            <el-option label="中" value="medium" />
            <el-option label="高" value="high" />
            <el-option label="严重" value="critical" />
          </el-select>
        </el-form-item>

        <el-form-item label="处理状态">
          <el-select v-model="searchForm.status" placeholder="请选择处理状态">
            <el-option label="全部" value="" />
            <el-option label="待处理" value="pending" />
            <el-option label="已确认" value="confirmed" />
            <el-option label="误报" value="false_positive" />
            <el-option label="已解决" value="resolved" />
          </el-select>
        </el-form-item>

        <el-form-item label="源IP">
          <el-input v-model="searchForm.sourceIp" placeholder="请输入源IP地址" />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="handleReset">
            <el-icon><Refresh /></el-icon>
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 事件列表 -->
    <el-card class="table-card">
      <el-table 
        :data="events" 
        :loading="loading"
        stripe
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="50" />
        
        <el-table-column prop="detectionTime" label="检测时间" width="160">
          <template #default="scope">
            {{ formatTime(scope.row.detectionTime) }}
          </template>
        </el-table-column>

        <el-table-column prop="sourceIp" label="源IP" width="120" />

        <el-table-column prop="threatType" label="威胁类型" width="100">
          <template #default="scope">
            <el-tag :type="getThreatTypeColor(scope.row.threatType)">
              {{ getThreatTypeName(scope.row.threatType) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="severityLevel" label="威胁级别" width="90">
          <template #default="scope">
            <el-tag :type="getSeverityColor(scope.row.severityLevel)">
              {{ getSeverityName(scope.row.severityLevel) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="targetUrl" label="目标URL" show-overflow-tooltip />

        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusColor(scope.row.status)">
              {{ getStatusName(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button type="primary" size="small" @click="viewDetail(scope.row)">
              详情
            </el-button>
            <el-button type="success" size="small" @click="confirmEvent(scope.row)">
              确认
            </el-button>
            <el-button type="warning" size="small" @click="markAsFalsePositive(scope.row)">
              误报
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh } from '@element-plus/icons-vue'
import { useEventsStore } from '@/stores/events'
import type { SecurityEvent } from '@/types'
import dayjs from 'dayjs'

const router = useRouter()
const eventsStore = useEventsStore()

// 响应式数据
const events = ref<SecurityEvent[]>([])
const loading = ref(false)
const selectedEvents = ref<SecurityEvent[]>([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)

// 搜索表单
const searchForm = ref({
  threatType: '',
  severityLevel: '',
  status: '',
  sourceIp: ''
})

// 工具函数
const formatTime = (time: string) => {
  return dayjs(time).format('MM-DD HH:mm:ss')
}

const getThreatTypeName = (type: string) => {
  const nameMap = {
    'sql_injection': 'SQL注入',
    'xss': 'XSS攻击',
    'command_injection': '命令注入',
    'path_traversal': '路径遍历',
    'brute_force': '暴力破解',
    'other': '其他'
  }
  return nameMap[type] || type
}

const getThreatTypeColor = (type: string) => {
  const colorMap = {
    'sql_injection': 'danger',
    'xss': 'warning',
    'command_injection': 'danger',
    'path_traversal': 'warning',
    'brute_force': 'info',
    'other': 'info'
  }
  return colorMap[type] || 'info'
}

const getSeverityName = (level: string) => {
  const nameMap = {
    'low': '低',
    'medium': '中',
    'high': '高',
    'critical': '严重'
  }
  return nameMap[level] || level
}

const getSeverityColor = (level: string) => {
  const colorMap = {
    'low': 'success',
    'medium': 'warning',
    'high': 'danger',
    'critical': 'danger'
  }
  return colorMap[level] || 'info'
}

const getStatusName = (status: string) => {
  const nameMap = {
    'pending': '待处理',
    'confirmed': '已确认',
    'false_positive': '误报',
    'resolved': '已解决'
  }
  return nameMap[status] || status
}

const getStatusColor = (status: string) => {
  const colorMap = {
    'pending': 'warning',
    'confirmed': 'danger',
    'false_positive': 'info',
    'resolved': 'success'
  }
  return colorMap[status] || 'info'
}

// 事件处理函数
const handleSearch = () => {
  currentPage.value = 1
  fetchEvents()
}

const handleReset = () => {
  searchForm.value = {
    threatType: '',
    severityLevel: '',
    status: '',
    sourceIp: ''
  }
  handleSearch()
}

const handleSelectionChange = (selection: SecurityEvent[]) => {
  selectedEvents.value = selection
}

const handleSizeChange = (newSize: number) => {
  pageSize.value = newSize
  fetchEvents()
}

const handleCurrentChange = (newPage: number) => {
  currentPage.value = newPage
  fetchEvents()
}

const viewDetail = (event: SecurityEvent) => {
  router.push(`/events/${event.id}`)
}

const confirmEvent = async (event: SecurityEvent) => {
  try {
    await eventsStore.updateStatus(event.id, 'confirmed')
    ElMessage.success('事件已确认')
    fetchEvents()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const markAsFalsePositive = async (event: SecurityEvent) => {
  try {
    await eventsStore.updateStatus(event.id, 'false_positive')
    ElMessage.success('已标记为误报')
    fetchEvents()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const refreshEvents = () => {
  fetchEvents()
}

// 获取事件数据
const fetchEvents = async () => {
  loading.value = true
  try {
    // 模拟数据
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    events.value = [
      {
        id: '1',
        eventId: 'EVT-001',
        sourceIp: '192.168.1.100',
        targetUrl: '/login.php?id=1\' OR 1=1--',
        httpMethod: 'GET',
        userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        threatType: 'sql_injection',
        severityLevel: 'high',
        detectionTime: '2024-01-15T10:30:00Z',
        rawRequest: 'GET /login.php?id=1\' OR 1=1-- HTTP/1.1',
        attackPayload: 'id=1\' OR 1=1--',
        aiAnalysis: 'AI分析：检测到SQL注入攻击，尝试绕过登录验证',
        status: 'pending',
        createdAt: '2024-01-15T10:30:00Z',
        updatedAt: '2024-01-15T10:30:00Z'
      }
    ]
    
    total.value = 1
  } catch (error) {
    ElMessage.error('获取数据失败')
  } finally {
    loading.value = false
  }
}

// 生命周期
onMounted(() => {
  fetchEvents()
})
</script>

<style scoped lang="scss">
.events-page {
  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    
    .title {
      margin: 0;
      font-size: 24px;
      font-weight: 500;
      color: #303133;
    }
  }

  .search-card {
    margin-bottom: 20px;
  }

  .table-card {
    .pagination {
      display: flex;
      justify-content: center;
      margin-top: 20px;
    }
  }
}
</style> 