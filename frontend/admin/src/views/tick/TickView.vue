<template>
  <div class="tick-dashboard">
    <!-- Header -->
    <header class="page-header">
      <div class="header-content">
        <h1 class="page-title">打卡Tick</h1>
        <p class="page-subtitle">培养好习惯，从今天开始</p>
      </div>
      <div class="header-actions" style="display:flex; gap:12px">
         <button class="btn-manage active-scale" @click="openGlobalLogsModal">
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 6h16M4 12h16M4 18h7"/></svg>
            打卡记录
         </button>
         <button class="btn-manage active-scale" @click="showManageModal = true">
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 15a3 3 0 100-6 3 3 0 000 6z"/><path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-2 2 2 2 0 01-2-2v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83 0 2 2 0 010-2.83l.06-.06a1.65 1.65 0 00.33-1.82 1.65 1.65 0 00-1.51-1H3a2 2 0 01-2-2 2 2 0 012-2h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 010-2.83 2 2 0 012.83 0l.06.06a1.65 1.65 0 001.82.33H9a1.65 1.65 0 001-1.51V3a2 2 0 012-2 2 2 0 012 2v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 0 2 2 0 010 2.83l-.06.06a1.65 1.65 0 00-.33 1.82V9a1.65 1.65 0 001.51 1H21a2 2 0 012 2 2 2 0 01-2 2h-.09a1.65 1.65 0 00-1.51 1z"/></svg>
            管理任务
         </button>
      </div>
    </header>

    <div class="dashboard-content" v-if="!loading">
      <!-- 今日本周期待办 -->
      <div class="pending-sections" v-if="pendingTasks.length > 0">
         <!-- Daily -->
         <section class="freq-section" v-if="dailyPending.length > 0">
            <h3 class="freq-title"><span class="emoji">🎯</span> 本日待打卡</h3>
            <div class="cards-grid">
               <div class="task-card active-scale" v-for="t in dailyPending" :key="t.id" @click="openTickModal(t)">
                 <div class="card-info">
                   <h3>{{ t.title }}</h3>
                   <div class="card-meta">
                      <span class="streak-fire"><span class="fire-icon">🔥</span> 已连打 <strong>{{ t.current_streak }}</strong> {{freqUnit(t.frequency)}}</span>
                      <span class="points-reward" v-if="t.enable_points">继续打卡可得 <strong>+{{ pointsIfTickedToday(t) }}</strong> 分</span>
                   </div>
                 </div>
                 <button class="btn-tick-action active-scale" @click.stop="openTickModal(t)">打卡</button>
               </div>
            </div>
         </section>
         
         <!-- Weekly -->
         <section class="freq-section" v-if="weeklyPending.length > 0">
            <h3 class="freq-title"><span class="emoji">🗓️</span> 本周待打卡 <span class="time-left">剩余 {{ remainingDaysWeek }} 天</span></h3>
            <div class="cards-grid">
               <div class="task-card active-scale" v-for="t in weeklyPending" :key="t.id" @click="openTickModal(t)">
                 <div class="card-info">
                   <h3>{{ t.title }}</h3>
                   <div class="card-meta">
                      <span class="streak-fire"><span class="fire-icon">🔥</span> 已连打 <strong>{{ t.current_streak }}</strong> {{freqUnit(t.frequency)}}</span>
                      <span class="points-reward" v-if="t.enable_points">继续打卡可得 <strong>+{{ pointsIfTickedToday(t) }}</strong> 分</span>
                   </div>
                 </div>
                 <button class="btn-tick-action active-scale" @click.stop="openTickModal(t)">打卡</button>
               </div>
            </div>
         </section>
         
         <!-- Monthly -->
         <section class="freq-section" v-if="monthlyPending.length > 0">
            <h3 class="freq-title"><span class="emoji">📅</span> 本月待打卡 <span class="time-left">剩余 {{ remainingDaysMonth }} 天</span></h3>
            <div class="cards-grid">
               <div class="task-card active-scale" v-for="t in monthlyPending" :key="t.id" @click="openTickModal(t)">
                 <div class="card-info">
                   <h3>{{ t.title }}</h3>
                   <div class="card-meta">
                      <span class="streak-fire"><span class="fire-icon">🔥</span> 已连打 <strong>{{ t.current_streak }}</strong> {{freqUnit(t.frequency)}}</span>
                      <span class="points-reward" v-if="t.enable_points">继续打卡可得 <strong>+{{ pointsIfTickedToday(t) }}</strong> 分</span>
                   </div>
                 </div>
                 <button class="btn-tick-action active-scale" @click.stop="openTickModal(t)">打卡</button>
               </div>
            </div>
         </section>
      </div>
      
      <section class="pending-section" v-else-if="tasks.length > 0">
         <div class="all-done-banner">
             🎉 太棒了！当前待办的打卡任务均已完成。
         </div>
      </section>
      
      <section class="pending-section" v-else>
         <div class="all-done-banner" style="cursor:pointer;" @click="showManageModal = true">
             👋 欢迎使用打卡功能！点击「管理任务」来创建你的第一个习惯吧。
         </div>
      </section>

      <!-- 全局日历 -->
      <section class="calendar-section" v-if="tasks.length > 0 || allTasks.length > 0">
        <div class="calendar-container">
          <div class="calendar-top">
            <div class="calendar-header-left">
               <h2>📅 打卡足迹</h2>
               <div class="filter-dropdown-container" @click.stop>
                  <button type="button" class="btn-secondary filter-trigger" @click="showCalendarFilterMenu = !showCalendarFilterMenu; showDrawerFilterMenu = false">
                     <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V19l-4 2v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"/></svg>
                     筛选视图任务 <span v-if="calendarFilterIds.length < tasks.length">({{ calendarFilterIds.length }}/{{ tasks.length }})</span>
                  </button>
                  <div v-show="showCalendarFilterMenu" class="dropdown-menu popup-menu filter-menu">
                     <label class="filter-option all-option">
                        <input type="checkbox" :checked="calendarFilterIds.length === tasks.length" @change="toggleAllCalendarFilter" /> 全选
                     </label>
                     <label class="filter-option" v-for="t in tasks" :key="t.id">
                        <input type="checkbox" :checked="calendarFilterIds.includes(t.id)" @change="toggleCalendarFilter(t.id)" /> <span class="task-opt-title">{{ t.title }}</span>
                     </label>
                  </div>
               </div>
            </div>
            <div class="month-nav">
              <button @click="prevMonth" class="icon-btn active-scale">
                 <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><path d="M15 18l-6-6 6-6"/></svg>
              </button>
              <span class="current-month">{{ currentYear }}年 {{ currentMonth }}月</span>
              <button @click="nextMonth" class="icon-btn active-scale">
                 <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg>
              </button>
            </div>
          </div>
          <div class="calendar-grid">
            <div class="weekday-header">
              <span v-for="w in ['一','二','三','四','五','六','日']" :key="w" :class="{'weekend': w==='六'||w==='日'}">{{ w }}</span>
            </div>
            <div class="days-grid">
               <div 
                 class="day-cell" 
                 v-for="d in calendarDays" 
                 :key="d.dateStr"
                 :class="{'out-of-month': !d.inMonth, 'is-today': d.isToday, 'is-weekend': d.isWeekend}"
               >
                 <div class="day-header">
                    <span class="date-num">{{ d.date }}</span>
                 </div>
                 <div class="day-ticks custom-scroll stamp-matrix">
                    <div v-for="item in getDayTasks(d.dateStr)" :key="item.task.id" 
                         :class="['stamp-item', item.isDone ? 'done' : 'missed']"
                         @mouseenter="(e) => item.isDone && showTooltip(e, item)"
                         @mousemove="item.isDone ? moveTooltip($event) : null"
                         @mouseleave="item.isDone ? hideTooltip() : null">
                       {{ item.task.title.charAt(0) }}
                    </div>
                 </div>
               </div>
            </div>
          </div>
        </div>
      </section>
    </div>

    <!-- 打卡操作弹窗 -->
    <Teleport to="body">
      <div v-if="tickDialogTask" class="modal-overlay" @click.self="tickDialogTask = null">
        <div class="tick-modal">
          <h3>完成打卡：{{ tickDialogTask.title }}</h3>
          
          <div v-if="tickDialogTask.enable_quality" class="field-item">
             <label>完成质量</label>
             <div class="stars">
                <button type="button" @click="tickForm.quality = s" v-for="s in 5" :key="s" class="star" :class="{'active': tickForm.quality >= s}">★</button>
             </div>
          </div>
          
          <div class="field-item">
             <label>备注记录（可选）</label>
             <textarea v-model="tickForm.note" class="form-input" rows="3" placeholder="记录下此时的心得..."></textarea>
          </div>
          
          <div class="form-actions">
             <button class="btn-cancel active-scale" @click="tickDialogTask = null">取消</button>
             <button class="btn-primary active-scale" @click="submitTick" :disabled="ticking">
                {{ ticking ? '打卡中...' : '确认打卡' }}
             </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- 管理任务抽屉 -->
    <Teleport to="body">
      <div v-if="showManageModal" class="drawer-overlay" @click.self="closeManageModal">
         <div class="drawer-panel">
            <div class="drawer-header">
               <h2>管理打卡任务</h2>
               <button class="icon-btn active-scale" @click="closeManageModal">
                  <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6L6 18M6 6l12 12"/></svg>
               </button>
            </div>
            <div class="drawer-body">
               <div class="list-actions" v-if="!showForm && !showLogsForm">
                  <button class="btn-primary active-scale w-full" @click="openCreateTaskForm">
                     + 新建打卡任务
                  </button>
               </div>
               
               <div class="task-list" v-if="!showForm && !showLogsForm">
                  <div class="elegant-list-item" v-for="t in allTasks" :key="t.id">
                     <div class="item-main">
                        <h4 class="item-title">{{ t.title }} <span class="tag" v-if="t.is_archived">已归档</span></h4>
                        <p class="item-sub">
                           {{ freqLabel(t.frequency) }} · 连打 {{ t.current_streak }} {{freqUnit(t.frequency)}}
                           <span v-if="t.enable_points"> · 累计 {{ t.total_points }} 积分</span>
                        </p>
                     </div>
                     <div class="item-actions">
                        <button class="text-btn text-info active-scale" @click="openEditTaskForm(t)">编辑配置</button>
                        <button class="text-btn text-danger active-scale" @click="deleteConfirmItem = t">删除</button>
                     </div>
                  </div>
               </div>
               
               <div class="form-container" v-if="showForm">
                  <h3 class="form-title">{{ editingTask ? '编辑任务' : '新建任务' }}</h3>
                  <form @submit.prevent="submitTaskForm" class="task-form">
                     <div class="field">
                        <label>标题</label>
                        <input v-model="form.title" class="form-input" required placeholder="例如：每日跳绳"/>
                     </div>

                     <div class="field">
                        <label>任务描述 (可选)</label>
                        <textarea v-model="form.description" class="form-input" rows="2" placeholder="填写一下备注或者任务要求"></textarea>
                     </div>
                     
                     <div class="field">
                        <label>周期频率</label>
                        <div class="segmented-control">
                          <button type="button" class="segment-btn" :class="{active: form.frequency === 'daily'}" @click="form.frequency = 'daily'">每天</button>
                          <button type="button" class="segment-btn" :class="{active: form.frequency === 'weekly'}" @click="form.frequency = 'weekly'">每周</button>
                          <button type="button" class="segment-btn" :class="{active: form.frequency === 'monthly'}" @click="form.frequency = 'monthly'">每月</button>
                        </div>
                     </div>

                     <div class="field-group">
                        <div class="field">
                           <label>开始日期</label>
                           <input v-model="form.start_date" type="date" class="form-input" required/>
                        </div>
                        <div class="field">
                           <label>结束日期</label>
                           <input v-model="form.end_date" type="date" class="form-input"/>
                        </div>
                     </div>
                     
                     <div class="field checkbox-field mt-4">
                        <input type="checkbox" v-model="form.enable_quality" id="eq"/> 
                        <label for="eq">记录打卡质量 (1-5星)</label>
                     </div>
                     <div class="field checkbox-field">
                        <input type="checkbox" v-model="form.enable_points" id="ep"/> 
                        <label for="ep">启用积分为连续打卡奖励</label>
                     </div>
                     
                     <div class="points-rule-container" v-if="form.enable_points">
                        <label class="block mt-2 mb-2 font-bold text-sm">阶梯积分规则</label>
                        <div class="rules-editor">
                           <div v-for="(r, i) in form.points_rule" :key="i" class="rule-row">
                             <span class="text-sm">连续第</span>
                             <input v-model.number="r.streak" type="number" min="1" class="form-input sm-input" />
                             <span class="text-sm">{{ freqUnit(form.frequency) }}{{ i === form.points_rule.length - 1 ? '及以后' : '' }}得</span>
                             <input v-model.number="r.points" type="number" min="0" class="form-input sm-input" />
                             <span class="text-sm">分</span>
                             <button type="button" class="icon-btn xs-delete" @click="form.points_rule.splice(i, 1)">×</button>
                           </div>
                           <button type="button" class="btn-cancel text-sm w-full mt-2 add-rule-btn" @click="form.points_rule.push({ streak: form.points_rule.length + 1, points: form.points_rule.length + 1 })">+ 添加阶梯规则</button>
                        </div>
                     </div>

                     <div class="field checkbox-field mt-4" v-if="editingTask">
                        <input type="checkbox" v-model="form.is_archived" id="ia"/> 
                        <label for="ia" class="text-danger">设为归档状态 (暂停打卡)</label>
                     </div>
                     
                     <div class="form-actions border-top-actions">
                        <button type="button" class="btn-cancel active-scale" @click="showForm = false">返回</button>
                        <button type="submit" class="btn-primary active-scale" :disabled="formSubmitting">保存</button>
                     </div>
                  </form>
               </div>

            </div>
         </div>
      </div>
    </Teleport>

    <!-- Global Logs Drawer -->
    <Teleport to="body">
       <div v-if="showGlobalLogsDrawer" class="drawer-overlay" @click.self="showGlobalLogsDrawer = false">
          <div class="drawer-panel" style="width: 540px;">
             <div class="drawer-header" style="flex-direction: column; align-items: stretch; padding-bottom: 8px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                   <h2 style="margin: 0; font-size: 24px; font-weight: 800;">打卡记录</h2>
                   <button class="icon-btn active-scale" @click="showGlobalLogsDrawer = false">
                      <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6L6 18M6 6l12 12"/></svg>
                   </button>
                </div>
                <div class="filter-dropdown-container" @click.stop>
                   <button type="button" class="btn-secondary filter-trigger" @click="showDrawerFilterMenu = !showDrawerFilterMenu; showCalendarFilterMenu = false">
                      <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V19l-4 2v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"/></svg>
                      筛选记录 <span v-if="drawerFilterIds.length < allTasks.length">({{ drawerFilterIds.length }}/{{ allTasks.length }})</span>
                   </button>
                   <div v-show="showDrawerFilterMenu" class="dropdown-menu popup-menu filter-menu">
                      <label class="filter-option all-option">
                         <input type="checkbox" :checked="drawerFilterIds.length === allTasks.length" @change="toggleAllDrawerFilter" /> 全选记录
                      </label>
                      <label class="filter-option" v-for="t in allTasks" :key="t.id">
                         <input type="checkbox" :checked="drawerFilterIds.includes(t.id)" @change="toggleDrawerFilter(t.id)" /> <span class="task-opt-title">{{ t.title }}</span>
                      </label>
                   </div>
                </div>
             </div>
             <div class="drawer-body logs-container" style="max-height: calc(100vh - 160px); padding: 0; background: var(--color-bg-base);">
                <div v-if="filteredListLogs.length === 0" class="empty-state">
                   <div class="empty-icon-wrap">📭</div>
                   <div class="empty-text">暂无打卡记录</div>
                   <div class="empty-sub">没有在这个分类下找到任何自律足迹</div>
                </div>
                <div class="global-log-list" style="padding: 16px;">
                   <div class="elegant-log-card" v-for="log in filteredListLogs" :key="log.id">
                        <div class="log-left">
                           <div class="log-icon-wrap" :class="'freq-'+getTaskValue(log.task_id, 'frequency')">
                              <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
                           </div>
                           <div class="log-info">
                              <h4>{{ getTaskTitle(log.task_id) }}</h4>
                              <div class="log-date">{{ new Date(log.ticked_at).toLocaleString('zh-CN', {month:'2-digit', day:'2-digit', hour:'2-digit', minute:'2-digit'}) }}</div>
                              <div class="log-note" v-if="log.note">"{{ log.note }}"</div>
                           </div>
                        </div>
                        <div class="log-right">
                           <div class="log-meta">
                              <span v-if="log.quality" class="tag tag-yellow">⭐ {{log.quality}}</span>
                              <span v-if="log.points_earned" class="tag tag-green">+{{log.points_earned}}分</span>
                           </div>
                           <button class="text-btn text-danger active-scale" style="margin-top:auto;" @click="undoGlobalLog(log)">撤销打卡</button>
                        </div>
                   </div>
                </div>
             </div>
          </div>
       </div>
    </Teleport>

    <!-- Custom Stamp Tooltip -->
    <Teleport to="body">
      <div v-if="tooltipState.visible && tooltipState.item" 
           class="custom-tooltip" 
           :style="{ top: tooltipState.y + 'px', left: tooltipState.x + 'px' }">
          <h4>{{ tooltipState.item.task.title }}</h4>
          <div v-if="tooltipState.item.isDone && tooltipState.item.log">
             <p>打卡时间: {{ new Date(tooltipState.item.log.ticked_at).toLocaleString() }}</p>
             <p v-if="tooltipState.item.log.quality">完成质量: ⭐ {{ tooltipState.item.log.quality }}</p>
             <p v-if="tooltipState.item.log.points_earned">获得积分: +{{ tooltipState.item.log.points_earned }}分</p>
             <p v-if="tooltipState.item.log.note">备注: {{ tooltipState.item.log.note }}</p>
          </div>
          <div v-else>
             <p style="color: var(--color-danger); font-weight: 700;">未完成 (遗落)</p>
          </div>
      </div>
    </Teleport>

    <!-- Delete Confirm Modal -->
    <Teleport to="body">
       <div v-if="deleteConfirmItem" class="modal-overlay" @click.self="deleteConfirmItem = null">
          <div class="tick-modal" style="max-width: 400px; text-align: center;">
             <div class="danger-icon" style="background: rgba(239, 68, 68, 0.1); width: 64px; height: 64px; border-radius: 50%; display: flex; align-items:center; justify-content:center; margin: 0 auto 20px auto; color: #ef4444;">
                <svg viewBox="0 0 24 24" width="32" height="32" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2M10 11v6M14 11v6"/></svg>
             </div>
             <h3 style="font-size: 20px; font-weight: 800; margin-bottom: 12px;">永久删除该任务？</h3>
             <p style="color: var(--color-text-secondary); font-size: 14px; margin-bottom: 28px; line-height: 1.5;">删除「{{deleteConfirmItem.title}}」后，其包含的所有打卡足迹和积分奖励将永久清空，此操作不可逆。</p>
             <div class="form-actions" style="margin-top: 0; justify-content: center; gap: 16px;">
                <button class="btn-cancel active-scale" @click="deleteConfirmItem = null">取消</button>
                <button class="btn-primary active-scale" style="background: var(--color-danger); box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);" @click="executeDelete">确认删除</button>
             </div>
          </div>
       </div>
    </Teleport>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, reactive } from 'vue'
