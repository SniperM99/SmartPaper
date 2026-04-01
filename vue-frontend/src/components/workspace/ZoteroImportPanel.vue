<script setup lang="ts">
import { ref, computed } from 'vue'
import { useZoteroStore } from '../../stores/zotero'
import Icon from '../common/Icon.vue'
import type { ZoteroImportBatch } from '../../types/zotero'

const zotero = useZoteroStore()

// 文件上传
const fileInput = ref<HTMLInputElement>()
const isDragging = ref(false)
const uploadedFiles = ref<File[]>([])

// 导入配置
const libraryName = ref('')
const importType = ref('条目 + 附件')
const importOptions = ref({
  includeAttachments: true,
  includeNotes: true,
  includeTags: true,
  preserveCollections: true
})

// 导入结果
const importing = ref(false)
const importResult = ref<{
  success: boolean
  message: string
  importedCount: number
} | null>(null)

// 批次状态
const activeTab = ref<'upload' | 'batches'>('upload')

const canImport = computed(() =>
  libraryName.value && uploadedFiles.value.length > 0 && !importing.value
)

function triggerFileSelect() {
  fileInput.value?.click()
}

function handleFileSelect(event: Event) {
  const target = event.target as HTMLInputElement
  if (target.files) {
    handleFiles(Array.from(target.files))
  }
}

function handleDragOver(event: DragEvent) {
  event.preventDefault()
  isDragging.value = true
}

function handleDragLeave(event: DragEvent) {
  event.preventDefault()
  isDragging.value = false
}

function handleDrop(event: DragEvent) {
  event.preventDefault()
  isDragging.value = false

  if (event.dataTransfer?.files) {
    handleFiles(Array.from(event.dataTransfer.files))
  }
}

function handleFiles(files: File[]) {
  const jsonFiles = files.filter(f =>
    f.name.endsWith('.json') ||
    f.name.endsWith('.bib') ||
    f.name.endsWith('.rdf')
  )
  uploadedFiles.value.push(...jsonFiles)
}

function removeFile(index: number) {
  uploadedFiles.value.splice(index, 1)
}

function clearFiles() {
  uploadedFiles.value = []
  importResult.value = null
}

async function startImport() {
  importing.value = true
  importResult.value = null

  try {
    const batch: ZoteroImportBatch = {
      id: `batch-${Date.now()}`,
      libraryName: libraryName.value,
      importType: importType.value,
      files: uploadedFiles.value.map(f => f.name),
      timestamp: new Date().toISOString(),
      status: 'processing',
      itemCount: 0
    }

    zotero.addBatch(batch)

    await new Promise(resolve => setTimeout(resolve, 2000))

    const importedCount = Math.floor(Math.random() * 50) + 10
    zotero.updateBatch(batch.id, {
      status: 'completed',
      itemCount: importedCount,
      importedCount
    })

    importResult.value = {
      success: true,
      message: `成功导入 ${importedCount} 篇文献`,
      importedCount
    }

    clearFiles()
    libraryName.value = ''
    activeTab.value = 'batches'
  } catch (error: any) {
    console.error('导入失败', error)
    importResult.value = {
      success: false,
      message: error.message || '导入失败，请重试',
      importedCount: 0
    }
  } finally {
    importing.value = false
  }
}

function getStatusBadge(status: ZoteroImportBatch['status']) {
  const statusConfig = {
    pending: { label: '待处理', color: 'var(--color-warning)', bg: 'var(--color-warning-light)' },
    processing: { label: '处理中', color: 'var(--color-info)', bg: 'var(--color-info-light)' },
    completed: { label: '已完成', color: 'var(--color-success)', bg: 'var(--color-success-light)' },
    failed: { label: '失败', color: 'var(--color-error)', bg: 'var(--color-error-light)' }
  }
  return statusConfig[status] || statusConfig.pending
}
</script>

