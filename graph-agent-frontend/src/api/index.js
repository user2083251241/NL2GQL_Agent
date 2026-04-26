import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
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
  submitQuery(query) {
    return api.post('/graph-agent/query', {
      query: query,
      timestamp: Date.now()
    });
  }
};

export default api;