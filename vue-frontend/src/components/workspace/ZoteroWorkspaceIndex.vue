<script setup lang="ts">
import { ref } from 'vue'
import { useZoteroStore } from '../../stores/zotero'
import { useAppStore } from '../../stores/app'
import { useAuthStore } from '../../stores/auth'
import ZoteroConfigPanel from './ZoteroConfigPanel.vue'
import ZoteroLibraryPanel from './ZoteroLibraryPanel.vue'
import ZoteroImportPanel from './ZoteroImportPanel.vue'
import Icon from '../common/Icon.vue'

const zotero = useZoteroStore()
const appStore = useAppStore()
const authStore = useAuthStore()

// 视图切换
const currentView = ref<'config' | 'library' | 'import'>('library')

// 状态显示
const statusMessage = ref<{ type: 'success' | 'error' | 'info'; message: string } | null>(null)

function showStatus(type: 'success' | 'error' | 'info', message: string) {
  appStore.addNotification(type, message, 5000)
  statusMessage.value = { type, message }
  setTimeout(() => {
    statusMessage.value = null
  }, 5000)
}

async function handleSync() {
  try {
    showStatus('info', '正在同步...')
    const result = await zotero.syncAll()

    if (result.success) {
      showStatus('success', result.message)
    } else {
      showStatus('error', result.message)
    }
  } catch (error: any) {
    showStatus('error', error.message || '同步失败')
  }
}

function getStatusIcon(type: string) {
  const icons = {
    success: 'check-circle',
    error: 'alert-circle',
    info: 'info'
  }
  return icons[type as keyof typeof icons] || 'info'
}

// 导航项
const navItems = [
  { key: 'config', label: '连接配置', icon: 'link' },
  { key: 'library', label: '文献库', icon: 'book' },
  { key: 'import', label: '导入管理', icon: 'upload' }
]
</script>

