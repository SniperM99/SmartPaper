/**
 * Zotero 集成相关类型定义
 */

export interface ZoteroConfig {
  apiKey: string
  libraryId: string
  libraryType: 'user' | 'group'
  baseUrl?: string
}

export interface ZoteroConnection {
  isConnected: boolean
  isConnecting: boolean
  lastSyncTime: string | null
  error: string | null
}

export interface ZoteroCollection {
  key: string
  name: string
  parentKey?: string
  itemCount?: number
}

export interface ZoteroTag {
  tag: string
  color?: string
}

export interface ZoteroAttachment {
  key: string
  title: string
  mimeType?: string
  path?: string
  size?: number
}

export interface ZoteroItem {
  key: string
  version: number
  itemType: string
  title: string
  creators?: Array<{
    creatorType: string
    firstName: string
    lastName: string
  }>
  abstractNote?: string
  date?: string
  DOI?: string
  url?: string
  collections?: string[]
  tags?: ZoteroTag[]
  attachments?: ZoteroAttachment[]
  dateAdded: string
  dateModified: string
}

export interface ZoteroImportBatch {
  id: string
  libraryName: string
  importType: string
  files: string[]
  timestamp: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  itemCount?: number
  importedCount?: number
}

export interface ZoteroSyncState {
  mode: 'full' | 'incremental'
  cursor?: number | null
  itemKeys?: string[]
  maxRemoteVersion?: number | null
}

export interface ZoteroWritebackPayload {
  provider: 'zotero'
  direction: string
  target: {
    library_id: string
    library_type: string
    item_key: string
    version: number
  }
  note: {
    title: string
    content_markdown: string
  }
  tags_to_upsert: Array<{ tag: string }>
  analysis_refs: string[]
}

export interface ZoteroSearchParams {
  q?: string
  itemType?: string
  collection?: string
  tags?: string[]
  since?: number
}

export interface ZoteroImportResult {
  success: boolean
  message: string
  importedCount: number
  failedCount: number
  errors?: Array<{ itemKey: string; error: string }>
}

export interface ZoteroSyncResult {
  success: boolean
  mode: 'full' | 'incremental'
  itemCount: number
  message: string
  newItems?: number
  updatedItems?: number
  deletedItems?: number
}
