/**
 * Zotero API 服务层
 * 负责与 Python 后端通信
 */

import type {
  ZoteroConfig,
  ZoteroItem,
  ZoteroCollection,
  ZoteroImportBatch,
  ZoteroSyncResult,
  ZoteroImportResult
} from '../types/zotero'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8713'

class ZoteroApiService {
  private baseUrl: string

  constructor() {
    this.baseUrl = API_BASE_URL
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`

    try {
      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      })

      if (!response.ok) {
        const error = await response.json().catch(() => ({
          error: `HTTP ${response.status}: ${response.statusText}`
        }))
        throw new Error(error.error || error.message || '请求失败')
      }

      return response.json()
    } catch (error: any) {
      if (error instanceof TypeError && error.message === 'Failed to fetch') {
        throw new Error('无法连接到后端服务，请确保服务已启动')
      }
      throw error
    }
  }

  // 测试连接
  async testConnection(config: ZoteroConfig): Promise<{ success: boolean; message: string }> {
    return this.request('/api/zotero/test-connection', {
      method: 'POST',
      body: JSON.stringify(config),
    })
  }

  // 获取文献列表
  async getItems(params?: {
    collection?: string
    since?: number
    limit?: number
  }): Promise<ZoteroItem[]> {
    const searchParams = new URLSearchParams()
    if (params?.collection) searchParams.append('collection', params.collection)
    if (params?.since) searchParams.append('since', params.since.toString())
    if (params?.limit) searchParams.append('limit', params.limit.toString())

    return this.request(`/api/zotero/items?${searchParams.toString()}`)
  }

  // 获取集合列表
  async getCollections(): Promise<ZoteroCollection[]> {
    return this.request('/api/zotero/collections')
  }

  // 同步所有数据
  async syncAll(mode: 'full' | 'incremental' = 'full'): Promise<ZoteroSyncResult> {
    return this.request('/api/zotero/sync', {
      method: 'POST',
      body: JSON.stringify({ mode }),
    })
  }

  // 上传导入文件
  async uploadImportFile(
    libraryName: string,
    importType: string,
    files: File[]
  ): Promise<ZoteroImportBatch> {
    const formData = new FormData()
    formData.append('libraryName', libraryName)
    formData.append('importType', importType)
    files.forEach((file, index) => {
      formData.append(`files`, file)
    })

    const response = await fetch(`${this.baseUrl}/api/zotero/import`, {
      method: 'POST',
      body: formData,
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ error: '上传失败' }))
      throw new Error(error.error || '上传失败')
    }

    return response.json()
  }

  // 获取导入批次列表
  async getImportBatches(): Promise<ZoteroImportBatch[]> {
    return this.request('/api/zotero/import/batches')
  }

  // 导入选中的文献到论文库
  async importToLibrary(
    itemKeys: string[],
    options?: {
      includeAttachments?: boolean
      includeNotes?: boolean
      includeTags?: boolean
    }
  ): Promise<ZoteroImportResult> {
    return this.request('/api/zotero/import-to-library', {
      method: 'POST',
      body: JSON.stringify({
        itemKeys,
        ...options,
      }),
    })
  }

  // 搜索文献
  async searchItems(query: string, filters?: {
    itemType?: string
    tags?: string[]
    collection?: string
  }): Promise<ZoteroItem[]> {
    const params: any = { q: query }
    if (filters?.itemType) params.itemType = filters.itemType
    if (filters?.collection) params.collection = filters.collection
    if (filters?.tags) params.tags = filters.tags

    const searchParams = new URLSearchParams(params)
    return this.request(`/api/zotero/search?${searchParams.toString()}`)
  }

  // 获取单个文献详情
  async getItemDetails(itemKey: string): Promise<ZoteroItem> {
    return this.request(`/api/zotero/items/${itemKey}`)
  }

  // 获取文献的附件
  async getItemAttachments(itemKey: string): Promise<ZoteroItem['attachments']> {
    return this.request(`/api/zotero/items/${itemKey}/attachments`)
  }

  // 回写分析结果到 Zotero
  async writebackAnalysis(
    itemKey: string,
    analysisSummary: string,
    tags?: string[]
  ): Promise<{ success: boolean; message: string }> {
    return this.request('/api/zotero/writeback-analysis', {
      method: 'POST',
      body: JSON.stringify({
        itemKey,
        analysisSummary,
        tags,
      }),
    })
  }
}

// 导出单例实例
export const zoteroApi = new ZoteroApiService()

// 导出类型
export type {
  ZoteroConfig,
  ZoteroItem,
  ZoteroCollection,
  ZoteroImportBatch,
  ZoteroSyncResult,
  ZoteroImportResult
}
