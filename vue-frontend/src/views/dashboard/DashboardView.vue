<template>
  <div class="dashboard-view">
    <!-- 页面头部 -->
    <div class="page-header">
      <div>
        <h1 class="page-title">管理后台</h1>
        <p class="page-subtitle">系统概览和统计分析</p>
      </div>
      <div class="page-actions">
        <button class="btn btn-secondary">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
            <polyline points="7 10 12 15 17 10"/>
            <line x1="12" y1="15" x2="12" y2="3"/>
          </svg>
          导出数据
        </button>
        <button class="btn btn-primary">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="12" y1="5" x2="12" y2="19"/>
            <line x1="5" y1="12" x2="19" y2="12"/>
          </svg>
          添加新用户
        </button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <StatCard
        label="论文总数"
        :value="stats.totalPapers"
        change="12%"
        variant="primary"
      >
        <template #icon>
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/>
            <polyline points="14 2 14 8 20 8"/>
          </svg>
        </template>
      </StatCard>

      <StatCard
        label="已分析"
        :value="stats.analyzed"
        change="8%"
        variant="success"
      >
        <template #icon>
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
            <polyline points="22 4 12 14.01 9 11.01"/>
          </svg>
        </template>
      </StatCard>

      <StatCard
        label="待处理"
        :value="stats.pending"
        change="-2%"
        variant="warning"
      >
        <template #icon>
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <polyline points="12 6 12 12 16 14"/>
          </svg>
        </template>
      </StatCard>

      <StatCard
        label="活跃用户"
        :value="stats.activeUsers"
        change="20%"
        variant="info"
      >
        <template #icon>
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
            <circle cx="9" cy="7" r="4"/>
            <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
            <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
          </svg>
        </template>
      </StatCard>
    </div>

    <!-- 内容区域 -->
    <div class="content-grid">
      <!-- 最近用户 -->
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">最近用户</h3>
          <router-link to="/admin/users" class="link">查看全部</router-link>
        </div>
        <div class="card-body">
          <DataTable
            :data="recentUsers"
            :columns="userColumns"
            :show-pagination="false"
            row-key="id"
          >
            <template #cell-status="{ value }">
              <span class="badge" :class="`badge-${value.toLowerCase()}-light`">
                {{ value }}
              </span>
            </template>
            <template #actions="{ row }">
              <button class="btn-icon" title="编辑">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                  <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                </svg>
              </button>
              <button class="btn-icon" title="删除" style="color: var(--color-error);">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M3 6h18"/>
                  <path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/>
                  <path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/>
                </svg>
              </button>
            </template>
          </DataTable>
        </div>
      </div>

      <!-- 系统状态 -->
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">系统状态</h3>
          <button class="btn btn-sm btn-secondary">刷新</button>
        </div>
        <div class="card-body">
          <div class="system-status">
            <div class="status-item" v-for="item in systemStatus" :key="item.name">
              <div class="status-info">
                <div class="status-name">{{ item.name }}</div>
                <div class="status-value">{{ item.value }}</div>
              </div>
              <div class="status-indicator" :class="`status-${item.status}`">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle v-if="item.status === 'running'" cx="12" cy="12" r="10"/>
                  <circle v-else-if="item.status === 'stopped'" cx="12" cy="12" r="10"/>
                  <path v-if="item.status === 'running'" d="M12 6v6l4 2"/>
                  <line v-else-if="item.status === 'stopped'" x1="15" y1="9" x2="9" y2="15"/>
                  <line v-else-if="item.status === 'stopped'" x1="9" y1="9" x2="15" y2="15"/>
                </svg>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 最近活动 -->
      <div class="card" style="grid-column: 1 / -1;">
        <div class="card-header">
          <h3 class="card-title">最近活动</h3>
        </div>
        <div class="card-body">
          <div class="activity-list">
            <div class="activity-item" v-for="activity in recentActivities" :key="activity.id">
              <div class="activity-icon" :class="`activity-icon-${activity.type}`">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path v-if="activity.type === 'upload'" d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                  <polyline v-if="activity.type === 'upload'" points="17 8 12 3 7 8"/>
                  <line v-if="activity.type === 'upload'" x1="12" x2="12" y1="3" y2="15"/>
                  <path v-else-if="activity.type === 'analysis'" d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/>
                  <polyline v-else-if="activity.type === 'analysis'" points="14 2 14 8 20 8"/>
                  <path v-else-if="activity.type === 'user'" d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                  <circle v-else-if="activity.type === 'user'" cx="12" cy="7" r="4"/>
                </svg>
              </div>
              <div class="activity-content">
                <div class="activity-title">{{ activity.title }}</div>
                <div class="activity-description">{{ activity.description }}</div>
                <div class="activity-time">{{ activity.time }}</div>
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
import StatCard from '@/components/common/StatCard.vue'
import DataTable from '@/components/common/DataTable.vue'

