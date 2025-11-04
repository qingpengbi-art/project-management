<template>
  <div class="dashboard">
    <!-- 顶部概览区域 - 三卡片横向布局 -->
      <div class="overview-section three-cards">
        <!-- 横向项目卡片 -->
        <div class="stat-card apple-card project-source-card horizontal-card">
          <!-- 顶部装饰条 -->
          <div class="card-accent-bar horizontal-accent"></div>
          
          <!-- 上半部分：信息区 -->
          <div class="card-info-section">
            <h3 class="card-title-large">横向项目</h3>
            <div class="card-number-display">{{ horizontalOverview.total }}</div>
          </div>
          
          <!-- 下半部分：状态区 -->
          <div class="card-status-section">
            <div class="status-grid-uniform">
              <div 
                v-for="status in orderedStatusList" 
                :key="status"
                class="status-item-uniform"
                :class="{ 'active': (horizontalOverview.statusDist[status] || 0) > 0 }"
                @click="navigateToProjectsBySource('horizontal', status)"
              >
                <div class="status-count-uniform">{{ horizontalOverview.statusDist[status] || 0 }}</div>
                <div class="status-label-uniform">{{ getStatusShortText(status) }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- 纵向项目卡片 -->
        <div class="stat-card apple-card project-source-card vertical-card">
          <!-- 顶部装饰条 -->
          <div class="card-accent-bar vertical-accent"></div>
          
          <!-- 上半部分：信息区 -->
          <div class="card-info-section">
            <h3 class="card-title-large">纵向项目</h3>
            <div class="card-number-display">{{ verticalOverview.total }}</div>
          </div>
          
          <!-- 下半部分：状态区 - 使用纵向专用状态 -->
          <div class="card-status-section">
            <div class="status-grid-vertical">
              <div 
                v-for="status in verticalStatusList" 
                :key="status"
                class="status-item-vertical"
                :class="{ 'active': (verticalOverview.statusDist[status] || 0) > 0 }"
                @click="navigateToProjectsBySource('vertical', status)"
              >
                <div class="status-count-uniform">{{ verticalOverview.statusDist[status] || 0 }}</div>
                <div class="status-label-uniform">{{ getStatusShortText(status) }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- 自研项目卡片 -->
        <div class="stat-card apple-card project-source-card self-card">
          <!-- 顶部装饰条 -->
          <div class="card-accent-bar self-accent"></div>
          
          <!-- 上半部分：信息区 -->
          <div class="card-info-section">
            <h3 class="card-title-large">自研项目</h3>
            <div class="card-number-display">{{ selfDevelopedOverview.total }}</div>
          </div>
          
          <!-- 下半部分：状态区（两个大卡片） -->
          <div class="card-status-section">
            <div class="self-status-grid-two">
              <div 
                class="self-status-item-large"
                :class="{ 'active': selfDevelopedOverview.inProgress > 0 }"
                @click="navigateToProjectsBySource('self_developed', 'project_implementation')"
              >
                <div class="self-status-count">{{ selfDevelopedOverview.inProgress }}</div>
                <div class="self-status-label">进行中</div>
              </div>
              <div 
                class="self-status-item-large"
                :class="{ 'active': selfDevelopedOverview.completed > 0 }"
                @click="navigateToProjectsBySource('self_developed', 'project_acceptance')"
              >
                <div class="self-status-count">{{ selfDevelopedOverview.completed }}</div>
                <div class="self-status-label">已完成</div>
              </div>
            </div>
          </div>
        </div>
      </div>

    <!-- 项目模块进度一览表 -->
    <div class="modules-overview apple-card">
      <div class="section-header">
        <h3 class="section-title">项目模块进度一览表</h3>
        <div class="section-actions">
          <el-button size="small" @click="refreshModulesData">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
          <el-button size="small" type="primary" @click="exportToExcel">
            <el-icon><Download /></el-icon>
            导出Excel
          </el-button>
        </div>
      </div>
      
      <div v-if="modulesLoading" class="loading-state">
        <el-skeleton :rows="5" animated />
      </div>
      
      <div v-else-if="projectsWithModules.length === 0" class="empty-state">
        <div class="empty-icon">
          <el-icon><Box /></el-icon>
        </div>
        <p>暂无项目模块数据</p>
      </div>
      
      <div v-else class="modules-table-container">
        <el-table 
          :data="projectsWithModules" 
          style="width: 100%"
          row-key="id"
          :expand-row-keys="expandedRows"
          @expand-change="handleExpandChange"
          :table-layout="'auto'"
        >
          <!-- 展开行 -->
          <el-table-column type="expand">
            <template #default="{ row }">
              <div class="expanded-modules">
                <div v-if="!row.modules || row.modules.length === 0" class="no-modules">
                  <p>该项目暂无模块</p>
                </div>
                <div v-else class="modules-grid">
                  <div
                    v-for="module in row.modules"
                    :key="module.id"
                    class="module-item"
                  >
                    <div class="module-header">
                      <div class="module-name">{{ module.name }}</div>
                      <div class="module-status" :class="module.status">
                        {{ getModuleStatusText(module.status) }}
                      </div>
                    </div>
                    <div class="module-assignees">
                      <div class="assignees-label">成员:</div>
                      <div class="assignees-list">
                        <div
                          v-if="module.assigned_users && module.assigned_users.length > 0"
                          v-for="user in module.assigned_users"
                          :key="user.id"
                          class="assignee-tag"
                          :title="`${user.name} - ${user.position || ''}`"
                        >
                          {{ user.name }}
                        </div>
                        <div v-else class="no-assignee">
                          未分配
                        </div>
                      </div>
                    </div>
                    
                    <div class="module-progress">
                      <div class="progress-info">
                        <span class="progress-text">{{ module.progress }}%</span>
                      </div>
                      <div class="progress-bar">
                        <div 
                          class="progress-fill"
                          :class="getProgressClass(module.progress)"
                          :style="{ width: module.progress + '%' }"
                        ></div>
                      </div>
                    </div>
                    
                    <div v-if="module.latest_work" class="module-work">
                      <div class="work-header">
                        <span class="work-period">{{ module.latest_work.week_label }}</span>
                        <span class="work-author">by {{ module.latest_work.created_by }}</span>
                      </div>
                      <div class="work-content">
                        <p class="work-description">{{ module.latest_work.work_content }}</p>
                        <div v-if="module.latest_work.achievements" class="work-achievements">
                          <strong>成果:</strong> {{ module.latest_work.achievements }}
                        </div>
                      </div>
                    </div>
                    
                    <div v-else class="no-work">
                      <p>暂无工作记录</p>
                    </div>
                    
                    <div class="module-meta">
                      <span class="update-time">{{ formatDate(module.updated_at) }}</span>
                      <div class="module-actions">
                        <el-button 
                          v-if="canUpdateModule(module, row)" 
                          size="small" 
                          type="success" 
                          plain 
                          @click="showUpdateModuleProgress(module, row.name)"
                        >
                          更新进度
                        </el-button>
                        <el-button size="small" type="primary" plain @click="showModuleWorkHistory(module, row.name)">
                          查看历史
                        </el-button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </template>
          </el-table-column>
          
          <!-- 项目名称 -->
          <el-table-column prop="name" label="项目名称" min-width="100" show-overflow-tooltip align="left" header-align="center">
            <template #default="{ row }">
              <div class="project-name">
                <span class="name">{{ row.name }}</span>
                <el-tag 
                  v-if="getUserProjectRole(row)" 
                  :type="getProjectRoleTagType(row)"
                  size="small"
                  class="role-tag"
                >
                  {{ getUserProjectRole(row) }}
                </el-tag>
              </div>
            </template>
          </el-table-column>
          
          <!-- 项目状态 -->
          <el-table-column prop="status" label="项目状态" width="120" align="center" header-align="center">
            <template #default="{ row }">
              <span class="status-badge" :class="row.status">{{ getStatusText(row.status) }}</span>
            </template>
          </el-table-column>
          
          <!-- 项目类型 -->
          <el-table-column prop="project_source" label="项目类型" width="100" align="center" header-align="center">
            <template #default="{ row }">
              <span class="source-tag" :class="`source-${row.project_source || 'horizontal'}`">
                {{ getSourceText(row.project_source) }}
              </span>
            </template>
          </el-table-column>
          
          <!-- 合作方（横向和纵向项目显示） -->
          <el-table-column prop="partner" label="合作方" width="150" align="center" header-align="center">
            <template #default="{ row }">
              <span v-if="(row.project_source === 'horizontal' || row.project_source === 'vertical') && row.partner" class="partner-text">
                {{ row.partner }}
              </span>
              <span v-else class="no-partner">-</span>
            </template>
          </el-table-column>
          
          <!-- 合同金额 -->
          <el-table-column prop="contract_amount" label="合同金额" width="120" align="right" header-align="center">
            <template #default="{ row }">
              <span v-if="row.contract_amount != null" class="amount-text">
                ¥{{ formatAmount(row.contract_amount) }}
              </span>
              <span v-else class="no-amount">-</span>
            </template>
          </el-table-column>
          
          <!-- 到账金额 -->
          <el-table-column prop="received_amount" label="到账金额" width="120" align="right" header-align="center">
            <template #default="{ row }">
              <span v-if="row.received_amount != null" class="amount-text">
                ¥{{ formatAmount(row.received_amount) }}
              </span>
              <span v-else class="no-amount">-</span>
            </template>
          </el-table-column>
          
          <!-- 项目进度（纵向项目不显示） -->
          <el-table-column prop="progress" label="项目进度" width="150" align="center" header-align="center">
            <template #default="{ row }">
              <div v-if="row.project_source !== 'vertical'" class="progress-cell">
                <div class="progress-bar">
                  <div 
                    class="progress-fill"
                    :class="getProgressClass(row.progress)"
                    :style="{ width: row.progress + '%' }"
                  ></div>
                </div>
                <span class="progress-text">{{ row.progress }}%</span>
              </div>
              <span v-else class="no-progress">-</span>
            </template>
          </el-table-column>
          
          <!-- 负责人 -->
          <el-table-column label="项目负责人" width="120" align="center" header-align="center">
            <template #default="{ row }">
              <div class="project-leader">
                <div
                  v-if="row.leader"
                  class="member-avatar"
                  :title="row.leader.name || '未知用户'"
                >
                  {{ (row.leader.name || '?').charAt(0) }}
                </div>
                <span v-else class="no-leader">未指定</span>
              </div>
            </template>
          </el-table-column>
          
          <!-- 最后更新 -->
          <el-table-column prop="updated_at" label="最后更新" width="120" align="center" header-align="center">
            <template #default="{ row }">
              {{ formatDate(row.updated_at) }}
            </template>
          </el-table-column>
          
          <!-- 操作 -->
          <el-table-column label="操作" width="100" align="center" header-align="center">
            <template #default="{ row }">
              <el-button
                size="small"
                type="primary"
                plain
                @click="goToProjectDetail(row.id)"
              >
                查看详情
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <!-- 更新进度对话框 -->
    <UpdateProgressDialog 
      v-model="updateDialogVisible"
      :project="selectedProject"
      @success="handleUpdateSuccess"
    />
    
    <!-- 模块进度更新对话框 -->
    <UpdateModuleProgressDialog
      v-model:visible="updateModuleProgressDialogVisible"
      :module="selectedModule"
      :project-name="selectedProjectName"
      @success="handleModuleUpdateSuccess"
    />
    
    <!-- 模块工作历史对话框 -->
    <ModuleWorkHistoryDialog
      v-model:visible="moduleHistoryDialogVisible"
      :module="selectedModule"
      :project-name="selectedProjectName"
    />

    <!-- 状态提示框 -->
    <teleport to="body">
      <div 
        v-if="statusTooltipVisible"
        class="status-tooltip-wrapper"
        :style="{
          left: statusTooltipPosition.x + 'px',
          top: statusTooltipPosition.y + 'px'
        }"
        v-html="statusTooltipContent"
      ></div>
    </teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElLoading } from 'element-plus'
