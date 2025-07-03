<template>
  <div class="event-detail">
    <div class="page-header">
      <h1 class="title">事件详情</h1>
      <el-button @click="$router.back()">
        <el-icon><ArrowLeft /></el-icon>
        返回
      </el-button>
    </div>

    <el-card>
      <div class="placeholder">
        <el-icon size="64" color="#909399">
          <Document />
        </el-icon>
        <p>事件详情页面正在开发中...</p>
        <p>事件ID: {{ $route.params.id }}</p>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ArrowLeft, Document } from '@element-plus/icons-vue'
</script>

<style scoped lang="scss">
.event-detail {
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
  
  .placeholder {
    text-align: center;
    padding: 60px 20px;
    color: #909399;
    
    p {
      margin: 10px 0;
      font-size: 16px;
    }
  }
}
</style> 