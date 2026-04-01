/**
 * Zotero 集成状态管理
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useAuthStore } from './auth'
import type {
  ZoteroConfig,
  ZoteroConnection,
  ZoteroItem,
  ZoteroCollection,
  ZoteroImportBatch,
  ZoteroSearchParams,
  ZoteroSyncResult,
  ZoteroImportResult
} from '../types/zotero'

export const useZoteroStore = defineStore('zotero', () => {
  const authStore = useAuthStore()

  // 配置与连接状态
  const config = ref<ZoteroConfig>({
    apiKey: '',
    libraryId: '',
    libraryType: 'user',
    baseUrl: 'https://api.zotero.org'
  })

  const connection = ref<ZoteroConnection>({
    isConnected: false,
    isConnecting: false,
    lastSyncTime: null,
    error: null
  })

  // 数据缓存
  const items = ref<ZoteroItem[]>([])
  const collections = ref<ZoteroCollection[]>([])
  const batches = ref<ZoteroImportBatch[]>([])

  // UI 状态
  const isLoading = ref(false)
  const selectedItems = ref<Set<string>>(new Set())
  const currentCollection = ref<string | null>(null)
  const searchParams = ref<ZoteroSearchParams>({})

  // 计算属性
  const filteredItems = computed(() => {
    let result = items.value

    // 按集合筛选
    if (currentCollection.value) {
      result = result.filter(item =>
        item.collections?.includes(currentCollection.value!)
      )
    }

    // 按搜索词筛选
    if (searchParams.value.q) {
      const query = searchParams.value.q.toLowerCase()
      result = result.filter(item =>
        item.title.toLowerCase().includes(query) ||
        item.creators?.some(c =>
          `${c.firstName} ${c.lastName}`.toLowerCase().includes(query)
        ) ||
        item.abstractNote?.toLowerCase().includes(query)
      )
    }

    // 按类型筛选
    if (searchParams.value.itemType) {
      result = result.filter(item => item.itemType === searchParams.value.itemType)
    }

    // 按标签筛选
    if (searchParams.value.tags && searchParams.value.tags.length > 0) {
      result = result.filter(item =>
        searchParams.value.tags!.some(tag =>
          item.tags?.some(t => t.tag === tag)
        )
      )
    }

    return result
  })

  const selectedItemCount = computed(() => selectedItems.value.size)

  const collectionTree = computed(() => {
    const buildTree = (parentKey?: string): ZoteroCollection[] => {
      return collections.value
        .filter(c => c.parentKey === parentKey)
        .map(c => ({
          ...c,
          children: buildTree(c.key)
        }))
    }
    return buildTree()
  })

  const allTags = computed(() => {
    const tagSet = new Set<string>()
    items.value.forEach(item => {
      item.tags?.forEach(tag => tagSet.add(tag.tag))
    })
    return Array.from(tagSet).sort()
  })

  const itemTypes = computed(() => {
    const typeSet = new Set<string>()
    items.value.forEach(item => typeSet.add(item.itemType))
    return Array.from(typeSet).sort()
  })

  // Actions
  function setConfig(newConfig: Partial<ZoteroConfig>) {
    config.value = { ...config.value, ...newConfig }
    // 保存到 localStorage，关联用户ID
    const userId = authStore.user?.id || 'default'
    const storageKey = `zotero_config_${userId}`
    localStorage.setItem(storageKey, JSON.stringify(config.value))
  }

  function loadConfig() {
    const userId = authStore.user?.id || 'default'
    const storageKey = `zotero_config_${userId}`
    const saved = localStorage.getItem(storageKey)
    if (saved) {
      try {
        config.value = JSON.parse(saved)
        if (config.value.apiKey && config.value.libraryId) {
          connection.value.isConnected = true
        }
      } catch (e) {
        console.error('加载 Zotero 配置失败', e)
      }
    }
  }

  async function testConnection(): Promise<boolean> {
    connection.value.isConnecting = true
    connection.value.error = null

    try {
      // 这里应该调用实际的 Zotero API
      // 暂时模拟连接测试
      await new Promise(resolve => setTimeout(resolve, 1000))

      if (config.value.apiKey && config.value.libraryId) {
        connection.value.isConnected = true
        connection.value.lastSyncTime = new Date().toISOString()
        setConfig(config.value)
        return true
      }

      throw new Error('API Key 和 Library ID 不能为空')
    } catch (error: any) {
      connection.value.isConnected = false
      connection.value.error = error.message
      return false
    } finally {
      connection.value.isConnecting = false
    }
  }

  async function fetchItems(params?: ZoteroSearchParams): Promise<void> {
    isLoading.value = true
    try {
      // 这里应该调用实际的 API
      // 暂时返回空数据
      await new Promise(resolve => setTimeout(resolve, 500))
      items.value = []
    } catch (error: any) {
      console.error('获取 Zotero 条目失败', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  async function fetchCollections(): Promise<void> {
    isLoading.value = true
    try {
      // 这里应该调用实际的 API
      await new Promise(resolve => setTimeout(resolve, 500))
      collections.value = []
    } catch (error: any) {
      console.error('获取 Zotero 集合失败', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  async function syncAll(mode: 'full' | 'incremental' = 'full'): Promise<ZoteroSyncResult> {
    isLoading.value = true
    connection.value.isConnecting = true

    try {
      await fetchItems()
      await fetchCollections()

      connection.value.lastSyncTime = new Date().toISOString()

      return {
        success: true,
        mode,
        itemCount: items.value.length,
        message: `成功同步 ${items.value.length} 个条目`
      }
    } catch (error: any) {
      console.error('同步失败', error)
      return {
        success: false,
        mode,
        itemCount: 0,
        message: error.message || '同步失败'
      }
    } finally {
      isLoading.value = false
      connection.value.isConnecting = false
    }
  }

  async function importSelectedToLibrary(): Promise<ZoteroImportResult> {
    isLoading.value = true

    try {
      const itemKeys = Array.from(selectedItems.value)
      await new Promise(resolve => setTimeout(resolve, 1000))

      return {
        success: true,
        message: `成功导入 ${itemKeys.length} 篇文献`,
        importedCount: itemKeys.length,
        failedCount: 0
      }
    } catch (error: any) {
      console.error('导入失败', error)
      return {
        success: false,
        message: error.message || '导入失败',
        importedCount: 0,
        failedCount: 0
      }
    } finally {
      isLoading.value = false
    }
  }

  function toggleItemSelection(key: string) {
    if (selectedItems.value.has(key)) {
      selectedItems.value.delete(key)
    } else {
      selectedItems.value.add(key)
    }
  }

  function selectAll() {
    filteredItems.value.forEach(item => selectedItems.value.add(item.key))
  }

  function clearSelection() {
    selectedItems.value.clear()
  }

  function addBatch(batch: ZoteroImportBatch) {
    batches.value.unshift(batch)
  }

  function updateBatch(id: string, updates: Partial<ZoteroImportBatch>) {
    const index = batches.value.findIndex(b => b.id === id)
    if (index !== -1) {
      batches.value[index] = { ...batches.value[index], ...updates }
    }
  }

  function setSearchParams(params: ZoteroSearchParams) {
    searchParams.value = { ...searchParams.value, ...params }
  }

  function resetSearch() {
    searchParams.value = {}
    currentCollection.value = null
  }

  // 初始化时加载配置
  loadConfig()

  return {
    // State
    config,
    connection,
    items,
    collections,
    batches,
    isLoading,
    selectedItems,
    currentCollection,
    searchParams,

    // Computed
    filteredItems,
    selectedItemCount,
    collectionTree,
    allTags,
    itemTypes,

    // Actions
    setConfig,
    testConnection,
    fetchItems,
    fetchCollections,
    syncAll,
    importSelectedToLibrary,
    toggleItemSelection,
    selectAll,
    clearSelection,
    addBatch,
    updateBatch,
    setSearchParams,
    resetSearch
  }
})
