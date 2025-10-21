import { useAuthStore } from '@/stores/auth'

/**
 * 路由守卫配置
 */

// 需要登录才能访问的路由
const protectedRoutes = [
  '/',
  '/dashboard',
  '/projects',
  '/users',
  '/project'
]

// 不同角色可以访问的路由
const roleRoutes = {
  'department_manager': ['/', '/dashboard', '/projects', '/users'],
  'member': ['/', '/dashboard', '/projects', '/users']
}

// 路由前置守卫
export const beforeEach = async (to, from, next) => {
  const authStore = useAuthStore()
  
  // 如果要访问登录页面
  if (to.path === '/login') {
    // 如果已经登录，重定向到首页
    if (authStore.isAuthenticated) {
      next('/')
      return
    }
    // 否则允许访问登录页面
    next()
    return
  }
  
  // 检查是否需要登录
  const needsAuth = protectedRoutes.some(route => {
    if (route === '/') return to.path === '/'
    return to.path.startsWith(route)
  })
  
  if (needsAuth) {
    // 如果未登录，重定向到登录页
    if (!authStore.isAuthenticated) {
      // 尝试从服务器验证登录状态
      const isValid = await authStore.checkAuth()
      if (!isValid) {
        next('/login')
        return
      }
    }
    
    // 检查角色权限
    if (authStore.user && authStore.user.role) {
      const userRole = authStore.user.role
      const allowedRoutes = roleRoutes[userRole] || []
      
      // 检查当前路由是否在允许的路由中
      const hasAccess = allowedRoutes.some(route => {
        if (route === '/') return to.path === '/'
        return to.path.startsWith(route)
      })
      
      if (!hasAccess) {
        // 如果没有权限，重定向到首页或显示403页面
        next('/')
        return
      }
    }
  }
  
  next()
}

// 路由后置守卫
export const afterEach = (to, from) => {
  // 可以在这里添加页面访问日志等功能
  console.log(`路由跳转: ${from.path} -> ${to.path}`)
}
