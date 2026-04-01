<template>
  <div class="research-graph-container">
    <!-- 控制面板 -->
    <div class="graph-controls">
      <div class="control-group">
        <label>布局:</label>
        <select v-model="layout" @change="applyLayout">
          <option value="force">力导向</option>
          <option value="circular">圆形</option>
          <option value="hierarchical">层级</option>
        </select>
      </div>

      <div class="control-group">
        <label>缩放:</label>
        <button @click="zoomIn" title="放大">
          <Icon name="zoom-in" :size="14" />
        </button>
        <button @click="zoomOut" title="缩小">
          <Icon name="zoom-out" :size="14" />
        </button>
        <button @click="resetZoom" title="重置">
          <Icon name="refresh" :size="14" />
        </button>
      </div>

      <div class="control-group">
        <label>过滤:</label>
        <select multiple v-model="entityTypeFilters" @change="handleFiltersChange">
          <option v-for="type in allEntityTypes" :key="type" :value="type">
            {{ ENTITY_TYPE_LABELS[type] }}
          </option>
        </select>
      </div>

      <div class="control-group">
        <label>最小提及数:</label>
        <input
          type="range"
          v-model.number="minMentionsFilter"
          min="0"
          max="10"
          @input="handleFiltersChange"
        />
        <span>{{ minMentionsFilter }}</span>
      </div>
    </div>

    <!-- 图谱画布 -->
    <svg ref="svgRef" class="graph-svg" @click="handleBackgroundClick">
      <g ref="zoomGroupRef" class="zoom-group">
        <!-- 边 -->
        <g class="edges">
          <line
            v-for="edge in visibleEdges"
            :key="edge.id"
            :x1="getNodePosition(edge.source).x"
            :y1="getNodePosition(edge.source).y"
            :x2="getNodePosition(edge.target).x"
            :y2="getNodePosition(edge.target).y"
            :stroke="edge.color"
            :stroke-width="edge.width"
            :stroke-opacity="edge.highlighted ? 1 : edge.selected ? 0.8 : 0.4"
            :stroke-dasharray="edge.selected ? '' : '5,5'"
            @click.stop="handleEdgeClick(edge)"
            @mouseenter="handleEdgeHover(edge, true)"
            @mouseleave="handleEdgeHover(edge, false)"
            class="graph-edge"
            :class="{ selected: edge.selected, highlighted: edge.highlighted }"
          />
          <!-- 边标签 -->
          <text
            v-for="edge in visibleEdges"
            :key="`label-${edge.id}`"
            :x="(getNodePosition(edge.source).x + getNodePosition(edge.target).x) / 2"
            :y="(getNodePosition(edge.source).y + getNodePosition(edge.target).y) / 2 - 5"
            text-anchor="middle"
            class="edge-label"
          >
            {{ RELATION_LABELS[edge.relation_type] }}
          </text>
        </g>

        <!-- 节点 -->
        <g class="nodes">
          <!-- 论文节点用矩形 -->
          <g
            v-for="node in visibleNodes.filter(n => n.entity_type === 'paper')"
            :key="node.id"
            :transform="`translate(${node.x}, ${node.y})`"
            @click.stop="handleNodeClick(node)"
            @mouseenter="handleNodeHover(node, true)"
            @mouseleave="handleNodeHover(node, false)"
            class="node-group"
            :class="{ selected: node.selected, highlighted: node.highlighted }"
          >
            <rect
              :x="-node.width! / 2"
              :y="-node.height! / 2"
              :width="node.width"
              :height="node.height"
              :fill="node.color"
              :fill-opacity="node.highlighted ? 1 : node.selected ? 0.9 : 0.7"
              :stroke="node.selected ? '#1e293b' : node.highlighted ? '#ffffff' : 'none'"
              :stroke-width="node.selected ? 2 : 1"
              rx="4"
              class="node-rect"
            />
            <text
              text-anchor="middle"
              :y="5"
              class="node-label"
              :class="{ 'label-white': node.selected || node.highlighted }"
            >
              {{ truncateLabel(node.label, 15) }}
            </text>
          </g>

          <!-- 其他节点用圆形 -->
          <g
            v-for="node in visibleNodes.filter(n => n.entity_type !== 'paper')"
            :key="node.id"
            :transform="`translate(${node.x}, ${node.y})`"
            @click.stop="handleNodeClick(node)"
            @mouseenter="handleNodeHover(node, true)"
            @mouseleave="handleNodeHover(node, false)"
            class="node-group"
            :class="{ selected: node.selected, highlighted: node.highlighted }"
          >
            <circle
              :r="node.r"
              :fill="node.color"
              :fill-opacity="node.highlighted ? 1 : node.selected ? 0.9 : 0.7"
              :stroke="node.selected ? '#1e293b' : node.highlighted ? '#ffffff' : 'none'"
              :stroke-width="node.selected ? 2 : 1"
              class="node-circle"
            />
            <text
              text-anchor="middle"
              :y="node.r! + 14"
              class="node-label-small"
            >
              {{ truncateLabel(node.label, 12) }}
            </text>
            <!-- 提及数徽章 -->
            <g v-if="node.mentions > 1" :transform="`translate(${node.r! - 2}, ${-node.r! + 2})`">
              <circle r="8" fill="#f59e0b" />
              <text
                text-anchor="middle"
                :y="3"
                fill="white"
                font-size="9"
                font-weight="bold"
              >
                {{ node.mentions }}
              </text>
            </g>
          </g>
        </g>
      </g>
    </svg>

    <!-- 节点详情面板 -->
    <transition name="slide">
      <div v-if="selectedNode" class="node-detail-panel">
        <div class="panel-header">
          <h3>{{ ENTITY_TYPE_LABELS[selectedNode.entity_type] }}详情</h3>
          <button @click="closeDetailPanel" class="close-btn">
            <Icon name="close" :size="18" />
          </button>
        </div>
        <div class="panel-content">
          <div class="detail-row">
            <span class="label">名称:</span>
            <span class="value">{{ selectedNode.label }}</span>
          </div>
          <div class="detail-row">
            <span class="label">提及数:</span>
            <span class="value">{{ selectedNode.mentions }}</span>
          </div>
          <div v-if="selectedNode.paper_ids.length" class="detail-row">
            <span class="label">关联论文:</span>
            <span class="value">{{ selectedNode.paper_ids.length }} 篇</span>
          </div>
          <div v-if="selectedNode.metadata.year" class="detail-row">
            <span class="label">年份:</span>
            <span class="value">{{ selectedNode.metadata.year }}</span>
          </div>
          <div v-if="selectedNode.metadata.venue" class="detail-row">
            <span class="label">来源:</span>
            <span class="value">{{ selectedNode.metadata.venue }}</span>
          </div>
          <div v-if="selectedNode.metadata.summary" class="detail-row full-width">
            <span class="label">摘要:</span>
            <p class="value">{{ selectedNode.metadata.summary }}</p>
          </div>
        </div>
      </div>
    </transition>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-overlay">
      <div class="spinner"></div>
      <p>加载研究地图...</p>
    </div>

    <!-- 空状态 -->
    <div v-if="!loading && visibleNodes.length === 0" class="empty-state">
      <Icon name="graph" :size="64" />
      <h3>暂无数据</h3>
      <p>调整过滤条件或选择更多论文以生成研究地图</p>
    </div>

    <!-- 图例 -->
    <div class="legend">
      <h4>图例</h4>
      <div v-for="(color, type) in ENTITY_TYPE_COLORS" :key="type" class="legend-item">
        <div class="legend-color" :style="{ backgroundColor: color }"></div>
        <span>{{ ENTITY_TYPE_LABELS[type] }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import * as d3 from 'd3'
import { useResearchMapStore } from '@/stores/researchMap'
import type {
  GraphNode,
  GraphEdge,
  EntityType,
  ResearchMapData
} from '@/types/research-map'
import {
  ENTITY_TYPE_COLORS,
  RELATION_LABELS,
  ENTITY_TYPE_LABELS,
} from '@/types/research-map'
import Icon from './common/Icon.vue'

// Store
const researchMapStore = useResearchMapStore()

// 解构 store
const {
  mapData,
  loading,
  layout: currentLayout,
  filters: storeFilters,
  selectedNode,
  selectNode,
  updateFilters
} = researchMapStore

// Local refs
const svgRef = ref<SVGElement>()
const zoomGroupRef = ref<SVGGElement>()
const simulation = ref<d3.Simulation<GraphNode, GraphEdge> | null>(null)
const zoom = ref<d3.ZoomBehavior<SVGElement, unknown> | null>(null)

// Local state
const layout = ref<'force' | 'circular' | 'hierarchical'>('force')
const entityTypeFilters = ref<EntityType[]>(['paper', 'topic', 'problem', 'method', 'dataset', 'metric', 'gap'])
const minMentionsFilter = ref(0)

// Computed
const allEntityTypes: EntityType[] = ['paper', 'topic', 'problem', 'method', 'dataset', 'metric', 'gap']

const nodes = ref<GraphNode[]>([])
const edges = ref<GraphEdge[]>([])

const visibleNodes = computed(() => {
  return nodes.value.filter(
    node =>
      entityTypeFilters.value.includes(node.entity_type) &&
      node.mentions >= minMentionsFilter.value
  )
})

const visibleEdges = computed(() => {
  const visibleNodeIds = new Set(visibleNodes.value.map(n => n.id))
  return edges.value.filter(
    edge =>
      visibleNodeIds.has(typeof edge.source === 'string' ? edge.source : edge.source.id) &&
      visibleNodeIds.has(typeof edge.target === 'string' ? edge.target : edge.target.id)
  )
})

// Methods
const initData = (data: ResearchMapData) => {
  nodes.value = data.entities.map(entity => ({
    ...entity,
    x: Math.random() * 800,
    y: Math.random() * 600,
    vx: 0,
    vy: 0,
    color: ENTITY_TYPE_COLORS[entity.entity_type],
    size: Math.max(20, Math.min(50, 20 + entity.mentions * 5)),
    r: entity.entity_type === 'paper' ? undefined : Math.max(20, Math.min(50, 20 + entity.mentions * 5)),
    width: entity.entity_type === 'paper' ? 120 : undefined,
    height: entity.entity_type === 'paper' ? 60 : undefined,
    selected: false,
    highlighted: false,
  }))

  edges.value = data.relations.map((relation, idx) => ({
    id: `edge-${idx}`,
    source: relation.source,
    target: relation.target,
    relation_type: relation.relation_type,
    weight: relation.weight,
    label: RELATION_LABELS[relation.relation_type],
    color: '#94a3b8',
    width: Math.max(1, relation.weight * 2),
    paper_ids: relation.evidence_paper_ids,
    metadata: relation.metadata,
    selected: false,
    highlighted: false,
  }))

  applyLayout()
}

const applyLayout = () => {
  if (simulation.value) {
    simulation.value.stop()
  }

  const layoutNodes = visibleNodes.value.map(n => ({ ...n }))
  const layoutEdges = visibleEdges.value.map(e => ({
    ...e,
    source: typeof e.source === 'string' ? layoutNodes.find(n => n.id === e.source)! : e.source,
    target: typeof e.target === 'string' ? layoutNodes.find(n => n.id === e.target)! : e.target,
  }))

  if (layoutNodes.length === 0) return

  const width = svgRef.value?.clientWidth || 800
  const height = svgRef.value?.clientHeight || 600

  switch (layout.value) {
    case 'force':
      applyForceLayout(layoutNodes, layoutEdges, width, height)
      break
    case 'circular':
      applyCircularLayout(layoutNodes, width, height)
      break
    case 'hierarchical':
      applyHierarchicalLayout(layoutNodes, layoutEdges, width, height)
      break
  }
}

const applyForceLayout = (layoutNodes: GraphNode[], layoutEdges: GraphEdge[], width: number, height: number) => {
  simulation.value = d3
    .forceSimulation(layoutNodes)
    .force('link', d3.forceLink(layoutEdges).id(d => (d as GraphNode).id).distance(100))
    .force('charge', d3.forceManyBody().strength(-300))
    .force('center', d3.forceCenter(width / 2, height / 2))
    .force('collision', d3.forceCollide().radius(d => (d as GraphNode).r! + 10))
    .on('tick', () => {
      layoutNodes.forEach(node => {
        const originalNode = nodes.value.find(n => n.id === node.id)
        if (originalNode) {
          originalNode.x = node.x
          originalNode.y = node.y
        }
      })
    })
}

const applyCircularLayout = (layoutNodes: GraphNode[], width: number, height: number) => {
  const centerX = width / 2
  const centerY = height / 2
  const radius = Math.min(width, height) / 2 - 100

  layoutNodes.forEach((node, i) => {
    const angle = (2 * Math.PI * i) / layoutNodes.length
    node.x = centerX + radius * Math.cos(angle)
    node.y = centerY + radius * Math.sin(angle)
  })
}

const applyHierarchicalLayout = (layoutNodes: GraphNode[], layoutEdges: GraphEdge[], width: number, height: number) => {
  const paperNodes = layoutNodes.filter(n => n.entity_type === 'paper')
  const otherNodes = layoutNodes.filter(n => n.entity_type !== 'paper')

  paperNodes.forEach((node, i) => {
    node.x = width / 2 + (i - paperNodes.length / 2) * 100
    node.y = height / 2
  })

  const levels: Record<EntityType, number> = {
    topic: 150,
    problem: 200,
    method: 250,
    dataset: 300,
    metric: 350,
    gap: 400,
  }

  otherNodes.forEach((node, i) => {
    const level = levels[node.entity_type] || 200
    const angle = (2 * Math.PI * i) / otherNodes.length
    node.x = width / 2 + level * Math.cos(angle)
    node.y = height / 2 + level * Math.sin(angle)
  })
}

const handleFiltersChange = () => {
  updateFilters({
    entityTypes: entityTypeFilters.value,
    minMentions: minMentionsFilter.value
  })
  applyLayout()
}

const handleNodeClick = (node: GraphNode) => {
  nodes.value.forEach(n => n.selected = false)
  edges.value.forEach(e => e.selected = false)
  node.selected = true
  selectNode(node)

  edges.value.forEach(edge => {
    const sourceId = typeof edge.source === 'string' ? edge.source : edge.source.id
    const targetId = typeof edge.target === 'string' ? edge.target : edge.target.id
    edge.highlighted = sourceId === node.id || targetId === node.id
  })
}

const handleEdgeClick = (edge: GraphEdge) => {
  nodes.value.forEach(n => n.selected = false)
  edges.value.forEach(e => e.selected = false)
  edge.selected = true
}

const handleNodeHover = (node: GraphNode, isHovering: boolean) => {
  node.highlighted = isHovering

  if (isHovering) {
    edges.value.forEach(edge => {
      const sourceId = typeof edge.source === 'string' ? edge.source : edge.source.id
      const targetId = typeof edge.target === 'string' ? edge.target : edge.target.id
      edge.highlighted = sourceId === node.id || targetId === node.id
    })
  } else {
    edges.value.forEach(e => e.highlighted = false)
  }
}

const handleEdgeHover = (edge: GraphEdge, isHovering: boolean) => {
  edge.highlighted = isHovering
}

const handleBackgroundClick = () => {
  nodes.value.forEach(n => {
    n.selected = false
    n.highlighted = false
  })
  edges.value.forEach(e => {
    e.selected = false
    e.highlighted = false
  })
}

const closeDetailPanel = () => {
  if (selectedNode.value) {
    selectedNode.value.selected = false
  }
}

const zoomIn = () => {
  zoom.value?.scaleBy(svgRef.value!, 1.3)
}

const zoomOut = () => {
  zoom.value?.scaleBy(svgRef.value!, 0.7)
}

const resetZoom = () => {
  zoom.value?.transform(
    d3.zoomIdentity.translate(0, 0).scale(1),
    svgRef.value!
  )
}

const getNodePosition = (nodeOrId: string | GraphNode): { x: number; y: number } => {
  const id = typeof nodeOrId === 'string' ? nodeOrId : nodeOrId.id
  const node = visibleNodes.value.find(n => n.id === id)
  return node ? { x: node.x!, y: node.y! } : { x: 0, y: 0 }
}

const truncateLabel = (label: string, maxLength: number): string => {
  return label.length > maxLength ? label.substring(0, maxLength) + '...' : label
}

const setupZoom = () => {
  if (!svgRef.value) return

  zoom.value = d3
    .zoom<SVGElement, unknown>()
    .scaleExtent([0.1, 4])
    .on('zoom', (event) => {
      if (zoomGroupRef.value) {
        d3.select(zoomGroupRef.value).attr(
          'transform',
          `translate(${event.transform.x}, ${event.transform.y}) scale(${event.transform.k})`
        )
      }
    })

  d3.select(svgRef.value).call(zoom.value)
}

// Watch
watch(mapData, newData => {
  if (newData) {
    initData(newData)
  }
}, { immediate: true })

// Lifecycle
onMounted(() => {
  nextTick(() => {
    setupZoom()
  })
})

onUnmounted(() => {
  if (simulation.value) {
    simulation.value.stop()
  }
})
</script>

<style scoped>
.research-graph-container {
  position: relative;
  width: 100%;
  height: 100%;
  min-height: 600px;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  border-radius: 8px;
  overflow: hidden;
}

.graph-controls {
  position: absolute;
  top: 16px;
  left: 16px;
  z-index: 10;
  background: white;
  padding: 12px;
  border-radius: 8px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  display: flex;
  gap: 16px;
  align-items: center;
  flex-wrap: wrap;
}

.control-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.control-group label {
  font-size: 12px;
  font-weight: 600;
  color: #475569;
}

.control-group select,
.control-group input[type="range"] {
  padding: 4px 8px;
  border: 1px solid #cbd5e1;
  border-radius: 4px;
  font-size: 12px;
}

.control-group select[multiple] {
  height: 80px;
  min-width: 100px;
}

.control-group button {
  padding: 4px 8px;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.control-group button:hover {
  background: #2563eb;
}

.graph-svg {
  width: 100%;
  height: 100%;
  cursor: grab;
}

.graph-svg:active {
  cursor: grabbing;
}

.graph-edge {
  cursor: pointer;
  transition: all 0.2s;
}

.graph-edge:hover {
  stroke-opacity: 0.8 !important;
}

.graph-edge.selected {
  stroke: #1e293b !important;
  stroke-width: 3 !important;
}

.graph-edge.highlighted {
  stroke-opacity: 0.9 !important;
  stroke-width: 2 !important;
}

.node-group {
  cursor: pointer;
  transition: all 0.2s;
}

.node-group:hover circle,
.node-group:hover rect {
  filter: brightness(1.1);
}

.node-group.selected circle,
.node-group.selected rect {
  stroke: #1e293b !important;
  stroke-width: 3 !important;
}

.node-group.highlighted circle,
.node-group.highlighted rect {
  stroke: #ffffff !important;
  stroke-width: 2 !important;
}

.node-rect,
.node-circle {
  transition: all 0.2s;
}

.node-label {
  font-size: 12px;
  fill: #1e293b;
  font-weight: 500;
  pointer-events: none;
}

.node-label-white {
  fill: white !important;
}

.node-label-small {
  font-size: 11px;
  fill: #475569;
  font-weight: 500;
  pointer-events: none;
}

.edge-label {
  pointer-events: none;
  opacity: 0.8;
  font-size: 10px;
  fill: #64748b;
}

.node-detail-panel {
  position: absolute;
  top: 16px;
  right: 16px;
  width: 300px;
  max-height: calc(100% - 32px);
  background: white;
  border-radius: 8px;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.15);
  z-index: 20;
  overflow-y: auto;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #e2e8f0;
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

.loading-overlay {
  position: absolute;
  inset: 0;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 30;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e2e8f0;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-overlay p {
  margin-top: 16px;
  color: #64748b;
  font-size: 14px;
}

.empty-state {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 25;
}

.empty-state h3 {
  margin: 16px 0 8px;
  font-size: 18px;
  color: #64748b;
}

.empty-state p {
  font-size: 14px;
  color: #94a3b8;
  text-align: center;
  max-width: 300px;
}

.legend {
  position: absolute;
  bottom: 16px;
  left: 16px;
  background: white;
  padding: 12px;
  border-radius: 8px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  z-index: 10;
}

.legend h4 {
  margin: 0 0 8px;
  font-size: 12px;
  font-weight: 600;
  color: #475569;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 2px;
}

.legend-item span {
  font-size: 11px;
  color: #64748b;
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
