<template>
  <div class="data-table-container">
    <!-- 表格工具栏 -->
    <div class="data-table-toolbar" v-if="$slots.toolbar || searchable">
      <slot name="toolbar">
        <div v-if="searchable" class="search-wrapper">
          <IconSearch />
          <input
            v-model="searchQuery"
            type="text"
            class="input search-input"
            placeholder="搜索..."
          />
        </div>
      </slot>
    </div>

    <!-- 数据表格 -->
    <div class="data-table-wrapper">
      <table class="data-table">
        <thead>
          <tr>
            <th v-for="column in columns" :key="column.key" :style="{ width: column.width }">
              <div class="th-content">
                {{ column.title }}
                <span v-if="column.sortable" class="sort-icon" @click="handleSort(column.key)">
                  <svg v-if="sortKey !== column.key" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="m21 16-4 4-4-4"/>
                    <path d="M17 20V4"/>
                    <path d="m3 8 4-4 4 4"/>
                    <path d="M7 4v16"/>
                  </svg>
                  <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path v-if="sortOrder === 'asc'" d="m21 16-4 4-4-4"/>
                    <path v-else d="m3 8 4-4 4 4"/>
                  </svg>
                </span>
              </div>
            </th>
            <th v-if="$slots.actions" class="actions-column">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, index) in paginatedData" :key="getRowKey(row, index)">
            <td v-for="column in columns" :key="column.key">
              <slot
                v-if="column.slot"
                :name="`cell-${column.slot}`"
                :row="row"
                :value="row[column.key]"
              >
                {{ row[column.key] }}
              </slot>
              <span v-else>{{ formatValue(row[column.key], column) }}</span>
            </td>
            <td v-if="$slots.actions" class="actions-column">
              <slot name="actions" :row="row" :index="index"></slot>
            </td>
          </tr>
          <tr v-if="paginatedData.length === 0">
            <td :colspan="columns.length + ($slots.actions ? 1 : 0)" class="empty-state">
              <div class="empty-content">
                <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                  <polyline points="14 2 14 8 20 8"/>
                  <line x1="16" x2="8" y1="13" y2="13"/>
                  <line x1="16" x2="8" y1="17" y2="17"/>
                  <polyline points="10 9 9 9 8 9"/>
                </svg>
                <p>暂无数据</p>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 分页 -->
    <div class="data-table-pagination" v-if="showPagination && total > pageSize">
      <div class="pagination-info">
        显示第 {{ (currentPage - 1) * pageSize + 1 }} 到 {{ Math.min(currentPage * pageSize, total) }} 条，共 {{ total }} 条
      </div>
      <div class="pagination-controls">
        <button
          class="btn-icon pagination-btn"
          :disabled="currentPage === 1"
          @click="currentPage--"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="m15 18-6-6 6-6"/>
          </svg>
        </button>
        <span class="pagination-current">{{ currentPage }} / {{ totalPages }}</span>
        <button
          class="btn-icon pagination-btn"
          :disabled="currentPage === totalPages"
          @click="currentPage++"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="m9 18 6-6-6-6"/>
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import IconSearch from '../icons/IconSearch.vue'

interface Column {
  key: string
  title: string
  width?: string
  sortable?: boolean
  slot?: string
  formatter?: (value: any) => string
}

interface Props {
  data: any[]
  columns: Column[]
  rowKey?: string | ((row: any) => string)
  searchable?: boolean
  showPagination?: boolean
  pageSize?: number
}

const props = withDefaults(defineProps<Props>(), {
  rowKey: 'id',
  searchable: false,
  showPagination: true,
  pageSize: 10
})

const emit = defineEmits<{
  sort: [key: string, order: 'asc' | 'desc']
}>()

const searchQuery = ref('')
const currentPage = ref(1)
const sortKey = ref('')
const sortOrder = ref<'asc' | 'desc'>('asc')

