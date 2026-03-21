<template>
  <router-view />
</template>

<script setup>
import { useThemeStore } from '@/stores/theme'
// Initialize theme on app mount
useThemeStore()
</script>
