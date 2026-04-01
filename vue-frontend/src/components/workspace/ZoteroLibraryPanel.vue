<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useZoteroStore } from '../../stores/zotero'
import Icon from '../common/Icon.vue'
import type { ZoteroItem } from '../../types/zotero'

const zotero = useZoteroStore()

// 搜索和筛选
const searchQuery = ref('')
const selectedItemType = ref('')
const selectedTags = ref<string[]>([])
const isFilterPanelOpen = ref(false)

// 视图模式
const viewMode = ref<'list' | 'card'>('list')

// 排序
const sortBy = ref<'date' | 'title' | 'dateAdded'>('dateAdded')
const sortOrder = ref<'asc' | 'desc'>('desc')

// 监听搜索和筛选变化
watch([searchQuery, selectedTags, selectedItemType], () => {
  zotero.setSearchParams({
    q: searchQuery.value || undefined,
    itemType: selectedItemType.value || undefined,
    tags: selectedTags.value.length > 0 ? selectedTags.value : undefined
  })
})

const sortedItems = computed(() => {
  const items = [...zotero.filteredItems]

  items.sort((a, b) => {
    let comparison = 0

    switch (sortBy.value) {
      case 'date':
        const dateA = new Date(a.date || '').getTime()
        const dateB = new Date(b.date || '').getTime()
        comparison = dateA - dateB
        break
      case 'title':
        comparison = a.title.localeCompare(b.title, 'zh-CN')
        break
      case 'dateAdded':
        comparison = new Date(a.dateAdded).getTime() - new Date(b.dateAdded).getTime()
        break
    }

    return sortOrder.value === 'asc' ? comparison : -comparison
  })

  return items
})

const creatorsString = (creators: ZoteroItem['creators']) => {
  if (!creators || creators.length === 0) return '未知作者'

  const names = creators.map(c => `${c.firstName} ${c.lastName}`)
  if (names.length <= 2) return names.join(', ')
  return `${names[0]} 等 ${creators.length} 位作者`
}

const handleSort(field: 'date' | 'title' | 'dateAdded') => {
  if (sortBy.value === field) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortBy.value = field
    sortOrder.value = 'desc'
  }
}

const toggleTagFilter = (tag: string) => {
  const index = selectedTags.value.indexOf(tag)
  if (index === -1) {
    selectedTags.value.push(tag)
  } else {
    selectedTags.value.splice(index, 1)
  }
}

const resetFilters = () => {
  searchQuery.value = ''
  selectedTags.value = []
  selectedItemType.value = ''
  zotero.resetSearch()
}
</script>