import * as api from '@/api/tick'

const loading = ref(true)
const tasks = ref([])     // Active tasks
const allTasks = ref([])  // Includes archived
const globalLogs = ref([])

const tooltipState = reactive({ visible: false, x: 0, y: 0, item: null })
const showTooltip = (e, item) => { tooltipState.item = item; tooltipState.visible = true; tooltipState.x = e.clientX + 15; tooltipState.y = e.clientY + 15; }
const hideTooltip = () => { tooltipState.visible = false; tooltipState.item = null; }
const moveTooltip = (e) => { if(tooltipState.visible) { tooltipState.x = e.clientX + 15; tooltipState.y = e.clientY + 15; } }

const showCalendarFilterMenu = ref(false)
const showDrawerFilterMenu = ref(false)

const handleOutsideClick = () => {
    showCalendarFilterMenu.value = false;
    showDrawerFilterMenu.value = false;
}

const calendarFilterIds = ref([])
const toggleCalendarFilter = (id) => {
    if (calendarFilterIds.value.includes(id)) {
        calendarFilterIds.value = calendarFilterIds.value.filter(x => x !== id)
    } else {
        calendarFilterIds.value.push(id)
    }
}
const toggleAllCalendarFilter = (e) => {
    if (e.target.checked) calendarFilterIds.value = tasks.value.map(t => t.id)
    else calendarFilterIds.value = []
}

