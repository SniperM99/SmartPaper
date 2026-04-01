<template>
  <div class="content-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1 class="page-title">工作台总览</h1>
      <p class="page-subtitle">欢迎回来！以下是您的研究工作概览</p>
    </div>

    <!-- 操作按钮 -->
    <div class="page-actions">
      <button class="btn btn-primary">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 5v14M5 12h14"/>
        </svg>
        导入新论文
      </button>
      <button class="btn btn-secondary">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M17 8l-5-5-5 5M12 3v12"/>
        </svg>
        批量导入
      </button>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon stat-icon-primary">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/>
          </svg>
        </div>
        <div class="stat-label">论文总数</div>
        <div class="stat-value">24</div>
        <div class="stat-change positive">↑ 12% 较上周</div>
      </div>

      <div class="stat-card">
        <div class="stat-icon stat-icon-success">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
        </div>
        <div class="stat-label">已分析</div>
        <div class="stat-value">18</div>
        <div class="stat-change positive">↑ 8% 较上周</div>
      </div>

      <div class="stat-card">
        <div class="stat-icon stat-icon-warning">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
        </div>
        <div class="stat-label">待处理</div>
        <div class="stat-value">6</div>
        <div class="stat-change negative">↓ 2% 较上周</div>
      </div>

      <div class="stat-card">
        <div class="stat-icon stat-icon-info">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M13 10V3L4 14h7v7l9-11h-7z"/>
          </svg>
        </div>
        <div class="stat-label">本周分析</div>
        <div class="stat-value">12</div>
        <div class="stat-change positive">↑ 20% 较上周</div>
      </div>
    </div>

    <!-- Tabs 区域 -->
    <div class="tabs-container">
      <div class="tabs-header">
        <div
          v-for="tab in tabs"
          :key="tab.key"
          class="tab-item"
          :class="{ active: activeTab === tab.key }"
          @click="activeTab = tab.key"
        >
          {{ tab.label }}
        </div>
      </div>

      <div class="tab-content">
        <div v-if="activeTab === 'recent'" class="tab-pane active">
          <div class="grid grid-cols-2 gap-6">
            <!-- 论文卡片示例 -->
            <div class="card card-clickable" v-for="i in 4" :key="i">
              <div class="card-header">
                <h3 class="card-title">Deep Learning for Natural Language Processing</h3>
              </div>
              <div class="card-body">
                <p class="text-secondary mb-2">Authors: Smith, J., Johnson, M.</p>
                <p class="text-secondary mb-2">Published: 2024</p>
                <div class="flex items-center gap-2">
                  <span class="badge badge-success-light">已完成</span>
                  <span class="badge badge-info-light">机器学习</span>
                </div>
              </div>
              <div class="card-footer">
                <span class="text-sm text-tertiary">最后更新: 2小时前</span>
              </div>
            </div>
          </div>
        </div>

        <div v-if="activeTab === 'progress'" class="tab-pane active">
          <div class="card">
            <div class="card-body">
              <div class="text-center py-8">
                <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" class="text-light">
                  <path d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
                </svg>
                <p class="text-secondary mt-4">分析进度图表将在此处显示</p>
              </div>
            </div>
          </div>
        </div>

        <div v-if="activeTab === 'activities'" class="tab-pane active">
          <div class="card">
            <div class="card-body">
              <div class="flex items-center gap-4 mb-4">
                <div class="badge badge-success-light"></div>
                <div>
                  <p class="font-semibold">论文 "Transformer Architecture" 分析完成</p>
                  <p class="text-sm text-tertiary">2小时前</p>
                </div>
              </div>
              <div class="flex items-center gap-4 mb-4">
                <div class="badge badge-info-light"></div>
                <div>
                  <p class="font-semibold">批量导入 5 篇新论文</p>
                  <p class="text-sm text-tertiary">4小时前</p>
                </div>
              </div>
              <div class="flex items-center gap-4">
                <div class="badge badge-warning-light"></div>
                <div>
                  <p class="font-semibold">论文 "Attention Mechanism" 分析失败</p>
                  <p class="text-sm text-tertiary">6小时前</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const activeTab = ref('recent')

const tabs = [
  { key: 'recent', label: '最近论文' },
  { key: 'progress', label: '分析进度' },
  { key: 'activities', label: '最近活动' }
]
</script>

<style scoped>
/* 页面特定样式 */
</style>
