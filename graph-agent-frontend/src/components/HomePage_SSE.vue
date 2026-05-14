<template>
  <div class="chat-layout">
    <!-- 左侧侧边栏：会话历史 -->
    <aside class="sidebar">
      <div class="sidebar-header">
        <button class="new-chat-btn" @click="createNewSession">
          <span class="icon">+</span> 新建会话
        </button>
      </div>
      <div class="session-list">
        <div
          v-for="session in sessions"
          :key="session.id"
          class="session-item"
          :class="{ active: session.id === activeSessionId }"
          @click="switchSession(session.id)"
        >
          <div class="session-info">
            <div class="session-title">{{ session.title || '新会话' }}</div>
            <div class="session-time">{{ formatTime(session.lastActiveTime) }}</div>
          </div>
          <!-- 删除按钮：hover显示 -->
          <button 
            class="delete-btn" 
            @click.stop="deleteSession(session.id)"
            title="删除会话"
          >
            ×
          </button>
        </div>
      </div>
    </aside>

    <!-- 右侧主聊天区域 -->
    <main class="chat-container">
      <!-- 聊天头部 -->
      <header class="chat-header">
        <h2 class="title">HugeGraph查询智能体</h2>
      </header>

      <!-- 消息列表区域 -->
      <div class="chat-messages" ref="messagesRef">
        <!-- 空状态提示 -->
        <div v-if="currentMessages.length === 0" class="empty-tip">
          <p>发送消息开始对话</p>
        </div>

        <!-- 消息气泡 -->
        <div
          v-for="msg in currentMessages"
          :key="msg.id"
          class="message-item"
          :class="msg.type"
        >
          <div class="message-bubble">
            <div class="message-avatar" v-if="msg.type === 'agent'"></div>
            <div class="message-content">
              <div class="message-text">{{ msg.content }}</div>
              <div class="message-time">{{ formatTime(msg.timestamp) }}</div>
            </div>
            <div class="message-avatar user-avatar" v-if="msg.type === 'user'"></div>
          </div>
        </div>

        <!-- 加载中状态（流式请求时不再显示固定加载文案） -->
        <div v-if="isSubmitting && !streamingMsgId" class="message-item agent">
          <div class="message-bubble">
            <div class="message-avatar"></div>
            <div class="message-content">
              <div class="loading-text">正在思考中...（前端）</div>
            </div>
          </div>
        </div>

        <!-- 错误提示 -->
        <div v-if="errorMessage" class="error-tip">
          ❌ {{ errorMessage }}
        </div>
      </div>

      <!-- 底部输入框区域 -->
      <div class="chat-input-area">
        <div class="input-wrapper">
          <textarea
            v-model="userInput"
            class="text-input"
            rows="1"
            placeholder="请输入您的问题或指令..."
            :disabled="isSubmitting"
            @keydown.enter.prevent="handleSubmit"
          ></textarea>
          <div class="button-group">
            <button 
              class="submit-btn" 
              @click="handleSubmit" 
              :disabled="isSubmitting || !userInput.trim()"
            >
              {{ isSubmitting ? '发送中' : '提交' }}
            </button>
            <button 
              class="clear-btn" 
              @click="clearInput" 
              :disabled="isSubmitting"
            >
              清空
            </button>
          </div>
        </div>
        <div class="input-caption">
           提示：您可以输入图查询语句或自然语言描述，Agent 会为您处理请求。
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'

// 响应式数据
const userInput = ref('')        
const isSubmitting = ref(false)  
const errorMessage = ref('')     
const messagesRef = ref(null)    
// 新增：流式消息ID（用于标记当前正在流式输出的Agent消息）
const streamingMsgId = ref('')

// 会话管理
const sessions = ref([])
const activeSessionId = ref(null)

// 当前会话的消息列表
const currentMessages = computed(() => {
  const session = sessions.value.find(s => s.id === activeSessionId.value)
  return session?.messages || []
})

// 初始化：创建默认会话
const initDefaultSession = () => {
  const newSession = createSession()
  sessions.value.push(newSession)
  activeSessionId.value = newSession.id
}

// 创建新会话
const createSession = () => {
  return {
    id: Date.now().toString(),
    title: '',
    messages: [],
    lastActiveTime: new Date()
  }
}

