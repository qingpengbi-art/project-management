<template>
  <div class="main-layout">
    <!-- 侧边栏 -->
    <aside class="sidebar" :class="{ collapsed: sidebarCollapsed }">
      <div class="sidebar-header">
        <div class="logo">
          <img src="/images/logo.jpeg" alt="Logo" class="logo-icon" />
          <span v-show="!sidebarCollapsed" class="logo-text">科创部项目管理</span>
        </div>
        <el-button 
          text 
          @click="toggleSidebar"
          class="collapse-btn"
        >
          <el-icon><Expand v-if="sidebarCollapsed" /><Fold v-else /></el-icon>
        </el-button>
      </div>
      
      <nav class="sidebar-nav">
        <ul class="nav-list">
          <li 
            v-for="item in menuItems" 
            :key="item.name"
            class="nav-item"
            :class="{ active: $route.name === item.name }"
          >
            <router-link :to="{ name: item.name }" class="nav-link">
              <el-icon class="nav-icon">
                <component :is="item.meta.icon" />
              </el-icon>
              <span v-show="!sidebarCollapsed" class="nav-text">{{ item.meta.title }}</span>
            </router-link>
          </li>
        </ul>
      </nav>
    </aside>

    <!-- 主内容区域 -->
    <main class="main-content">
      <!-- 顶部导航 -->
      <header class="main-header">
        <div class="header-left">
          <h1 class="page-title">{{ currentPageTitle }}</h1>
        </div>
        <div class="header-right">
          <!-- 用户信息 -->
          <el-dropdown @command="handleUserCommand" class="user-dropdown">
            <div class="user-info">
              <div class="user-avatar">
                {{ authStore.userName.charAt(0) }}
              </div>
              <div class="user-details">
                <div class="user-name">{{ authStore.userName }}</div>
                <div class="user-role">{{ getRoleDisplayText(authStore.userRole) }}</div>
              </div>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </header>

      <!-- 页面内容 -->
      <div class="page-content">
        <router-view />
      </div>
    </main>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Expand, Fold } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const authStore = useAuthStore()

// 侧边栏状态
const sidebarCollapsed = ref(false)

// 菜单项
const menuItems = computed(() => {
  const allRoutes = router.getRoutes()
    .find(r => r.name === 'Layout')
    ?.children?.filter(child => !child.meta?.hidden) || []
  
  // 根据用户角色过滤菜单项
  return allRoutes.filter(route => {
    // 用户管理只有部门主管可以访问
    if (route.name === 'Users') {
      return authStore.hasPermission('access_user_management')
    }
    // 其他菜单项都可以访问
    return true
  })
})

// 当前页面标题
const currentPageTitle = computed(() => {
  return route.meta?.title || '项目管理'
})

// 切换侧边栏
const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

// 获取角色显示文本
const getRoleDisplayText = (role) => {
  const roleMap = {
    'department_manager': '部门主管',
    'member': '普通成员'
  }
  return roleMap[role] || role
}

// 处理用户命令
const handleUserCommand = async (command) => {
  if (command === 'logout') {
    try {
      await authStore.logout()
      ElMessage.success('退出登录成功')
      router.push('/login')
    } catch (error) {
      console.error('退出登录失败:', error)
      ElMessage.error('退出登录失败')
    }
  }
}

// 初始化
onMounted(async () => {
  // 只有部门主管才需要加载用户列表（用于项目成员选择）
  if (authStore.hasPermission('view_users')) {
    try {
      await userStore.fetchUsers()
    } catch (error) {
      console.error('加载用户列表失败:', error)
    }
  }
})
</script>

<style scoped lang="scss">
.main-layout {
  display: flex;
  height: 100vh;
  background: var(--bg-secondary);
}

.sidebar {
  width: 240px;
  background: var(--bg-primary);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease;
  
  &.collapsed {
    width: 64px;
  }
}

.sidebar-header {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  border-bottom: 1px solid var(--border-color);
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  color: var(--apple-blue);
  font-weight: 600;
  font-size: 18px;
  
  .logo-icon {
    width: 28px;
    height: 28px;
    flex-shrink: 0;
    object-fit: contain;
    border-radius: 4px;
    background: linear-gradient(135deg, #0f172a 0%, #334155 50%, #475569 100%);
    padding: 4px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.15);
    border: 1px solid rgba(34, 211, 238, 0.15);
  }
  
  .logo-text {
    white-space: nowrap;
  }
}

.collapse-btn {
  padding: 8px;
  color: var(--text-secondary);
  
  &:hover {
    color: var(--apple-blue);
  }
}

.sidebar-nav {
  flex: 1;
  padding: 16px 0;
}

.nav-list {
  list-style: none;
  margin: 0;
  padding: 0;
}

.nav-item {
  margin: 4px 12px;
  
  &.active .nav-link {
    background: rgba(0, 122, 255, 0.1);
    color: var(--apple-blue);
  }
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-radius: var(--border-radius-small);
  color: var(--text-secondary);
  text-decoration: none;
  transition: all 0.2s ease;
  
  &:hover {
    background: var(--apple-gray-light);
    color: var(--text-primary);
  }
}

.nav-icon {
  font-size: 20px;
  flex-shrink: 0;
}

.nav-text {
  font-weight: 500;
  white-space: nowrap;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.main-header {
  height: 64px;
  background: var(--bg-primary);
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  flex-shrink: 0;
}

.header-left {
  display: flex;
  align-items: center;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-dropdown {
  cursor: pointer;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.user-info:hover {
  background: var(--bg-secondary);
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--apple-blue);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 14px;
  box-shadow: 0 2px 6px rgba(0, 122, 255, 0.3);
  transition: all 0.2s ease;
  
  &:hover {
    transform: scale(1.05);
    box-shadow: 0 3px 8px rgba(0, 122, 255, 0.4);
  }
}

.user-details {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.user-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.user-role {
  font-size: 12px;
  color: var(--text-secondary);
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.page-content {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

// 响应式设计
@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    top: 0;
    left: 0;
    height: 100vh;
    z-index: 1000;
    transform: translateX(-100%);
    
    &:not(.collapsed) {
      transform: translateX(0);
    }
  }
  
  .main-content {
    margin-left: 0;
  }
  
  .main-header {
    padding: 0 16px;
  }
  
  .page-content {
    padding: 16px;
  }
  
  .page-title {
    font-size: 20px;
  }
}
</style>