<template>
  <div class="zotero-workspace">
    <!-- 页面头部 -->
    <header class="workspace-header">
      <div class="header-left">
        <button class="btn-icon" @click="appStore.toggleSidebar" title="切换侧边栏">
          <Icon name="menu" :size="20" />
        </button>

        <div class="header-title">
          <h1>Zotero 集成</h1>
          <p>连接 Zotero 文献管理工具，导入文献到 SmartPaper</p>
        </div>
      </div>

      <div class="header-right">
        <button
          class="btn btn-primary"
          :disabled="zotero.isLoading || !zotero.connection.isConnected"
          @click="handleSync"
        >
          <Icon v-if="zotero.isLoading" name="loading" :size="16" class="spin" />
          <Icon v-else name="sync" :size="16" />
          <span>{{ zotero.isLoading ? '同步中...' : '同步全部' }}</span>
        </button>
      </div>
    </header>

    <!-- 主内容区 -->
    <div class="workspace-content">
      <!-- 左侧导航栏 -->
      <nav class="sidebar-nav">
        <div class="nav-section">
          <div class="nav-section-title">功能</div>

          <button
            v-for="item in navItems"
            :key="item.key"
            class="nav-item"
            :class="{ active: currentView === item.key }"
            @click="currentView = item.key as any"
          >
            <Icon :name="item.icon" :size="18" />
            <span class="nav-label">{{ item.label }}</span>

            <!-- 未连接提示 -->
            <span v-if="item.key === 'config' && !zotero.connection.isConnected" class="nav-badge">
              <Icon name="alert-circle" :size="12" />
            </span>

            <!-- 计数徽章 -->
            <span v-if="item.key === 'library' && zotero.items.length" class="nav-count">
              {{ zotero.items.length }}
            </span>
            <span v-if="item.key === 'import' && zotero.batches.length" class="nav-count">
              {{ zotero.batches.length }}
            </span>
          </button>
        </div>

        <!-- 连接状态 -->
        <div class="connection-status">
          <div class="status-indicator" :class="{ connected: zotero.connection.isConnected }">
            <span class="indicator-dot"></span>
            <span class="indicator-text">
              {{ zotero.connection.isConnected ? '已连接' : '未连接' }}
            </span>
          </div>
          <div v-if="zotero.connection.lastSyncTime" class="last-sync">
            <Icon name="refresh" :size="12" />
            最后同步：{{ new Date(zotero.connection.lastSyncTime).toLocaleString('zh-CN') }}
          </div>
        </div>

        <!-- 用户信息 -->
        <div class="user-info">
          <div class="user-avatar">
            {{ authStore.user?.name?.charAt(0).toUpperCase() || 'U' }}
          </div>
          <div class="user-details">
            <div class="user-name">{{ authStore.user?.name || 'User' }}</div>
            <div class="user-email">{{ authStore.user?.email || '' }}</div>
          </div>
        </div>
      </nav>

      <!-- 主内容区 -->
      <main class="workspace-main">
        <!-- 配置视图 -->
        <section v-if="currentView === 'config'" class="view-section">
          <div class="view-header">
            <h2>连接配置</h2>
            <p>配置 Zotero API 连接信息，以便同步文献数据</p>
          </div>
          <ZoteroConfigPanel />
        </section>

        <!-- 文献库视图 -->
        <section v-if="currentView === 'library'" class="view-section">
          <div class="view-header">
            <h2>文献库</h2>
            <p>浏览、搜索和管理从 Zotero 同步的文献</p>
          </div>
          <ZoteroLibraryPanel />
        </section>

        <!-- 导入视图 -->
        <section v-if="currentView === 'import'" class="view-section">
          <div class="view-header">
            <h2>导入管理</h2>
            <p>上传 Zotero 导出文件，批量导入文献到 SmartPaper</p>
          </div>
          <ZoteroImportPanel />
        </section>
      </main>
    </div>

    <!-- 帮助面板 -->
    <div class="help-panel">
      <details class="help-details">
        <summary class="help-summary">
          <Icon name="help" :size="16" />
          <span>使用帮助</span>
          <Icon name="menu-dots" :size="16" />
        </summary>
        <div class="help-content">
          <h4>快速开始</h4>
          <ol>
            <li>前往「连接配置」，输入 Zotero API Key 和 Library ID</li>
            <li>点击「测试连接并同步」，等待数据同步完成</li>
            <li>在「文献库」中浏览、搜索和筛选文献</li>
            <li>选中需要的文献，点击「导入到论文库」</li>
          </ol>

          <h4>常见问题</h4>
          <ul>
            <li><strong>如何获取 API Key？</strong>前往 Zotero 网站账户设置中的 Feeds/API 部分</li>
            <li><strong>Library ID 是什么？</strong>个人用户为用户ID，群组库为群组ID</li>
            <li><strong>支持离线导入吗？</strong>支持，可上传 Zotero JSON 导出文件</li>
            <li><strong>导入的文献包含哪些信息？</strong>元数据、附件、标签、笔记等</li>
          </ul>
        </div>
      </details>
    </div>
  </div>
</template>

<style scoped>
.zotero-workspace {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
  background: var(--color-bg-secondary);
}

/* 页面头部 */
.workspace-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  background: var(--color-bg-primary);
  border-bottom: 1px solid var(--color-border);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.header-title h1 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.header-title p {
  margin: 0;
  font-size: var(--font-size-sm);
  color: var(--color-text-tertiary);
}

.header-right {
  display: flex;
  gap: var(--spacing-md);
}

