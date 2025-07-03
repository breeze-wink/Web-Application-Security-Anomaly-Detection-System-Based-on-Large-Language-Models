<template>
  <div class="app-layout">
    <!-- 侧边栏 -->
    <aside class="sidebar" :class="{ collapsed: sidebarCollapsed }">
      <div class="logo">
        <h1>{{ sidebarCollapsed ? '安全' : 'Web安全管理' }}</h1>
      </div>
      
      <nav class="navigation">
        <el-menu
          :default-active="$route.path"
          :unique-opened="true"
          :collapse="sidebarCollapsed"
          router
          text-color="#fff"
          active-text-color="#409EFF"
          background-color="#304156"
        >
          <el-menu-item index="/dashboard">
            <el-icon><Monitor /></el-icon>
            <span>监控大屏</span>
          </el-menu-item>
          
          <el-menu-item index="/events">
            <el-icon><Warning /></el-icon>
            <span>事件管理</span>
          </el-menu-item>
          
          <el-menu-item index="/analytics">
            <el-icon><DataAnalysis /></el-icon>
            <span>统计分析</span>
          </el-menu-item>
          
          <el-menu-item index="/settings">
            <el-icon><Setting /></el-icon>
            <span>系统配置</span>
          </el-menu-item>
        </el-menu>
      </nav>
    </aside>

    <!-- 主内容区域 -->
    <main class="main-content">
      <!-- 顶部导航 -->
      <header class="header">
        <div class="header-left">
          <el-button 
            :icon="sidebarCollapsed ? 'Expand' : 'Fold'"
            @click="toggleSidebar"
            text
          />
          <span class="page-title">{{ currentPageTitle }}</span>
        </div>
        
        <div class="header-right">
          <!-- 实时状态 -->
          <div class="status-indicator">
            <el-badge :value="pendingCount" :max="99" class="badge">
              <el-icon class="status-icon" :class="systemStatus">
                <CircleCheckFilled v-if="systemStatus === 'normal'" />
                <WarningFilled v-else-if="systemStatus === 'warning'" />
                <CircleCloseFilled v-else />
              </el-icon>
            </el-badge>
            <span class="status-text">{{ systemStatusText }}</span>
          </div>
          
          <!-- 刷新按钮 -->
          <el-button :icon="Refresh" @click="refreshData" circle />
        </div>
      </header>

      <!-- 页面内容 -->
      <div class="page-content">
        <RouterView />
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useEventsStore } from '@/stores/events'
import { 
  Monitor, Warning, DataAnalysis, Setting, 
  Expand, Fold, Refresh,
  CircleCheckFilled, WarningFilled, CircleCloseFilled
} from '@element-plus/icons-vue'

// 状态管理
const eventsStore = useEventsStore()
const route = useRoute()

// 响应式状态
const sidebarCollapsed = ref(false)
const systemStatus = ref<'normal' | 'warning' | 'error'>('normal')

// 计算属性
const currentPageTitle = computed(() => {
  return route.meta?.title || '页面'
})

const pendingCount = computed(() => {
  return eventsStore.pendingEventsCount
})

const systemStatusText = computed(() => {
  const statusMap = {
    normal: '系统正常',
    warning: '系统警告',
    error: '系统错误'
  }
  return statusMap[systemStatus.value]
})

// 方法
const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

const refreshData = () => {
  // 刷新当前页面数据
  eventsStore.refreshEvents()
}

// 生命周期
onMounted(() => {
  // 初始化数据
  eventsStore.fetchEvents()
})
</script>

<style scoped lang="scss">
.app-layout {
  display: flex;
  height: 100vh;
  background-color: #f5f7fa;
}

.sidebar {
  width: 250px;
  background-color: #304156;
  color: #fff;
  transition: width 0.3s ease;
  
  &.collapsed {
    width: 64px;
  }
  
  .logo {
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-bottom: 1px solid #434a50;
    
    h1 {
      font-size: 18px;
      font-weight: 500;
      margin: 0;
    }
  }
  
  .navigation {
    height: calc(100vh - 60px);
    overflow-y: auto;
    
    :deep(.el-menu) {
      border-right: none;
      
      .el-menu-item {
        &:hover {
          background-color: #263445;
        }
        
        &.is-active {
          background-color: #409EFF;
        }
      }
    }
  }
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.header {
  height: 60px;
  background-color: #fff;
  border-bottom: 1px solid #e4e7ed;
  padding: 0 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  
  .header-left {
    display: flex;
    align-items: center;
    gap: 15px;
    
    .page-title {
      font-size: 16px;
      font-weight: 500;
      color: #303133;
    }
  }
  
  .header-right {
    display: flex;
    align-items: center;
    gap: 15px;
    
    .status-indicator {
      display: flex;
      align-items: center;
      gap: 8px;
      
      .status-icon {
        font-size: 16px;
        
        &.normal {
          color: #67C23A;
        }
        
        &.warning {
          color: #E6A23C;
        }
        
        &.error {
          color: #F56C6C;
        }
      }
      
      .status-text {
        font-size: 12px;
        color: #909399;
      }
    }
  }
}

.page-content {
  flex: 1;
  overflow: auto;
  padding: 20px;
}

// 响应式适配
@media (max-width: 768px) {
  .sidebar {
    width: 64px;
    
    &.collapsed {
      width: 0;
    }
  }
  
  .header {
    padding: 0 15px;
    
    .header-left {
      gap: 10px;
    }
    
    .header-right {
      gap: 10px;
    }
  }
  
  .page-content {
    padding: 15px;
  }
}
</style> 