import { 
  FolderOpened, 
  Timer, 
  TrendCharts, 
  CircleCheck,
  ArrowRight,
  Refresh,
  Box,
  Download,
  ArrowDown,
  DocumentCopy,
  Document,
  Picture,
  DataLine
} from '@element-plus/icons-vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { PieChart, BarChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
} from 'echarts/components'
import { useProjectStore } from '@/stores/project'
import { useModuleStore } from '@/stores/module'
import { useAuthStore } from '@/stores/auth'
import { moduleApi } from '@/utils/api'
import UpdateProgressDialog from '@/components/UpdateProgressDialog.vue'
import UpdateModuleProgressDialog from '@/components/UpdateModuleProgressDialog.vue'
import ModuleWorkHistoryDialog from '@/components/ModuleWorkHistoryDialog.vue'

// 注册ECharts组件
use([
  CanvasRenderer,
  PieChart,
  BarChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
])

const router = useRouter()
const projectStore = useProjectStore()
const moduleStore = useModuleStore()
const authStore = useAuthStore()

// 响应式数据
const updateDialogVisible = ref(false)
const selectedProject = ref(null)
const projectsWithModules = ref([])
const modulesLoading = ref(false)
const expandedRows = ref([])
const updateModuleProgressDialogVisible = ref(false)
const moduleHistoryDialogVisible = ref(false)
const selectedModule = ref(null)
const selectedProjectName = ref('')

// 状态提示框相关
const statusTooltipVisible = ref(false)
const statusTooltipContent = ref('')
const statusTooltipPosition = ref({ x: 0, y: 0 })

// 横向项目按业务流程顺序排列的状态列表
const orderedStatusList = [
  'initial_contact',      // 初步接触
  'proposal_submitted',   // 提交方案
  'quotation_submitted',  // 提交报价
  'user_confirmation',    // 用户确认
  'contract_signed',      // 合同签订
  'project_implementation', // 项目实施
  'project_acceptance',   // 项目验收
  'warranty_period',      // 维保期内
  'post_warranty',        // 维保期外
  'no_follow_up'          // 不再跟进
]

// 纵向项目专用状态列表
const verticalStatusList = [
  'vertical_declaration', // 申报阶段
  'vertical_review',      // 审核阶段
  'vertical_approved',    // 审核通过
  'vertical_rejected'     // 审核未通过
]

// 计算属性
const overview = computed(() => projectStore.overview)

const completedCount = computed(() => {
  const dist = overview.value.summary.status_distribution || {}
  return (dist.project_acceptance || 0) + (dist.warranty_period || 0) + (dist.post_warranty || 0)
})

