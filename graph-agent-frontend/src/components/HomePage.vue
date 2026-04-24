<template>
  <div class="home-page">
    <div class="card">
      <h2 class="title">✨ Graph Agent 交互演示</h2>

      <!-- 文本输入框 -->
      <textarea
        v-model="userInput"
        class="text-input"
        rows="4"
        placeholder="请输入您的问题或指令..."
        :disabled="isSubmitting"
      ></textarea>

      <!-- 底部文字说明（位于输入框正下方） -->
      <div class="input-caption">
        💡 提示：您可以输入图查询语句或自然语言描述，点击提交按钮后 Agent 会处理您的请求。
      </div>

      <!-- 提交按钮 + 清空按钮 -->
      <div class="button-group">
        <button 
          class="submit-btn" 
          @click="handleSubmit" 
          :disabled="isSubmitting"
        >
          {{ isSubmitting ? '提交中...' : '提交' }}
        </button>
        <button class="clear-btn" @click="clearInput" :disabled="isSubmitting">
          清空
        </button>
      </div>

      <!-- 反馈区域：显示最近提交的内容 -->
      <div class="feedback-area" v-if="lastSubmitted">
        <div class="feedback-success">
          ✅ 提交成功！<br />
          <span class="submitted-text">“{{ lastSubmitted }}”</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

// 响应式数据
const userInput = ref('')        // 输入框内容
const isSubmitting = ref(false)  // 提交状态
const lastSubmitted = ref('')    // 最后一次提交的内容

// 提交处理
const handleSubmit = async () => {
  const trimmed = userInput.value.trim()
  if (!trimmed) {
    alert('❌ 请输入有效内容后再提交')
    return
  }
  if (isSubmitting.value) return

  isSubmitting.value = true

  // 模拟异步提交（如调用后端 API）
  await new Promise(resolve => setTimeout(resolve, 500))

  // 更新反馈
  lastSubmitted.value = trimmed
  console.log('[HomePage] 用户提交:', trimmed)

  // 可选：提交后清空输入框（若需要保留，注释下面一行）
  // userInput.value = ''

  isSubmitting.value = false
}

// 清空输入框及反馈
const clearInput = () => {
  userInput.value = ''
  lastSubmitted.value = ''
}
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f5f7fa 0%, #e9edf2 100%);
  padding: 1.5rem;
}

.card {
  max-width: 700px;
  width: 100%;
  background: white;
  border-radius: 2rem;
  box-shadow: 0 20px 35px -12px rgba(0, 0, 0, 0.15);
  padding: 2rem 2rem 2.5rem;
  transition: all 0.2s;
}

.title {
  font-size: 1.8rem;
  font-weight: 600;
  margin-bottom: 1.8rem;
  background: linear-gradient(120deg, #1e293b, #2d3a4f);
  background-clip: text;
  -webkit-background-clip: text;
  color: transparent;
  border-left: 4px solid #3b82f6;
  padding-left: 1rem;
}

.text-input {
  width: 100%;
  padding: 1rem;
  font-size: 1rem;
  font-family: inherit;
  border: 1.5px solid #e2e8f0;
  border-radius: 1rem;
  resize: vertical;
  outline: none;
  transition: border 0.2s, box-shadow 0.2s;
  margin-bottom: 0.75rem;
}

.text-input:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
}

.text-input:disabled {
  background-color: #f9fafb;
  cursor: not-allowed;
}

.input-caption {
  font-size: 0.85rem;
  color: #475569;
  background: #f8fafc;
  padding: 0.6rem 1rem;
  border-radius: 1rem;
  margin-bottom: 1.5rem;
  border-left: 3px solid #3b82f6;
  line-height: 1.4;
}

.button-group {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-bottom: 1.8rem;
}

.submit-btn, .clear-btn {
  padding: 0.7rem 1.8rem;
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
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
}

.submit-btn:hover:not(:disabled) {
  background: #2563eb;
  transform: translateY(-1px);
  box-shadow: 0 8px 18px rgba(59, 130, 246, 0.3);
}

.submit-btn:active:not(:disabled) {
  transform: translateY(1px);
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
  transform: translateY(-1px);
}

.clear-btn:active:not(:disabled) {
  transform: translateY(1px);
}

.clear-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.feedback-area {
  background: #f0fdf4;
  border-radius: 1rem;
  padding: 1rem;
  border-left: 4px solid #22c55e;
}

.feedback-success {
  color: #166534;
  font-size: 0.95rem;
  line-height: 1.5;
}

.submitted-text {
  font-weight: 500;
  background: #dcfce7;
  padding: 0.2rem 0.5rem;
  border-radius: 0.5rem;
  display: inline-block;
  margin-top: 0.3rem;
  word-break: break-word;
}

@media (max-width: 560px) {
  .card {
    padding: 1.5rem;
  }
  .title {
    font-size: 1.5rem;
  }
  .button-group {
    flex-direction: column;
  }
  .submit-btn, .clear-btn {
    width: 100%;
    justify-content: center;
  }
}
</style>