const drawerFilterIds = ref([])
const toggleDrawerFilter = (id) => {
    if (drawerFilterIds.value.includes(id)) {
        drawerFilterIds.value = drawerFilterIds.value.filter(x => x !== id)
    } else {
        drawerFilterIds.value.push(id)
    }
}
const toggleAllDrawerFilter = (e) => {
    if (e.target.checked) drawerFilterIds.value = allTasks.value.map(t => t.id)
    else drawerFilterIds.value = []
}

const currentDate = ref(new Date())

// --- Data Fetching ---
const fetchTasks = async () => {
    // 获取列表时不加参数将得到 active 和 archived, 取决于后端逻辑，
    // 如果想要所有任务：后端如果传 params 可以获取对应。Admin 中目前可以先获取全部，因为我们在本地分开
    const resActive = await api.getTasks({ is_archived: false })
    const resArchived = await api.getTasks({ is_archived: true })
    
    tasks.value = resActive.data.items || []
    allTasks.value = [...(resActive.data.items || []), ...(resArchived.data.items || [])]
    if (calendarFilterIds.value.length === 0) {
        calendarFilterIds.value = tasks.value.map(t => t.id)
    }
}

const fetchGlobalLogs = async () => {
    try {
      const y = currentDate.value.getFullYear()
      const m = currentDate.value.getMonth()
      const firstDay = new Date(y, m, 1)
      const lastDay = new Date(y, m + 1, 0)
      
      const startStr = new Date(firstDay.getTime() - 7 * 86400000).toISOString().slice(0, 10)
      const endStr = new Date(lastDay.getTime() + 7 * 86400000).toISOString().slice(0, 10)
      
      const { data } = await api.getAllLogs({ start_date: startStr, end_date: endStr })
      globalLogs.value = data.items || []
    } catch(e) {
      console.warn("Could not fetch global logs", e)
    }
}

