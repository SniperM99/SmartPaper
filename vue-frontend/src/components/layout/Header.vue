<template>
  <header class="header">
    <div class="header-left">
      <!-- 侧边栏切换按钮 -->
      <button class="btn-icon" @click="toggleSidebar">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="3" y1="12" x2="21" y2="12"/>
          <line x1="3" y1="6" x2="21" y2="6"/>
          <line x1="3" y1="18" x2="21" y2="18"/>
        </svg>
      </button>

      <!-- 面包屑导航 -->
      <nav class="header-breadcrumb">
        <span class="breadcrumb-item">
          <span class="breadcrumb-separator">/</span>
          <span class="breadcrumb-item active">{{ currentPage }}</span>
        </span>
      </nav>
    </div>

    <div class="header-right">
      <!-- 搜索框 -->
      <div class="search-box">
        <IconSearch />
        <input
          type="text"
          placeholder="搜索论文..."
          class="input search-input"
        />
      </div>

      <!-- 通知图标 -->
      <button class="btn-icon" title="通知">
        <IconBell />
        <span class="notification-badge">3</span>
      </button>

      <!-- 用户头像 -->
      <button class="btn-icon user-btn" title="用户菜单">
        <div class="user-avatar">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
            <circle cx="12" cy="7" r="4"/>
          </svg>
        </div>
      </button>
    </div>
  </header>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import IconSearch from '../icons/IconSearch.vue'
import IconBell from '../icons/IconBell.vue'

const route = useRoute()

// 当前页面名称
const currentPage = computed(() => {
  const pathMap: Record<string, string> = {
    'overview': '工作台总览',
    'intake': '导入与解析',
    'library': '论文库',
    'analysis': '分析工作流',
    'zotero': 'Zotero 集成',
    'settings': '系统设置',
    'help': '帮助文档'
  }

  const pathSegments = route.path.split('/').filter(Boolean)
  const firstSegment = pathSegments[0] || 'overview'
  return pathMap[firstSegment] || firstSegment
})

// 切换侧边栏
const toggleSidebar = () => {
  // 触发侧边栏切换事件
}
</script>

<style scoped>
.search-box {
  display: flex;
  align-items: center;
  gap: 8px;
  position: relative;
}

.search-box > svg {
  position: absolute;
  left: 12px;
  width: 16px;
  height: 16px;
  color: var(--color-text-light);
  pointer-events: none;
}

.search-input {
  width: 240px;
  padding-left: 36px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  height: 36px;
  font-size: 14px;
}

.search-input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(30, 64, 175, 0.1);
}

.notification-badge {
  position: absolute;
  top: 4px;
  right: 4px;
  width: 16px;
  height: 16px;
  background-color: var(--color-error);
  color: white;
  border-radius: 50%;
  font-size: 10px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background-color: var(--color-primary);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-icon {
  position: relative;
}
</style>