// 横向项目统计
const horizontalOverview = computed(() => {
  const projects = overview.value.projects.filter(p => !p.project_source || p.project_source === 'horizontal')
  const statusDist = {}
  orderedStatusList.forEach(status => {
    statusDist[status] = projects.filter(p => p.status === status).length
  })
  const totalProgress = projects.reduce((sum, p) => sum + (p.progress || 0), 0)
  return {
    total: projects.length,
    avgProgress: projects.length > 0 ? Math.round(totalProgress / projects.length) : 0,
    statusDist
  }
})

// 纵向项目统计 - 使用纵向专用状态
const verticalOverview = computed(() => {
  const projects = overview.value.projects.filter(p => p.project_source === 'vertical')
  const statusDist = {}
  verticalStatusList.forEach(status => {
    statusDist[status] = projects.filter(p => p.status === status).length
  })
  return {
    total: projects.length,
    statusDist
  }
})

// 自研项目统计 - 只有进行中和已完成两个状态
const selfDevelopedOverview = computed(() => {
  const projects = overview.value.projects.filter(p => p.project_source === 'self_developed')
  const inProgress = projects.filter(p => p.status === 'project_implementation').length
  const completed = projects.filter(p => p.status === 'project_acceptance').length
  const totalProgress = projects.reduce((sum, p) => sum + (p.progress || 0), 0)
  return {
    total: projects.length,
    avgProgress: projects.length > 0 ? Math.round(totalProgress / projects.length) : 0,
    inProgress,
    completed
  }
})


// 状态分布图表配置
const statusChartOption = computed(() => {
  const statusMap = {
    'initial_contact': '初步接触',
    'proposal_submitted': '提交方案',
    'quotation_submitted': '提交报价',
    'user_confirmation': '用户确认',
    'contract_signed': '合同签订',
    'project_implementation': '项目实施',
    'project_acceptance': '项目验收',
    'warranty_period': '维保期内',
    'post_warranty': '维保期外',
    'no_follow_up': '不再跟进'
  }
  
  const colorMap = {
    'initial_contact': '#8E8E93',        // 浅灰色 - 初步接触
    'proposal_submitted': '#5AC8FA',     // 天蓝色 - 提交方案
    'quotation_submitted': '#007AFF',    // 蓝色 - 提交报价
    'user_confirmation': '#AF52DE',      // 紫色 - 用户确认
    'contract_signed': '#FF9500',        // 橙色 - 合同签订
    'project_implementation': '#34C759', // 绿色 - 项目实施
    'project_acceptance': '#32D74B',     // 深绿色 - 项目验收
    'warranty_period': '#FFD60A',        // 黄色 - 维保期内
    'post_warranty': '#A2845E',          // 棕色 - 维保期外
    'no_follow_up': '#FF3B30'            // 红色 - 不再跟进
  }
  
  const data = orderedStatusList
    .map(status => ({
      status,
      count: overview.value.summary.status_distribution[status] || 0
    }))
    .filter(item => item.count > 0)
    .map(({ status, count }) => ({
      name: statusMap[status] || status,
      value: count,
      itemStyle: { color: colorMap[status] }
    }))

  return {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      bottom: '10px',
      left: 'center',
      itemGap: 6,
      itemWidth: 10,
      itemHeight: 10,
      textStyle: {
        fontSize: 10,
        color: '#666'
      },
      type: 'scroll',
      pageIconColor: '#666',
      pageIconInactiveColor: '#ccc',
      pageTextStyle: {
        color: '#666',
        fontSize: 9
      }
    },
    series: [
      {
        name: '项目状态',
        type: 'pie',
        radius: ['40%', '65%'],
        center: ['50%', '40%'],
        avoidLabelOverlap: false,
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: '16',
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: false
        },
        data
      }
    ]
  }
})

// 进度分布图表配置 - 水平条形图
const progressChartOption = computed(() => {
  const projects = overview.value.projects || []
  const ranges = [
    { name: '0-20%', label: '起步阶段', min: 0, max: 20, color: '#ff3b30' },
    { name: '21-40%', label: '初期进展', min: 21, max: 40, color: '#ff9500' },
    { name: '41-60%', label: '推进中', min: 41, max: 60, color: '#ffcc02' },
    { name: '61-80%', label: '接近完成', min: 61, max: 80, color: '#007aff' },
    { name: '81-100%', label: '即将交付', min: 81, max: 100, color: '#34c759' }
  ]
  
  const data = ranges.map(range => ({
    name: range.name,
    label: range.label,
    value: projects.filter(p => 
      p.progress >= range.min && p.progress <= range.max
    ).length,
    itemStyle: { 
      color: range.color,
      borderRadius: [0, 4, 4, 0]
    }
  }))

  return {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      formatter: (params) => {
        const item = params[0]
        return `<div style="padding: 4px 0;">
          <div style="font-weight: 600; margin-bottom: 4px;">${item.name}</div>
          <div style="color: #666;">${item.data.label}</div>
          <div style="margin-top: 4px; font-size: 14px; font-weight: 700; color: ${item.color};">
            ${item.value} 个项目
          </div>
        </div>`
      }
    },
    grid: {
      left: '12%',
      right: '12%',
      top: '8%',
      bottom: '8%',
      containLabel: true
    },
    xAxis: {
      type: 'value',
      axisLabel: {
        formatter: '{value}',
        fontSize: 12,
        color: '#666'
      },
      splitLine: {
        lineStyle: {
          color: '#f0f0f0'
        }
      }
    },
    yAxis: {
      type: 'category',
      data: data.map(d => d.name).reverse(),
      axisLabel: {
        fontSize: 13,
        fontWeight: 600,
        color: '#333'
      },
      axisLine: {
        show: false
      },
      axisTick: {
        show: false
      }
    },
    series: [
      {
        name: '项目数量',
        type: 'bar',
        barWidth: '45%',
        data: data.reverse(),
        label: {
          show: true,
          position: 'right',
          formatter: '{c}',
          fontSize: 13,
          fontWeight: 700,
          color: '#333'
        },
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.2)'
          }
        }
      }
    ]
  }
})

// 方法
const getStatusText = (status) => projectStore.getStatusText(status)

// 获取项目类型文本
const getSourceText = (source) => {
  const sourceMap = {
    'horizontal': '横向',
    'vertical': '纵向',
    'self_developed': '自研'
  }
  return sourceMap[source] || '横向'
}

const goToProject = (id) => {
  router.push(`/projects/${id}`)
}

const showUpdateProgress = (project) => {
  selectedProject.value = project
  updateDialogVisible.value = true
}

const handleUpdateSuccess = () => {
  ElMessage.success('进度更新成功')
  // 刷新数据
  loadData()
}

const loadData = async () => {
  try {
    await Promise.all([
      projectStore.fetchDepartmentOverview(),
      fetchModulesData()
    ])
  } catch (error) {
    ElMessage.error('加载数据失败')
  }
}

// 模块相关方法
const fetchModulesData = async () => {
  try {
    modulesLoading.value = true
    const response = await moduleApi.getModulesOverview()
    if (response.success) {
      // 定义项目来源的优先级顺序：横向 → 纵向 → 自研
      const sourceOrder = {
        'horizontal': 1,
        'vertical': 2,
        'self_developed': 3
      }
      
      // 先按项目来源排序，再按状态排序
      const sortedProjects = response.data.sort((a, b) => {
        // 获取项目来源（默认为横向）
        const aSource = a.project_source || 'horizontal'
        const bSource = b.project_source || 'horizontal'
        
        // 先按项目来源排序
        const sourceCompare = (sourceOrder[aSource] || 99) - (sourceOrder[bSource] || 99)
        if (sourceCompare !== 0) return sourceCompare
        
        // 相同来源的项目，按状态排序
        const aIndex = orderedStatusList.indexOf(a.status)
        const bIndex = orderedStatusList.indexOf(b.status)
        
        // 如果状态不在有序列表中，放到最后
        if (aIndex === -1 && bIndex === -1) return 0
        if (aIndex === -1) return 1
        if (bIndex === -1) return -1
        
        return aIndex - bIndex
      })
      
      projectsWithModules.value = sortedProjects
    }
  } catch (error) {
    console.error('获取模块概览失败:', error)
    ElMessage.error('获取模块数据失败')
  } finally {
    modulesLoading.value = false
  }
}

