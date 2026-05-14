<template>
  <div class="query-history">
    <h3 class="history-title">提问记录</h3>
    <div class="history-list">
      <div 
        v-for="(record, index) in queryRecords" 
        :key="index"
        class="history-item"
        @click="selectRecord(record)"
      >
        <div class="record-content">{{ record.question }}</div>
        <div class="record-time">{{ formatTime(record.timestamp) }}</div>
      </div>
      <div v-if="queryRecords.length === 0" class="empty-state">
        暂无提问记录
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

// 响应式数据
const queryRecords = ref([])

// 定义事件
const emit = defineEmits(['recordSelected'])

// 格式化时间
const formatTime = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  return date.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 选择记录
const selectRecord = (record) => {
  emit('recordSelected', record)
}

// 从 localStorage 加载历史记录
const loadHistory = () => {
  try {
    const savedRecords = localStorage.getItem('graphAgentQueryHistory')
    if (savedRecords) {
      queryRecords.value = JSON.parse(savedRecords)
    }
  } catch (error) {
    console.error('加载历史记录失败:', error)
    queryRecords.value = []
  }
}

// 组件挂载时加载历史记录
onMounted(() => {
  loadHistory()
})

// 提供方法供父组件调用以添加新记录
defineExpose({
  addQueryRecord: (question, answer) => {
    const newRecord = {
      question,
      answer,
      timestamp: Date.now()
    }
    
    // 添加到开头（最新在前）
    queryRecords.value.unshift(newRecord)
    
    // 限制最多保存50条记录
    if (queryRecords.value.length > 50) {
      queryRecords.value = queryRecords.value.slice(0, 50)
    }
    
    // 保存到 localStorage
    try {
      localStorage.setItem('graphAgentQueryHistory', JSON.stringify(queryRecords.value))
    } catch (error) {
      console.error('保存历史记录失败:', error)
    }
  },
  
  clearHistory: () => {
    queryRecords.value = []
    localStorage.removeItem('graphAgentQueryHistory')
  }
})
</script>

<style scoped>
.query-history {
  width: 100%;
  height: 100%;
  background: white;
  border-radius: 1rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.history-title {
  padding: 1.25rem 1.5rem;
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: #1e293b;
  border-bottom: 1px solid #e2e8f0;
  background: linear-gradient(120deg, #f8fafc, #f1f5f9);
}

.history-list {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem 0;
}

.history-item {
  padding: 0.75rem 1.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
  border-left: 3px solid transparent;
}

.history-item:hover {
  background-color: #f8fafc;
  border-left-color: #3b82f6;
}

.record-content {
  font-size: 0.95rem;
  color: #1e293b;
  line-height: 1.4;
  margin-bottom: 0.25rem;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

.record-time {
  font-size: 0.75rem;
  color: #64748b;
}

.empty-state {
  padding: 2rem 1.5rem;
  text-align: center;
  color: #64748b;
  font-size: 0.9rem;
}

/* 滚动条样式 */
.history-list::-webkit-scrollbar {
  width: 6px;
}

.history-list::-webkit-scrollbar-track {
  background: #f1f5f9;
}

.history-list::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

.history-list::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}
</style>