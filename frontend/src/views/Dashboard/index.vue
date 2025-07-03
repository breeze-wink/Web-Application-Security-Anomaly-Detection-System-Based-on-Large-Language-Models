<template>
  <div class="dashboard">
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="12" :sm="6" :md="6" :lg="6" :xl="6">
        <div class="stats-card danger">
          <div class="stats-value">{{ dashboardData.todayAttacks }}</div>
          <div class="stats-title">今日攻击次数</div>
          <div class="stats-trend up">
            <el-icon><TrendCharts /></el-icon>
            较昨日 +12%
          </div>
        </div>
      </el-col>
      
      <el-col :xs="12" :sm="6" :md="6" :lg="6" :xl="6">
        <div class="stats-card success">
          <div class="stats-value">{{ dashboardData.blockedThreats }}</div>
          <div class="stats-title">已拦截威胁</div>
          <div class="stats-trend down">
            <el-icon><TrendCharts /></el-icon>
            较昨日 -8%
          </div>
        </div>
      </el-col>
      
      <el-col :xs="12" :sm="6" :md="6" :lg="6" :xl="6">
        <div class="stats-card warning">
          <div class="stats-value">{{ dashboardData.uniqueIps }}</div>
          <div class="stats-title">独立IP访问</div>
          <div class="stats-trend up">
            <el-icon><TrendCharts /></el-icon>
            较昨日 +5%
          </div>
        </div>
      </el-col>
      
      <el-col :xs="12" :sm="6" :md="6" :lg="6" :xl="6">
        <div class="stats-card info">
          <div class="stats-value">{{ systemStatusText }}</div>
          <div class="stats-title">系统状态</div>
          <div class="stats-trend">
            <el-icon><CircleCheckFilled /></el-icon>
            运行正常
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="20" class="charts-row">
      <el-col :xs="24" :sm="16" :md="16" :lg="16" :xl="16">
        <div class="chart-container">
          <div class="chart-title">威胁趋势分析</div>
          <div class="chart-content" style="height: 300px;">
            <v-chart 
              :option="trendChartOption" 
              autoresize
              style="height: 100%"
            />
          </div>
        </div>
      </el-col>
      
      <el-col :xs="24" :sm="8" :md="8" :lg="8" :xl="8">
        <div class="chart-container">
          <div class="chart-title">威胁类型分布</div>
          <div class="chart-content" style="height: 300px;">
            <v-chart 
              :option="pieChartOption" 
              autoresize
              style="height: 100%"
            />
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 实时事件列表 -->
    <div class="recent-events">
      <div class="section-title">
        <h3>最近事件</h3>
        <el-button type="primary" @click="$router.push('/events')">
          查看全部
        </el-button>
      </div>
      
      <el-table 
        :data="dashboardData.recentEvents" 
        stripe
        style="width: 100%"
      >
        <el-table-column prop="detectionTime" label="检测时间" width="180">
          <template #default="scope">
            {{ formatTime(scope.row.detectionTime) }}
          </template>
        </el-table-column>
        
        <el-table-column prop="sourceIp" label="源IP" width="140" />
        
        <el-table-column prop="threatType" label="威胁类型" width="120">
          <template #default="scope">
            <el-tag :type="getThreatTypeColor(scope.row.threatType)">
              {{ getThreatTypeName(scope.row.threatType) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="severityLevel" label="威胁级别" width="100">
          <template #default="scope">
            <el-tag :type="getSeverityColor(scope.row.severityLevel)">
              {{ getSeverityName(scope.row.severityLevel) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="targetUrl" label="目标URL" show-overflow-tooltip />
        
        <el-table-column label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusColor(scope.row.status)">
              {{ getStatusName(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="120">
          <template #default="scope">
            <el-button 
              type="primary" 
              size="small" 
              @click="viewDetail(scope.row)"
            >
              查看详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, PieChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
} from 'echarts/components'
import VChart from 'vue-echarts'
import { TrendCharts, CircleCheckFilled } from '@element-plus/icons-vue'
import { getDashboardData } from '@/services/statistics'
import type { DashboardData, SecurityEvent } from '@/types'
import dayjs from 'dayjs'

// 注册ECharts组件
use([
  CanvasRenderer,
  LineChart,
  PieChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
])

const router = useRouter()

// 响应式数据
const dashboardData = ref<DashboardData>({
  todayAttacks: 0,
  blockedThreats: 0,
  uniqueIps: 0,
  systemStatus: 'normal',
  threatStats: [],
  recentEvents: [],
  trendData: []
})

// 计算属性
const systemStatusText = computed(() => {
  const statusMap = {
    normal: '正常',
    warning: '警告',
    error: '错误'
  }
  return statusMap[dashboardData.value.systemStatus]
})

// 趋势图配置
const trendChartOption = computed(() => ({
  title: {
    show: false
  },
  tooltip: {
    trigger: 'axis'
  },
  legend: {
    data: ['攻击次数']
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    containLabel: true
  },
  xAxis: {
    type: 'category',
    data: dashboardData.value.trendData.map(item => item.date)
  },
  yAxis: {
    type: 'value'
  },
  series: [
    {
      name: '攻击次数',
      type: 'line',
      data: dashboardData.value.trendData.map(item => item.count),
      smooth: true,
      lineStyle: {
        color: '#409EFF'
      },
      areaStyle: {
        color: 'rgba(64, 158, 255, 0.1)'
      }
    }
  ]
}))

// 饼图配置
const pieChartOption = computed(() => ({
  tooltip: {
    trigger: 'item',
    formatter: '{a} <br/>{b}: {c} ({d}%)'
  },
  legend: {
    orient: 'vertical',
    left: 'left',
    data: dashboardData.value.threatStats.map(item => getThreatTypeName(item.threatType))
  },
  series: [
    {
      name: '威胁类型',
      type: 'pie',
      radius: '50%',
      data: dashboardData.value.threatStats.map(item => ({
        value: item.count,
        name: getThreatTypeName(item.threatType)
      })),
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowOffsetX: 0,
          shadowColor: 'rgba(0, 0, 0, 0.5)'
        }
      }
    }
  ]
}))

// 工具函数
const formatTime = (time: string) => {
  return dayjs(time).format('YYYY-MM-DD HH:mm:ss')
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

const viewDetail = (event: SecurityEvent) => {
  router.push(`/events/${event.id}`)
}

// 获取仪表板数据
const fetchDashboardData = async () => {
  try {
    const data = await getDashboardData()
    dashboardData.value = data
  } catch (error) {
    console.error('获取仪表板数据失败:', error)
  }
}

// 生命周期
onMounted(() => {
  fetchDashboardData()
})
</script>

<style scoped lang="scss">
.dashboard {
  .stats-row {
    margin-bottom: 20px;
  }
  
  .stats-card {
    background: #fff;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
    text-align: center;
    position: relative;
    
    &.danger {
      border-left: 4px solid #F56C6C;
    }
    
    &.success {
      border-left: 4px solid #67C23A;
    }
    
    &.warning {
      border-left: 4px solid #E6A23C;
    }
    
    &.info {
      border-left: 4px solid #409EFF;
    }
    
    .stats-value {
      font-size: 32px;
      font-weight: bold;
      color: #303133;
      margin: 10px 0;
    }
    
    .stats-title {
      color: #909399;
      font-size: 14px;
      margin-bottom: 10px;
    }
    
    .stats-trend {
      font-size: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 4px;
      
      &.up {
        color: #F56C6C;
      }
      
      &.down {
        color: #67C23A;
      }
    }
  }
  
  .charts-row {
    margin-bottom: 20px;
  }
  
  .chart-container {
    background: #fff;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
    
    .chart-title {
      font-size: 16px;
      font-weight: 500;
      color: #303133;
      margin-bottom: 20px;
    }
  }
  
  .recent-events {
    background: #fff;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
    
    .section-title {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
      
      h3 {
        margin: 0;
        font-size: 16px;
        font-weight: 500;
        color: #303133;
      }
    }
  }
}

// 响应式设计
@media (max-width: 768px) {
  .dashboard {
    .stats-card {
      margin-bottom: 15px;
      
      .stats-value {
        font-size: 24px;
      }
    }
    
    .charts-row {
      .el-col {
        margin-bottom: 15px;
      }
    }
  }
}
</style> 