<script setup lang="ts">
import { ref } from 'vue'
import { useZoteroStore } from '../stores/zotero'
import ZoteroConfigPanel from '../components/workspace/ZoteroConfigPanel.vue'
import ZoteroLibraryPanel from '../components/workspace/ZoteroLibraryPanel.vue'
import ZoteroImportPanel from '../components/workspace/ZoteroImportPanel.vue'

const zotero = useZoteroStore()

// 视图切换
const currentView = ref<'config' | 'library' | 'import'>('library')

// 状态显示
const statusMessage = ref<{ type: 'success' | 'error' | 'info'; message: string } | null>(null)

function showStatus(type: 'success' | 'error' | 'info', message: string) {
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
  switch (type) {
    case 'success': return '✅'
    case 'error': return '❌'
    case 'info': return 'ℹ️'
    default: return ''
  }
}
</script>

<template>
  <div class="zotero-workspace">
    <!-- 页面头部 -->
    <header class="workspace-header">
      <div class="header-left">
        <h1 class="page-title">🗂️ Zotero 集成</h1>
        <p class="page-subtitle">
          连接 Zotero 文献管理工具，导入文献到 SmartPaper
        </p>
      </div>

      <div class="header-right">
        <button
          class="btn btn-primary"
          :disabled="zotero.isLoading || !zotero.connection.isConnected"
          @click="handleSync"
        >
          <span v-if="zotero.isLoading">⏳ 同步中...</span>
          <span v-else>🔄 同步全部</span>
        </button>
      </div>
    </header>

    <!-- 状态通知 -->
    <transition name="fade">
      <div v-if="statusMessage" class="status-notification" :class="statusMessage.type">
        <span class="status-icon">{{ getStatusIcon(statusMessage.type) }}</span>
        <span class="status-text">{{ statusMessage.message }}</span>
        <button class="btn-close" @click="statusMessage = null">×</button>
      </div>
    </transition>

    <!-- 主内容区 -->
    <div class="workspace-content">
      <!-- 左侧导航栏 -->
      <nav class="sidebar-nav">
        <div class="nav-section">
          <div class="nav-section-title">功能</div>

          <button
            class="nav-item"
            :class="{ active: currentView === 'config' }"
            @click="currentView = 'config'"
          >
            <span class="nav-icon">🔗</span>
            <span class="nav-label">连接配置</span>
            <span v-if="!zotero.connection.isConnected" class="nav-badge">!</span>
          </button>

          <button
            class="nav-item"
            :class="{ active: currentView === 'library' }"
            @click="currentView = 'library'"
          >
            <span class="nav-icon">📚</span>
            <span class="nav-label">文献库</span>
            <span class="nav-count">{{ zotero.items.length }}</span>
          </button>

          <button
            class="nav-item"
            :class="{ active: currentView === 'import' }"
            @click="currentView = 'import'"
          >
            <span class="nav-icon">📤</span>
            <span class="nav-label">导入管理</span>
            <span class="nav-count">{{ zotero.batches.length }}</span>
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
            最后同步：{{ new Date(zotero.connection.lastSyncTime).toLocaleString('zh-CN') }}
          </div>
        </div>
      </nav>

      <!-- 主内容区 -->
      <main class="workspace-main">
        <!-- 配置视图 -->
        <section v-if="currentView === 'config'" class="view-section">
          <div class="view-header">
            <h2>🔗 连接配置</h2>
            <p class="view-description">
              配置 Zotero API 连接信息，以便同步文献数据
            </p>
          </div>
          <ZoteroConfigPanel />
        </section>

        <!-- 文献库视图 -->
        <section v-if="currentView === 'library'" class="view-section">
          <div class="view-header">
            <h2>📚 文献库</h2>
            <p class="view-description">
              浏览、搜索和管理从 Zotero 同步的文献
            </p>
          </div>
          <ZoteroLibraryPanel />
        </section>

        <!-- 导入视图 -->
        <section v-if="currentView === 'import'" class="view-section">
          <div class="view-header">
            <h2>📤 导入管理</h2>
            <p class="view-description">
              上传 Zotero 导出文件，批量导入文献到 SmartPaper
            </p>
          </div>
          <ZoteroImportPanel />
        </section>
      </main>
    </div>

    <!-- 帮助信息 -->
    <div class="help-panel">
      <details class="help-details">
        <summary class="help-summary">❓ 使用帮助</summary>
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
  height: 100vh;
  overflow: hidden;
  background: var(--bg-color);
}

/* 页面头部 */
.workspace-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 2rem;
  background: var(--surface-color);
  border-bottom: 1px solid var(--border-color);
}

.header-left {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.page-title {
  margin: 0;
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--text-primary);
}