.btn-icon {
  padding: 0.5rem;
  background: transparent;
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  color: var(--color-text-secondary);
  transition: all var(--transition-fast);
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-icon:hover {
  background: var(--color-bg-hover);
  color: var(--color-text-primary);
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
  transform: translateY(-1px);
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 主内容区 */
.workspace-content {
  flex: 1;
  display: flex;
  overflow: hidden;
}

/* 侧边栏导航 */
.sidebar-nav {
  width: 260px;
  background: var(--color-bg-primary);
  border-right: 1px solid var(--color-border);
  padding: 1rem 0;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.nav-section {
  padding: 0 0.75rem;
}

.nav-section-title {
  padding: 0.5rem 0.75rem;
  font-size: 0.75rem;
  font-weight: var(--font-weight-semibold);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-text-tertiary);
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  width: 100%;
  padding: 0.625rem 0.75rem;
  margin-bottom: 0.25rem;
  background: transparent;
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
  text-align: left;
  color: var(--color-text-secondary);
}

.nav-item:hover {
  background: var(--color-bg-hover);
  color: var(--color-text-primary);
}

.nav-item.active {
  background: var(--color-primary-light);
  color: var(--color-primary);
}

.nav-label {
  flex: 1;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
}

.nav-badge {
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-warning);
  color: white;
  padding: 0.125rem;
  border-radius: var(--radius-full);
  min-width: 1.25rem;
}

.nav-count {
  background: var(--color-bg-tertiary);
  color: var(--color-text-tertiary);
  padding: 0.125rem 0.5rem;
  border-radius: var(--radius-full);
  font-size: 0.7rem;
  font-weight: var(--font-weight-medium);
  min-width: 1.25rem;
  text-align: center;
}

/* 连接状态 */
.connection-status {
  padding: 0.75rem;
  margin: 0 0.75rem 0.75rem;
  background: var(--color-bg-tertiary);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.indicator-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--color-error);
  transition: background var(--transition-base);
}

.status-indicator.connected .indicator-dot {
  background: var(--color-success);
}

.indicator-text {
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
}

.last-sync {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.7rem;
  color: var(--color-text-tertiary);
}

/* 用户信息 */
.user-info {
  padding: 0.75rem;
  margin: 0 0.75rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background: var(--color-bg-tertiary);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--color-primary);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: var(--font-weight-semibold);
  font-size: var(--font-size-sm);
}

.user-details {
  flex: 1;
  min-width: 0;
}

.user-name {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.user-email {
  font-size: 0.7rem;
  color: var(--color-text-tertiary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 主视图区 */
.workspace-main {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
}

.view-section {
  max-width: 1200px;
  margin: 0 auto;
}

.view-header {
  margin-bottom: 1.5rem;
}

.view-header h2 {
  margin: 0 0 0.375rem 0;
  font-size: 1.5rem;
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.view-header p {
  margin: 0;
  font-size: var(--font-size-sm);
  color: var(--color-text-tertiary);
}

/* 帮助面板 */
.help-panel {
  position: fixed;
  bottom: 1.5rem;
  right: 1.5rem;
  z-index: var(--z-index-fixed);
}

.help-details {
  background: var(--color-bg-primary);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-xl);
  overflow: hidden;
  width: 400px;
  max-width: calc(100vw - 3rem);
}

.help-summary {
  padding: 0.75rem 1rem;
  background: var(--color-primary);
  color: white;
  font-weight: var(--font-weight-medium);
  cursor: pointer;
  list-style: none;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.help-summary::-webkit-details-marker {
  display: none;
}

.help-content {
  padding: 1rem;
  max-height: 400px;
  overflow-y: auto;
}

.help-content h4 {
  margin: 1rem 0 0.5rem 0;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.help-content h4:first-child {
  margin-top: 0;
}

.help-content ol,
.help-content ul {
  margin: 0.5rem 0;
  padding-left: 1.25rem;
}

.help-content li {
  margin-bottom: 0.5rem;
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  line-height: var(--line-height-relaxed);
}

.help-content strong {
  color: var(--color-text-primary);
}

/* 响应式 */
@media (max-width: 1024px) {
  .sidebar-nav {
    width: 220px;
  }

  .workspace-main {
    padding: 1rem;
  }

  .help-panel {
    bottom: 1rem;
    right: 1rem;
  }
}

@media (max-width: 768px) {
  .workspace-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }

  .workspace-content {
    flex-direction: column;
  }

  .sidebar-nav {
    width: 100%;
    border-right: none;
    border-bottom: 1px solid var(--color-border);
  }

  .nav-section {
    padding: 0 0.5rem;
  }

  .help-details {
    width: calc(100vw - 2rem);
  }
}
</style>
