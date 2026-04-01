/** API 请求工具 */

import type { ResearchMapData } from '@/types/research-map'
import { useAuthStore } from '@/stores/auth'

// API 基础地址
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

/**
 * 获取认证头
 */
function getAuthHeaders(): Record<string, string> {
  const authStore = useAuthStore()
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  }

  if (authStore.token) {
    headers['Authorization'] = `Bearer ${authStore.token}`
  }

  return headers
}

/**
 * 通用 API 请求函数
 */
async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`

  const response = await fetch(url, {
    ...options,
    headers: {
      ...getAuthHeaders(),
      ...options.headers,
    },
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ message: response.statusText }))
    throw new Error(error.message || `API 请求失败: ${response.statusText}`)
  }

  return response.json()
}

/**
 * 获取研究地图数据
 */
export async function fetchResearchMap(cacheKeys?: string[]): Promise<ResearchMapData> {
  const params = new URLSearchParams()
  if (cacheKeys && cacheKeys.length > 0) {
    params.set('cacheKeys', cacheKeys.join(','))
  }

  const endpoint = `/research-map${params.toString() ? `?${params.toString()}` : ''}`
  const response = await apiRequest<{ data: ResearchMapData }>(endpoint)
  return response.data
}

/**
 * 获取单个实体详情
 */
export async function fetchEntityDetail(entityId: string): Promise<any> {
  const response = await apiRequest<{ entity: any; relatedPapers: any[]; relations: any[] }>(
    `/entities/${entityId}`
  )
  return response
}

/**
 * 搜索节点
 */
export async function searchNodes(query: string, filters?: {
  entityTypes?: string[]
  minMentions?: number
}): Promise<any[]> {
  const params = new URLSearchParams({ q: query })

  if (filters?.entityTypes?.length) {
    params.set('entityTypes', filters.entityTypes.join(','))
  }

  if (filters?.minMentions !== undefined) {
    params.set('minMentions', filters.minMentions.toString())
  }

  const response = await apiRequest<{ results: any[]; total: number }>(
    `/search?${params.toString()}`
  )
  return response.results
}

/**
 * 导出研究地图
 */
export async function exportResearchMap(format: 'json' | 'svg' = 'json', cacheKeys?: string[]): Promise<Blob> {
  const params = new URLSearchParams({ format })
  if (cacheKeys && cacheKeys.length > 0) {
    params.set('cacheKeys', cacheKeys.join(','))
  }

  const authStore = useAuthStore()
  const headers: Record<string, string> = {}

  if (authStore.token) {
    headers['Authorization'] = `Bearer ${authStore.token}`
  }

  const url = `${API_BASE_URL}/research-map/export?${params.toString()}`
  const response = await fetch(url, { headers })

  if (!response.ok) {
    throw new Error(`导出失败: ${response.statusText}`)
  }

  return response.blob()
}