const refreshModulesData = async () => {
  await fetchModulesData()
  ElMessage.success('数据已刷新')
}

// 导出为Excel
const exportToExcel = async () => {
  try {
    const loading = ElLoading.service({
      lock: true,
      text: '正在生成Excel文件...',
      background: 'rgba(0, 0, 0, 0.7)'
    })
    
    const { utils, writeFile } = await import('xlsx')
    
    // 准备导出数据
  const exportData = []
  
  // 添加汇总信息
  exportData.push({
    '项目名称': '=== 项目汇总信息 ===',
    '状态': '',
    '合作方': '',
    '合同金额': '',
    '到账金额': '',
    '进度': '',
    '负责人': '',
    '模块名称': '',
    '模块状态': '',
    '模块进度': '',
    '模块负责人': '',
    '负责人职位': '',
    '上次工作': '',
    '最新工作': '',
    '更新时间': ''
  })
  
  exportData.push({
    '项目名称': `总项目数: ${overview.value.summary.total_projects}`,
    '状态': `进行中: ${overview.value.summary.active_projects}`,
    '合作方': '',
    '合同金额': '',
    '到账金额': '',
    '进度': `平均进度: ${overview.value.summary.avg_progress}%`,
    '负责人': `已完成: ${completedCount.value}`,
    '模块名称': '',
    '模块状态': '',
    '模块进度': '',
    '模块负责人': '',
    '负责人职位': '',
    '上次工作': '',
    '最新工作': '',
    '更新时间': ''
  })
  
  exportData.push({}) // 空行分隔
  
  // 添加项目详细数据
  projectsWithModules.value.forEach(project => {
    // 纵向项目不显示进度
    const progressDisplay = project.project_source === 'vertical' ? '-' : `${project.progress}%`
    
    // 项目基本信息
    exportData.push({
      '项目名称': project.name,
      '状态': getStatusText(project.status),
      '合作方': project.partner || '-',
      '合同金额': project.contract_amount != null ? `¥${formatAmount(project.contract_amount)}` : '-',
      '到账金额': project.received_amount != null ? `¥${formatAmount(project.received_amount)}` : '-',
      '进度': progressDisplay,
      '负责人': project.leader?.name || '未指定',
      '模块名称': '=== 项目模块 ===',
      '模块状态': '',
      '模块进度': '',
      '模块负责人': '',
      '负责人职位': '',
      '上次工作': '',
      '最新工作': '',
      '更新时间': formatDate(project.updated_at)
    })
    
    // 项目模块信息
    project.modules.forEach(module => {
      // 获取最近2次工作内容
      const recentWorks = module.recent_works || []
      
      // 格式化最新工作（第1条）
      let latestWork = '暂无工作记录'
      if (recentWorks.length > 0) {
        const work = recentWorks[0]
        const weekLabel = work.week_label ? `[${work.week_label}]` : ''
        const content = work.work_content || ''
        const achievements = work.achievements ? `\n成果: ${work.achievements}` : ''
        latestWork = `${weekLabel} ${content}${achievements}`
      }
      
      // 格式化上次工作（第2条）
      let previousWork = ''
      if (recentWorks.length > 1) {
        const work = recentWorks[1]
        const weekLabel = work.week_label ? `[${work.week_label}]` : ''
        const content = work.work_content || ''
        const achievements = work.achievements ? `\n成果: ${work.achievements}` : ''
        previousWork = `${weekLabel} ${content}${achievements}`
      }
      
      exportData.push({
        '项目名称': '',
        '状态': '',
        '合作方': '',
        '合同金额': '',
        '到账金额': '',
        '进度': '',
        '负责人': '',
        '模块名称': module.name,
        '模块状态': getModuleStatusText(module.status),
        '模块进度': `${module.progress}%`,
        '模块负责人': module.assigned_to?.name || '未分配',
        '负责人职位': module.assigned_to?.position || '',
        '上次工作': previousWork,
        '最新工作': latestWork,
        '更新时间': recentWorks[0]?.updated_at ? formatDate(recentWorks[0].updated_at) : ''
      })
    })
    
    exportData.push({}) // 项目间空行分隔
  })
  
  // 创建工作表
  const ws = utils.json_to_sheet(exportData)
  
  // 设置列宽
  ws['!cols'] = [
    { width: 20 }, // 项目名称
    { width: 10 }, // 状态
    { width: 10 }, // 进度
    { width: 15 }, // 负责人
    { width: 20 }, // 模块名称
    { width: 12 }, // 模块状态
    { width: 12 }, // 模块进度
    { width: 15 }, // 模块负责人
    { width: 15 }, // 负责人职位
    { width: 35 }, // 上次工作
    { width: 35 }, // 最新工作
    { width: 20 }  // 更新时间
  ]
  
  // 创建工作簿
  const wb = utils.book_new()
  utils.book_append_sheet(wb, ws, '项目模块进度一览')
  
  // 生成文件名
  const timestamp = new Date().toISOString().slice(0, 19).replace(/[:-]/g, '')
  const filename = `项目模块进度一览表_${timestamp}.xlsx`
  
  // 导出文件
  writeFile(wb, filename)
  
  loading.close()
  ElMessage.success('Excel文件导出成功！')
  } catch (error) {
    console.error('Excel导出失败:', error)
    ElMessage.error('导出失败，请重试')
  }
}

// 删除了 PDF、图片、JSON 导出功能，只保留 Excel 导出

const handleExpandChange = (row, expandedRows) => {
  // 处理表格展开状态
}

const goToProjectDetail = (id) => {
  router.push(`/projects/${id}`)
}

const showUpdateModuleProgress = (module, projectName) => {
  selectedModule.value = module
  selectedProjectName.value = projectName
  updateModuleProgressDialogVisible.value = true
}

const showModuleWorkHistory = (module, projectName) => {
  selectedModule.value = module
  selectedProjectName.value = projectName
  moduleHistoryDialogVisible.value = true
}

const handleModuleUpdateSuccess = () => {
  ElMessage.success('模块进度更新成功')
  fetchModulesData()
}

// 权限检查方法
const canUpdateModule = (module, project) => {
  // 直接使用传入的project参数，它已经包含了完整的成员信息
  return authStore.canUpdateModule(module, project)
}

// 获取用户在项目中的角色
const getUserProjectRole = (project) => {
  if (!authStore.user || !project.members) return null
  
  const membership = project.members.find(m => m.user_id === authStore.user.id)
  if (!membership) return null
  
  return membership.role === 'leader' ? '负责人' : '成员'
}

// 获取项目角色标签类型
const getProjectRoleTagType = (project) => {
  const role = getUserProjectRole(project)
  if (role === '负责人') return 'danger'  // 红色标签
  if (role === '成员') return 'info'      // 蓝色标签
  return ''
}

// 工具方法
const formatDate = (dateString) => {
  if (!dateString) return '未设置'
  return new Date(dateString).toLocaleDateString('zh-CN')
}

