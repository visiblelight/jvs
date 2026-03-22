<template>
  <div class="mobile-layout">
    <div class="page-area">
      <router-view v-slot="{ Component, route }">
        <transition :name="transitionName" mode="out-in">
          <component :is="Component" :key="route.path" />
        </transition>
      </router-view>
    </div>
    <transition name="fade">
      <BottomNav v-if="showTabBar" />
    </transition>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import BottomNav from '@/components/BottomNav.vue'

const route = useRoute()
const showTabBar = computed(() => !!route.meta.tabBar)
const transitionName = computed(() => route.meta.tabBar ? 'fade' : 'slide-left')
</script>

<style scoped>
.mobile-layout {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.page-area {
  flex: 1;
  overflow: hidden;
  position: relative;
}
</style>
