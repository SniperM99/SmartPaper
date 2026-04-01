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
        <h1 class="auth-title">设置新密码</h1>
        <p class="auth-subtitle">请输入您的新密码</p>
      </div>

      <!-- 重置密码表单 -->
      <form class="auth-form" @submit.prevent="handleSubmit">
        <div class="form-group">
          <label class="form-label" for="password">新密码</label>
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
          <label class="form-label" for="confirmPassword">确认新密码</label>
          <div class="input-with-icon">
            <input
              id="confirmPassword"
              v-model="form.confirmPassword"
              :type="showConfirmPassword ? 'text' : 'password'"
              class="input"
              :class="{ 'input-error': !passwordsMatch }"
              placeholder="再次输入新密码"
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

        <!-- 密码强度指示器 -->
        <div class="password-strength">
          <div class="password-strength-label">密码强度</div>
          <div class="password-strength-meter">
            <div
              class="password-strength-bar"
              :class="strengthClass"
              :style="{ width: strengthWidth }"
            ></div>
          </div>
          <div class="password-strength-text">{{ strengthText }}</div>
        </div>

        <button
          type="submit"
          class="btn btn-primary btn-full"
          :disabled="!passwordsMatch || strength < 2"
        >
          重置密码
        </button>
      </form>

      <!-- 返回登录 -->
      <div class="auth-footer">
        <router-link to="/auth/login" class="link">返回登录</router-link>
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
  password: '',
  confirmPassword: ''
})

const passwordsMatch = computed(() => {
  if (!form.confirmPassword) return true
  return form.password === form.confirmPassword
})

// 密码强度计算
const strength = computed(() => {
  let score = 0
  if (form.password.length >= 8) score++
  if (form.password.length >= 12) score++
  if (/[a-z]/.test(form.password) && /[A-Z]/.test(form.password)) score++
  if (/\d/.test(form.password)) score++
  if (/[^a-zA-Z0-9]/.test(form.password)) score++
  return Math.min(score, 4)
})

const strengthClass = computed(() => {
  const classes = ['', 'weak', 'fair', 'good', 'strong']
  return classes[strength.value]
})

const strengthWidth = computed(() => {
  return `${(strength.value / 4) * 100}%`
})

const strengthText = computed(() => {
  const texts = ['太短', '弱', '中等', '强', '很强']
  return texts[strength.value]
})

const handleSubmit = () => {
  if (!passwordsMatch.value || strength.value < 2) return

  // 重置密码逻辑
  console.log('Reset password:', form)
  // router.push('/auth/login')
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

.password-strength {
  margin-bottom: 24px;
}

.password-strength-label {
  font-size: 12px;
  color: var(--color-text-secondary);
  margin-bottom: 8px;
}

.password-strength-meter {
  height: 4px;
  background-color: var(--color-bg-tertiary);
  border-radius: 2px;
  overflow: hidden;
  margin-bottom: 4px;
}

.password-strength-bar {
  height: 100%;
  transition: width 0.3s ease, background-color 0.3s ease;
}

.password-strength-bar.weak {
  background-color: var(--color-error);
}

.password-strength-bar.fair {
  background-color: var(--color-warning);
}

.password-strength-bar.good {
  background-color: var(--color-info);
}

.password-strength-bar.strong {
  background-color: var(--color-success);
}

.password-strength-text {
  font-size: 12px;
  color: var(--color-text-tertiary);
}

.btn-full {
  width: 100%;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.auth-footer {
  text-align: center;
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
