<template>
  <aside class="sidebar" :class="{ collapsed: isCollapsed }">
    <!-- Logo 区域 -->
    <div class="sidebar-logo">
      <div class="sidebar-logo-icon">
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/>
          <polyline points="14 2 14 8 20 8"/>
          <path d="M12 18v-6"/>
          <path d="M9 15l3 3 3-3"/>
        </svg>
      </div>
      <span class="sidebar-logo-text">SmartPaper</span>
    </div>

    <!-- 导航菜单 -->
    <nav class="sidebar-nav">
      <!-- 工作区 -->
      <div class="sidebar-nav-group">
        <div class="sidebar-nav-group-title">工作区</div>

        <router-link
          v-for="item in workspaceItems"
          :key="item.key"
          :to="item.path"
          class="nav-item"
          :class="{ active: isActive(item.key) }"
        >
          <component :is="item.icon" />
          <span class="nav-item-text">{{ item.label }}</span>
          <span v-if="item.badge" class="nav-item-badge">{{ item.badge }}</span>
        </router-link>
      </div>

      <!-- 分析工具 -->
      <div class="sidebar-nav-group">
        <div class="sidebar-nav-group-title">分析工具</div>

        <router-link
          v-for="item in toolItems"
          :key="item.key"
          :to="item.path"
          class="nav-item"
          :class="{ active: isActive(item.key) }"
        >
          <component :is="item.icon" />
          <span class="nav-item-text">{{ item.label }}</span>
        </router-link>
      </div>

      <!-- 设置 -->
      <div class="sidebar-nav-group">
        <div class="sidebar-nav-group-title">设置</div>

        <router-link
          v-for="item in settingItems"
          :key="item.key"
          :to="item.path"
          class="nav-item"
          :class="{ active: isActive(item.key) }"
        >
          <component :is="item.icon" />
          <span class="nav-item-text">{{ item.label }}</span>
        </router-link>
      </div>
    </nav>

    <!-- 用户信息 -->
    <div class="sidebar-footer">
      <div class="sidebar-user">
        <div class="sidebar-user-avatar">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
            <circle cx="12" cy="7" r="4"/>
          </svg>
        </div>
        <div class="sidebar-user-info">
          <div class="sidebar-user-name">User Name</div>
          <div class="sidebar-user-email">user@example.com</div>
        </div>
      </div>
    </div>

    <!-- 遮罩层（移动端） -->
    <div class="sidebar-overlay" :class="{ active: isOpen }" @click="closeSidebar"></div>
  </aside>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import IconHome from '../icons/IconHome.vue'
import IconUpload from '../icons/IconUpload.vue'
import IconLibrary from '../icons/IconLibrary.vue'
import IconAnalysis from '../icons/IconAnalysis.vue'
import IconFileText from '../icons/IconFileText.vue'
import IconCompare from '../icons/IconCompare.vue'
import IconMap from '../icons/IconMap.vue'
import IconDatabase from '../icons/IconDatabase.vue'
import IconSettings from '../icons/IconSettings.vue'

const route = useRoute()

const isCollapsed = computed(() => false) // 可从状态管理获取
const isOpen = computed(() => false) // 可从状态管理获取

// 工作区导航项
const workspaceItems = [
  {
    key: 'overview',
    label: '工作台总览',
    path: '/overview',
    icon: IconHome,
    badge: null
  },
  {
    key: 'intake',
    label: '导入与解析',
    path: '/intake',
    icon: IconUpload,
    badge: null
  },
  {
    key: 'library',
    label: '论文库',
    path: '/library',
    icon: IconLibrary,
    badge: '12'
  },
  {
    key: 'analysis',
    label: '分析工作流',
    path: '/analysis',
    icon: IconAnalysis,
    badge: null
  },
  {
    key: 'zotero',
    label: 'Zotero 集成',
    path: '/zotero',
    icon: IconDatabase,
    badge: null
  }
]

// 分析工具导航项
const toolItems = [
  {
    key: 'single-paper',
    label: '单篇分析',
    path: '/analysis/single',
    icon: IconFileText,
    badge: null
  },
  {
    key: 'multi-paper',
    label: '多篇对比',
    path: '/analysis/multi',
    icon: IconCompare,
    badge: null
  },
  {
    key: 'research-map',
    label: '研究地图',
    path: '/analysis/map',
    icon: IconMap,
    badge: null
  }
]

// 设置导航项
const settingItems = [
  {
    key: 'settings',
    label: '系统设置',
    path: '/settings',
    icon: IconSettings,
    badge: null
  },
  {
    key: 'help',
    label: '帮助文档',
    path: '/help',
    icon: IconHome,
    badge: null
  }
]

// 检查是否为当前激活的路由
const isActive = (key: string): boolean => {
  return route.path.startsWith(`/${key}`)
}

// 关闭侧边栏（移动端）
const closeSidebar = () => {
  // 触发侧边栏关闭事件
}
</script>

<style scoped>
/* 组件特定的样式可以在这里添加 */
.sidebar-logo-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.sidebar-user-avatar {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-full);
  background-color: rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}
</style>
