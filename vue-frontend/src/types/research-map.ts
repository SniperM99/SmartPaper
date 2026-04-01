/** 研究地图类型定义 */

export type EntityType =
  | 'paper'
  | 'topic'
  | 'problem'
  | 'method'
  | 'dataset'
  | 'metric'
  | 'gap'

export type RelationType =
  | 'studies_topic'
  | 'addresses_problem'
  | 'uses_method'
  | 'evaluates_on_dataset'
  | 'evaluated_by_metric'
  | 'related_to'
  | 'evolves_from'
  | 'highlights_gap'

export interface ResearchEntity {
  id: string
  entity_type: EntityType
  label: string
  aliases: string[]
  paper_ids: string[]
  mentions: number
  metadata: Record<string, any>
}

export interface ResearchRelation {
  source: string
  target: string
  relation_type: RelationType
  weight: number
  evidence_paper_ids: string[]
  metadata: Record<string, any>
}

export interface TimelineEvent {
  year: string
  paper_ids: string[]
  key_topics: string[]
  key_methods: string[]
  highlights: string[]
}

export interface ResearchCluster {
  id: string
  label: string
  paper_ids: string[]
  topic_ids: string[]
  method_ids: string[]
  summary: string
}

export interface ResearchGap {
  id: string
  title: string
  description: string
  gap_type: 'explicit_gap' | 'sparse_topic' | 'missing_evaluation'
  priority: 'high' | 'medium' | 'low'
  evidence_paper_ids: string[]
  related_entity_ids: string[]
}

export interface ResearchMapData {
  overview: Record<string, any>
  entities: ResearchEntity[]
  relations: ResearchRelation[]
  timeline: TimelineEvent[]
  clusters: ResearchCluster[]
  gaps: ResearchGap[]
}

/** 图谱节点（用于前端可视化） */
export interface GraphNode {
  id: string
  entity_type: EntityType
  label: string
  x?: number
  y?: number
  vx?: number
  vy?: number
  r?: number // 半径（圆形节点）
  width?: number // 宽度（矩形节点）
  height?: number // 高度（矩形节点）
  color: string
  size: number
  paper_ids: string[]
  mentions: number
  metadata: Record<string, any>
  selected?: boolean
  highlighted?: boolean
}

/** 图谱边（用于前端可视化） */
export interface GraphEdge {
  id: string
  source: string | GraphNode
  target: string | GraphNode
  relation_type: RelationType
  weight: number
  label: string
  color: string
  width: number
  paper_ids: string[]
  metadata: Record<string, any>
  selected?: boolean
  highlighted?: boolean
}

/** 图谱视图状态 */
export interface GraphViewState {
  transform: {
    x: number
    y: number
    k: number
  }
  selectedNode: GraphNode | null
  selectedEdge: GraphEdge | null
  hoveredNode: GraphNode | null
  hoveredEdge: GraphEdge | null
  filters: {
    entityTypes: EntityType[]
    minMentions: number
  }
  layout: 'force' | 'circular' | 'hierarchical'
}

/** 实体类型颜色配置 */
export const ENTITY_TYPE_COLORS: Record<EntityType, string> = {
  paper: '#3b82f6',       // 蓝色
  topic: '#10b981',       // 绿色
  problem: '#f59e0b',     // 橙色
  method: '#8b5cf6',      // 紫色
  dataset: '#ec4899',     // 粉色
  metric: '#06b6d4',      // 青色
  gap: '#ef4444',         // 红色
}

/** 关系类型标签映射 */
export const RELATION_LABELS: Record<RelationType, string> = {
  studies_topic: '研究主题',
  addresses_problem: '解决问题',
  uses_method: '使用方法',
  evaluates_on_dataset: '评估数据集',
  evaluated_by_metric: '评估指标',
  related_to: '相关',
  evolves_from: '演化自',
  highlights_gap: '指出空白',
}

/** 实体类型标签映射 */
export const ENTITY_TYPE_LABELS: Record<EntityType, string> = {
  paper: '论文',
  topic: '主题',
  problem: '问题',
  method: '方法',
  dataset: '数据集',
  metric: '指标',
  gap: '空白',
}
