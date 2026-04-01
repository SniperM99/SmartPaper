/**
 * 研究地图状态管理
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type {
  ResearchMapData,
  GraphNode,
  GraphEdge,
  EntityType,
  TimelineEvent,
  ResearchGap,
  ResearchCluster
} from '@/types/research-map'
import { fetchResearchMap as apiFetchResearchMap } from '@/utils/api'

export const useResearchMapStore = defineStore('researchMap', () => {
  // State
  const mapData = ref<ResearchMapData | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // 视图状态
  const activeTab = ref<'graph' | 'timeline' | 'gaps' | 'clusters'>('graph')
  const currentLayout = ref<'force' | 'circular' | 'hierarchical'>('force')
  const selectedNode = ref<GraphNode | null>(null)
  const selectedEdge = ref<GraphEdge | null>(null)
  const selectedEvent = ref<TimelineEvent | null>(null)
  const selectedGap = ref<ResearchGap | null>(null)
  const selectedCluster = ref<ResearchCluster | null>(null)

  // 筛选状态
  const filters = ref<{
    entityTypes: EntityType[]
    minMentions: number
  }>({
    entityTypes: ['paper', 'topic', 'problem', 'method', 'dataset', 'metric', 'gap'],
    minMentions: 0
  })

  // 搜索状态
  const searchQuery = ref('')
  const searchResults = ref<GraphNode[]>([])
  const showSearch = ref(false)

  // Computed
  const hasData = computed(() => mapData.value !== null)

  const nodeCount = computed(() => mapData.value?.entities.length || 0)
  const edgeCount = computed(() => mapData.value?.relations.length || 0)
  const clusterCount = computed(() => mapData.value?.clusters.length || 0)
  const gapCount = computed(() => mapData.value?.gaps.length || 0)
  const paperCount = computed(
    () => mapData.value?.entities.filter(e => e.entity_type === 'paper').length || 0
  )

  const visibleNodes = computed(() => {
    if (!mapData.value) return []
    return mapData.value.entities.filter(
      entity =>
        filters.value.entityTypes.includes(entity.entity_type) &&
        entity.mentions >= filters.value.minMentions
    )
  })

  const timelineEvents = computed(() => mapData.value?.timeline || [])
  const gaps = computed(() => mapData.value?.gaps || [])
  const clusters = computed(() => mapData.value?.clusters || [])

  // Actions
  async function fetchResearchMap(cacheKeys?: string[]) {
    loading.value = true
    error.value = null

    try {
      const data = await apiFetchResearchMap(cacheKeys)
      mapData.value = data
    } catch (err) {
      error.value = err instanceof Error ? err.message : '加载研究地图失败'
      console.error('加载研究地图失败:', err)
    } finally {
      loading.value = false
    }
  }

  function setLayout(layout: 'force' | 'circular' | 'hierarchical') {
    currentLayout.value = layout
  }

  function setActiveTab(tab: 'graph' | 'timeline' | 'gaps' | 'clusters') {
    activeTab.value = tab
  }

  function selectNode(node: GraphNode) {
    selectedNode.value = node
    selectedEdge.value = null
  }

  function selectEdge(edge: GraphEdge) {
    selectedEdge.value = edge
    selectedNode.value = null
  }

  function selectEvent(event: TimelineEvent) {
    selectedEvent.value = event
  }

  function selectGap(gap: ResearchGap) {
    selectedGap.value = gap
  }

  function selectCluster(cluster: ResearchCluster) {
    selectedCluster.value = cluster
  }

  function clearSelection() {
    selectedNode.value = null
    selectedEdge.value = null
    selectedEvent.value = null
    selectedGap.value = null
    selectedCluster.value = null
  }

  function updateFilters(newFilters: {
    entityTypes?: EntityType[]
    minMentions?: number
  }) {
    if (newFilters.entityTypes) {
      filters.value.entityTypes = newFilters.entityTypes
    }
    if (newFilters.minMentions !== undefined) {
      filters.value.minMentions = newFilters.minMentions
    }
  }

  async function searchNodes(query: string) {
    searchQuery.value = query

    if (!query.trim() || !mapData.value) {
      searchResults.value = []
      return
    }

    const q = query.toLowerCase()
    searchResults.value = mapData.value.entities
      .filter(entity => entity.label.toLowerCase().includes(q))
      .slice(0, 10)
  }

  function toggleSearch() {
    showSearch.value = !showSearch.value
    if (!showSearch.value) {
      searchQuery.value = ''
      searchResults.value = []
    }
  }

  function reset() {
    mapData.value = null
    loading.value = false
    error.value = null
    clearSelection()
    searchQuery.value = ''
    searchResults.value = []
    showSearch.value = false
  }

  return {
    // State
    mapData,
    loading,
    error,
    activeTab,
    currentLayout,
    selectedNode,
    selectedEdge,
    selectedEvent,
    selectedGap,
    selectedCluster,
    filters,
    searchQuery,
    searchResults,
    showSearch,

    // Computed
    hasData,
    nodeCount,
    edgeCount,
    clusterCount,
    gapCount,
    paperCount,
    visibleNodes,
    timelineEvents,
    gaps,
    clusters,

    // Actions
    fetchResearchMap,
    setLayout,
    setActiveTab,
    selectNode,
    selectEdge,
    selectEvent,
    selectGap,
    selectCluster,
    clearSelection,
    updateFilters,
    searchNodes,
    toggleSearch,
    reset
  }
})
