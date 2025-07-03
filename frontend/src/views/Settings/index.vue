<template>
  <div class="settings-page">
    <div class="page-header">
      <h1 class="title">系统配置</h1>
    </div>

    <el-card>
      <div class="placeholder">
        <el-icon size="64" color="#909399">
          <Setting />
        </el-icon>
        <p>系统配置页面正在开发中...</p>
        <p>将包含检测规则配置、AI模型设置、告警策略等功能</p>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { Setting } from '@element-plus/icons-vue'
</script>

<style scoped lang="scss">
.settings-page {
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