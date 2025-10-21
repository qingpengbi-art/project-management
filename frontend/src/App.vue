<template>
  <router-view />
</template>

<script setup>
import { provide } from 'vue'
import { ElMessage } from 'element-plus'

// 提供全局方法
provide('$message', ElMessage)
</script>

<style scoped>
#app {
  min-height: 100vh;
}
</style>
