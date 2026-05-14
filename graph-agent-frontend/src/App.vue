<template>
  <div id="app">
    <HomePage_SSE />
  </div>
</template>

<script setup>
import HomePage_SSE from './components/HomePage_SSE.vue'
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}
body {
  overflow: hidden; /* 禁止浏览器滑动 */
  height: 95vh;
  font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
  background: #f0f2f5;
}
#app {
  width: 100%;
  min-height: 100vh;
}
</style>