// 统计数据
const stats = ref({
  totalPapers: 156,
  analyzed: 128,
  pending: 28,
  activeUsers: 45
})

// 用户表格列
const userColumns = [
  { key: 'name', title: '姓名' },
  { key: 'email', title: '邮箱' },
  { key: 'status', title: '状态' },
  { key: 'lastLogin', title: '最后登录' }
]

// 最近用户数据
const recentUsers = ref([
  { id: 1, name: '张三', email: 'zhangsan@example.com', status: 'Active', lastLogin: '2小时前' },
  { id: 2, name: '李四', email: 'lisi@example.com', status: 'Active', lastLogin: '5小时前' },
  { id: 3, name: '王五', email: 'wangwu@example.com', status: 'Inactive', lastLogin: '3天前' },
  { id: 4, name: '赵六', email: 'zhaoliu@example.com', status: 'Active', lastLogin: '1天前' },
])

// 系统状态
const systemStatus = ref([
  { name: 'API 服务器', value: '99.9%', status: 'running' },
  { name: '数据库', value: '正常', status: 'running' },
  { name: '缓存服务', value: '正常', status: 'running' },
  { name: '任务队列', value: '2 个待处理', status: 'running' },
])

// 最近活动
const recentActivities = ref([
  {
    id: 1,
    type: 'upload',
    title: '新论文上传',
    description: '张三上传了《深度学习在自然语言处理中的应用》',
    time: '10分钟前'
  },
  {
    id: 2,
    type: 'analysis',
    title: '分析完成',
    description: '《机器学习基础》分析完成，生成报告',
    time: '30分钟前'
  },
  {
    id: 3,
    type: 'user',
    title: '新用户注册',
    description: '用户 user@example.com 完成注册',
    time: '1小时前'
  },
  {
    id: 4,
    type: 'analysis',
    title: '批量分析启动',
    description: '开始批量分析 10 篇论文',
    time: '2小时前'
  },
  {
    id: 5,
    type: 'upload',
    title: '论文更新',
    description: '李四更新了《计算机视觉综述》',
    time: '3小时前'
  }
])
</script>

<style scoped>
.dashboard-view {
  padding: 24px;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 32px;
}

.page-title {
  font-size: 32px;
  font-weight: 700;
  color: var(--color-text-primary);
  margin-bottom: 8px;
}

.page-subtitle {
  font-size: 14px;
  color: var(--color-text-secondary);
  margin: 0;
}

.page-actions {
  display: flex;
  gap: 12px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 20px;
  margin-bottom: 32px;
}

.content-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.card {
  background: white;
  border: 1px solid var(--color-border);
  border-radius: 12px;
  overflow: hidden;
}

.card-header {
  padding: 20px 24px;
  border-bottom: 1px solid var(--color-border);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0;
}

.card-body {
  padding: 24px;
}

.link {
  color: var(--color-primary);
  font-size: 14px;
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
}

.system-status {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.status-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.status-info {
  flex: 1;
}

.status-name {
  font-size: 14px;
  color: var(--color-text-primary);
  margin-bottom: 4px;
}

.status-value {
  font-size: 13px;
  color: var(--color-text-tertiary);
}

.status-indicator {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.status-running {
  background-color: var(--color-success-light);
  color: var(--color-success);
}

.status-stopped {
  background-color: var(--color-error-light);
  color: var(--color-error);
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.activity-item {
  display: flex;
  gap: 16px;
  padding: 16px;
  background-color: var(--color-bg-secondary);
  border-radius: 8px;
}

.activity-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.activity-icon-upload {
  background-color: var(--color-primary-light);
  color: var(--color-primary);
}

.activity-icon-analysis {
  background-color: var(--color-info-light);
  color: var(--color-info);
}

.activity-icon-user {
  background-color: var(--color-success-light);
  color: var(--color-success);
}

.activity-content {
  flex: 1;
}

.activity-title {
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text-primary);
  margin-bottom: 4px;
}

.activity-description {
  font-size: 13px;
  color: var(--color-text-secondary);
  margin-bottom: 4px;
}

.activity-time {
  font-size: 12px;
  color: var(--color-text-tertiary);
}

@media (max-width: 1024px) {
  .content-grid {
    grid-template-columns: 1fr;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
}
</style>
