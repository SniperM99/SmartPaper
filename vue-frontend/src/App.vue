<template>
  <div id="app" :data-theme="theme">
    <router-view />
  </div>
</template>

<script setup lang="ts">
import { onMounted, computed } from 'vue'
import { useAppStore } from './stores/app'

const appStore = useAppStore()

const theme = computed(() => appStore.theme)

onMounted(() => {
  // 加载认证信息
  const { loadAuth } = require('./stores/auth')
  loadAuth()

  // 应用主题
  document.documentElement.setAttribute('data-theme', appStore.theme)
})
</script>

<style>
:root {
  --color-primary: #3b82f6;
  --color-primary-dark: #2563eb;
  --color-text: #1e293b;
  --color-text-secondary: #64748b;
  --color-border: #e2e8f0;
  --color-border-dark: #94a3b8;
  --color-bg: #f1f5f9;
  --color-white: #ffffff;
  --color-success: #10b981;
  --color-warning: #f59e0b;
  --color-error: #ef4444;
}

[data-theme="dark"] {
  --color-primary: #60a5fa;
  --color-primary-dark: #3b82f6;
  --color-text: #f8fafc;
  --color-text-secondary: #94a3b8;
  --color-border: #334155;
  --color-border-dark: #475569;
  --color-bg: #0f172a;
  --color-white: #1e293b;
  --color-success: #22c55e;
  --color-warning: #fbbf24;
  --color-error: #f87171;
}

#app {
  width: 100%;
  height: 100vh;
  margin: 0;
  padding: 0;
  overflow: hidden;
  background: var(--color-bg);
  color: var(--color-text);
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html,
body {
  width: 100%;
  height: 100%;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* 滚动条样式 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: var(--color-bg);
}

::-webkit-scrollbar-thumb {
  background: var(--color-border);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: var(--color-border-dark);
}
</style>