const loadData = async () => {
   loading.value = true
   await fetchTasks()
   await fetchGlobalLogs()
   loading.value = false
}

onMounted(() => {
   loadData()
   document.addEventListener('click', handleOutsideClick)
})
onUnmounted(() => {
   document.removeEventListener('click', handleOutsideClick)
})

// --- Pending Tasks ---
const pendingTasks = computed(() => {
   return tasks.value.filter(t => !t.ticked_this_period)
})

const dailyPending = computed(() => pendingTasks.value.filter(t => t.frequency === 'daily'))
const weeklyPending = computed(() => pendingTasks.value.filter(t => t.frequency === 'weekly'))
const monthlyPending = computed(() => pendingTasks.value.filter(t => t.frequency === 'monthly'))

const remainingDaysWeek = computed(() => {
    const d = new Date().getDay();
    return d === 0 ? 0 : 7 - d;
})

const remainingDaysMonth = computed(() => {
    const today = new Date();
    const lastDay = new Date(today.getFullYear(), today.getMonth() + 1, 0).getDate();
    return lastDay - today.getDate();
})

const pointsIfTickedToday = (t) => {
   if (!t.enable_points) return 0;
   const rules = t.points_rule;
   if (!rules || rules.length === 0) return 0;
   
   const newStreak = t.current_streak + 1;
   let awarded = 0;
   const sorted = [...rules].sort((a,b) => a.streak - b.streak);
   for(const r of sorted) {
      if (newStreak >= r.streak) { awarded = r.points; }
   }
   return awarded;
}

// --- Calendar Logic ---
const currentYear = computed(() => currentDate.value.getFullYear())
const currentMonth = computed(() => currentDate.value.getMonth() + 1)

const prevMonth = () => {
   currentDate.value = new Date(currentYear.value, currentMonth.value - 2, 1)
   fetchGlobalLogs()
}

const nextMonth = () => {
   currentDate.value = new Date(currentYear.value, currentMonth.value, 1)
   fetchGlobalLogs()
}

const checkWeekend = (dStr) => {
  const day = new Date(dStr).getDay();
  return day === 0 || day === 6;
}

const calendarDays = computed(() => {
  const y = currentYear.value
  const m = currentMonth.value - 1
  const firstDay = new Date(y, m, 1)
  const lastDay = new Date(y, m + 1, 0)
  
  const days = []
  
  const startDay = firstDay.getDay()
  const leadingDays = startDay === 0 ? 6 : startDay - 1
  for (let i = leadingDays; i > 0; i--) {
     const d = new Date(y, m, 1 - i)
     const tzOffset = d.getTimezoneOffset() * 60000;
     const localIso = (new Date(d.getTime() - tzOffset)).toISOString().slice(0, 10);
     days.push({ date: d.getDate(), dateStr: localIso, inMonth: false, isWeekend: checkWeekend(localIso) })
  }
  
  const tzOffset = new Date().getTimezoneOffset() * 60000;
  const todayStr = (new Date(Date.now() - tzOffset)).toISOString().slice(0, 10)
  
  for (let i = 1; i <= lastDay.getDate(); i++) {
     const d = new Date(y, m, i)
     const tzOffset = d.getTimezoneOffset() * 60000;
     const localIso = (new Date(d.getTime() - tzOffset)).toISOString().slice(0, 10);
     days.push({ date: i, dateStr: localIso, inMonth: true, isToday: localIso === todayStr, isWeekend: checkWeekend(localIso) })
  }
  
  const remaining = (7 - (days.length % 7)) % 7
  for (let i = 1; i <= remaining; i++) {
     const d = new Date(y, m + 1, i)
     const tzOffset = d.getTimezoneOffset() * 60000;
     const localIso = (new Date(d.getTime() - tzOffset)).toISOString().slice(0, 10);
     days.push({ date: d.getDate(), dateStr: localIso, inMonth: false, isWeekend: checkWeekend(localIso) })
  }
  return days
})

const logsByDate = computed(() => {
  const map = {}
  globalLogs.value.forEach(log => {
      const d = new Date(log.ticked_at)
      const tzOffset = d.getTimezoneOffset() * 60000;
      const localIso = (new Date(d.getTime() - tzOffset)).toISOString().slice(0, 10);
      if (!map[localIso]) map[localIso] = []
      map[localIso].push(log)
  })
  return map
})

const isLastDayOfWeek = (dateStr) => new Date(dateStr).getDay() === 0;
const isLastDayOfMonth = (dateStr) => {
    const d = new Date(dateStr);
    const tmr = new Date(d);
    tmr.setDate(d.getDate() + 1);
    return tmr.getMonth() !== d.getMonth();
}

