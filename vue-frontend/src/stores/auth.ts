/**
 * 认证状态管理
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export interface User {
  id: string
  name: string
  email: string
  avatar?: string
}

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null)
  const token = ref<string | null>(null)
  const isAuthenticated = computed(() => !!token.value && !!user.value)

  // 从 localStorage 加载认证信息
  function loadAuth() {
    const savedToken = localStorage.getItem('auth_token')
    const savedUser = localStorage.getItem('auth_user')

    if (savedToken && savedUser) {
      try {
        token.value = savedToken
        user.value = JSON.parse(savedUser)
      } catch (e) {
        console.error('加载认证信息失败', e)
        clearAuth()
      }
    }
  }

  // 保存认证信息
  function saveAuth(accessToken: string, userData: User) {
    token.value = accessToken
    user.value = userData
    localStorage.setItem('auth_token', accessToken)
    localStorage.setItem('auth_user', JSON.stringify(userData))
  }

  // 清除认证信息
  function clearAuth() {
    token.value = null
    user.value = null
    localStorage.removeItem('auth_token')
    localStorage.removeItem('auth_user')
  }

  // 登录
  async function login(email: string, password: string) {
    // 这里应该调用实际的 API
    // 暂时模拟登录
    await new Promise(resolve => setTimeout(resolve, 500))

    // 模拟成功登录
    const mockUser: User = {
      id: '1',
      name: 'User Name',
      email: email
    }

    saveAuth('mock-token-' + Date.now(), mockUser)
    return { success: true, user: mockUser }
  }

  // 登出
  function logout() {
    clearAuth()
  }

  // 检查 token 有效性
  async function validateToken() {
    if (!token.value) return false

    // 这里应该调用实际的 API 验证 token
    // 暂时返回 true
    return true
  }

  // 初始化时加载认证信息
  loadAuth()

  return {
    // State
    user,
    token,
    isAuthenticated,

    // Actions
    login,
    logout,
    loadAuth,
    saveAuth,
    clearAuth,
    validateToken
  }
})
