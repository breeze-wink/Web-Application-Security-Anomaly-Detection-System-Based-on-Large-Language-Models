<template>
  <div class="analytics-page">
    <div class="page-header">
      <h1 class="title">统计分析</h1>
    </div>

    <el-card>
      <div class="placeholder">
        <el-icon size="64" color="#909399">
          <DataAnalysis />
        </el-icon>
        <p>统计分析页面正在开发中...</p>
        <p>将包含威胁趋势分析、攻击类型统计、AI分析报告等功能</p>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { DataAnalysis } from '@element-plus/icons-vue'
</script>

<style scoped lang="scss">
.analytics-page {
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