// 过滤后的数据
const filteredData = computed(() => {
  if (!searchQuery.value) return props.data

  const query = searchQuery.value.toLowerCase()
  return props.data.filter(row => {
    return props.columns.some(column => {
      const value = row[column.key]
      return String(value).toLowerCase().includes(query)
    })
  })
})

// 排序后的数据
const sortedData = computed(() => {
  if (!sortKey.value) return filteredData.value

  return [...filteredData.value].sort((a, b) => {
    const aValue = a[sortKey.value]
    const bValue = b[sortKey.value]

    let comparison = 0
    if (aValue > bValue) comparison = 1
    if (aValue < bValue) comparison = -1

    return sortOrder.value === 'asc' ? comparison : -comparison
  })
})

// 分页后的数据
const paginatedData = computed(() => {
  if (!props.showPagination) return sortedData.value

  const start = (currentPage.value - 1) * props.pageSize
  const end = start + props.pageSize
  return sortedData.value.slice(start, end)
})

// 总数据量
const total = computed(() => sortedData.value.length)

// 总页数
const totalPages = computed(() => Math.ceil(total.value / props.pageSize))

// 获取行的唯一标识
const getRowKey = (row: any, index: number): string => {
  if (typeof props.rowKey === 'function') {
    return props.rowKey(row)
  }
  return row[props.rowKey] || String(index)
}

// 格式化值
const formatValue = (value: any, column: Column): string => {
  if (column.formatter) {
    return column.formatter(value)
  }
  return String(value ?? '-')
}

// 处理排序
const handleSort = (key: string) => {
  if (sortKey.value === key) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortKey.value = key
    sortOrder.value = 'asc'
  }

  emit('sort', sortKey.value, sortOrder.value)
}

// 监听数据变化，重置页码
watch(() => props.data.length, () => {
  currentPage.value = 1
})
</script>

<style scoped>
.data-table-container {
  background: white;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.data-table-toolbar {
  padding: 16px;
  border-bottom: 1px solid var(--color-border);
  background-color: var(--color-bg-secondary);
}

.search-wrapper {
  position: relative;
  width: 300px;
}

.search-wrapper > svg {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  width: 16px;
  height: 16px;
  color: var(--color-text-light);
  pointer-events: none;
}

.search-input {
  padding-left: 36px;
  height: 36px;
  font-size: 14px;
}

.data-table-wrapper {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table thead {
  background-color: var(--color-bg-secondary);
}

.data-table th {
  padding: 12px 16px;
  text-align: left;
  font-weight: 600;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-text-tertiary);
  border-bottom: 1px solid var(--color-border);
  white-space: nowrap;
}

.th-content {
  display: flex;
  align-items: center;
  gap: 4px;
}

.sort-icon {
  cursor: pointer;
  color: var(--color-text-light);
  transition: color 0.2s;
}

.sort-icon:hover {
  color: var(--color-text-tertiary);
}

.data-table td {
  padding: 12px 16px;
  font-size: 14px;
  color: var(--color-text-primary);
  border-bottom: 1px solid var(--color-border);
}

.data-table tbody tr:hover {
  background-color: var(--color-bg-hover);
}

.data-table tbody tr:last-child td {
  border-bottom: none;
}

.empty-state {
  padding: 48px 24px;
}

.empty-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  color: var(--color-text-light);
}

.empty-content svg {
  color: var(--color-text-tertiary);
}

.actions-column {
  text-align: center;
}

.data-table-pagination {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-top: 1px solid var(--color-border);
  background-color: var(--color-bg-secondary);
}

.pagination-info {
  font-size: 14px;
  color: var(--color-text-secondary);
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 12px;
}

.pagination-btn {
  padding: 4px;
  color: var(--color-text-tertiary);
}

.pagination-btn:hover:not(:disabled) {
  color: var(--color-primary);
}

.pagination-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.pagination-current {
  font-size: 14px;
  color: var(--color-text-secondary);
}
</style>

<script>
import { watch } from 'vue'
</script>
