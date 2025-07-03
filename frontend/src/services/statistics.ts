import api from './api'
import type { 
  DashboardData, 
  ThreatStatistics, 
  TrendData,
  IpBlacklist 
} from '@/types'

// 获取仪表板数据
export function getDashboardData() {
  return api.get<DashboardData>('/v1/statistics/dashboard')
}

// 获取威胁趋势数据
export function getThreatTrends(params: {
  startDate: string
  endDate: string
  granularity?: 'hour' | 'day' | 'week'
}) {
  return api.get<TrendData[]>('/v1/statistics/trends', { params })
}

// 获取威胁类型分布
export function getThreatTypeDistribution(params: {
  startDate: string
  endDate: string
}) {
  return api.get<ThreatStatistics[]>('/v1/statistics/threat-types', { params })
}

// 获取TOP攻击IP
export function getTopAttackIPs(params: {
  startDate: string
  endDate: string
  limit?: number
}) {
  return api.get<Array<{
    ip: string
    count: number
    threatTypes: string[]
    lastSeen: string
  }>>('/v1/statistics/top-ips', { params })
}

// 获取实时统计
export function getRealTimeStats() {
  return api.get<{
    currentAttacks: number
    activeConnections: number
    systemLoad: number
    memoryUsage: number
  }>('/v1/monitoring/realtime')
}

// 获取系统健康状态
export function getSystemHealth() {
  return api.get<{
    status: 'healthy' | 'warning' | 'error'
    components: Array<{
      name: string
      status: 'healthy' | 'warning' | 'error'
      message: string
    }>
  }>('/v1/monitoring/health')
}

// 生成分析报告
export function generateReport(params: {
  startDate: string
  endDate: string
  reportType: 'daily' | 'weekly' | 'monthly'
}) {
  return api.post<{
    reportId: string
    content: string
    generatedAt: string
  }>('/v1/statistics/report', params)
} 