<template>
  <div class="research-map-view">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">研究地图</h1>
        <p class="page-subtitle">交互式知识图谱可视化分析</p>
      </div>
      <div class="header-actions">
        <button
          @click="handleRefresh"
          class="btn btn-secondary"
          :disabled="loading"
        >
          <Icon name="refresh" :size="18" />
          <span>刷新</span>
        </button>
        <button
          @click="handleExport"
          class="btn btn-secondary"
          :disabled="!hasData"
        >
          <Icon name="download" :size="18" />
          <span>导出</span>
        </button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div v-if="hasData" class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon stat-icon-paper">
          <Icon name="document" :size="24" />
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ paperCount }}</div>
          <div class="stat-label">论文</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon stat-icon-relation">
          <Icon name="link" :size="24" />
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ edgeCount }}</div>
          <div class="stat-label">关系</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon stat-icon-cluster">
          <Icon name="cluster" :size="24" />
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ clusterCount }}</div>
          <div class="stat-label">聚类</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon stat-icon-gap">
          <Icon name="target" :size="24" />
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ gapCount }}</div>
          <div class="stat-label">空白</div>
        </div>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <div class="spinner"></div>
      <p>加载研究地图数据...</p>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error" class="error-container">
      <Icon name="warning" :size="48" />
      <h3>加载失败</h3>
      <p>{{ error }}</p>
      <button @click="handleRefresh" class="btn btn-primary">重试</button>
    </div>

    <!-- 主内容区域 -->
    <div v-else-if="hasData" class="map-content">
      <!-- 图谱区域 -->
      <div class="graph-section">
        <ResearchGraph />
      </div>

      <!-- 侧边栏 -->
      <div class="sidebar">
        <!-- 标签页导航 -->
        <div class="tabs-nav">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            :class="['tab-btn', { active: activeTab === tab.id }]"
            @click="setActiveTab(tab.id)"
          >
            <Icon :name="tab.icon" :size="16" />
            <span>{{ tab.label }}</span>
            <span v-if="tab.count" class="tab-badge">{{ tab.count }}</span>
          </button>
        </div>

        <!-- 标签页内容 -->
        <div class="tabs-content">
          <component
            :is="currentTabComponent"
            v-if="activeTab !== 'graph'"
            v-bind="currentTabProps"
          />
        </div>
      </div>
    </div>

    <!-- 搜索面板 -->
    <transition name="slide-down">
      <div v-if="showSearch" class="search-panel">
        <div class="search-input-wrapper">
          <Icon name="search" :size="18" />
          <input
            ref="searchInput"
            v-model="searchQuery"
            @input="handleSearchInput"
            placeholder="搜索节点..."
            class="search-input"
          />
          <button @click="toggleSearch" class="search-close">
            <Icon name="close" :size="16" />
          </button>
        </div>
        <div v-if="searchResults.length > 0" class="search-results">
          <div
            v-for="result in searchResults"
            :key="result.id"
            class="search-result-item"
            @click="handleSelectSearchResult(result)"
          >
            <span class="result-type">{{ ENTITY_TYPE_LABELS[result.entity_type] }}</span>
            <span class="result-label">{{ result.label }}</span>
          </div>
        </div>
      </div>
    </transition>

    <!-- 搜索按钮 -->
    <button @click="toggleSearch" class="search-toggle-btn" title="搜索节点">
      <Icon name="search" :size="20" />
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useResearchMapStore } from '@/stores/researchMap'
import { ENTITY_TYPE_LABELS } from '@/types/research-map'
import ResearchGraph from '@/components/ResearchGraph.vue'
import ResearchTimeline from '@/components/ResearchTimeline.vue'
import ResearchGaps from '@/components/ResearchGaps.vue'
import ResearchClusters from '@/components/ResearchClusters.vue'
import Icon from '@/components/common/Icon.vue'
import { fetchResearchMap } from '@/utils/api'

// Store
const researchMapStore = useResearchMapStore()

// 解构 store
const {
  mapData,
  loading,
  error,
  hasData,
  activeTab,
  currentLayout,
  selectedNode,
  selectedEdge,
  searchQuery,
  searchResults,
  showSearch,
  nodeCount,
  edgeCount,
  clusterCount,
  gapCount,
  paperCount,
  timelineEvents,
  gaps,
  clusters,
  fetchResearchMap: fetchMap,
  setLayout,
  setActiveTab,
  selectNode,
  selectEdge,
  searchNodes,
  toggleSearch
} = researchMapStore

// Refs
const searchInput = ref<HTMLInputElement>()

// Computed
const tabs = computed(() => [
  {
    id: 'graph' as const,
    label: '图谱',
    icon: 'graph',
    count: nodeCount.value
  },
  {
    id: 'timeline' as const,
    label: '时间线',
    icon: 'timeline',
    count: timelineEvents.value.length
  },
  {
    id: 'gaps' as const,
    label: '研究空白',
    icon: 'target',
    count: gaps.value.length
  },
  {
    id: 'clusters' as const,
    label: '聚类',
    icon: 'cluster',
    count: clusters.value.length
  }
])

const currentTabComponent = computed(() => {
  switch (activeTab.value) {
    case 'timeline':
      return ResearchTimeline
    case 'gaps':
      return ResearchGaps
    case 'clusters':
      return ResearchClusters
    default:
      return null
  }
})

const currentTabProps = computed(() => {
  switch (activeTab.value) {
    case 'timeline':
      return { events: timelineEvents.value }
    case 'gaps':
      return { gaps: gaps.value }
    case 'clusters':
      return { clusters: clusters.value }
    default:
      return {}
  }
})

// Methods
const handleRefresh = async () => {
  await fetchMap()
}