<template>
  <div class="zotero-library-panel">
    <!-- 工具栏 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <div class="search-box">
          <Icon name="search" :size="18" />
          <input
            v-model="searchQuery"
            type="text"
            class="search-input"
            placeholder="搜索标题、作者、摘要..."
          />
        </div>

        <button
          class="btn btn-secondary"
          :class="{ active: isFilterPanelOpen }"
          @click="isFilterPanelOpen = !isFilterPanelOpen"
        >
          <Icon name="filter" :size="16" />
          <span>筛选</span>
          <span v-if="selectedTags.length > 0" class="badge">
            {{ selectedTags.length }}
          </span>
        </button>
      </div>

      <div class="toolbar-right">
        <div class="sort-controls">
          <select v-model="sortBy" class="sort-select">
            <option value="dateAdded">添加时间</option>
            <option value="date">发表时间</option>
            <option value="title">标题</option>
          </select>
          <button
            class="btn btn-icon"
            :title="sortOrder === 'asc' ? '升序' : '降序'"
            @click="sortOrder = sortOrder === 'asc' ? 'desc' : 'asc'"
          >
            <Icon :name="sortOrder === 'asc' ? 'sort-asc' : 'sort-desc'" :size="18" />
          </button>
        </div>

        <div class="view-toggles">
          <button
            class="btn btn-icon"
            :class="{ active: viewMode === 'list' }"
            title="列表视图"
            @click="viewMode = 'list'"
          >
            <Icon name="list" :size="18" />
          </button>
          <button
            class="btn btn-icon"
            :class="{ active: viewMode === 'card' }"
            title="卡片视图"
            @click="viewMode = 'card'"
          >
            <Icon name="grid" :size="18" />
          </button>
        </div>
      </div>
    </div>

    <!-- 筛选面板 -->
    <div v-if="isFilterPanelOpen" class="filter-panel">
      <div class="filter-group">
        <label>文献类型</label>
        <select v-model="selectedItemType" class="filter-select">
          <option value="">全部</option>
          <option v-for="type in zotero.itemTypes" :key="type" :value="type">
            {{ type }}
          </option>
        </select>
      </div>

      <div class="filter-group">
        <label>标签</label>
        <div class="tags-cloud">
          <span
            v-for="tag in zotero.allTags"
            :key="tag"
            class="tag"
            :class="{ active: selectedTags.includes(tag) }"
            @click="toggleTagFilter(tag)"
          >
            {{ tag }}
          </span>
        </div>
      </div>

      <button class="btn btn-link" @click="resetFilters">
        <Icon name="refresh" :size="14" />
        重置所有筛选
      </button>
    </div>

    <!-- 批量操作栏 -->
    <div v-if="zotero.selectedItemCount > 0" class="batch-actions">
      <div class="selection-info">
        已选择 <strong>{{ zotero.selectedItemCount }}</strong> 篇文献
      </div>
      <div class="action-buttons">
        <button class="btn btn-primary" @click="zotero.importSelectedToLibrary">
          <Icon name="download" :size="16" />
          导入到论文库
        </button>
        <button class="btn btn-secondary" @click="zotero.clearSelection">
          <Icon name="close" :size="16" />
          取消选择
        </button>
      </div>
    </div>

    <!-- 文献列表 -->
    <div class="library-content">
      <div v-if="zotero.isLoading" class="loading-state">
        <Icon name="loading" :size="48" class="spin" />
        <p>加载中...</p>
      </div>

      <div v-else-if="sortedItems.length === 0" class="empty-state">
        <Icon name="book" :size="64" class="empty-icon" />
        <h3>暂无文献</h3>
        <p>{{ zotero.connection.isConnected ? '点击上方"同步"按钮获取文献' : '请先配置并连接 Zotero' }}</p>
      </div>

      <!-- 列表视图 -->
      <div v-else-if="viewMode === 'list'" class="items-list">
        <div
          v-for="item in sortedItems"
          :key="item.key"
          class="item-row"
          :class="{ selected: zotero.selectedItems.has(item.key) }"
        >
          <input
            type="checkbox"
            :checked="zotero.selectedItems.has(item.key)"
            @change="zotero.toggleItemSelection(item.key)"
          />

          <div class="item-content">
            <div class="item-header">
              <h4 class="item-title">{{ item.title }}</h4>
              <div class="item-type">{{ item.itemType }}</div>
            </div>

            <div class="item-authors">{{ creatorsString(item.creators) }}</div>

            <div v-if="item.date" class="item-meta">
              <Icon name="calendar" :size="14" />
              <span>{{ item.date }}</span>
            </div>

            <div v-if="item.abstractNote" class="item-abstract">
              {{ item.abstractNote.substring(0, 200) }}...
            </div>

            <div v-if="item.tags && item.tags.length > 0" class="item-tags">
              <span v-for="tag in item.tags.slice(0, 5)" :key="tag.tag" class="tag">
                {{ tag.tag }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- 卡片视图 -->
      <div v-else class="items-grid">
        <div
          v-for="item in sortedItems"
          :key="item.key"
          class="item-card"
          :class="{ selected: zotero.selectedItems.has(item.key) }"
          @click="zotero.toggleItemSelection(item.key)"
        >
          <input
            type="checkbox"
            :checked="zotero.selectedItems.has(item.key)"
            @click.stop="zotero.toggleItemSelection(item.key)"
          />

          <div class="card-header">
            <span class="card-type">{{ item.itemType }}</span>
            <button class="btn btn-icon btn-sm">
              <Icon name="menu-dots" :size="16" />
            </button>
          </div>

          <h4 class="card-title">{{ item.title }}</h4>

          <div class="card-authors">{{ creatorsString(item.creators) }}</div>

          <div v-if="item.date" class="card-meta">
            <Icon name="calendar" :size="14" />
            <span>{{ item.date }}</span>
          </div>

          <div v-if="item.attachments && item.attachments.length > 0" class="card-attachments">
            <Icon name="file-text" :size="14" />
            <span>{{ item.attachments.length }} 个附件</span>
          </div>

          <div v-if="item.tags && item.tags.length > 0" class="card-tags">
            <span v-for="tag in item.tags.slice(0, 3)" :key="tag.tag" class="tag">
              {{ tag.tag }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- 统计信息 -->
    <div class="library-stats">
      <span>共 <strong>{{ sortedItems.length }}</strong> 篇文献</span>
      <span v-if="zotero.selectedItemCount > 0">
        | 已选择 {{ zotero.selectedItemCount }} 篇
      </span>
    </div>
  </div>
</template>

<style scoped>
.zotero-library-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  gap: 1rem;
}

/* 工具栏 */
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.toolbar-left,
.toolbar-right {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  min-width: 280px;
}

.search-box:focus-within {
  border-color: var(--color-primary);
}

.search-input {
  border: none;
  background: transparent;
  font-size: var(--font-size-base);
  color: var(--color-text-primary);
  flex: 1;
}

.search-input::placeholder {
  color: var(--color-text-tertiary);
}

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

.btn-secondary {
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border);
  color: var(--color-text-primary);
}

.btn-secondary:hover {
  background: var(--color-bg-hover);
}

