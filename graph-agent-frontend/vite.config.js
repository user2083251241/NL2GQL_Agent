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
  // 配置路径别名（可选，方便导入文件）
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  // 解决跨域问题（对接后端Flask接口时用）
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:5000', // 后端Flask服务地址
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
    port: 3000, // 前端启动端口（避免和后端5000冲突）
  },
  // 确保Vite正确处理字体等静态资源
  assetsInclude: ['**/*.woff', '**/*.woff2', '**/*.ttf'],
})