import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  timeout: 300000, // 增加到300秒超时用于调试
  headers: {
    'Content-Type': 'application/json'
  }
});

api.interceptors.request.use(
  (config) => {
    console.log('[API] Request:', config);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

api.interceptors.response.use(
  (response) => {
    console.log('[API] Response:', response);
    return response.data;
  },
  (error) => {
    console.error('[API] Error:', error);
    return Promise.reject(error);
  }
);

export const graphAgentApi = {
  // 普通查询（非流式）
  submitQuery(query, enableSelfCorrection = true) {
    return api.post('/graph-agent/query', {
      query: query,
      timestamp: Date.now(),
      enable_self_correction: enableSelfCorrection
    });
  },

  // 流式查询（SSE）- 使用原生 fetch
  async submitQueryStream(query, enableSelfCorrection = true, onMessage) {
    const response = await fetch('/api/graph-agent/query/stream', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        query: query,
        timestamp: Date.now(),
        enable_self_correction: enableSelfCorrection
      })
    });

    if (!response.ok) {
      throw new Error(`接口请求失败，状态码：${response.status}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let result = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      result += decoder.decode(value, { stream: true });
      
      const lines = result.split('\n\n');
      result = lines.pop(); // 保留最后一个不完整的数据块
      
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const json = JSON.parse(line.replace('data: ', ''));
            if (onMessage) {
              onMessage(json.content);
            }
          } catch (e) {
            continue;
          }
        }
      }
    }
  }
};

export default api;