<template>
  <div class="todo-category-tree">
    <template v-for="cat in categories" :key="cat.id">
      <div class="tree-item-group">
        
        <!-- Normal Mode -->
        <button
          v-if="editCatId !== cat.id"
          class="tree-item active-scale"
          :class="{ active: selectedId === cat.id }"
          :style="{ paddingLeft: (12 + level * 16) + 'px' }"
          @click="$emit('select', cat.id)"
        >
          <span class="item-name">{{ cat.name }}</span>
          <span class="tree-actions">
            <span class="action-icon edit" @click.stop="enterEdit(cat)" title="重命名分类">✎</span>
            <span class="action-icon" @click.stop="$emit('add', cat.id)" title="添加子分类">+</span>
            <span class="action-icon del" @click.stop="$emit('delete', cat)" title="删除分类">×</span>
          </span>
        </button>

        <!-- Edit Mode -->
        <div v-else class="inline-add" :style="{ paddingLeft: (12 + level * 16) + 'px', marginBottom: '4px' }">
          <input 
            v-model="editCatName" 
            placeholder="输入新名称回车..." 
            @keyup.enter="submitEdit(cat)" 
            @keyup.esc="cancelEdit" 
            class="inline-input" 
            autofocus 
          />
          <button class="inline-cancel" @click="cancelEdit" title="取消">×</button>
        </div>
        
        <!-- Parent Adding a Child -->
        <div v-if="addParentId === cat.id" class="inline-add" :style="{ paddingLeft: (28 + level * 16) + 'px' }">
          <input 
            v-model="localNewName" 
            placeholder="输入后回车..." 
            @keyup.enter="handleEnter(cat.id)" 
            @keyup.esc="$emit('cancel-add')" 
            class="inline-input" 
            autofocus 
          />
          <button class="inline-cancel" @click="$emit('cancel-add')" title="取消">×</button>
        </div>

        <!-- Recursive children rendering -->
        <TodoCategoryTree
          v-if="cat.children && cat.children.length > 0"
          :categories="cat.children"
          :level="level + 1"
          :selected-id="selectedId"
          :add-parent-id="addParentId"
          @select="$emit('select', $event)"
          @add="$emit('add', $event)"
          @delete="$emit('delete', $event)"
          @submit-add="$emit('submit-add', $event)"
          @submit-edit="$emit('submit-edit', $event)"
          @cancel-add="$emit('cancel-add')"
        />
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  categories: { type: Array, required: true },
  level: { type: Number, default: 0 },
  selectedId: { type: [Number, String], default: null },
  addParentId: { type: [Number, String, Boolean], default: false }
})

const emit = defineEmits(['select', 'add', 'delete', 'submit-add', 'submit-edit', 'cancel-add'])

const localNewName = ref('')
const editCatId = ref(null)
const editCatName = ref('')

// Clear local input when adding stops
watch(() => props.addParentId, (val) => {
  if (val === false) {
    localNewName.value = ''
  }
})

function handleEnter(parentId) {
  const txt = localNewName.value.trim()
  if (txt) {
    emit('submit-add', { parentId, name: txt })
    localNewName.value = ''
  }
}

function enterEdit(cat) {
  editCatId.value = cat.id
  editCatName.value = cat.name
}

function submitEdit(cat) {
  const txt = editCatName.value.trim()
  if (txt && txt !== cat.name) {
    emit('submit-edit', { id: cat.id, name: txt })
  }
  editCatId.value = null
}

function cancelEdit() {
  editCatId.value = null
}
</script>

<style scoped>
.todo-category-tree {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.tree-item-group {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.tree-item {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  padding-top: 8px;
  padding-bottom: 8px;
  padding-right: 12px;
  border: none;
  border-radius: var(--radius-sm);
  background: transparent;
  font-family: var(--font-body);
  font-size: 13px;
  font-weight: 500;
  color: var(--color-text-secondary);
  cursor: pointer;
  text-align: left;
  transition: all var(--transition-fast);
}

.item-name {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.tree-actions {
  display: flex;
  gap: 4px;
  opacity: 0;
}
.action-icon {
  color: var(--color-text-tertiary);
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  border-radius: 4px;
}
.action-icon:hover {
  color: var(--color-text);
  background: var(--color-surface-hover);
}
.action-icon.del:hover {
  color: var(--color-danger);
  background: var(--color-danger-subtle, rgba(239, 68, 68, 0.15));
}
.action-icon.edit:hover {
  color: var(--color-accent);
  background: var(--color-accent-subtle);
}

.tree-item:hover {
  background: var(--color-surface-hover);
  color: var(--color-text);
}
.tree-item:hover .tree-actions {
  opacity: 1;
}

.tree-item.active {
  background: var(--color-accent-subtle);
  color: var(--color-accent-text);
}

.inline-add {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 8px;
  padding-right: 12px;
  animation: fadeIn 0.15s cubic-bezier(0.3, 1.2, 0.2, 1);
}

.inline-input {
  flex: 1;
  width: 100%;
  padding: 8px 10px;
  border: 1px solid var(--color-accent);
  border-radius: var(--radius-sm);
  background: var(--color-surface);
  color: var(--color-text);
  font-size: 12px;
  outline: none;
  box-shadow: 0 0 0 3px var(--color-accent-subtle);
}

.inline-cancel {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  border-radius: var(--radius-sm);
  background: var(--color-bg-base);
  color: var(--color-text-secondary);
  cursor: pointer;
}
.inline-cancel:hover {
  background: var(--color-surface-hover);
  color: var(--color-text);
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-4px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