const handleExport = () => {
  if (!mapData.value) return

  const dataStr = JSON.stringify(mapData.value, null, 2)
  const blob = new Blob([dataStr], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `research-map-${Date.now()}.json`
  link.click()
  URL.revokeObjectURL(url)
}

const handleSearchInput = () => {
  searchNodes(searchQuery.value)
}

const handleSelectSearchResult = (result: any) => {
  selectNode(result)
  toggleSearch()
}

// Watch search visibility
watch(showSearch, (visible) => {
  if (visible) {
    nextTick(() => {
      searchInput.value?.focus()
    })
  }
})

// Lifecycle
onMounted(async () => {
  // 从 URL 参数获取 cacheKeys
  const urlParams = new URLSearchParams(window.location.search)
  const cacheKeysParam = urlParams.get('cacheKeys')
  const initialCacheKeys = cacheKeysParam ? cacheKeysParam.split(',') : []

  if (initialCacheKeys.length > 0) {
    await fetchMap(initialCacheKeys)
  } else {
    // 使用模拟数据用于演示
    await fetchMap()
  }
})
</script>

<style scoped>
.research-map-view {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--color-bg);
  overflow: hidden;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  background: white;
  border-bottom: 1px solid var(--color-border);
}

.header-content {
  flex: 1;
}

.page-title {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: var(--color-text);
}

.page-subtitle {
  margin: 4px 0 0;
  font-size: 14px;
  color: var(--color-text-secondary);
}

.header-actions {
  display: flex;
  gap: 12px;
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px 16px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid transparent;
  background: white;
  color: var(--color-text);
  border-color: var(--color-border);
}

.btn:hover:not(:disabled) {
  background: var(--color-bg);
  border-color: var(--color-border-dark);
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: var(--color-primary);
  color: white;
  border-color: var(--color-primary);
}

.btn-primary:hover:not(:disabled) {
  background: var(--color-primary-dark);
  border-color: var(--color-primary-dark);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  padding: 16px 24px;
  background: white;
  border-bottom: 1px solid var(--color-border);
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: var(--color-bg);
  border-radius: 8px;
  transition: transform 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-icon-paper {
  background: #dbeafe;
  color: #1e40af;
}

.stat-icon-relation {
  background: #ede9fe;
  color: #6d28d9;
}

.stat-icon-cluster {
  background: #dcfce7;
  color: #166534;
}

.stat-icon-gap {
  background: #fef3c7;
  color: #d97706;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--color-text);
  line-height: 1;
}

.stat-label {
  font-size: 12px;
  color: var(--color-text-secondary);
  margin-top: 4px;
}

.loading-container,
.error-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid var(--color-border);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-container p,
.error-container p {
  margin: 0;
  color: var(--color-text-secondary);
}

.error-container h3 {
  margin: 0;
  color: var(--color-text);
}

.error-container .icon {
  color: #f59e0b;
}

.map-content {
  flex: 1;
  display: grid;
  grid-template-columns: 1fr 400px;
  gap: 16px;
  padding: 16px 24px;
  overflow: hidden;
}

.graph-section {
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.sidebar {
  display: flex;
  flex-direction: column;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  overflow: hidden;
}

.tabs-nav {
  display: flex;
  border-bottom: 1px solid var(--color-border);
  background: var(--color-bg);
}

.tab-btn {
  flex: 1;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 14px 16px;
  background: none;
  border: none;
  font-size: 13px;
  font-weight: 500;
  color: var(--color-text-secondary);
  cursor: pointer;
  position: relative;
  transition: all 0.2s;
}

.tab-btn:hover {
  color: var(--color-text);
  background: rgba(0, 0, 0, 0.02);
}

.tab-btn.active {
  color: var(--color-primary);
  background: white;
}

.tab-btn.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: var(--color-primary);
}

.tab-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 20px;
  height: 20px;
  padding: 0 6px;
  background: #dbeafe;
  color: #1e40af;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 600;
  line-height: 1;
}

.tabs-content {
  flex: 1;
  overflow: hidden;
}

.search-panel {
  position: fixed;
  top: 80px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 100;
  width: 500px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.15);
}

.search-input-wrapper {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid var(--color-border);
  gap: 12px;
}

.search-input {
  flex: 1;
  padding: 10px 12px;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
}

.search-input:focus {
  border-color: var(--color-primary);
}

.search-input-wrapper .icon {
  color: var(--color-text-secondary);
}

.search-close {
  padding: 4px;
  background: none;
  border: none;
  color: var(--color-text-secondary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.search-close:hover {
  color: var(--color-text);
}

.search-results {
  max-height: 300px;
  overflow-y: auto;
  padding: 8px;
}

.search-result-item {
  display: flex;
  gap: 12px;
  align-items: center;
  padding: 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
}

.search-result-item:hover {
  background: var(--color-bg);
}

.result-type {
  padding: 4px 10px;
  background: var(--color-bg);
  color: var(--color-text-secondary);
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
  flex-shrink: 0;
}

.result-label {
  font-size: 13px;
  color: var(--color-text);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.search-toggle-btn {
  position: fixed;
  bottom: 32px;
  right: 32px;
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: var(--color-primary);
  color: white;
  border: none;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
  transition: all 0.2s;
  z-index: 90;
  display: flex;
  align-items: center;
  justify-content: center;
}

.search-toggle-btn:hover {
  background: var(--color-primary-dark);
  transform: scale(1.05);
}

.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.2s ease;
}

.slide-down-enter-from,
.slide-down-leave-to {
  opacity: 0;
  transform: translate(-50%, -10px);
}

@media (max-width: 1200px) {
  .map-content {
    grid-template-columns: 1fr;
  }

  .sidebar {
    display: none;
  }
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .page-header {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }

  .header-actions {
    width: 100%;
  }

  .header-actions .btn {
    flex: 1;
  }
}
</style>
