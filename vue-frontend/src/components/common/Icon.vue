<template>
  <span class="icon" :class="[`icon-${name}`, { [`size-${size}`]: true }]" />
</template>

<script setup lang="ts">
interface Props {
  name: string
  size?: 12 | 14 | 16 | 18 | 20 | 24 | 32 | 48
}

withDefaults(defineProps<Props>(), {
  size: 16
})
</script>

<style scoped>
.icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 1em;
  height: 1em;
  font-family: 'smartpaper-icons', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  font-style: normal;
  font-variant: normal;
  font-weight: normal;
  line-height: 1;
  text-rendering: auto;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.size-12 { font-size: 12px; }
.size-14 { font-size: 14px; }
.size-16 { font-size: 16px; }
.size-18 { font-size: 18px; }
.size-20 { font-size: 20px; }
.size-24 { font-size: 24px; }
.size-32 { font-size: 32px; }
.size-48 { font-size: 48px; }

/* 图标定义 - 使用 CSS content 实现简单图标 */
.icon-refresh::before {
  content: '';
  width: 0.9em;
  height: 0.9em;
  border: 2px solid currentColor;
  border-top-color: transparent;
  border-radius: 50%;
}

.icon-download::before {
  content: '↓';
  font-weight: bold;
}

.icon-zoom-in::before {
  content: '+';
  font-weight: bold;
}

.icon-zoom-out::before {
  content: '−';
  font-weight: bold;
}

.icon-document::before {
  content: '📄';
}

.icon-link::before {
  content: '🔗';
}

.icon-cluster::before {
  content: '📊';
}

.icon-target::before {
  content: '🎯';
}

.icon-graph::before {
  content: '◉';
}

.icon-timeline::before {
  content: '📅';
}

.icon-search::before {
  content: '🔍';
}

.icon-close::before {
  content: '×';
  font-size: 1.2em;
}

.icon-warning::before {
  content: '⚠';
}
</style>