// 格式化金额
const formatAmount = (amount) => {
  if (amount == null) return '-'
  return Number(amount).toLocaleString('zh-CN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })
}

const getModuleStatusText = (status) => {
  const statusMap = {
    'not_started': '待开始',
    'in_progress': '进行中', 
    'completed': '已完成',
    'paused': '暂停',
    // 兼容大写格式
    'NOT_STARTED': '待开始',
    'IN_PROGRESS': '进行中',
    'COMPLETED': '已完成',
    'PAUSED': '暂停'
  }
  return statusMap[status] || status
}

const getPriorityText = (priority) => {
  const priorityMap = {
    'low': '低',
    'medium': '中',
    'high': '高',
    'urgent': '紧急'
  }
  return priorityMap[priority] || priority
}

const getProgressClass = (progress) => {
  if (progress >= 80) return 'success'
  if (progress < 40) return 'warning'
  return ''
}

// 状态相关方法
const getStatusColor = (status) => {
  const colorMap = {
    'initial_contact': '#8E8E93',        // 浅灰色 - 初步接触
    'proposal_submitted': '#5AC8FA',     // 天蓝色 - 提交方案
    'quotation_submitted': '#007AFF',    // 蓝色 - 提交报价
    'user_confirmation': '#AF52DE',      // 紫色 - 用户确认
    'contract_signed': '#FF9500',        // 橙色 - 合同签订
    'project_implementation': '#34C759', // 绿色 - 项目实施
    'project_acceptance': '#32D74B',     // 深绿色 - 项目验收
    'warranty_period': '#FFD60A',        // 黄色 - 维保期内
    'post_warranty': '#A2845E',          // 棕色 - 维保期外
    'no_follow_up': '#FF3B30'            // 红色 - 不再跟进
  }
  return colorMap[status] || '#8e8e93'
}

const getStatusShortText = (status) => {
  const shortTextMap = {
    // 横向项目状态
    'initial_contact': '初步接触',
    'proposal_submitted': '提交方案',
    'quotation_submitted': '提交报价',
    'user_confirmation': '用户确认',
    'contract_signed': '合同签订',
    'project_implementation': '项目实施',
    'project_acceptance': '项目验收',
    'warranty_period': '维保期内',
    'post_warranty': '维保期外',
    'no_follow_up': '不再跟进',
    // 纵向项目专用状态
    'vertical_declaration': '申报阶段',
    'vertical_review': '审核阶段',
    'vertical_approved': '审核通过',
    'vertical_rejected': '审核未通过'
  }
  return shortTextMap[status] || status
}

// 点击状态跳转到项目列表
const navigateToProjectsByStatus = (status) => {
  const count = overview.value.summary.status_distribution[status] || 0
  if (count === 0) return
  
  // 跳转到项目列表页面，并传递状态过滤参数
  router.push({
    path: '/projects',
    query: { status: status }
  })
}

// 按项目类型和状态跳转到项目列表
const navigateToProjectsBySource = (source, status) => {
  // 跳转到项目列表页面，并传递类型和状态过滤参数
  router.push({
    path: '/projects',
    query: { 
      project_source: source,
      status: status 
    }
  })
}

// 显示状态提示框
const showStatusTooltip = (status, count, event) => {
  const statusText = getStatusShortText(status)
  const projects = overview.value.projects.filter(p => p.status === status)
  
  let content = `<div class="status-tooltip">
    <div class="tooltip-header">
      <span class="tooltip-title">${statusText}</span>
      <span class="tooltip-count">${count} 个项目</span>
    </div>`
  
  if (projects.length > 0) {
    content += '<div class="tooltip-projects">'
    projects.slice(0, 3).forEach(project => {
      content += `<div class="tooltip-project">
        <span class="project-name">${project.name}</span>
        <span class="project-progress">${project.progress}%</span>
      </div>`
    })
    if (projects.length > 3) {
      content += `<div class="tooltip-more">还有 ${projects.length - 3} 个项目...</div>`
    }
    content += '</div>'
  }
  
  content += '</div>'
  
  statusTooltipContent.value = content
  statusTooltipPosition.value = {
    x: event.clientX,
    y: event.clientY
  }
  statusTooltipVisible.value = true
}

// 隐藏状态提示框
const hideStatusTooltip = () => {
  statusTooltipVisible.value = false
}

// 获取状态健康度类别（用于颜色区分）
const getStatusHealth = (status) => {
  // 积极进展状态
  const positive = ['contract_signed', 'project_implementation', 'project_acceptance', 'warranty_period']
  // 等待/初期状态
  const neutral = ['initial_contact', 'proposal_submitted', 'quotation_submitted', 'user_confirmation']
  // 消极/结束状态
  const negative = ['no_follow_up', 'post_warranty']
  
  if (positive.includes(status)) return 'positive'
  if (neutral.includes(status)) return 'neutral'
  if (negative.includes(status)) return 'negative'
  return 'neutral'
}

// 生命周期
onMounted(() => {
  loadData()
})
</script>

<style scoped lang="scss">
.dashboard {
  max-width: 1200px;
  margin: 0 auto;
}

// 顶部概览区域
.overview-section {
  display: flex;
  gap: 24px;
  margin-bottom: 32px;
  align-items: stretch;
}

// 三卡片横向布局 - 从左到右：横向(50%) 纵向(25%) 自研(25%)
.overview-section.three-cards {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr; // 横向(50%) 纵向(25%) 自研(25%)
  grid-template-areas: "horizontal vertical self";
  gap: 20px;
  align-items: stretch; // 高度拉伸对齐
  
  // 确保每个卡片宽度完全一致
  > .project-source-card {
    min-width: 0; // 防止内容撑开
    width: 100%; // 填满grid单元格
  }
  
  // 指定卡片位置
  > .horizontal-card {
    grid-area: horizontal;
  }
  
  > .vertical-card {
    grid-area: vertical;
  }
  
  > .self-card {
    grid-area: self;
  }
}

// 左侧统计卡片容器 - 单列布局
.stats-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
  flex: 0 0 480px;
}

.stat-card {
  padding: 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.stat-content {
  flex: 1;
}

.stat-number {
  font-size: 32px;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: var(--text-secondary);
  font-weight: 500;
}

.stat-icon {
  font-size: 48px;
  color: var(--apple-blue);
  opacity: 0.8;
  
  &.in-progress {
    color: var(--apple-blue);
  }
  
  &.success {
    color: var(--apple-green);
  }
  
  &.completed {
    color: var(--apple-green);
  }
}

// 右侧进度图表卡片
// ========== 现代化项目卡片样式 ==========
.project-source-card {
  padding: 0;
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  box-sizing: border-box; // 确保padding不影响总宽度
  
  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15) !important;
  }
}

// 主题色定义 - 精修后的配色
.horizontal-card {
  --theme-color: #4B7BF5;
  --theme-light: rgba(75, 123, 245, 0.1);
  --theme-lighter: rgba(75, 123, 245, 0.05);
}

.vertical-card {
  --theme-color: #F59D52;
  --theme-light: rgba(245, 157, 82, 0.1);
  --theme-lighter: rgba(245, 157, 82, 0.05);
}

.self-card {
  --theme-color: #5FD068;
  --theme-light: rgba(95, 208, 104, 0.1);
  --theme-lighter: rgba(95, 208, 104, 0.05);
}

// 顶部装饰条
.card-accent-bar {
  height: 4px;
  width: 100%;
}

