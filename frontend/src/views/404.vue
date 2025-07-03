<template>
  <div class="not-found">
    <div class="not-found-content">
      <div class="not-found-icon">
        <el-icon size="120" color="#E6A23C">
          <WarningFilled />
        </el-icon>
      </div>
      
      <h1 class="not-found-title">404</h1>
      <p class="not-found-description">抱歉，您访问的页面不存在</p>
      
      <div class="not-found-actions">
        <el-button type="primary" @click="$router.push('/')">
          返回首页
        </el-button>
        <el-button @click="$router.back()">
          返回上一页
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { WarningFilled } from '@element-plus/icons-vue'
</script>

<style scoped lang="scss">
.not-found {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 60vh;
  
  .not-found-content {
    text-align: center;
    
    .not-found-icon {
      margin-bottom: 30px;
    }
    
    .not-found-title {
      font-size: 72px;
      font-weight: bold;
      color: #E6A23C;
      margin: 0 0 20px 0;
    }
    
    .not-found-description {
      font-size: 16px;
      color: #909399;
      margin: 0 0 30px 0;
    }
    
    .not-found-actions {
      display: flex;
      gap: 15px;
      justify-content: center;
    }
  }
}
</style> 