<template>
  <div class="clusters-container">
    <h3 class="clusters-title">研究聚类</h3>
    <div class="clusters-content">
      <div
        v-for="cluster in clusters"
        :key="cluster.id"
        class="cluster-card"
        :class="{ selected: selectedCluster?.id === cluster.id }"
        @click="selectCluster(cluster)"
      >
        <div class="cluster-header">
          <Icon name="cluster" :size="24" />
          <h4 class="cluster-name">{{ cluster.label }}</h4>
        </div>
        <div class="cluster-stats">
          <div class="stat-item">
            <span class="stat-value">{{ cluster.paper_ids.length }}</span>
            <span class="stat-label">论文</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ cluster.topic_ids.length }}</span>
            <span class="stat-label">主题</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ cluster.method_ids.length }}</span>
            <span class="stat-label">方法</span>
          </div>
        </div>
        <p v-if="cluster.summary" class="cluster-summary">{{ cluster.summary }}</p>
      </div>
    </div>
    <transition name="slide">
      <div v-if="selectedCluster" class="cluster-detail-panel">
        <div class="panel-header">
          <h3>聚类详情</h3>
          <button @click="closeDetail" class="close-btn">
            <Icon name="close" :size="18" />
          </button>
        </div>
        <div class="panel-content">
          <div class="detail-row">
            <span class="label">名称:</span>
            <span class="value">{{ selectedCluster.label }}</span>
          </div>
          <div class="detail-row">
            <span class="label">论文数:</span>
            <span class="value">{{ selectedCluster.paper_ids.length }}</span>
          </div>
          <div class="detail-row">
            <span class="label">主题数:</span>
            <span class="value">{{ selectedCluster.topic_ids.length }}</span>
          </div>
          <div class="detail-row">
            <span class="label">方法数:</span>
            <span class="value">{{ selectedCluster.method_ids.length }}</span>
          </div>
          <div v-if="selectedCluster.summary" class="detail-row full-width">
            <span class="label">摘要:</span>
            <p class="value">{{ selectedCluster.summary }}</p>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { ResearchCluster } from '@/types/research-map'
import Icon from './common/Icon.vue'

interface Props {
  clusters: ResearchCluster[]
}

const props = defineProps<Props>()

const emit = defineEmits<{
  clusterClick: [cluster: ResearchCluster]
}>()

const selectedCluster = ref<ResearchCluster | null>(null)

const selectCluster = (cluster: ResearchCluster) => {
  selectedCluster.value = cluster
  emit('clusterClick', cluster)
}

const closeDetail = () => {
  selectedCluster.value = null
}
</script>

<style scoped>
.clusters-container {
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

.clusters-title {
  margin: 0;
  padding: 16px;
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  border-bottom: 1px solid #e2e8f0;
}

.clusters-content {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
}

.cluster-card {
  padding: 16px;
  margin-bottom: 12px;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.cluster-card:hover {
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.cluster-card.selected {
  background: #eff6ff;
  border-color: #3b82f6;
}

.cluster-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.cluster-header .icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background: #eff6ff;
  border-radius: 8px;
  color: #3b82f6;
}

.cluster-name {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
  color: #1e293b;
}

.cluster-stats {
  display: flex;
  gap: 16px;
  margin-bottom: 12px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-value {
  font-size: 18px;
  font-weight: 700;
  color: #3b82f6;
}

.stat-label {
  font-size: 11px;
  color: #64748b;
  margin-top: 2px;
}

.cluster-summary {
  margin: 0;
  font-size: 13px;
  color: #64748b;
  line-height: 1.5;
}

.cluster-detail-panel {
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