.horizontal-accent {
  background: linear-gradient(90deg, #4B7BF5 0%, #6B95F7 100%);
}

.vertical-accent {
  background: linear-gradient(90deg, #F59D52 0%, #F8B176 100%);
}

.self-accent {
  background: linear-gradient(90deg, #5FD068 0%, #7FDB86 100%);
}

// ========== 统一的上下两部分结构 ==========

// 上半部分：信息区
.card-info-section {
  padding: 24px 24px 20px;
  background: white;
  text-align: center;
  width: 100%; // 确保宽度一致
  box-sizing: border-box; // padding不影响总宽度
}

.card-title-large {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 16px 0;
  letter-spacing: 0.5px;
}

.card-number-display {
  font-size: 64px;
  font-weight: 900;
  color: var(--theme-color);
  line-height: 1;
  letter-spacing: -2px;
  margin-bottom: 20px;
}

.card-progress-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.progress-label-small {
  font-size: 12px;
  color: var(--text-secondary);
  font-weight: 500;
}

.progress-value-small {
  font-size: 16px;
  font-weight: 700;
}

.horizontal-color {
  color: #4B7BF5;
}

.vertical-color {
  color: #F59D52;
}

.self-color {
  color: #5FD068;
}

.progress-bar-slim {
  height: 8px;
  background: rgba(0, 0, 0, 0.04);
  border-radius: 4px;
  overflow: hidden;
  box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.05);
}

.progress-fill-slim {
  height: 100%;
  border-radius: 4px;
  transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12);
}

.horizontal-fill {
  background: linear-gradient(90deg, #4B7BF5 0%, #6B95F7 100%);
}

.vertical-fill {
  background: linear-gradient(90deg, #F59D52 0%, #F8B176 100%);
}

.self-fill {
  background: linear-gradient(90deg, #5FD068 0%, #7FDB86 100%);
}

// 下半部分：状态区
.card-status-section {
  background: var(--theme-lighter);
  padding: 16px 20px 20px;
  height: 200px; // 固定高度，让所有卡片的状态区域严格一致
  width: 100%; // 确保宽度一致
  box-sizing: border-box; // padding不影响总宽度
  display: flex;
  flex-direction: column;
  justify-content: flex-start; // 从上开始排列，不居中
}

// 横向项目状态网格 - 5x2布局，更好地利用宽度
.status-grid-uniform {
  display: grid;
  grid-template-columns: repeat(5, 1fr); // 每行5个，共2行
  gap: 8px; // 增加间距，因为横向卡片更宽了
}

// 纵向项目专用网格布局（2x2）- 与横向项目间距保持一致
.status-grid-vertical {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px; // 与横向项目保持一致
  height: 100%; // 填满容器
  align-content: start; // 从顶部开始
}

// 横向项目状态项 - 优化字体大小，更易阅读
.status-item-uniform {
  padding: 12px 6px; // 增加padding，让内容更舒展
  background: white;
  border-radius: 6px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  border: 2px solid transparent;
  display: flex;
  flex-direction: column;
  justify-content: center;
  min-height: 70px; // 保证高度一致
  
  &.active {
    box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.06), 0 1px 3px rgba(0, 0, 0, 0.04);
    
    .status-count-uniform {
      color: var(--theme-color);
    }
    
    &:hover {
      border-color: var(--theme-color);
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
  }
  
  &:not(.active) {
    background: rgba(255, 255, 255, 0.4);
    opacity: 0.45;
    cursor: not-allowed;
    
    &:hover {
      transform: none;
    }
    
    .status-count-uniform {
      color: #C7C7CC !important;
    }
  }
}

// 纵向项目状态项样式（2x2布局）- 与横向项目方框大小完全一致
.status-item-vertical {
  padding: 12px 6px; // 与横向项目保持一致
  background: white;
  border-radius: 6px; // 与横向项目保持一致
  text-align: center;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  border: 2px solid transparent;
  display: flex;
  flex-direction: column;
  justify-content: center;
  min-height: 70px; // 与横向项目保持一致
  
  &.active {
    box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.06), 0 1px 3px rgba(0, 0, 0, 0.04);
    
    .status-count-uniform {
      color: var(--theme-color);
    }
    
    &:hover {
      border-color: var(--theme-color);
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
  }
  
  &:not(.active) {
    background: rgba(255, 255, 255, 0.4);
    opacity: 0.45;
    cursor: not-allowed;
    
    &:hover {
      transform: none;
    }
    
    .status-count-uniform {
      color: #C7C7CC !important;
    }
  }
}

// 统一的状态数字和标签样式 - 适用于所有卡片
.status-count-uniform {
  font-size: 22px; // 统一增大到22px，更清晰易读
  font-weight: 800;
  margin-bottom: 4px;
  line-height: 1;
}

.status-label-uniform {
  font-size: 12px; // 统一增大到12px，更清晰易读
  color: var(--text-secondary);
  font-weight: 600;
  line-height: 1.2;
}

// 自研项目特殊布局（一列两行）- 与横向项目间距保持一致
.self-status-grid-two {
  display: flex;
  flex-direction: column; // 垂直排列
  gap: 8px; // 与横向项目保持一致
  justify-content: flex-start; // 从顶部开始
  align-items: stretch; // 宽度拉伸
  height: 100%; // 填满容器
}

.self-status-item-large {
  flex: 1; // 垂直方向平分空间
  padding: 12px 6px; // 与横向项目保持一致的padding
  background: white; // 白色方框背景
  border-radius: 6px; // 与横向项目保持一致的圆角
  text-align: center;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  border: 2px solid transparent;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  min-height: 70px; // 与横向项目状态项高度保持一致
  
  &.active {
    box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.06), 0 1px 3px rgba(0, 0, 0, 0.04);
    
    .self-status-count {
      color: var(--theme-color);
    }
    
    &:hover {
      border-color: var(--theme-color);
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
  }
  
  &:not(.active) {
    background: rgba(255, 255, 255, 0.4);
    opacity: 0.45;
    cursor: not-allowed;
    
    &:hover {
      transform: none;
    }
    
    .self-status-count {
      color: #C7C7CC !important;
    }
  }
}

.self-status-count {
  font-size: 22px; // 与其他卡片统一的字体大小
  font-weight: 800;
  line-height: 1;
  margin-bottom: 4px;
}

.self-status-label {
  font-size: 12px; // 与其他卡片统一的字体大小
  color: var(--text-secondary);
  font-weight: 600;
  line-height: 1.2;
}

.progress-chart-card {
  flex: 1;
  padding: 20px;
  display: block !important;
}

.progress-chart-header {
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-color);
}

.chart-title-section {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.chart-main-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
  line-height: 1.2;
}

.chart-sub-title {
  font-size: 12px;
  color: var(--text-secondary);
  margin: 0;
  font-weight: 500;
}

.progress-chart-content {
  width: 100%;
  height: 240px;
}

.progress-chart {
  width: 100%;
  height: 100%;
}

.recent-section {
  padding: 24px;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.section-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

/* 导出按钮样式优化 - Apple风格纯色 */
.section-actions .el-dropdown .el-button {
  background: var(--apple-blue);
  border: none;
  color: white;
  font-weight: 500;
  transition: all 0.2s ease;
  box-shadow: 0 2px 8px rgba(0, 122, 255, 0.25);
}

.section-actions .el-dropdown .el-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 122, 255, 0.35);
  background: #0051d5;
}

.section-actions .el-dropdown .el-button:active {
  transform: translateY(0);
  background: #004ec4;
}

/* 下拉菜单项样式 */
:deep(.el-dropdown-menu__item) {
  padding: 8px 16px;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s ease;
}

:deep(.el-dropdown-menu__item:hover) {
  background-color: #f8faff;
  color: #667eea;
}

:deep(.el-dropdown-menu__item .el-icon) {
  font-size: 16px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.project-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.project-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  background: var(--bg-secondary);
  border-radius: var(--border-radius-small);
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    background: var(--apple-gray-light);
    transform: translateX(4px);
  }
}

.project-info {
  flex: 1;
}

.project-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.project-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.project-meta {
  display: flex;
  align-items: center;
  gap: 8px;
}

.project-progress {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.progress-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 14px;
}

.progress-text {
  color: var(--text-primary);
  font-weight: 500;
}

.project-leaders {
  color: var(--text-secondary);
}

.project-actions {
  margin-left: 16px;
}

// 响应式设计
@media (max-width: 1200px) {
  .overview-section {
    flex-direction: column;
    align-items: stretch;
  }
  
  .stats-container {
    flex: none;
    width: 100%;
  }
  
  .progress-chart-card {
    width: 100%;
  }
  
  .progress-chart {
    min-height: 220px;
    max-height: 260px;
  }
}

@media (max-width: 768px) {
  .stats-container {
    grid-template-columns: 1fr;
    gap: 12px;
  }
  
  .charts-container {
    padding: 16px;
  }
  
  .project-item {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }
  
  .project-actions {
    margin-left: 0;
    display: flex;
    justify-content: flex-end;
  }
}

// 模块相关样式
.modules-overview {
  padding: 24px;
}

.loading-state, .empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  color: var(--text-secondary);
}