// 新建会话按钮
const createNewSession = () => {
  const newSession = createSession()
  sessions.value.unshift(newSession) 
  activeSessionId.value = newSession.id
  clearInput()
}

// 切换会话
const switchSession = (sessionId) => {
  activeSessionId.value = sessionId
  clearInput()
}

// 删除会话（核心功能）
const deleteSession = (sessionId) => {
  // 禁止删除最后一个会话
  if (sessions.value.length <= 1) {
    alert('❌ 至少保留一个会话')
    return
  }
  
  // 确认删除
  if (!confirm('确定要删除该会话吗？此操作不可恢复！')) {
    return
  }

  // 删除会话
  sessions.value = sessions.value.filter(s => s.id !== sessionId)

  // 如果删除的是当前激活的会话，自动切换到第一个会话
  if (activeSessionId.value === sessionId) {
    activeSessionId.value = sessions.value[0].id
  }
}

// 格式化时间
const formatTime = (date) => {
  const d = new Date(date)
  return d.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

// 自动滚动到底部
const scrollToBottom = () => {
  nextTick(() => {
    if (messagesRef.value) {
      messagesRef.value.scrollTop = messagesRef.value.scrollHeight
    }
  })
}

// 监听消息变化，自动滚动
watch(currentMessages, () => {
  scrollToBottom()
}, { deep: true })

// 新增：更新流式消息内容
const updateStreamingMessage = (content) => {
  const currentSession = sessions.value.find(s => s.id === activeSessionId.value)
  const msgIndex = currentSession.messages.findIndex(m => m.id === streamingMsgId.value)
  if (msgIndex > -1) {
    currentSession.messages[msgIndex].content = content
    currentSession.lastActiveTime = new Date()
  }
}

// 新增：关闭SSE连接
const closeSSEConnection = (eventSource) => {
  if (eventSource) {
    eventSource.close()
  }
  isSubmitting.value = false
  streamingMsgId.value = ''
}

// 提交按钮核心处理函数：发送用户问题，接收后端SSE流式响应
const handleSubmit = async () => {
  // 1. 校验输入框：去除首尾空格，判断是否为空
  const trimmed = userInput.value.trim()
  if (!trimmed) {
    alert('❌ 请输入有效内容后再提交')
    return
  }
  // 防止重复提交：如果正在请求中，直接返回
  if (isSubmitting.value) return

  // 2. 重置状态：开启加载状态，清空错误提示
  isSubmitting.value = true
  errorMessage.value = ''
  streamingMsgId.value = ''

  // 3. 构造用户消息对象
  const userMsg = {
    id: Date.now().toString(),    // 唯一ID：时间戳
    type: 'user',                 // 消息类型：用户消息
    content: trimmed,             // 消息内容
    timestamp: new Date()         // 消息时间
  }

  // 4. 获取当前活跃的会话，将用户消息添加到列表
  const currentSession = sessions.value.find(s => s.id === activeSessionId.value)
  currentSession.messages.push(userMsg)
  currentSession.lastActiveTime = new Date()

  // 5. 自动设置会话标题（取第一条用户消息的前15个字符）
  if (!currentSession.title) {
    currentSession.title = trimmed.length > 15 ? `${trimmed.slice(0, 15)}...` : trimmed
  }
  // 提交后清空输入框
  userInput.value = ''

  // 6. 创建AI机器人消息（初始为空，用于流式实时填充内容）
  const agentMsgId = (Date.now() + 1).toString()
  currentSession.messages.push({
    id: agentMsgId,
    type: 'agent',
    content: '正在思考中...（前端蓝色）',
    timestamp: new Date()
  })
  // 标记当前正在流式输出的消息ID
  streamingMsgId.value = agentMsgId

  try {
    // ========================
    // 核心：原生 fetch 请求 SSE 流式接口（axios不支持流式，必须用fetch）
    // ========================
    const response = await fetch('/api/graph-agent/query/stream', {
      method: 'POST',                          // 请求方式：POST
      headers: {
        'Content-Type': 'application/json'     // 参数格式：JSON
      },
      // 传递给后端的参数：和后端接口接收字段一致
      body: JSON.stringify({
        query: trimmed,
        timestamp: Date.now(),
        enable_self_correction: true
      })
    })

    // 判断HTTP请求是否成功（状态码200）
    if (!response.ok) throw new Error(`接口请求失败，状态码：${response.status}`)

    // 7. 解析后端返回的流式数据
    const reader = response.body.getReader()   // 创建流读取器
    const decoder = new TextDecoder('utf-8')  // 文本解码器
    let result = ''                            // 存储完整的流数据

    // 循环读取流数据（直到后端传输完毕）
    while (true) {
      const { done, value } = await reader.read()
      // 后端传输完成，退出循环
      if (done) break

      // 解码流数据并拼接到结果中
      result += decoder.decode(value, { stream: true })
      
      // 按 SSE 标准格式拆分数据（data: {}\n\n）
      const lines = result.split('\n\n')
      let fullContent = ''
      
      // 遍历解析每一行SSE数据
      for (const line of lines) {
        // 只处理以 data: 开头的有效数据
        if (line.startsWith('data: ')) {
          try {
            // 去掉前缀，解析JSON
            const json = JSON.parse(line.replace('data: ', ''))
            // 拼接后端返回的内容
            fullContent += json.content + '\n'
          } catch (e) {
            // 解析失败跳过（不影响主逻辑）
            continue
          }
        }
      }

      // 8. 实时更新AI消息内容（打字机效果）
      const msg = currentSession.messages.find(m => m.id === streamingMsgId.value)
      if (msg) msg.content = fullContent
    }

  } catch (error) {
    // 9. 异常处理：打印错误，显示错误提示
    console.error('[Chat] 流式请求错误：', error)
    errorMessage.value = '连接失败，请稍后重试'
    
    // 错误提示3秒后自动消失
    setTimeout(() => errorMessage.value = '', 3000)
  } finally {
    // 10. 最终执行：无论成功/失败，关闭加载状态
    isSubmitting.value = false
    streamingMsgId.value = ''
  }
}

// 清空输入框
const clearInput = () => {
  userInput.value = ''
  errorMessage.value = ''
}

// 初始化
initDefaultSession()
</script>

<style scoped>
/* 全局基础重置 */
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html, body, #app {
  height: 100%;
  overflow: hidden;
}

