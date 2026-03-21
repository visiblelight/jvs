<template>
  <div class="user-avatar" :style="{ width: size + 'px', height: size + 'px' }">
    <img
      v-if="avatar && !imgError"
      :src="'/uploads/avatars/' + avatar + '?t=' + ts"
      :alt="alt"
      class="avatar-img"
      @error="imgError = true"
    />
    <svg
      v-else
      viewBox="0 0 24 24"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      class="avatar-default"
    >
      <circle cx="12" cy="8" r="3.5" stroke="currentColor" stroke-width="1.5"/>
      <path
        d="M4.5 19.5C4.5 16.186 7.186 13.5 10.5 13.5h3c3.314 0 6 2.686 6 6"
        stroke="currentColor"
        stroke-width="1.5"
        stroke-linecap="round"
      />
    </svg>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  avatar: { type: String, default: null },
  size: { type: Number, default: 32 },
  alt: { type: String, default: '用户头像' },
  ts: { type: Number, default: 0 },
})

const imgError = ref(false)

watch(() => props.ts, () => { imgError.value = false })
</script>

<style scoped>
.user-avatar {
  border-radius: 50%;
  overflow: hidden;
  background: var(--color-accent-subtle);
  color: var(--color-accent-text);
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.avatar-default {
  width: 60%;
  height: 60%;
}
</style>
