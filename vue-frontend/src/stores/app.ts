/**
 * 应用全局状态管理
 */

import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAppStore = defineStore('app', () => {
  // 侧边栏状态
  const sidebarCollapsed = ref(false)
  const sidebarMobileOpen = ref(false)

  // 主题模式
  const theme = ref<'light' | 'dark'>('light')

  // 加载状态
  const globalLoading = ref(false)

  // 通知消息
  const notifications = ref<Array<{
    id: string
    type: 'success' | 'error' | 'warning' | 'info'
    message: string
    duration?: number
  }>>([])

  // 切换侧边栏
  function toggleSidebar() {
    sidebarCollapsed.value = !sidebarCollapsed.value
  }

  // 设置侧边栏状态
  function setSidebarCollapsed(collapsed: boolean) {
    sidebarCollapsed.value = collapsed
  }

  // 切换移动端侧边栏
  function toggleMobileSidebar() {
    sidebarMobileOpen.value = !sidebarMobileOpen.value
  }

  // 关闭移动端侧边栏
  function closeMobileSidebar() {
    sidebarMobileOpen.value = false
  }

  // 切换主题
  function toggleTheme() {
    theme.value = theme.value === 'light' ? 'dark' : 'light'
    document.documentElement.setAttribute('data-theme', theme.value)
  }

  // 设置主题
  function setTheme(mode: 'light' | 'dark') {
    theme.value = mode
    document.documentElement.setAttribute('data-theme', mode)
  }

  // 设置全局加载
  function setGlobalLoading(loading: boolean) {
    globalLoading.value = loading
  }

  // 添加通知
  function addNotification(
    type: 'success' | 'error' | 'warning' | 'info',
    message: string,
    duration = 5000
  ) {
    const id = 'notification-' + Date.now()
    notifications.value.push({ id, type, message, duration })

    if (duration > 0) {
      setTimeout(() => {
        removeNotification(id)
      }, duration)
    }

    return id
  }

  // 移除通知
  function removeNotification(id: string) {
    const index = notifications.value.findIndex(n => n.id === id)
    if (index !== -1) {
      notifications.value.splice(index, 1)
    }
  }

  // 清空所有通知
  function clearNotifications() {
    notifications.value = []
  }

  return {
    // State
    sidebarCollapsed,
    sidebarMobileOpen,
    theme,
    globalLoading,
    notifications,

    // Actions
    toggleSidebar,
    setSidebarCollapsed,
    toggleMobileSidebar,
    closeMobileSidebar,
    toggleTheme,
    setTheme,
    setGlobalLoading,
    addNotification,
    removeNotification,
    clearNotifications
  }
})
