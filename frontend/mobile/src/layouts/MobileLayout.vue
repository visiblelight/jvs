<template>
  <div class="mobile-layout">
    <div class="page-area" :class="{ 'has-tab-bar': showTabBar }">
      <router-view v-slot="{ Component, route }">
        <transition :name="transitionName" mode="out-in">
          <component :is="Component" :key="route.path" />
        </transition>
      </router-view>
    </div>
    <transition name="fade">
      <div class="tab-bar-wrapper" v-if="showTabBar">
        <BottomNav />
      </div>
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
  position: relative;
}
.page-area {
  flex: 1;
  overflow: auto;
  position: relative;
  height: 100%;
}
.page-area.has-tab-bar {
  /* Leave space for the floating tab bar */
  padding-bottom: var(--tab-bar-height);
}
.tab-bar-wrapper {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 100;
  pointer-events: none; /* Let clicks pass through empty spaces */
}
</style>
