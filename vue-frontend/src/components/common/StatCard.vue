<template>
  <div class="stat-card" :class="`stat-card-${variant}`">
    <div class="stat-icon" :class="`stat-icon-${variant}`">
      <slot name="icon">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/>
        </svg>
      </slot>
    </div>
    <div class="stat-content">
      <div class="stat-label">{{ label }}</div>
      <div class="stat-value">{{ formattedValue }}</div>
      <div class="stat-change" :class="`stat-change-${changeType}`" v-if="change">
        <svg v-if="changeType === 'positive'" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="m18 15-6-6-6 6"/>
        </svg>
        <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="m6 9 6 6 6-6"/>
        </svg>
        {{ change }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  label: string
  value: number | string
  change?: string
  variant?: 'primary' | 'success' | 'warning' | 'info'
  format?: 'number' | 'percent' | 'currency'
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'primary',
  format: 'number'
})

const changeType = computed(() => {
  if (!props.change) return 'neutral'
  const changeStr = props.change.replace(/[^\d.-]/g, '')
  const changeNum = parseFloat(changeStr)
  if (isNaN(changeNum)) return 'neutral'
  return changeNum > 0 ? 'positive' : changeNum < 0 ? 'negative' : 'neutral'
})

const formattedValue = computed(() => {
  if (typeof props.value === 'string') return props.value

  switch (props.format) {
    case 'percent':
      return `${props.value}%`
    case 'currency':
      return new Intl.NumberFormat('zh-CN', {
        style: 'currency',
        currency: 'CNY'
      }).format(props.value)
    case 'number':
    default:
      return new Intl.NumberFormat('zh-CN').format(props.value)
  }
})
</script>

<style scoped>
.stat-card {
  background-color: white;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 24px;
  transition: all 0.2s;
  display: flex;
  gap: 16px;
}

.stat-card:hover {
  box-shadow: var(--shadow-md);
  border-color: var(--color-border-hover);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-icon-primary {
  background-color: var(--color-primary-light);
  color: var(--color-primary);
}

.stat-icon-success {
  background-color: var(--color-success-light);
  color: var(--color-success);
}

.stat-icon-warning {
  background-color: var(--color-warning-light);
  color: var(--color-warning);
}

.stat-icon-info {
  background-color: var(--color-info-light);
  color: var(--color-info);
}

.stat-content {
  flex: 1;
}

.stat-label {
  font-size: 12px;
  font-weight: 500;
  color: var(--color-text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: var(--color-text-primary);
  line-height: 1.2;
  margin-bottom: 4px;
}

.stat-change {
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 4px;
  font-weight: 500;
}

.stat-change-positive {
  color: var(--color-success);
}

.stat-change-negative {
  color: var(--color-error);
}

.stat-change-neutral {
  color: var(--color-text-tertiary);
}
</style>
