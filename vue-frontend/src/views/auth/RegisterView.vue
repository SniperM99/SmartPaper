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
        <h1 class="auth-title">创建账户</h1>
        <p class="auth-subtitle">注册并开始使用 SmartPaper</p>
      </div>

      <!-- 注册表单 -->
      <form class="auth-form" @submit.prevent="handleSubmit">
        <div class="form-group">
          <label class="form-label" for="name">姓名</label>
          <input
            id="name"
            v-model="form.name"
            type="text"
            class="input"
            placeholder="请输入您的姓名"
            required
          />
        </div>

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
        </div>

        <div class="form-group">
          <label class="form-label" for="password">密码</label>
          <div class="input-with-icon">
            <input
              id="password"
              v-model="form.password"
              :type="showPassword ? 'text' : 'password'"
              class="input"
              placeholder="至少8个字符"
              required
              minlength="8"
            />
            <button
              type="button"
              class="input-icon-btn"
              @click="showPassword = !showPassword"
            >
              <svg v-if="showPassword" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                <circle cx="12" cy="12" r="3"/>
              </svg>
              <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
                <line x1="1" y1="1" x2="23" y2="23"/>
              </svg>
            </button>
          </div>
        </div>

        <div class="form-group">
          <label class="form-label" for="confirmPassword">确认密码</label>
          <div class="input-with-icon">
            <input
              id="confirmPassword"
              v-model="form.confirmPassword"
              :type="showConfirmPassword ? 'text' : 'password'"
              class="input"
              :class="{ 'input-error': !passwordsMatch }"
              placeholder="再次输入密码"
              required
            />
            <button
              type="button"
              class="input-icon-btn"
              @click="showConfirmPassword = !showConfirmPassword"
            >
              <svg v-if="showConfirmPassword" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                <circle cx="12" cy="12" r="3"/>
              </svg>
              <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
                <line x1="1" y1="1" x2="23" y2="23"/>
              </svg>
            </button>
          </div>
          <p v-if="!passwordsMatch && form.confirmPassword" class="form-error">
            两次输入的密码不一致
          </p>
        </div>

        <div class="form-group">
          <label class="checkbox-label">
            <input v-model="form.agreeTerms" type="checkbox" required />
            <span>我已阅读并同意 <a href="/terms" class="link">服务条款</a> 和 <a href="/privacy" class="link">隐私政策</a></span>
          </label>
        </div>

        <button
          type="submit"
          class="btn btn-primary btn-full"
          :disabled="!passwordsMatch || !form.agreeTerms"
        >
          注册
        </button>
      </form>

      <!-- 第三方登录 -->
      <div class="auth-divider">
        <span>或使用</span>
      </div>

      <div class="social-login">
        <button class="btn btn-social btn-full">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
            <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
            <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
            <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
            <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
          </svg>
          Google 注册
        </button>
      </div>

      <!-- 登录链接 -->
      <div class="auth-footer">
        <span>已有账户?</span>
        <router-link to="/auth/login" class="link">立即登录</router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const showPassword = ref(false)
const showConfirmPassword = ref(false)

const form = reactive({
  name: '',
  email: '',
  password: '',
  confirmPassword: '',
  agreeTerms: false
})

const passwordsMatch = computed(() => {
  if (!form.confirmPassword) return true
  return form.password === form.confirmPassword
})

const handleSubmit = () => {
  if (!passwordsMatch.value || !form.agreeTerms) return

  // 注册逻辑
  console.log('Register:', form)
  // router.push('/overview')
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
  margin-bottom: 20px;
}

.form-label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text-primary);
  margin-bottom: 8px;
}

.form-error {
  color: var(--color-error);
  font-size: 12px;
  margin-top: 4px;
}

.input-with-icon {
  position: relative;
}

.input-icon-btn {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  padding: 4px;
  cursor: pointer;
  color: var(--color-text-light);
}

.input-icon-btn:hover {
  color: var(--color-text-tertiary);
}

.btn-full {
  width: 100%;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-social {
  background-color: white;
  border: 1px solid var(--color-border);
  color: var(--color-text-primary);
  gap: 12px;
}

.btn-social:hover {
  background-color: var(--color-bg-secondary);
  transform: none;
  box-shadow: var(--shadow-sm);
}

.auth-divider {
  position: relative;
  text-align: center;
  margin: 24px 0;
}

.auth-divider::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  height: 1px;
  background-color: var(--color-border);
}

.auth-divider span {
  position: relative;
  background-color: white;
  padding: 0 16px;
  color: var(--color-text-light);
  font-size: 14px;
}

.social-login {
  margin-bottom: 24px;
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
