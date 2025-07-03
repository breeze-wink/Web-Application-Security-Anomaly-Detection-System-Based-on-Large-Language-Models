// 通用响应接口
export interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
  timestamp: string
}

// 分页响应接口
export interface PageResponse<T = any> {
  list: T[]
  total: number
  page: number
  size: number
}

// 安全事件接口
export interface SecurityEvent {
  id: string
  eventId: string
  sourceIp: string
  targetUrl: string
  httpMethod: string
  userAgent: string
  threatType: ThreatType
  severityLevel: SeverityLevel
  detectionTime: string
  rawRequest: string
  attackPayload: string
  aiAnalysis: string
  status: EventStatus
  createdAt: string
  updatedAt: string
}

// 威胁类型枚举
export type ThreatType = 
  | 'sql_injection'
  | 'xss'
  | 'command_injection'
  | 'path_traversal'
  | 'brute_force'
  | 'other'

// 威胁级别枚举
export type SeverityLevel = 'low' | 'medium' | 'high' | 'critical'

// 事件状态枚举
export type EventStatus = 'pending' | 'confirmed' | 'false_positive' | 'resolved'

// 统计数据接口
export interface ThreatStatistics {
  threatType: ThreatType
  count: number
  percentage: number
}

// 趋势数据接口
export interface TrendData {
  date: string
  count: number
  threatType?: ThreatType
}

// 仪表板数据接口
export interface DashboardData {
  todayAttacks: number
  blockedThreats: number
  uniqueIps: number
  systemStatus: 'normal' | 'warning' | 'error'
  threatStats: ThreatStatistics[]
  recentEvents: SecurityEvent[]
  trendData: TrendData[]
}

// IP黑名单接口
export interface IpBlacklist {
  id: string
  ipAddress: string
  reason: string
  threatCount: number
  firstSeen: string
  lastSeen: string
  status: 'active' | 'inactive'
  createdAt: string
  updatedAt: string
}

// 搜索表单接口
export interface EventSearchForm {
  threatType?: ThreatType | ''
  severityLevel?: SeverityLevel | ''
  status?: EventStatus | ''
  sourceIp?: string
  dateRange?: [string, string]
  keyword?: string
}

// 系统配置接口
export interface SystemConfig {
  id: string
  key: string
  value: string
  description: string
  type: 'string' | 'number' | 'boolean' | 'json'
  updatedAt: string
}

// WebSocket消息接口
export interface WebSocketMessage {
  type: 'new_event' | 'stats_update' | 'system_alert'
  data: any
  timestamp: string
} 