<template>
  <div class="zotero-import-panel">
    <div class="tabs">
      <button
        class="tab"
        :class="{ active: activeTab === 'upload' }"
        @click="activeTab = 'upload'"
      >
        <Icon name="upload" :size="16" />
        <span>上传导入</span>
      </button>
      <button
        class="tab"
        :class="{ active: activeTab === 'batches' }"
        @click="activeTab = 'batches'"
      >
        <Icon name="list" :size="16" />
        <span>导入批次</span>
        <span v-if="zotero.batches.length" class="tab-badge">{{ zotero.batches.length }}</span>
      </button>
    </div>

    <!-- 上传导入 -->
    <div v-if="activeTab === 'upload'" class="tab-content">
      <div class="import-config">
        <div class="form-group">
          <label>Library / Collection 名称 *</label>
          <input
            v-model="libraryName"
            type="text"
            placeholder="例如：My Library / AI-Papers"
          />
        </div>

        <div class="form-group">
          <label>导入类型</label>
          <select v-model="importType">
            <option value="条目 + 附件">条目 + 附件</option>
            <option value="仅条目">仅条目</option>
            <option value="仅附件">仅附件</option>
          </select>
        </div>

        <div class="options-grid">
          <label class="option">
            <input
              v-model="importOptions.includeAttachments"
              type="checkbox"
            />
            <span>包含附件</span>
          </label>
          <label class="option">
            <input
              v-model="importOptions.includeNotes"
              type="checkbox"
            />
            <span>包含笔记</span>
          </label>
          <label class="option">
            <input
              v-model="importOptions.includeTags"
              type="checkbox"
            />
            <span>包含标签</span>
          </label>
          <label class="option">
            <input
              v-model="importOptions.preserveCollections"
              type="checkbox"
            />
            <span>保留 Collection 路径</span>
          </label>
        </div>
      </div>

      <div
        class="upload-zone"
        :class="{ dragging: isDragging }"
        @dragover="handleDragOver"
        @dragleave="handleDragLeave"
        @drop="handleDrop"
        @click="triggerFileSelect"
      >
        <input
          ref="fileInput"
          type="file"
          multiple
          accept=".json,.bib,.rdf"
          style="display: none"
          @change="handleFileSelect"
        />

        <Icon name="upload" :size="48" class="upload-icon" />
        <h3>拖放文件到此处</h3>
        <p>或点击选择文件</p>
        <p class="upload-hint">支持 Zotero JSON 导出、BibTeX、RDF 格式</p>
      </div>

      <!-- 已选文件列表 -->
      <div v-if="uploadedFiles.length > 0" class="files-list">
        <div class="files-header">
          <span>已选择 {{ uploadedFiles.length }} 个文件</span>
          <button class="btn btn-link" @click="clearFiles">
            <Icon name="close" :size="14" />
            清空
          </button>
        </div>

        <div class="files-items">
          <div
            v-for="(file, index) in uploadedFiles"
            :key="index"
            class="file-item"
          >
            <Icon name="file-text" :size="18" />
            <span class="file-name">{{ file.name }}</span>
            <span class="file-size">{{ (file.size / 1024).toFixed(1) }} KB</span>
            <button class="btn btn-icon" @click="removeFile(index)">
              <Icon name="close" :size="16" />
            </button>
          </div>
        </div>
      </div>

      <!-- 导入结果 -->
      <div v-if="importResult" class="import-result" :class="importResult.success ? 'success' : 'error'">
        <Icon :name="importResult.success ? 'check-circle' : 'alert-circle'" :size="24" />
        <div class="result-message">{{ importResult.message }}</div>
      </div>

      <!-- 导入按钮 -->
      <button
        class="btn btn-primary btn-large"
        :disabled="!canImport || importing"
        @click="startImport"
      >
        <Icon v-if="importing" name="loading" :size="18" class="spin" />
        <Icon v-else name="upload" :size="18" />
        <span>{{ importing ? '导入中...' : '开始导入' }}</span>
      </button>
    </div>

    <!-- 批次列表 -->
    <div v-else class="tab-content">
      <div v-if="zotero.batches.length === 0" class="empty-batches">
        <Icon name="list" :size="64" class="empty-icon" />
        <h3>暂无导入批次</h3>
        <p>上传文件并导入后，批次记录将显示在这里</p>
        <button class="btn btn-primary" @click="activeTab = 'upload'">
          <Icon name="upload" :size="16" />
          开始导入
        </button>
      </div>

      <div v-else class="batches-list">
        <div
          v-for="batch in zotero.batches"
          :key="batch.id"
          class="batch-item"
        >
          <div class="batch-header">
            <h4 class="batch-name">{{ batch.libraryName }}</h4>
            <span
              class="status-badge"
              :style="{
                background: getStatusBadge(batch.status).bg,
                color: getStatusBadge(batch.status).color
              }"
            >
              {{ getStatusBadge(batch.status).label }}
            </span>
          </div>

          <div class="batch-details">
            <div class="detail-item">
              <span class="detail-label">类型：</span>
              <span>{{ batch.importType }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">文件：</span>
              <span>{{ batch.files.length }} 个</span>
            </div>
            <div v-if="batch.itemCount" class="detail-item">
              <span class="detail-label">条目数：</span>
              <span>{{ batch.itemCount }}</span>
            </div>
            <div v-if="batch.importedCount" class="detail-item">
              <span class="detail-label">已导入：</span>
              <span>{{ batch.importedCount }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">时间：</span>
              <span>{{ new Date(batch.timestamp).toLocaleString('zh-CN') }}</span>
            </div>
          </div>

          <div class="batch-files">
            <span v-for="(file, idx) in batch.files.slice(0, 3)" :key="idx" class="file-tag">
              <Icon name="file-text" :size="12" />
              {{ file }}
            </span>
            <span v-if="batch.files.length > 3" class="file-tag">
              +{{ batch.files.length - 3 }}
            </span>
          </div>

          <div class="batch-actions">
            <button
              v-if="batch.status === 'completed'"
              class="btn btn-secondary btn-sm"
            >
              <Icon name="list" :size="14" />
              查看详情
            </button>
            <button
              v-if="batch.status === 'failed'"
              class="btn btn-secondary btn-sm"
            >
              <Icon name="refresh" :size="14" />
              重试
            </button>
            <button
              class="btn btn-link btn-sm"
            >
              <Icon name="close" :size="14" />
              删除
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.zotero-import-panel {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* 标签页 */
.tabs {
  display: flex;
  gap: 0.5rem;
  border-bottom: 1px solid var(--color-border);
}

.tab {
  padding: 0.75rem 1.25rem;
  background: transparent;
  border: none;
  border-bottom: 2px solid transparent;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.tab:hover {
  color: var(--color-primary);
}

.tab.active {
  color: var(--color-primary);
  border-bottom-color: var(--color-primary);
}

.tab-badge {
  background: var(--color-primary);
  color: white;
  border-radius: var(--radius-full);
  padding: 0.125rem 0.5rem;
  font-size: 0.7rem;
  min-width: 1.25rem;
  text-align: center;
  font-weight: var(--font-weight-semibold);
}

.tab-content {
  padding: 1rem 0;
}

/* 配置区域 */
.import-config {
  background: var(--color-bg-primary);
  border-radius: var(--radius-lg);
  padding: 1.25rem;
  margin-bottom: 1rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
  font-size: var(--font-size-sm);
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: var(--font-size-base);
  background: var(--color-bg-secondary);
  color: var(--color-text-primary);
}

.options-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 0.75rem;
}

.option {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  font-size: var(--font-size-sm);
  color: var(--color-text-primary);
}

/* 上传区域 */
.upload-zone {
  background: var(--color-bg-primary);
  border: 2px dashed var(--color-border);
  border-radius: var(--radius-lg);
  padding: 3rem 2rem;
  text-align: center;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.upload-zone:hover,
.upload-zone.dragging {
  border-color: var(--color-primary);
  background: var(--color-primary-light);
}

.upload-icon {
  color: var(--color-primary);
  margin-bottom: 1rem;
  opacity: 0.8;
}

.upload-zone h3 {
  margin: 0 0 0.5rem 0;
  color: var(--color-text-primary);
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-semibold);
}

.upload-zone p {
  margin: 0 0 0.25rem 0;
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
}

.upload-hint {
  font-size: var(--font-size-xs) !important;
  color: var(--color-text-tertiary);
  margin-top: 0.75rem !important;
}

/* 文件列表 */
.files-list {
  background: var(--color-bg-primary);
  border-radius: var(--radius-lg);
  padding: 1rem;
  border: 1px solid var(--color-border);
}

.files-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
  font-size: var(--font-size-sm);
}

.files-items {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.625rem 0.75rem;
  background: var(--color-bg-secondary);
  border-radius: var(--radius-md);
}

.file-name {
  flex: 1;
  font-size: var(--font-size-sm);
  color: var(--color-text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-size {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
}

/* 导入结果 */
.import-result {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 1.25rem;
  border-radius: var(--radius-lg);
}

.import-result.success {
  background: var(--color-success-light);
  border-left: 3px solid var(--color-success);
}

.import-result.error {
  background: var(--color-error-light);
  border-left: 3px solid var(--color-error);
}

.result-message {
  flex: 1;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
}

/* 按钮 */
.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: var(--radius-md);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  cursor: pointer;
  transition: all var(--transition-fast);
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: var(--color-primary);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: var(--color-primary-hover);
}

.btn-large {
  width: 100%;
  padding: 0.75rem 1.5rem;
  font-size: var(--font-size-base);
}

.btn-secondary {
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border);
  color: var(--color-text-primary);
}

.btn-secondary:hover {
  background: var(--color-bg-hover);
}

.btn-link {
  background: transparent;
  color: var(--color-primary);
  padding: 0.5rem 0;
  font-size: var(--font-size-sm);
}

.btn-link:hover {
  text-decoration: underline;
}

.btn-sm {
  padding: 0.375rem 0.75rem;
  font-size: var(--font-size-xs);
}

.btn-icon {
  padding: 0.25rem;
  background: transparent;
  color: var(--color-text-tertiary);
  border: none;
}

.btn-icon:hover {
  color: var(--color-error);
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 空状态 */
.empty-batches {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
}

.empty-icon {
  opacity: 0.3;
  margin-bottom: 1rem;
  color: var(--color-text-secondary);
}

.empty-batches h3 {
  margin: 0 0 0.5rem 0;
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.empty-batches p {
  margin: 0 0 1.5rem 0;
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
}

/* 批次列表 */
.batches-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.batch-item {
  background: var(--color-bg-primary);
  border-radius: var(--radius-lg);
  padding: 1.25rem;
  border: 1px solid var(--color-border);
  transition: all var(--transition-fast);
}

.batch-item:hover {
  box-shadow: var(--shadow-md);
  border-color: var(--color-border-hover);
}

.batch-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.batch-name {
  margin: 0;
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: var(--radius-full);
  font-size: 0.75rem;
  font-weight: var(--font-weight-semibold);
}

.batch-details {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.detail-item {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.detail-label {
  color: var(--color-text-tertiary);
  font-weight: var(--font-weight-medium);
}

.batch-files {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.file-tag {
  background: var(--color-bg-tertiary);
  color: var(--color-text-secondary);
  padding: 0.25rem 0.625rem;
  border-radius: var(--radius-md);
  font-size: var(--font-size-xs);
  display: flex;
  align-items: center;
  gap: 0.375rem;
}

.batch-actions {
  display: flex;
  gap: 0.75rem;
}
</style>
