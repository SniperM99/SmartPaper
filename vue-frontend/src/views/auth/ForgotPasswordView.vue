<template>
  <div class="auth-container">
    <div class="auth-card">
      <!-- Logo 区域 -->
      <div class="auth-logo">
        <div class="auth-logo-icon">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/>
            <polyline points="14 2 14 8 20 8"/>
            <path d="M12 18v-6"/>
            <path d="M9 15l3 3 3-3"/>
          </svg>
        </div>
        <h1 class="auth-title">重置密码</h1>
        <p class="auth-subtitle">输入您的邮箱地址，我们将发送重置链接</p>
      </div>

      <!-- 忘记密码表单 -->
      <form class="auth-form" @submit.prevent="handleSubmit">
        <div class="form-group">
          <label class="form-label" for="email">邮箱地址</label>
          <input
            id="email"
            v-model="form.email"
            type="email"
            class="input"
            placeholder="your@email.com"
            required
          />
          <p class="form-hint">请使用您注册时的邮箱地址</p>
        </div>

        <button type="submit" class="btn btn-primary btn-full" :disabled="isLoading">
          <span v-if="!isLoading">发送重置链接</span>
          <span v-else>发送中...</span>
        </button>
      </form>

      <!-- 返回登录 -->
      <div class="auth-footer">
        <span>记得密码了?</span>
        <router-link to="/auth/login" class="link">返回登录</router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const isLoading = ref(false)

const form = reactive({
  email: ''
})

const handleSubmit = async () => {
  isLoading.value = true

  // 模拟 API 调用
  await new Promise(resolve => setTimeout(resolve, 2000))

  console.log('Reset password for:', form.email)
  isLoading.value = false

  // 跳转到重置确认页面
  // router.push('/auth/reset-password/sent')
}
</script>

<style scoped>
.auth-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 24px;
}

.auth-card {
  width: 100%;
  max-width: 420px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  padding: 48px;
}

.auth-logo {
  text-align: center;
  margin-bottom: 32px;
}

.auth-logo-icon {
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, var(--color-primary) 0%, #667eea 100%);
  border-radius: 20px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: white;
  margin-bottom: 16px;
}

.auth-title {
  font-size: 28px;
  font-weight: 700;
  color: var(--color-text-primary);
  margin-bottom: 8px;
}

.auth-subtitle {
  color: var(--color-text-secondary);
  font-size: 14px;
}

.auth-form {
  margin-bottom: 24px;
}

.form-group {
  margin-bottom: 24px;
}

.form-label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text-primary);
  margin-bottom: 8px;
}

.form-hint {
  font-size: 12px;
  color: var(--color-text-tertiary);
  margin-top: 4px;
}

.btn-full {
  width: 100%;
}

.auth-footer {
  text-align: center;
  color: var(--color-text-secondary);
  font-size: 14px;
}

.link {
  color: var(--color-primary);
  font-weight: 500;
  text-decoration: none;
}

.link:hover {
  color: var(--color-primary-hover);
  text-decoration: underline;
}
</style>