const getDayTasks = (dateStr) => {
  const today = (new Date(Date.now() - new Date().getTimezoneOffset() * 60000)).toISOString().slice(0, 10);
  const isFuture = dateStr > today;
  
  const activeTasks = allTasks.value.filter(t => t.start_date <= dateStr && (!t.end_date || t.end_date >= dateStr) && calendarFilterIds.value.includes(t.id));
  const logsOnDate = logsByDate.value[dateStr] || [];
  
  const results = [];
  activeTasks.forEach(t => {
      const log = logsOnDate.find(l => l.task_id === t.id);
      if (log) {
          results.push({ task: t, isDone: true, log });
      } else if (!isFuture) {
          if (t.frequency === 'daily') {
              results.push({ task: t, isDone: false, log: null });
          } else if (t.frequency === 'weekly') {
              if (isLastDayOfWeek(dateStr)) {
                  const dTime = new Date(dateStr).getTime();
                  const tickedInWeek = globalLogs.value.some(l => l.task_id === t.id && (new Date(l.ticked_at.split('T')[0]).getTime() >= dTime - 6 * 86400000) && (new Date(l.ticked_at.split('T')[0]).getTime() <= dTime));
                  if (!tickedInWeek) results.push({ task: t, isDone: false, log: null });
              }
          } else if (t.frequency === 'monthly') {
              if (isLastDayOfMonth(dateStr)) {
                  const prefix = dateStr.slice(0, 7);
                  const tickedInMonth = globalLogs.value.some(l => l.task_id === t.id && l.ticked_at.startsWith(prefix));
                  if (!tickedInMonth) results.push({ task: t, isDone: false, log: null });
              }
          }
      }
  });
  return results;
}

const getTaskTitle = (id) => {
   const t = allTasks.value.find(x => x.id === id)
   return t ? t.title : '任务'
}

function freqLabel(f) {
  return { daily: '每天', weekly: '每周', monthly: '每月' }[f] || f
}
function freqUnit(f) {
  return { daily: '天', weekly: '周', monthly: '月' }[f] || '次'
}

// --- Ticking Logic ---
const tickDialogTask = ref(null)
const tickForm = reactive({ quality: 0, note: '' })
const ticking = ref(false)

const openTickModal = (t) => {
   tickDialogTask.value = t
   tickForm.quality = 0
   tickForm.note = ''
}

const submitTick = async () => {
   if(!tickDialogTask.value) return
   ticking.value = true
   try {
     const body = {}
     if (tickDialogTask.value.enable_quality && tickForm.quality > 0) body.quality = tickForm.quality
     if (tickForm.note.trim()) body.note = tickForm.note.trim()
     await api.doTick(tickDialogTask.value.id, body)
     await loadData() // Refresh
     tickDialogTask.value = null
   } catch(e) {
     alert(e?.response?.data?.detail || '打卡失败')
   } finally {
     ticking.value = false
   }
}

// --- Management Logic ---
const showManageModal = ref(false)
const closeManageModal = () => { showManageModal.value = false; showForm.value = false; showLogsForm.value = false; }

const showForm = ref(false)
const showLogsForm = ref(false)
const editingTask = ref(null)
const formSubmitting = ref(false)
const form = reactive({
  title: '',
  description: '',
  frequency: 'daily',
  start_date: new Date().toISOString().slice(0, 10),
  end_date: '',
  enable_quality: false,
  enable_points: false,
  is_archived: false,
  points_rule: []
})

const openCreateTaskForm = () => {
   editingTask.value = null
   form.title = ''
   form.description = ''
   form.frequency = 'daily'
   const tzOffset = new Date().getTimezoneOffset() * 60000;
   form.start_date = (new Date(Date.now() - tzOffset)).toISOString().slice(0, 10)
   form.end_date = ''
   form.enable_quality = false
   form.enable_points = false
   form.is_archived = false
   form.points_rule = []
   showForm.value = true
   showLogsForm.value = false
}

const openEditTaskForm = (t) => {
   editingTask.value = t
   form.title = t.title
   form.description = t.description || ''
   form.frequency = t.frequency
   form.start_date = t.start_date
   form.end_date = t.end_date || ''
   form.enable_quality = t.enable_quality
   form.enable_points = t.enable_points
   form.is_archived = t.is_archived
   form.points_rule = t.points_rule ? t.points_rule.map(r => ({...r})) : []
   showForm.value = true
   showLogsForm.value = false
}

const submitTaskForm = async () => {
   formSubmitting.value = true
   try {
     const payload = {
       title: form.title,
       frequency: form.frequency,
       frequency_config: {},
       start_date: form.start_date,
       end_date: form.end_date || null,
       enable_quality: form.enable_quality,
       enable_points: form.enable_points,
       is_archived: form.is_archived,
       points_rule: form.enable_points ? form.points_rule : []
     }
     if(editingTask.value) {
        await api.updateTask(editingTask.value.id, payload)
     } else {
        await api.createTask(payload)
     }
     await loadData()
     showForm.value = false
   } catch(e) {
     alert(e?.response?.data?.detail || '保存失败')
   } finally {
     formSubmitting.value = false
   }
}

const deleteConfirmItem = ref(null)
const executeDelete = async () => {
   if (!deleteConfirmItem.value) return
   try {
      await api.deleteTask(deleteConfirmItem.value.id)
      deleteConfirmItem.value = null
      await loadData()
   } catch(e) {
      alert('删除失败')
   }
}

// --- Global Logs Viewer ---
const showGlobalLogsDrawer = ref(false)
const globalListLogs = ref([])

const filteredListLogs = computed(() => {
    return globalListLogs.value.filter(log => drawerFilterIds.value.includes(log.task_id))
})

const getTaskValue = (id, key) => { const t = allTasks.value.find(x => x.id === id); return t ? t[key] : '' }

const openGlobalLogsModal = async () => {
    showGlobalLogsDrawer.value = true
    try {
        const { data } = await api.getAllLogs() // Fetch all globally without date constraints
        globalListLogs.value = data.items || []
        // Sort descending
        globalListLogs.value.sort((a,b) => new Date(b.ticked_at) - new Date(a.ticked_at))
        if (drawerFilterIds.value.length === 0) {
            drawerFilterIds.value = allTasks.value.map(t => t.id)
        }
    } catch(e) { 
        alert('拉取记录失败') 
    }
}

const undoGlobalLog = async (log) => {
    if(!confirm(`确认撤销这条对 "${getTaskTitle(log.task_id)}" 的打卡记录吗？`)) return;
    try {
        await api.deleteLog(log.id);
        const { data } = await api.getAllLogs()
        globalListLogs.value = data.items || [];
        globalListLogs.value.sort((a,b) => new Date(b.ticked_at) - new Date(a.ticked_at))
        await loadData();
    } catch(e) {
        alert(e?.response?.data?.detail || '撤销失败')
    }
}

</script>

