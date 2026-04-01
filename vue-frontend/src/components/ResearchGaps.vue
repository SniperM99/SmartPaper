<template>
  <div class="gaps-container">
    <div class="gaps-header">
      <h3>研究空白</h3>
      <div class="filter-controls">
        <select v-model="filterPriority" @change="applyFilters">
          <option value="all">全部优先级</option>
          <option value="high">高</option>
          <option value="medium">中</option>
          <option value="low">低</option>
        </select>
      </div>
    </div>
    <div class="gaps-content">
      <div
        v-for="gap in filteredGaps"
        :key="gap.id"
        class="gap-card"
        :class="[`priority-${gap.priority}`, { selected: selectedGap?.id === gap.id }]"
        @click="selectGap(gap)"
      >
        <div class="gap-header">
          <div class="gap-priority">
            <span :class="`priority-badge ${gap.priority}`">
              {{ PRIORITY_LABELS[gap.priority] }}
            </span>
            <span class="gap-type">{{ GAP_TYPE_LABELS[gap.gap_type] }}</span>
          </div>
        </div>
        <h4 class="gap-title">{{ gap.title }}</h4>
        <p class="gap-description">{{ gap.description }}</p>
        <div v-if="gap.evidence_paper_ids.length" class="gap-evidence">
          <Icon name="document" :size="14" />
          <span class="evidence-label">依据:</span>
          <span class="evidence-count">{{ gap.evidence_paper_ids.length }} 篇论文</span>
        </div>
      </div>
    </div>
    <transition name="slide">
      <div v-if="selectedGap" class="gap-detail-panel">
        <div class="panel-header">
          <h3>空白详情</h3>
          <button @click="closeDetail" class="close-btn">
            <Icon name="close" :size="18" />
          </button>
        </div>
        <div class="panel-content">
          <div class="detail-row">
            <span class="label">标题:</span>
            <span class="value">{{ selectedGap.title }}</span>
          </div>
          <div class="detail-row">
            <span class="label">类型:</span>
            <span class="value">{{ GAP_TYPE_LABELS[selectedGap.gap_type] }}</span>
          </div>
          <div class="detail-row">
            <span class="label">优先级:</span>
            <span :class="`priority-badge ${selectedGap.priority}`">
              {{ PRIORITY_LABELS[selectedGap.priority] }}
            </span>
          </div>
          <div class="detail-row full-width">
            <span class="label">描述:</span>
            <p class="value">{{ selectedGap.description }}</p>
          </div>
          <div class="detail-row">
            <span class="label">依据论文:</span>
            <span class="value">{{ selectedGap.evidence_paper_ids.length }} 篇</span>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { ResearchGap } from '@/types/research-map'
import Icon from './common/Icon.vue'

interface Props {
  gaps: ResearchGap[]
}

const props = defineProps<Props>()

const emit = defineEmits<{
  gapClick: [gap: ResearchGap]
}>()

const PRIORITY_LABELS: Record<string, string> = {
  high: '高',
  medium: '中',
  low: '低',
}

const GAP_TYPE_LABELS: Record<string, string> = {
  explicit_gap: '明确空白',
  sparse_topic: '稀疏主题',
  missing_evaluation: '缺失评估',
}

const filterPriority = ref<string>('all')
const selectedGap = ref<ResearchGap | null>(null)

const filteredGaps = computed(() => {
  if (filterPriority.value === 'all') {
    return props.gaps
  }
  return props.gaps.filter(gap => gap.priority === filterPriority.value)
})

const applyFilters = () => {
  // 过滤逻辑已在 computed 中处理
}

const selectGap = (gap: ResearchGap) => {
  selectedGap.value = gap
  emit('gapClick', gap)
}

const closeDetail = () => {
  selectedGap.value = null
}
</script>

<style scoped>
.gaps-container {
  width: 100%;
  height: 100%;
  min-height: 400px;
  background: white;
  border-radius: 8px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  position: relative;
}

.gaps-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #e2e8f0;
}

.gaps-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
}

.filter-controls select {
  padding: 6px 12px;
  border: 1px solid #cbd5e1;
  border-radius: 4px;
  font-size: 12px;
  color: #475569;
  cursor: pointer;
}

.gaps-content {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
}

.gap-card {
  padding: 16px;
  margin-bottom: 12px;
  background: white;
  border: 1px solid #e2e8f0;
  border-left: 4px solid #94a3b8;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.gap-card:hover {
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  transform: translateX(2px);
}

.gap-card.priority-high {
  border-left-color: #ef4444;
}

.gap-card.priority-medium {
  border-left-color: #f59e0b;
}

.gap-card.priority-low {
  border-left-color: #22c55e;
}

.gap-card.selected {
  background: #eff6ff;
  border-color: #3b82f6;
}

.gap-header {
  margin-bottom: 8px;
}

.gap-priority {
  display: flex;
  gap: 8px;
  align-items: center;
}

.priority-badge {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
}

.priority-badge.high {
  background: #fef2f2;
  color: #dc2626;
}

.priority-badge.medium {
  background: #fffbeb;
  color: #d97706;
}

.priority-badge.low {
  background: #f0fdf4;
  color: #16a34a;
}

.gap-type {
  font-size: 11px;
  color: #64748b;
}

.gap-title {
  margin: 8px 0;
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
}

.gap-description {
  margin: 0 0 12px;
  font-size: 13px;
  color: #64748b;
  line-height: 1.5;
}

.gap-evidence {
  display: flex;
  gap: 6px;
  align-items: center;
}

.gap-evidence .icon {
  color: #94a3b8;
}

.evidence-label {
  font-size: 11px;
  color: #94a3b8;
  font-weight: 500;
}

.evidence-count {
  font-size: 11px;
  color: #64748b;
}

.gap-detail-panel {
  position: absolute;
  top: 0;
  right: 0;
  width: 320px;
  max-height: 100%;
  background: white;
  border-left: 1px solid #e2e8f0;
  box-shadow: -4px 0 12px rgba(0, 0, 0, 0.1);
  z-index: 10;
  overflow-y: auto;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #e2e8f0;
  background: #f8fafc;
}

.panel-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
}

.close-btn {
  background: none;
  border: none;
  color: #94a3b8;
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color 0.2s;
}

.close-btn:hover {
  color: #475569;
}

.panel-content {
  padding: 16px;
}

.detail-row {
  display: flex;
  margin-bottom: 12px;
  align-items: flex-start;
}

.detail-row.full-width {
  flex-direction: column;
}

.detail-row .label {
  min-width: 80px;
  font-size: 13px;
  font-weight: 600;
  color: #64748b;
}

.detail-row .value {
  font-size: 13px;
  color: #334155;
  word-break: break-word;
}

.detail-row .value p {
  margin: 4px 0 0;
  line-height: 1.5;
}

.slide-enter-active,
.slide-leave-active {
  transition: all 0.3s ease;
}

.slide-enter-from,
.slide-leave-to {
  opacity: 0;
  transform: translateX(20px);
}
</style>
