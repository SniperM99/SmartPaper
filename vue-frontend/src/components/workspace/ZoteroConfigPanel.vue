<script setup lang="ts">
import { computed } from 'vue'
import { useZoteroStore } from '../../stores/zotero'
import Icon from '../common/Icon.vue'

const zotero = useZoteroStore()

const isConfigured = computed(() =>
  zotero.config.apiKey && zotero.config.libraryId
)

const canConnect = computed(() =>
  zotero.config.apiKey && zotero.config.libraryId && !zotero.connection.isConnecting
)

async function handleTestConnection() {
  const success = await zotero.testConnection()
  if (success) {
    // 连接成功后自动同步
    await zotero.syncAll()
  }
}

function handleSaveConfig() {
  zotero.setConfig({
    apiKey: zotero.config.apiKey,
    libraryId: zotero.config.libraryId,
    libraryType: zotero.config.libraryType
  })
}
</script>

<template>
  <div class="zotero-config-panel">
    <div class="panel-header">
      <Icon name="link" :size="20" />
      <h3>连接配置</h3>
    </div>

    <div v-if="!isConfigured" class="config-guide">
      <div class="info-box">
        <h4>
          <Icon name="info" :size="16" />
          如何获取 API 配置信息
        </h4>
        <ol>
          <li>打开 Zotero 官网并登录你的账户</li>
          <li>前往 Account Settings 页面</li>
          <li>滚动到 Feeds/API 部分</li>
          <li>创建新的 Private Key（勾选所有权限）</li>
          <li>复制生成的 API Key</li>
          <li>你的 Library ID 就是你的用户 ID（在个人资料页面查看）</li>
        </ol>
      </div>
    </div>

    <div class="config-form">
      <div class="form-group">
        <label>API Key *</label>
        <input
          v-model="zotero.config.apiKey"
          type="password"
          placeholder="粘贴你的 Zotero API Key"
          @input="handleSaveConfig"
        />
      </div>

      <div class="form-group">
        <label>Library ID *</label>
        <input
          v-model="zotero.config.libraryId"
          type="text"
          placeholder="用户 ID 或群组 ID"
          @input="handleSaveConfig"
        />
      </div>

      <div class="form-group">
        <label>Library Type</label>
        <select
          v-model="zotero.config.libraryType"
          @change="handleSaveConfig"
        >
          <option value="user">User Library (个人库)</option>
          <option value="group">Group Library (群组库)</option>
        </select>
      </div>

      <div class="form-group">
        <label>Base URL (可选)</label>
        <input
          v-model="zotero.config.baseUrl"
          type="text"
          placeholder="https://api.zotero.org"
          @input="handleSaveConfig"
        />
      </div>

      <div class="form-actions">
        <button
          :disabled="!canConnect"
          class="btn btn-primary"
          :class="{ loading: zotero.connection.isConnecting }"
          @click="handleTestConnection"
        >
          <Icon v-if="zotero.connection.isConnecting" name="loading" :size="16" class="spin" />
          <Icon v-else name="sync" :size="16" />
          <span>{{ zotero.connection.isConnecting ? '测试连接中...' : '测试连接并同步' }}</span>
        </button>

        <button
          v-if="zotero.connection.error"
          class="btn btn-secondary"
          @click="zotero.connection.error = null"
        >
          <Icon name="close" :size="16" />
          清除错误
        </button>
      </div>

      <!-- 连接状态显示 -->
      <div v-if="zotero.connection.error" class="alert alert-error">
        <Icon name="alert-circle" :size="18" />
        <div class="alert-content">
          <strong>连接失败</strong>
          <p>{{ zotero.connection.error }}</p>
        </div>
      </div>

      <div v-if="zotero.connection.isConnected && !zotero.connection.error" class="alert alert-success">
        <Icon name="check-circle" :size="18" />
        <div class="alert-content">
          <strong>连接成功</strong>
          <div v-if="zotero.connection.lastSyncTime" class="sync-time">
            最后同步：{{ new Date(zotero.connection.lastSyncTime).toLocaleString('zh-CN') }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.zotero-config-panel {
  background: var(--color-bg-primary);
  border-radius: var(--radius-lg);
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  box-shadow: var(--shadow-sm);
}

.panel-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
  color: var(--color-primary);
}

.panel-header h3 {
  margin: 0;
  font-size: 1.125rem;
  font-weight: var(--font-weight-semibold);
}

.config-guide {
  margin-bottom: 1.5rem;
}

.info-box {
  background: var(--color-info-light);
  border-left: 3px solid var(--color-info);
  border-radius: var(--radius-md);
  padding: 1.25rem;
}

.info-box h4 {
  margin: 0 0 0.75rem 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--color-text-primary);
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-medium);
}

.info-box ol {
  margin: 0;
  padding-left: 1.5rem;
  line-height: var(--line-height-relaxed);
}

.info-box li {
  margin-bottom: 0.5rem;
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
}

.config-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
  font-size: var(--font-size-sm);
}

.form-group input,
.form-group select {
  padding: 0.625rem 0.875rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: var(--font-size-base);
  background: var(--color-input-bg);
  color: var(--color-text-primary);
  transition: all var(--transition-fast);
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(30, 64, 175, 0.08);
}

.form-actions {
  display: flex;
  gap: 0.75rem;
  margin-top: 0.5rem;
}

.btn {
  padding: 0.625rem 1.25rem;
  border: none;
  border-radius: var(--radius-md);
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-medium);
  cursor: pointer;
  transition: all var(--transition-fast);
  display: inline-flex;
  align-items: center;
  justify-content: center;
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

.btn-secondary {
  background: var(--color-bg-tertiary);
  color: var(--color-text-primary);
  border: 1px solid var(--color-border);
}

.btn-secondary:hover {
  background: var(--color-bg-hover);
}

.alert {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 1rem 1.25rem;
  border-radius: var(--radius-md);
  font-size: var(--font-size-sm);
}

.alert-error {
  background: var(--color-error-light);
  border-left: 3px solid var(--color-error);
}

.alert-success {
  background: var(--color-success-light);
  border-left: 3px solid var(--color-success);
}

.alert-content {
  flex: 1;
}

.alert-content strong {
  display: block;
  margin-bottom: 0.25rem;
  font-weight: var(--font-weight-semibold);
}

.alert-content p {
  margin: 0;
  opacity: 0.9;
}

.sync-time {
  margin-top: 0.5rem;
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