<style scoped>
.tick-dashboard {
  padding: 32px 40px;
  max-width: 1300px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 40px;
}

.page-title {
  font-size: 32px;
  font-weight: 800;
  margin: 0 0 6px 0;
  background: linear-gradient(135deg, var(--color-accent), #CF8BF3);
  -webkit-background-clip: text;
  color: transparent;
}
.page-subtitle {
  color: var(--color-text-secondary);
  font-size: 15px;
  margin: 0;
}

.btn-manage {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  color: var(--color-text);
  font-weight: 700;
  font-size: 14px;
  cursor: pointer;
  box-shadow: var(--shadow-sm);
  transition: all 0.25s ease;
}
.btn-manage:hover {
  background: var(--color-surface-hover);
  border-color: var(--color-accent);
  color: var(--color-accent);
}

.section-title {
  font-size: 20px;
  font-weight: 700;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
}
.badge {
  background: var(--color-accent);
  color: #fff;
  padding: 2px 10px;
  border-radius: var(--radius-pill);
  font-size: 13px;
  font-weight: 800;
}

.pending-sections { margin-bottom: 40px; }
.freq-section { margin-bottom: 28px; }
.freq-title { font-size: 18px; font-weight: 800; margin-bottom: 16px; display: flex; align-items: center; gap: 10px; }
.freq-title .emoji { font-size: 20px; }
.time-left { font-size: 13px; font-weight: 600; color: var(--color-text-tertiary); background: rgba(0,0,0,0.04); padding: 4px 8px; border-radius: 6px; margin-left: 8px; }
[data-theme="dark"] .time-left { background: rgba(255,255,255,0.05); }

.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}

.task-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 16px;
  padding: 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 20px rgba(0,0,0,0.02);
}
.task-card:hover {  
  transform: translateY(-4px); 
  box-shadow: 0 12px 30px rgba(0,0,0,0.05); 
  border-color: var(--color-accent-subtle);
}
.task-card h3 { 
  margin: 0 0 10px 0; font-size: 20px; font-weight: 800; color: var(--color-text); transition: color 0.2s;
}
.task-card:hover h3 { color: var(--color-accent); }

.card-info { flex: 1; }
.card-meta { display: flex; flex-direction: column; gap: 6px; margin-top: 8px; }