.empty-icon {
  font-size: 48px;
  color: var(--border-color);
  margin-bottom: 16px;
}

.modules-table-container {
  overflow: auto;
}

.expanded-modules {
  padding: 16px 24px;
  background-color: var(--bg-secondary);
}

.no-modules {
  text-align: center;
  color: var(--text-secondary);
  padding: 20px;
}

.modules-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.module-item {
  background: var(--bg-primary);
  border-radius: var(--border-radius);
  padding: 20px;
  border: 1px solid var(--border-color);
}

.module-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.module-name {
  font-weight: 600;
  font-size: 16px;
  color: var(--text-primary);
}

.module-status {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  
  &.NOT_STARTED {
    background-color: #f5f5f7;
    color: #8e8e93;
  }
  
  &.IN_PROGRESS {
    background-color: #e3f2fd;
    color: #1976d2;
  }
  
  &.COMPLETED {
    background-color: #e8f5e8;
    color: #2e7d32;
  }
  
  &.PAUSED {
    background-color: #fff3e0;
    color: #f57c00;
  }
}

.module-assignees {
  margin-bottom: 12px;
}

.assignees-label {
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 4px;
}

.assignees-list {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.assignee-tag {
  padding: 2px 8px;
  background-color: var(--apple-blue);
  color: white;
  border-radius: 12px;
  font-size: 12px;
}

.no-assignee {
  color: var(--text-secondary);
  font-size: 12px;
}

.module-progress {
  margin-bottom: 12px;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
  font-size: 12px;
}

.progress-text {
  font-weight: 600;
  color: var(--text-primary);
}

.priority {
  color: var(--text-secondary);
}

.progress-bar {
  height: 6px;
  background-color: var(--border-color);
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background-color: var(--apple-blue);
  transition: width 0.3s ease;
  
  &.success {
    background-color: var(--apple-green);
  }
  
  &.warning {
    background-color: var(--apple-orange);
  }
}

.module-work {
  background-color: var(--bg-secondary);
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 12px;
}

.work-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  font-size: 12px;
}

.work-period {
  font-weight: 600;
  color: var(--text-primary);
}

.work-author {
  color: var(--text-secondary);
}

.work-content {
  font-size: 13px;
}

.work-description {
  color: var(--text-primary);
  margin-bottom: 4px;
}

.work-achievements {
  color: var(--text-secondary);
}

.no-work {
  text-align: center;
  color: var(--text-secondary);
  font-size: 12px;
  padding: 12px;
  background-color: var(--bg-secondary);
  border-radius: 8px;
  margin-bottom: 12px;
}

.module-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12px;
  border-top: 1px solid var(--border-color);
}

.update-time {
  font-size: 11px;
  color: var(--text-secondary);
}

.module-actions {
  display: flex;
  gap: 8px;
}

.module-actions .el-button {
  font-weight: 500;
  border: 1px solid;
  transition: all 0.2s ease;
}

.module-actions .el-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.module-actions .el-button--success.is-plain {
  color: #67c23a;
  border-color: #67c23a;
  background-color: #f0f9ff;
}

.module-actions .el-button--success.is-plain:hover {
  color: #ffffff;
  background-color: #67c23a;
  border-color: #67c23a;
}

.module-actions .el-button--primary.is-plain {
  color: #409eff;
  border-color: #409eff;
  background-color: #ecf5ff;
}

.module-actions .el-button--primary.is-plain:hover {
  color: #ffffff;
  background-color: #409eff;
  border-color: #409eff;
}

.project-name {
  display: flex;
  align-items: center;
  gap: 12px;
}