.btn-secondary.active {
  background: var(--color-primary);
  color: white;
  border-color: var(--color-primary);
}

.btn-icon {
  padding: 0.5rem;
  background: transparent;
  border: 1px solid transparent;
}

.btn-icon:hover {
  background: var(--color-bg-hover);
}

.btn-icon.active {
  background: var(--color-primary-light);
  color: var(--color-primary);
  border-color: var(--color-primary);
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

.badge {
  background: var(--color-primary);
  color: white;
  border-radius: var(--radius-full);
  padding: 0.125rem 0.5rem;
  font-size: 0.7rem;
  min-width: 1.25rem;
  text-align: center;
  font-weight: var(--font-weight-semibold);
}

.sort-controls {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.sort-select {
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: var(--font-size-sm);
  background: var(--color-bg-primary);
  color: var(--color-text-primary);
}

/* 筛选面板 */
.filter-panel {
  background: var(--color-bg-primary);
  border-radius: var(--radius-lg);
  padding: 1rem;
  border: 1px solid var(--color-border);
}

.filter-group {
  margin-bottom: 1rem;
}

.filter-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
}

.filter-select {
  width: 100%;
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: var(--font-size-sm);
  background: var(--color-bg-primary);
  color: var(--color-text-primary);
}

.tags-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.tag {
  background: var(--color-bg-tertiary);
  color: var(--color-text-secondary);
  padding: 0.25rem 0.75rem;
  border-radius: var(--radius-full);
  font-size: var(--font-size-xs);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.tag:hover {
  background: var(--color-border-hover);
}

.tag.active {
  background: var(--color-primary);
  color: white;
}

/* 批量操作栏 */
.batch-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--color-primary-light);
  border-radius: var(--radius-lg);
  padding: 0.75rem 1rem;
  border-left: 3px solid var(--color-primary);
}

.selection-info {
  font-size: var(--font-size-sm);
  color: var(--color-text-primary);
}

.selection-info strong {
  color: var(--color-primary);
}

.action-buttons {
  display: flex;
  gap: 0.75rem;
}

/* 内容区 */
.library-content {
  flex: 1;
  min-height: 300px;
  overflow-y: auto;
}

.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  color: var(--color-text-tertiary);
}

.spin {
  animation: spin 1s linear infinite;
  color: var(--color-primary);
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-icon {
  opacity: 0.3;
  margin-bottom: 1rem;
}

.empty-state h3 {
  margin: 0 0 0.5rem 0;
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.empty-state p {
  margin: 0;
  font-size: var(--font-size-sm);
}

/* 列表视图 */
.items-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.item-row {
  display: flex;
  gap: 1rem;
  background: var(--color-bg-primary);
  border-radius: var(--radius-lg);
  padding: 1rem;
  border: 2px solid transparent;
  transition: all var(--transition-fast);
}

.item-row:hover {
  box-shadow: var(--shadow-md);
  border-color: var(--color-border);
}

.item-row.selected {
  border-color: var(--color-primary);
  background: var(--color-primary-light);
}

.item-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
}

.item-title {
  margin: 0;
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  flex: 1;
  line-height: var(--line-height-relaxed);
}

.item-type {
  background: var(--color-bg-tertiary);
  padding: 0.25rem 0.75rem;
  border-radius: var(--radius-full);
  font-size: 0.75rem;
  color: var(--color-text-secondary);
}

.item-authors {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.item-meta {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: var(--font-size-sm);
  color: var(--color-text-tertiary);
}

.item-abstract {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  line-height: var(--line-height-relaxed);
}

.item-tags {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

/* 卡片视图 */
.items-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
}

.item-card {
  background: var(--color-bg-primary);
  border-radius: var(--radius-lg);
  padding: 1rem;
  border: 2px solid transparent;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.item-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
  border-color: var(--color-border);
}

.item-card.selected {
  border-color: var(--color-primary);
  background: var(--color-primary-light);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.card-type {
  background: var(--color-bg-tertiary);
  padding: 0.25rem 0.75rem;
  border-radius: var(--radius-full);
  font-size: 0.75rem;
  color: var(--color-text-secondary);
}

.card-title {
  margin: 0 0 0.5rem 0;
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-height: var(--line-height-relaxed);
}

.card-authors {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin-bottom: 0.5rem;
}

.card-meta {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
  margin-bottom: 0.5rem;
}

.card-attachments {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
  margin-bottom: 0.5rem;
}

.card-tags {
  display: flex;
  gap: 0.375rem;
  flex-wrap: wrap;
}

.btn-sm {
  padding: 0.25rem 0.5rem;
}

/* 统计信息 */
.library-stats {
  padding: 0.75rem 1rem;
  background: var(--color-bg-primary);
  border-radius: var(--radius-lg);
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  text-align: center;
  border: 1px solid var(--color-border);
}

.library-stats strong {
  color: var(--color-text-primary);
}
</style>
