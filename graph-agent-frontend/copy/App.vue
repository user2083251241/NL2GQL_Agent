<template>
  <div id="app">
    <HomePage />
  </div>
</template>

<script setup>
import HomePage from './components/HomePage.vue'
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}
body {
  font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
  background: #f0f2f5;
}
#app {
  width: 100%;
  min-height: 100vh;
}
</style>