.name {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.role-tag {
  margin-left: 4px;
}

// 项目状态标签 - 使用与卡片一致的颜色
.status-badge {
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
  white-space: nowrap;
  
  // 初步接触 - 浅灰色
  &.initial_contact {
    background: rgba(142, 142, 147, 0.15);
    color: #8E8E93;
  }
  
  // 提交方案 - 天蓝色
  &.proposal_submitted {
    background: rgba(90, 200, 250, 0.15);
    color: #5AC8FA;
  }
  
  // 提交报价 - 蓝色
  &.quotation_submitted {
    background: rgba(0, 122, 255, 0.15);
    color: #007AFF;
  }
  
  // 用户确认 - 紫色
  &.user_confirmation {
    background: rgba(175, 82, 222, 0.15);
    color: #AF52DE;
  }
  
  // 合同签订 - 橙色
  &.contract_signed {
    background: rgba(255, 149, 0, 0.15);
    color: #FF9500;
  }
  
  // 项目实施 - 绿色
  &.project_implementation {
    background: rgba(52, 199, 89, 0.15);
    color: #34C759;
  }
  
  // 项目验收 - 深绿色
  &.project_acceptance {
    background: rgba(50, 215, 75, 0.15);
    color: #32D74B;
  }
  
  // 维保期内 - 黄色
  &.warranty_period {
    background: rgba(255, 214, 10, 0.15);
    color: #FFD60A;
  }
  
  // 维保期外 - 棕色
  &.post_warranty {
    background: rgba(162, 132, 94, 0.15);
    color: #A2845E;
  }
  
  // 不再跟进 - 红色
  &.no_follow_up {
    background: rgba(255, 59, 48, 0.15);
    color: #FF3B30;
  }
}

// 项目类型标签
.source-tag {
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  
  &.source-horizontal {
    background: #4B7BF5; // 与横向项目卡片一致
    color: white;
  }
  
  &.source-vertical {
    background: #F59D52; // 与纵向项目卡片一致
    color: white;
  }
  
  &.source-self_developed {
    background: #5FD068; // 与自研项目卡片一致
    color: white;
  }
}

// 合作方文本
.partner-text {
  font-size: 13px;
  color: var(--text-primary);
  font-weight: 500;
}

.no-partner {
  color: var(--apple-gray-5);
  font-size: 13px;
}

.amount-text {
  font-size: 13px;
  color: var(--text-primary);
  font-weight: 600;
  font-family: 'SF Mono', 'Monaco', 'Courier New', monospace;
}

.no-amount {
  color: var(--apple-gray-5);
  font-size: 13px;
}

.progress-cell {
  display: flex;
  flex-direction: column;
  gap: 4px;
  align-items: center;
}

.progress-text {
  font-size: 12px;
  font-weight: 500;
  color: var(--text-primary);
}


.members-avatars {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}

.project-leader {
  display: flex;
  align-items: center;
  justify-content: center;
}

.no-leader {
  color: var(--apple-gray-6);
  font-size: 12px;
}

.member-avatar {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background-color: var(--apple-blue);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  font-weight: 600;
}

.member-more {
  font-size: 10px;
  color: var(--text-secondary);
  font-weight: 500;
}

// Element Plus 表格样式覆盖
:deep(.el-table) {
  border-radius: var(--border-radius-small);
  overflow: hidden;
  font-size: 13px;
}

:deep(.el-table th) {
  background-color: var(--bg-secondary);
  color: var(--text-primary);
  font-weight: 600;
}

:deep(.el-table td) {
  border-bottom: 1px solid var(--border-color);
}

:deep(.el-table--enable-row-hover .el-table__body tr:hover > td) {
  background-color: var(--bg-hover);
}

// 表格中的按钮样式
.el-table .el-button.is-plain {
  font-weight: 500;
  border: 1px solid;
  transition: all 0.2s ease;
}

.el-table .el-button.is-plain:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.el-table .el-button--primary.is-plain {
  color: #409eff;
  border-color: #409eff;
  background-color: #ecf5ff;
}

.el-table .el-button--primary.is-plain:hover {
  color: #ffffff;
  background-color: #409eff;
  border-color: #409eff;
}

// 项目总数与状态分布合并卡片样式
.projects-overview-card {
  padding: 20px;
  display: block !important; // 覆盖父类的 flex 布局
}

.projects-overview-content {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.overview-header {
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-color);
}

// 集成的进度条样式
.integrated-progress {
  margin-top: 16px;
}

.progress-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.progress-label {
  font-size: 13px;
  color: var(--text-secondary);
  font-weight: 500;
}

.progress-value {
  font-size: 18px;
  font-weight: 700;
  color: var(--apple-blue);
}

.progress-bar-horizontal {
  height: 8px;
  background: var(--border-color);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 12px;
}

.progress-fill-horizontal {
  height: 100%;
  background: linear-gradient(90deg, var(--apple-blue) 0%, var(--apple-green) 100%);
  border-radius: 4px;
  transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  
  &::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.3) 50%, transparent 100%);
    animation: progress-shine 2s ease-in-out infinite;
  }
  
  &.success {
    background: linear-gradient(90deg, var(--apple-green) 0%, #2ecc71 100%);
  }
  
  &.warning {
    background: linear-gradient(90deg, var(--apple-orange) 0%, #e67e22 100%);
  }
}

@keyframes progress-shine {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

.progress-stats {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: var(--text-secondary);
  font-weight: 500;
}

.stat-icon-small {
  font-size: 14px;
  
  &.success {
    color: var(--apple-green);
  }
  
  &.in-progress {
    color: var(--apple-blue);
  }
}

.overview-main {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.total-projects {
  display: flex;
  flex-direction: column;
}

.total-number {
  font-size: 32px;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1;
  margin-bottom: 4px;
}

.total-label {
  font-size: 14px;
  color: var(--text-secondary);
  font-weight: 500;
}

.overview-icon {
  font-size: 48px;
  color: var(--apple-blue);
  opacity: 0.8;
}

.overview-subtitle {
  font-size: 12px;
  color: var(--text-secondary);
  font-weight: 500;
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 4px;
  flex: 1;
  width: 100%;
  box-sizing: border-box;
}

.status-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 8px 4px;
  border-radius: 6px;
  background: var(--bg-secondary);
  transition: all 0.3s ease;
  cursor: pointer;
  position: relative;
  width: 100%;
  box-sizing: border-box;
  min-height: 58px;
  border: 1px solid transparent;
  
  &:hover {
    background: var(--bg-hover);
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  }
  
  // 健康度颜色区分
  &.has-projects {
    &.status-health.positive {
      border-left: 3px solid var(--apple-green);
      
      &:hover {
        background: rgba(52, 199, 89, 0.08);
      }
    }
    
    &.status-health.neutral {
      border-left: 3px solid var(--apple-blue);
      
      &:hover {
        background: rgba(0, 122, 255, 0.08);
      }
    }
    
    &.status-health.negative {
      border-left: 3px solid var(--apple-red);
      
      &:hover {
        background: rgba(255, 59, 48, 0.08);
      }
    }
  }
  
  &:not(.has-projects) {
    opacity: 0.4;
    cursor: not-allowed;
    
    &:hover {
      transform: none;
      box-shadow: none;
      background: var(--bg-secondary);
    }
  }
}

.status-count {
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 4px;
  transition: color 0.3s ease;
}

.status-name {
  font-size: 10px;
  color: var(--text-secondary);
  text-align: center;
  line-height: 1.2;
  font-weight: 500;
}

// 状态提示框样式
.status-tooltip-wrapper {
  position: fixed;
  z-index: 9999;
  pointer-events: none;
  transform: translate(-50%, -100%);
  margin-top: -10px;
}

:deep(.status-tooltip) {
  background: rgba(0, 0, 0, 0.9);
  color: white;
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 12px;
  max-width: 280px;
  backdrop-filter: blur(10px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

:deep(.tooltip-header) {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

:deep(.tooltip-title) {
  font-weight: 600;
  font-size: 13px;
}

:deep(.tooltip-count) {
  font-size: 11px;
  opacity: 0.8;
}

:deep(.tooltip-projects) {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

:deep(.tooltip-project) {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 2px 0;
}

:deep(.project-name) {
  flex: 1;
  font-size: 14px;
  opacity: 0.9;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-right: 8px;
}

:deep(.project-progress) {
  font-size: 11px;
  font-weight: 500;
  color: #5ac8fa;
}

:deep(.tooltip-more) {
  font-size: 10px;
  opacity: 0.7;
  text-align: center;
  margin-top: 4px;
  padding-top: 4px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

// 响应式调整
@media (max-width: 1200px) {
  .stats-container {
    flex: 0 0 auto;
    width: 100%;
  }
  
  .total-number {
    font-size: 28px;
  }
  
  .overview-icon {
    font-size: 40px;
  }
  
  .status-grid {
    grid-template-columns: repeat(5, 1fr);
    gap: 3px;
  }
  
  .status-item {
    padding: 6px 2px;
    min-height: 54px;
  }
  
  .status-count {
    font-size: 16px;
  }
  
  .status-name {
    font-size: 9px;
  }
}

@media (max-width: 768px) {
  .overview-main {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .total-number {
    font-size: 24px;
  }
  
  .overview-icon {
    font-size: 32px;
    align-self: flex-end;
  }
  
  .status-grid {
    grid-template-columns: repeat(3, 1fr);
    gap: 3px;
  }
  
  .status-item {
    padding: 6px 2px;
    min-height: 50px;
  }
  
  .status-count {
    font-size: 14px;
  }
  
  .status-name {
    font-size: 8px;
  }
  
  .progress-value {
    font-size: 16px;
  }
}
</style>
