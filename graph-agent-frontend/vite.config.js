import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    // 自动导入Element Plus
    AutoImport({
      resolvers: [ElementPlusResolver()],
    }),
    Components({
      resolvers: [ElementPlusResolver()],
    }),
  ],
  // 路径别名设置，方便你都文件引入
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  // 开发服务器配置（以对接后端接口时用）
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:5000', // 恢复为正确的后端地址
        changeOrigin: true,
        // 移除 rewrite 规则，保持完整路径
      },
    },
    port: 3000, // 前端监听端口，避免和后端5000冲突
    strictPort: true // 端口被占用时直接报错，而不是自动切换端口
  },
  // 确保Vite正确处理字体等静态资源
  assetsInclude: ['**/*.woff', '**/*.woff2', '**/*.ttf'],
})