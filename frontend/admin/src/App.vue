<template>
  <router-view />
  <GlobalDialog />
</template>

<script setup>
import { useThemeStore } from '@/stores/theme'
import GlobalDialog from '@/components/GlobalDialog.vue'
useThemeStore()
</script>