.page-subtitle {
  margin: 0;
  font-size: 0.95rem;
  color: var(--text-secondary);
}

.header-right {
  display: flex;
  gap: 1rem;
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: var(--border-radius);
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: var(--primary-color);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: var(--primary-dark);
  transform: translateY(-1px);
}

/* 状态通知 */
.status-notification {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 1.5rem;
  margin: 1rem 2rem 0;
  border-radius: var(--border-radius);
  animation: slideDown 0.3s ease;
}

.status-notification.success {
  background: var(--success-bg);
  border-left: 4px solid var(--success-color);
}

.status-notification.error {
  background: var(--error-bg);
  border-left: 4px solid var(--error-color);
}

.status-notification.info {
  background: var(--info-bg);
  border-left: 4px solid var(--info-color);
}

.status-icon {
  font-size: 1.25rem;
}

.status-text {
  flex: 1;
  font-size: 0.95rem;
  font-weight: 500;
}

.btn-close {
  background: transparent;
  border: none;
  font-size: 1.5rem;
  color: inherit;
  cursor: pointer;
  opacity: 0.7;
  transition: opacity 0.2s;
}

.btn-close:hover {
  opacity: 1;
}

/* 主内容区 */
.workspace-content {
  flex: 1;
  display: flex;
  overflow: hidden;
}

/* 侧边栏导航 */
.sidebar-nav {
  width: 280px;
  background: var(--surface-color);
  border-right: 1px solid var(--border-color);
  padding: 1.5rem 0;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.nav-section {
  padding: 0 1rem;
}

.nav-section-title {
  padding: 0.5rem 0.75rem;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-secondary);
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  width: 100%;
  padding: 0.875rem 1rem;
  margin-bottom: 0.25rem;
  background: transparent;
  border: none;
  border-radius: var(--border-radius);
  cursor: pointer;
  transition: all 0.2s;
  text-align: left;
}

.nav-item:hover {
  background: var(--hover-bg);
}

.nav-item.active {
  background: var(--primary-light);
  color: var(--primary-color);
}

.nav-icon {
  font-size: 1.25rem;
}

.nav-label {
  flex: 1;
  font-size: 0.95rem;
  font-weight: 500;
}

.nav-badge {
  background: var(--error-color);
  color: white;
  padding: 0.125rem 0.5rem;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 600;
}

.nav-count {
  background: var(--tag-bg);
  color: var(--tag-color);
  padding: 0.125rem 0.5rem;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 500;
}

/* 连接状态 */
.connection-status {
  padding: 1rem;
  margin: 0 1rem 1rem;
  background: var(--input-bg);
  border-radius: var(--border-radius);
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
  background: var(--error-color);
  transition: background 0.3s;
}

.status-indicator.connected .indicator-dot {
  background: var(--success-color);
}

.indicator-text {
  font-size: 0.9rem;
  font-weight: 500;
}

.last-sync {
  font-size: 0.8rem;
  color: var(--text-secondary);
}

/* 主视图区 */
.workspace-main {
  flex: 1;
  overflow-y: auto;
  padding: 2rem;
}

.view-section {
  max-width: 1200px;
  margin: 0 auto;
}

.view-header {
  margin-bottom: 2rem;
}

.view-header h2 {
  margin: 0 0 0.5rem 0;
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-primary);
}

.view-description {
  margin: 0;
  font-size: 0.95rem;
  color: var(--text-secondary);
}

/* 帮助面板 */
.help-panel {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  z-index: 100;
}

.help-details {
  background: var(--surface-color);
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-lg);
  overflow: hidden;
}

.help-summary {
  padding: 0.75rem 1.25rem;
  background: var(--primary-color);
  color: white;
  font-weight: 500;
  cursor: pointer;
  list-style: none;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.help-summary::-webkit-details-marker {
  display: none;
}

.help-content {
  padding: 1.25rem;
  max-width: 400px;
  max-height: 400px;
  overflow-y: auto;
}

.help-content h4 {
  margin: 1rem 0 0.5rem 0;
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
}

.help-content h4:first-child {
  margin-top: 0;
}

.help-content ol,
.help-content ul {
  margin: 0.5rem 0;
  padding-left: 1.5rem;
}

.help-content li {
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
  color: var(--text-secondary);
  line-height: 1.6;
}

.help-content strong {
  color: var(--text-primary);
}

/* 动画 */
.fade-enter-active,
.fade-leave-active {
  transition: all 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 响应式 */
@media (max-width: 1024px) {
  .sidebar-nav {
    width: 240px;
  }

  .workspace-main {
    padding: 1.5rem;
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
    border-bottom: 1px solid var(--border-color);
  }

  .nav-section {
    padding: 0 0.5rem;
  }

  .help-panel {
    bottom: 1rem;
    right: 1rem;
  }
}
</style>
