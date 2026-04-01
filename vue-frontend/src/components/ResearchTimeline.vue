<template>
  <div class="timeline-container">
    <h3 class="timeline-title">研究时间线</h3>
    <div class="timeline-content">
      <div
        v-for="(event, index) in events"
        :key="index"
        class="timeline-item"
        :class="{ selected: selectedIndex === index }"
        @click="selectEvent(index)"
      >
        <div class="timeline-year">{{ event.year }}</div>
        <div class="timeline-body">
          <div class="timeline-meta">
            <Icon name="document" :size="14" />
            <span class="paper-count">{{ event.paper_ids.length }} 篇论文</span>
          </div>
          <div v-if="event.key_topics.length" class="timeline-topics">
            <span class="section-label">主题:</span>
            <span
              v-for="(topic, i) in event.key_topics.slice(0, 3)"
              :key="i"
              class="topic-tag"
            >
              {{ topic }}
            </span>
          </div>
          <div v-if="event.key_methods.length" class="timeline-methods">
            <span class="section-label">方法:</span>
            <span
              v-for="(method, i) in event.key_methods.slice(0, 3)"
              :key="i"
              class="method-tag"
            >
              {{ method }}
            </span>
          </div>
          <div v-if="event.highlights.length" class="timeline-highlights">
            <p
              v-for="(highlight, i) in event.highlights.slice(0, 2)"
              :key="i"
              class="highlight-text"
            >
              {{ highlight }}
            </p>
          </div>
        </div>
      </div>
    </div>
    <div v-if="selectedEvent" class="event-detail">
      <h4>{{ selectedEvent.year }} 详情</h4>
      <p class="detail-summary">
        共 {{ selectedEvent.paper_ids.length }} 篇论文，
        {{ selectedEvent.key_topics.length }} 个主题，
        {{ selectedEvent.key_methods.length }} 个方法
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { TimelineEvent } from '@/types/research-map'
import Icon from './common/Icon.vue'

interface Props {
  events: TimelineEvent[]
}

const props = defineProps<Props>()

const emit = defineEmits<{
  eventClick: [event: TimelineEvent]
}>()

const selectedIndex = ref<number | null>(null)

const selectedEvent = computed(() => {
  return selectedIndex.value !== null ? props.events[selectedIndex.value] : null
})

const selectEvent = (index: number) => {
  selectedIndex.value = index
  emit('eventClick', props.events[index])
}
</script>

<style scoped>
.timeline-container {
  width: 100%;
  height: 100%;
  min-height: 400px;
  background: white;
  border-radius: 8px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.timeline-title {
  margin: 0;
  padding: 16px;
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  border-bottom: 1px solid #e2e8f0;
}

.timeline-content {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
}

.timeline-item {
  display: flex;
  padding: 12px;
  margin-bottom: 8px;
  background: #f8fafc;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  border-left: 3px solid transparent;
}

.timeline-item:hover {
  background: #f1f5f9;
}

.timeline-item.selected {
  background: #eff6ff;
  border-left-color: #3b82f6;
}

.timeline-year {
  min-width: 80px;
  font-size: 18px;
  font-weight: 700;
  color: #3b82f6;
  display: flex;
  align-items: center;
}

.timeline-body {
  flex: 1;
}

.timeline-meta {
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.timeline-meta .icon {
  color: #94a3b8;
}

.paper-count {
  font-size: 12px;
  color: #64748b;
  font-weight: 500;
}

.timeline-topics,
.timeline-methods {
  margin-bottom: 6px;
  font-size: 12px;
}

.section-label {
  color: #64748b;
  font-weight: 500;
  margin-right: 6px;
}

.topic-tag {
  display: inline-block;
  padding: 2px 8px;
  margin-right: 4px;
  margin-bottom: 2px;
  background: #dcfce7;
  color: #166534;
  border-radius: 4px;
  font-size: 11px;
}

.method-tag {
  display: inline-block;
  padding: 2px 8px;
  margin-right: 4px;
  margin-bottom: 2px;
  background: #ede9fe;
  color: #5b21b6;
  border-radius: 4px;
  font-size: 11px;
}

.timeline-highlights {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid #e2e8f0;
}

.highlight-text {
  margin: 4px 0;
  font-size: 12px;
  color: #475569;
  line-height: 1.5;
}

.event-detail {
  padding: 16px;
  background: #f8fafc;
  border-top: 1px solid #e2e8f0;
}

.event-detail h4 {
  margin: 0 0 8px;
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
}

.detail-summary {
  margin: 0;
  font-size: 13px;
  color: #64748b;
}
</style>