.streak-fire { font-size: 13px; color: var(--color-text-secondary); font-weight: 600; }
.streak-fire strong { color: #f97316; font-size: 14px; font-weight: 800; }
.points-reward { font-size: 12px; color: #059669; font-weight: 600; }
.points-reward strong { font-size: 14px; font-weight: 800; }
[data-theme="dark"] .points-reward { color: #34d399; }

.btn-tick-action {
  background: var(--color-bg-base);
  border: 2px solid var(--color-border);
  color: var(--color-text);
  font-weight: 800;
  font-size: 15px;
  padding: 12px 24px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
  margin-left: 20px;
}
.btn-tick-action:hover {
  background: var(--color-accent);
  color: white;
  border-color: var(--color-accent);
}

.all-done-banner {
  padding: 24px;
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  color: var(--color-text-secondary);
  text-align: center;
  font-size: 16px;
  font-weight: 600;
  border: 1px dashed var(--color-border);
  margin-bottom: 48px;
}

/* 日历视图 */
.calendar-container {
  background: var(--color-surface);
  border-radius: var(--radius-xl);
  padding: 32px;
  box-shadow: 0 10px 40px rgba(0,0,0,0.03);
  border: 1px solid var(--color-border);
}

.calendar-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}
.calendar-header-left { display: flex; flex-direction: column; gap: 8px; }
.calendar-header-left h2 { margin: 0; font-size: 22px; font-weight: 800; }

/* Filter Dropdown Standardized Styles */
.filter-dropdown-container { position: relative; display: inline-block; }
.filter-trigger { display: inline-flex; align-items: center; gap: 8px; padding: 6px 14px; border-radius: 8px; font-size: 13px; font-weight: 700; color: var(--color-text-secondary); background: transparent; border: 1px solid var(--color-border); cursor: pointer; transition: all 0.2s; }
.filter-trigger:hover, .filter-trigger:active { background: var(--color-surface-hover); color: var(--color-text); }
.popup-menu.filter-menu { position: absolute; top: calc(100% + 8px); left: 0; min-width: 200px; max-height: 320px; overflow-y: auto; background: var(--color-surface-raised); backdrop-filter: blur(24px); -webkit-backdrop-filter: blur(24px); border: 1px solid var(--color-border); border-radius: 12px; box-shadow: 0 10px 40px rgba(0,0,0,0.15); z-index: 100; display: flex; flex-direction: column; padding: 8px 0; }
.filter-option { display: flex; align-items: center; gap: 10px; padding: 8px 16px; cursor: pointer; font-size: 14px; color: var(--color-text); font-weight: 600; transition: background 0.2s; user-select: none; }
.filter-option:hover { background: rgba(0,0,0,0.03); }
[data-theme="dark"] .filter-option:hover { background: rgba(255,255,255,0.05); }
.filter-option input[type="checkbox"] { flex-shrink: 0; width: 16px; height: 16px; cursor: pointer; accent-color: var(--color-accent); }
.filter-option.all-option { border-bottom: 1px solid var(--color-divider); padding-bottom: 12px; margin-bottom: 4px; color: var(--color-text-secondary); }
.task-opt-title { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 150px; }

.month-nav {
  display: flex;
  align-items: center;
  gap: 12px;
}

.icon-btn {
  background: var(--color-bg-base);
  border: 1px solid var(--color-border);
  width: 40px;
  height: 40px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  color: var(--color-text);
}
.icon-btn:hover { background: var(--color-surface-hover); color: var(--color-accent); border-color: var(--color-accent); }
.current-month { font-weight: 700; font-size: 16px; min-width: 110px; text-align: center; }

.calendar-grid {
  display: flex;
  flex-direction: column;
}

.weekday-header {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  text-align: center;
  font-weight: 700;
  color: var(--color-text-tertiary);
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--color-divider);
}
.weekday-header span.weekend { color: #ea580c; font-weight: 800; }
[data-theme="dark"] .weekday-header span.weekend { color: #fb923c; }

.days-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  grid-auto-rows: minmax(130px, auto);
  gap: 12px;
}

.day-cell {
  background: var(--color-bg-base);
  border-radius: 14px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  border: 1px solid var(--color-border);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
}
.day-cell:hover { border-color: var(--color-accent-subtle); transform: translateY(-2px); box-shadow: 0 8px 24px rgba(0,0,0,0.04); }
.day-cell.out-of-month { opacity: 0.4; background: rgba(0,0,0,0.01); }
[data-theme="dark"] .day-cell.out-of-month { background: rgba(255,255,255,0.01); opacity: 0.3; }
.day-cell.is-today {
  border: 2px solid var(--color-accent);
  background: rgba(var(--color-accent-rgb), 0.02);
}
.day-cell.is-today .date-num {
  color: var(--color-accent);
}

/* Weekend Distinct Pattern */
.day-cell.is-weekend {
   border: 1px solid rgba(234, 88, 12, 0.4);
   box-shadow: inset 0 0 12px rgba(234, 88, 12, 0.03);
}
[data-theme="dark"] .day-cell.is-weekend {
   border: 1px solid rgba(251, 146, 60, 0.4);
   box-shadow: inset 0 0 12px rgba(251, 146, 60, 0.03);
}
.day-cell.is-weekend .date-num {
   color: #ea580c;
}
[data-theme="dark"] .day-cell.is-weekend .date-num {
   color: #fb923c;
}

.day-header {
  display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;
}
.date-num {
  font-size: 15px;
  font-weight: 800;
  color: var(--color-text-secondary);
}

.day-ticks {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
  overflow-y: auto;
  padding-right: 2px;
}
/* custom thin scrollbar */
.custom-scroll::-webkit-scrollbar { width: 4px; }
.custom-scroll::-webkit-scrollbar-thumb { background: var(--color-divider); border-radius: 4px; }

/* Minimalist Stamp Matrix */
.stamp-matrix {
   display: grid;
   grid-template-columns: repeat(auto-fill, minmax(28px, 1fr));
   gap: 6px;
   align-content: start;
   padding-bottom: 4px;
}
.stamp-item {
   height: 28px;
   width: 28px;
   border-radius: 50%;
   display: flex;
   align-items: center;
   justify-content: center;
   font-size: 13px;
   font-weight: 800;
   cursor: pointer;
   transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}
.stamp-item:hover {
   transform: scale(1.15) rotate(5deg);
   box-shadow: 0 4px 12px rgba(0,0,0,0.1);
   z-index: 10;
}
.stamp-item.done {
   background: transparent;
   color: #10b981;
   border: 2px solid #10b981;
}
.stamp-item.missed {
   background: transparent;
   border: 2px dashed #fca5a5;
   color: #ef4444;
}
[data-theme="dark"] .stamp-item.done { border-color: #34d399; color: #34d399; }
[data-theme="dark"] .stamp-item.missed { border-color: rgba(239, 68, 68, 0.4); color: #f87171; }

/* Modals & Drawers */
.tick-modal {
  background: var(--color-surface-raised);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border: 1px solid var(--color-border);
  border-radius: 24px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
  padding: 36px;
  max-width: 440px;
}
.tick-modal h3 { font-size: 22px; margin-bottom: 24px; }
.field-item { margin-bottom: 20px; }
.field-item label { display: block; font-size: 14px; font-weight: 700; color: var(--color-text-secondary); margin-bottom: 8px; }

.stars { display: flex; gap: 8px; }
.star {
  font-size: 36px;
  margin: 0 2px;
  color: var(--color-text-tertiary);
  opacity: 0.4;
  background: none;
  border: none;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}
.star:hover {
  transform: scale(1.2);
  opacity: 0.8;
  color: #fbbf24;
}
.star.active { 
  color: #f59e0b; 
  opacity: 1;
  text-shadow: 0 0 14px rgba(245, 158, 11, 0.5); 
  transform: scale(1.1);
}

.form-input {
  width: 100%;
  padding: 14px 16px;
  border: 1px solid var(--color-border);
  border-radius: 12px;
  background: var(--color-bg-base);
  color: var(--color-text);
  font-family: inherit;
  font-size: 15px;
  outline: none;
  transition: border 0.3s;
}
.form-input:focus { border-color: var(--color-accent); }

.form-actions { display: flex; justify-content: flex-end; gap: 12px; margin-top: 32px; }
.btn-primary {
  padding: 12px 24px;
  background: var(--color-accent);
  color: white;
  border: none;
  border-radius: 12px;
  font-weight: 700;
  font-size: 15px;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}
.btn-cancel {
  padding: 12px 24px;
  background: transparent;
  color: var(--color-text-secondary);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  font-weight: 700;
  font-size: 15px;
  cursor: pointer;
}

.list-actions { margin-bottom: 20px; }
.w-full { width: 100%; justify-content: center; }

.elegant-list-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: var(--color-surface);
  border-radius: 12px;
  margin-bottom: 12px;
  border: 1px solid var(--color-border);
  transition: all 0.2s ease;
}
.elegant-list-item:hover {
  border-color: var(--color-accent-subtle);
  box-shadow: 0 4px 12px rgba(0,0,0,0.03);
  transform: translateY(-1px);
}
.item-title { margin: 0 0 6px 0; font-size: 16px; font-weight: 700; display: flex; align-items: center; gap: 8px;}
.item-sub { margin: 0; font-size: 13px; color: var(--color-text-tertiary); }
.tag { font-size: 11px; font-weight: 600; background: rgba(0,0,0,0.04); padding: 3px 6px; border-radius: 4px; }
[data-theme="dark"] .tag { background: rgba(255,255,255,0.05); }

.item-actions { display: flex; gap: 6px; opacity: 0; transform: translateX(10px); transition: all 0.2s; }
.elegant-list-item:hover .item-actions { opacity: 1; transform: translateX(0); }
.text-btn { background: none; border: none; font-weight: 600; padding: 6px 12px; border-radius: 6px; cursor: pointer; font-size: 13px; transition: all 0.2s; }
.text-btn:hover { background: rgba(0,0,0,0.04); }
[data-theme="dark"] .text-btn:hover { background: rgba(255,255,255,0.05); }
.text-info { color: var(--color-accent); }
.text-danger { color: var(--color-danger); }

/* Modal Overlay Base */
.modal-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.4); backdrop-filter: blur(4px);
  display: flex; align-items: center; justify-content: center; z-index: 1000;
  animation: fadeIn 0.2s;
}

/* Drawer Fixes */
.drawer-header {
  padding: 24px;
  border-bottom: 1px solid var(--color-border);
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.drawer-header h2 { margin: 0; font-size: 24px; font-weight: 800; }
.drawer-body {
  padding: 24px;
  flex: 1;
  overflow-y: auto;
}

.form-container { animation: fadeIn 0.3s ease;}
.form-title { font-size: 22px; margin-bottom: 24px; }
.field { margin-bottom: 20px; }
.field label { display: block; font-weight: 700; font-size: 14px; margin-bottom: 8px; color: var(--color-text-secondary); }
.field-group { display: flex; gap: 16px; flex-wrap: wrap; }
.field-group .field { flex: 1; min-width: 150px; }
.checkbox-field { display: flex; align-items: center; gap: 12px; cursor: pointer; margin-bottom: 20px;}
.checkbox-field input[type="checkbox"] { width: 18px; height: 18px; margin: 0; accent-color: var(--color-accent); cursor: pointer;}
.checkbox-field label { font-weight: 600; font-size: 14px; margin-bottom: 0 !important; cursor: pointer; display: inline-flex !important; align-items: center; }

/* Segmented Control for Frequency */
.segmented-control {
  display: flex; background: var(--color-bg-base); border-radius: var(--radius-sm); padding: 4px; gap: 4px; border: 1px solid var(--color-border);
}
.segment-btn {
  flex: 1; padding: 10px; border: none; background: transparent; color: var(--color-text-secondary); border-radius: 8px; font-weight: 600; cursor: pointer; transition: all 0.2s;
}
.segment-btn:hover { background: rgba(0,0,0,0.03); }
[data-theme="dark"] .segment-btn:hover { background: rgba(255,255,255,0.03); }
.segment-btn.active { background: var(--color-surface); color: var(--color-accent); box-shadow: var(--shadow-sm); }

/* Points Rules */
.points-rule-container { background: rgba(var(--color-accent-rgb), 0.05); padding: 16px; border-radius: 12px; margin-top: 12px; border: 1px dashed var(--color-border); }
.rules-editor { display: flex; flex-direction: column; gap: 10px; }
.rule-row { display: flex; align-items: center; gap: 8px; background: var(--color-surface); padding: 8px 12px; border-radius: 8px; border: 1px solid var(--color-border); }
.sm-input { padding: 6px 10px; width: 60px; text-align: center; font-weight: 700; color: var(--color-accent); }
.xs-delete { font-size: 16px; color: var(--color-danger); margin-left: auto; width: 24px; height: 24px; border-radius: 4px;}
.add-rule-btn { border-style: dashed; }
.text-sm { font-size: 13px; } .font-bold { font-weight: bold; } .block { display: block; } .mt-2 { margin-top: 8px; } .mt-4 { margin-top: 16px; } .mb-2 { margin-bottom: 8px; }
.border-top-actions { border-top: 1px solid var(--color-border); padding-top: 20px; }

/* Logs Viewer */
.logs-container { max-height: calc(100vh - 200px); display: flex; flex-direction: column; overflow: hidden; }
.logs-header { display: flex; align-items: center; gap: 12px; margin-bottom: 24px; padding-bottom: 16px; border-bottom: 1px solid var(--color-border); }
.m-0 { margin: 0; }
.logs-list { flex: 1; overflow-y: auto; padding-right: 8px; }
.log-info { display: flex; flex-direction: column; justify-content: center; }
.log-info h4 { margin: 0 0 6px 0; font-size: 16px; font-weight: 700; color: var(--color-text); }
.log-date { font-weight: 600; font-size: 13px; color: var(--color-text-secondary); margin-bottom: 2px;}

.elegant-log-card { display: flex; justify-content: space-between; background: var(--color-surface); border-radius: 14px; padding: 16px; margin-bottom: 12px; border: 1px solid var(--color-border); transition: all 0.2s;}
.elegant-log-card:hover { border-color: var(--color-accent-subtle); box-shadow: 0 4px 12px rgba(0,0,0,0.03); }
.log-left { display: flex; gap: 16px; align-items: stretch; }
.log-right { display: flex; flex-direction: column; align-items: flex-end; justify-content: space-between; }
.log-icon-wrap { width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; border-radius: 12px; background: rgba(0,0,0,0.03); color: var(--color-text-tertiary); }
[data-theme="dark"] .log-icon-wrap { background: rgba(255,255,255,0.05); }

.log-meta { display: flex; gap: 6px; flex-wrap: wrap; justify-content: flex-end; }
.log-note { font-size: 13px; color: var(--color-text-secondary); max-width: 250px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-top: 4px; font-style: italic; }
.tag-yellow { background: #fef3c7; color: #d97706; font-weight: 800; border-radius: 6px; padding: 4px 8px; font-size: 11px;}
.tag-green { background: #d1fae5; color: #059669; font-weight: 800; border-radius: 6px; padding: 4px 8px; font-size: 11px; }
[data-theme="dark"] .tag-yellow { background: rgba(245, 158, 11, 0.15); }
[data-theme="dark"] .tag-green { background: rgba(16, 185, 129, 0.15); }
.flex-wrap { flex-wrap: wrap; } .gap-2 { gap: 8px; } .gap-1 { gap: 4px; } .items-center { align-items: center; } .flex { display: flex; }

/* Filter Dropdown Standardized Styles */
.filter-dropdown-container { position: relative; display: inline-block; }
.filter-trigger { display: inline-flex; align-items: center; gap: 8px; padding: 6px 14px; border-radius: 8px; font-size: 13px; font-weight: 700; color: var(--color-text-secondary); background: transparent; border: 1px solid var(--color-border); cursor: pointer; transition: all 0.2s; }
.filter-trigger:hover, .filter-trigger:active { background: var(--color-surface-hover); color: var(--color-text); }
.popup-menu.filter-menu { position: absolute; top: calc(100% + 8px); left: 0; min-width: 200px; max-height: 320px; overflow-y: auto; background: var(--color-surface-raised); backdrop-filter: blur(24px); -webkit-backdrop-filter: blur(24px); border: 1px solid var(--color-border); border-radius: 12px; box-shadow: 0 10px 40px rgba(0,0,0,0.15); z-index: 100; display: flex; flex-direction: column; padding: 8px 0; }
.filter-option { display: flex; align-items: center; gap: 10px; padding: 8px 16px; cursor: pointer; font-size: 14px; color: var(--color-text); font-weight: 600; transition: background 0.2s; user-select: none; }
.filter-option:hover { background: rgba(0,0,0,0.03); }
[data-theme="dark"] .filter-option:hover { background: rgba(255,255,255,0.05); }
.filter-option input[type="checkbox"] { flex-shrink: 0; width: 16px; height: 16px; cursor: pointer; accent-color: var(--color-accent); }
.filter-option.all-option { border-bottom: 1px solid var(--color-divider); padding-bottom: 12px; margin-bottom: 4px; color: var(--color-text-secondary); }
.task-opt-title { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 150px; }
.empty-state { text-align: center; color: var(--color-text-tertiary); padding: 60px 0; display: flex; flex-direction: column; align-items: center; }
.empty-icon-wrap { font-size: 48px; filter: grayscale(1) opacity(0.3); margin-bottom: 16px; }
.empty-text { font-size: 18px; font-weight: 800; color: var(--color-text-secondary); }
.empty-sub { font-size: 13px; margin-top: 8px; }

.custom-tooltip {
  position: fixed;
  z-index: 10000;
  background: var(--color-surface-raised);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid var(--color-border);
  box-shadow: 0 10px 40px rgba(0,0,0,0.15);
  padding: 12px 16px;
  border-radius: 12px;
  pointer-events: none;
  font-size: 13px;
  min-width: 180px;
}
.custom-tooltip h4 { margin: 0 0 8px 0; font-size: 15px; font-weight: 800; border-bottom: 1px solid var(--color-divider); padding-bottom: 6px; color: var(--color-text);}
.custom-tooltip p { margin: 4px 0; color: var(--color-text-secondary); line-height: 1.4; }
</style>