.chat-layout {
  display: flex;
  height: 95vh;
  margin: 0 auto;  /* 居中显示 */
  background: #f7f8fa;
}

/* 左侧侧边栏 */
.sidebar {
  width: 240px;
  background: rgb(226, 226, 226);
  border-right: 1px solid #e5e7eb;
  display: flex;
  flex-direction: column;
  padding: 1rem;
}

.sidebar-header {
  margin-bottom: 1rem;
}

.new-chat-btn {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid #ffffff;
  border-radius: 0.75rem;
  background: #ffffff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  font-size: 0.95rem;
  color: #374151;
  transition: all 0.2s;
}

.new-chat-btn:hover {
  background: #e8e8e8;
  border-color: #d1d5db;
}

.session-list {
  flex: 1;
  overflow-y: auto;
}

/* 会话项：弹性布局，容纳删除按钮 */
.session-item {
  padding: 0.75rem 1rem;
  border-radius: 0.75rem;
  margin-bottom: 0.5rem;
  cursor: pointer;
  transition: background 0.2s;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.session-item:hover {
  background: #f3f4f6;
}

.session-item.active {
  background: #eff6ff;
  color: #2563eb;
}

.session-info {
  flex: 1;
  overflow: hidden;
}

.session-title {
  font-size: 0.9rem;
  font-weight: 500;
  margin-bottom: 0.25rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.session-time {
  font-size: 0.75rem;
  color: #9ca3af;
}

/* 删除按钮样式 */
.delete-btn {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  border: none;
  background: transparent;
  color: #9ca3af;
  font-size: 14px;
  cursor: pointer;
  display: none;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

/* 悬浮时显示删除按钮 */
.session-item:hover .delete-btn {
  display: flex;
}

.delete-btn:hover {
  background: #ef4444;
  color: white;
}

/* 右侧聊天容器 */
.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #ffffff;
}

.chat-header {
  padding: 1.5rem 2rem;
  border-bottom: 1px solid #e5e7eb;
}

.title {
  font-size: 1.5rem;
  font-weight: 600;
  background: linear-gradient(120deg, #1e293b, #2d3a4f);
  background-clip: text;
  -webkit-background-clip: text;
  color: transparent;
}

/* 消息列表 */
.chat-messages {
  flex: 1;
  padding: 2rem;
  overflow-y: auto;
  background: #f9fafb;
}

.empty-tip {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #9ca3af;
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.message-item {
  margin-bottom: 1.5rem;
  display: flex;
}

.message-item.user {
  justify-content: flex-end;
}

.message-item.agent {
  justify-content: flex-start;
}

.message-bubble {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  max-width: 70%;
}

.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #e5e7eb;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-size: 1.2rem;
}

.user-avatar {
  background: #3b82f6;
  color: white;
}

.message-content {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.message-text {
  background: white;
  padding: 1rem 1.25rem;
  border-radius: 1rem;
  line-height: 1.6;
  font-size: 0.95rem;
  color: #1f2937;
  box-shadow: 0 1px 2px rgba(0,0,0,0.05);
  white-space: pre-wrap; /* 支持换行符 */
}

.message-item.user .message-text {
  background: #3b82f6;
  color: white;
  border-bottom-right-radius: 0.25rem;
  text-align: justify;
  text-justify: inter-word;
}

.message-item.agent .message-text {
  background: white;
  border-bottom-left-radius: 0.25rem;
  text-align: justify;
  text-justify: inter-word;
}

.message-time {
  font-size: 0.75rem;
  color: #9ca3af;
  align-self: flex-end;
}

.message-item.user .message-time {
  align-self: flex-start;
}

.loading-text {
  background: white;
  padding: 1rem 1.25rem;
  border-radius: 1rem;
  border-bottom-left-radius: 0.25rem;
  line-height: 1.6;
  font-size: 0.95rem;
  color: #6b7280;
  box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}

.error-tip {
  color: #dc2626;
  background: #fef2f2;
  border-radius: 0.75rem;
  padding: 1rem;
  border-left: 4px solid #ef4444;
  font-size: 0.95rem;
  margin: 0 auto;
  max-width: 70%;
}

/* 底部输入框区域 */
.chat-input-area {
  padding: 1.5rem 2rem;
  border-top: 1px solid #e5e7eb;
  background: white;
}

.input-wrapper {
  display: flex;
  gap: 1rem;
  align-items: flex-end;
  margin-bottom: 0.75rem;
}

.text-input {
  flex: 1;
  padding: 1rem;
  font-size: 1rem;
  font-family: inherit;
  border: 1.5px solid #e2e8f0;
  border-radius: 1rem;
  resize: none;
  outline: none;
  transition: border 0.2s, box-shadow 0.2s;
  min-height: 50px;
  max-height: 150px;
  overflow-y: auto;
}

.text-input:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
}

.text-input:disabled {
  background-color: #f9fafb;
  cursor: not-allowed;
}

.button-group {
  display: flex;
  gap: 0.75rem;
}

.submit-btn, .clear-btn {
  padding: 0.75rem 1.5rem;
  border-radius: 2rem;
  font-weight: 600;
  font-size: 0.95rem;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
  font-family: inherit;
}

.submit-btn {
  background: #3b82f6;
  color: white;
}

.submit-btn:hover:not(:disabled) {
  background: #2563eb;
  transform: translateY(-1px);
}

.submit-btn:disabled {
  background: #94a3b8;
  cursor: not-allowed;
  opacity: 0.7;
}

.clear-btn {
  background: #f1f5f9;
  color: #1e293b;
  border: 1px solid #e2e8f0;
}

.clear-btn:hover:not(:disabled) {
  background: #e2e8f0;
}

.input-caption {
  font-size: 0.85rem;
  color: #64748b;
  text-align: center;
}

/* 响应式适配 */
@media (max-width: 768px) {
  .sidebar {
    display: none;
  }

  .chat-header,
  .chat-messages,
  .chat-input-area {
    padding: 1rem;
  }

  .message-bubble {
    max-width: 85%;
  }
}
</style>