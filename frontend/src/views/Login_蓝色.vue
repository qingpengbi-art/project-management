<template>
  <div class="login-wrapper">
    <!-- 动态背景 -->
    <div class="animated-background">
      <div class="gradient-sphere sphere-1"></div>
      <div class="gradient-sphere sphere-2"></div>
      <div class="gradient-sphere sphere-3"></div>
    </div>
    
    <!-- 主内容区 -->
    <div class="main-content">
      <!-- 左侧品牌展示区 -->
      <div class="brand-zone">
        <div class="brand-inner">
          <!-- Logo区域 - 改进配色方案 -->
          <div class="logo-section">
            <div class="logo-wrapper">
              <!-- 使用渐变白色背景，与页面主题协调 -->
              <div class="logo-glow"></div>
              <div class="logo-bg">
                <img src="/images/logo.jpeg" alt="Logo" class="logo-img" />
              </div>
            </div>
          </div>
          
          <!-- 系统信息 -->
          <div class="title-section">
            <h1 class="system-title">科创部项目管理系统</h1>
            <div class="title-divider"></div>
            <p class="system-slogan">智能化项目管理 · 高效协作平台</p>
          </div>
          
          <!-- 特色标签 - 改进配色 -->
          <div class="features-row">
            <div class="feature-tag feature-primary">
              <svg class="feature-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              <span>快速高效</span>
            </div>
            <div class="feature-tag feature-success">
              <svg class="feature-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
              <span>安全可靠</span>
            </div>
            <div class="feature-tag feature-info">
              <svg class="feature-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
              <span>团队协作</span>
      </div>
    </div>
    
          <!-- 底部机构信息 - 优化样式 -->
          <div class="institution-info">
            <div class="institution-line"></div>
            <p class="institution-name">天津大学浙江国际创新设计与智造研究院</p>
            <p class="institution-abbr">IDIM · Innovation Design Institute</p>
          </div>
        </div>
        </div>
      
      <!-- 右侧登录表单区 -->
      <div class="form-zone">
        <div class="form-card">
          <!-- 表单头部 -->
          <div class="form-header">
            <h2 class="form-title">账号登录</h2>
            <p class="form-desc">欢迎使用科创部项目管理系统</p>
          </div>
          
          <!-- 登录表单 -->
      <el-form
        ref="loginFormRef"
        :model="loginForm"
        :rules="loginRules"
        class="login-form"
        @submit.prevent="handleLogin"
      >
            <!-- 用户名 -->
        <el-form-item prop="username">
              <div class="field-group">
                <label class="field-label">用户名</label>
          <el-input
            v-model="loginForm.username"
            placeholder="请输入用户名"
            clearable
                  size="large"
            @keyup.enter="handleLogin"
                >
                  <template #prefix>
                    <el-icon class="field-icon"><User /></el-icon>
                  </template>
                </el-input>
              </div>
        </el-form-item>
        
            <!-- 密码 -->
        <el-form-item prop="password">
              <div class="field-group">
                <label class="field-label">密码</label>
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            show-password
            clearable
                  size="large"
            @keyup.enter="handleLogin"
                >
                  <template #prefix>
                    <el-icon class="field-icon"><Lock /></el-icon>
                  </template>
                </el-input>
              </div>
        </el-form-item>
        
            <!-- 记住我 -->
            <div class="form-extra">
              <el-checkbox v-model="rememberMe" class="remember-check">
              记住登录状态
            </el-checkbox>
          </div>
            
            <!-- 登录按钮 -->
            <el-form-item class="form-submit">
              <button
                type="button"
                class="submit-btn"
                :class="{ 'is-loading': loading }"
                :disabled="loading"
            @click="handleLogin"
          >
                <span v-if="!loading" class="btn-inner">
                  <span>登录</span>
                  <svg class="btn-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M13 7l5 5m0 0l-5 5m5-5H6" />
                  </svg>
                </span>
                <span v-else class="btn-loading">
                  <el-icon class="loading-icon"><Loading /></el-icon>
                  <span>登录中...</span>
                </span>
              </button>
        </el-form-item>
      </el-form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, Loading } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

// 响应式数据
const loginFormRef = ref(null)
const loading = ref(false)
const rememberMe = ref(true)

const loginForm = ref({
  username: '',
  password: ''
})

// 表单验证规则
const loginRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 2, max: 50, message: '用户名长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6个字符', trigger: 'blur' }
  ]
}

// 方法
const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  try {
    // 表单验证
    const valid = await loginFormRef.value.validate()
    if (!valid) return
    
    loading.value = true
    
    // 调用登录
    const success = await authStore.login(loginForm.value.username, loginForm.value.password)
    
    if (success) {
      ElMessage.success('登录成功')
      
      // 保存登录状态
      if (rememberMe.value) {
        localStorage.setItem('rememberLogin', 'true')
      } else {
        localStorage.removeItem('rememberLogin')
      }
      
      // 跳转到主页
      router.push('/')
    }
    
  } catch (error) {
    console.error('登录失败:', error)
    ElMessage.error(error.message || '登录失败，请重试')
  } finally {
    loading.value = false
  }
}

// 组件挂载时检查是否已登录
onMounted(async () => {
  // 检查是否已登录
  if (authStore.isAuthenticated) {
    router.push('/')
    return
  }
  
  // 检查是否有记住的登录状态
  const remembered = localStorage.getItem('rememberLogin')
  if (remembered === 'true') {
    rememberMe.value = true
  }
})
</script>

<style scoped>
/* ==================== 全局容器 ==================== */
.login-wrapper {
  min-height: 100vh;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  /* 方案3：优雅深蓝风 - 高端商务深蓝渐变 */
  background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
}
  
/* ==================== 动态背景 ==================== */
.animated-background {
    position: absolute;
    top: 0;
    left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
  z-index: 0;
}

.gradient-sphere {
    position: absolute;
  border-radius: 50%;
  filter: blur(100px);
  opacity: 0.4;
  animation: float-sphere 20s ease-in-out infinite;
}

.sphere-1 {
  width: 600px;
  height: 600px;
  background: radial-gradient(circle, #4facfe 0%, #00f2fe 100%);
  top: -200px;
  left: -200px;
  animation-delay: 0s;
}

.sphere-2 {
  width: 500px;
  height: 500px;
  background: radial-gradient(circle, #43e97b 0%, #38f9d7 100%);
  bottom: -150px;
  right: -150px;
  animation-delay: 7s;
}

.sphere-3 {
  width: 450px;
  height: 450px;
  background: radial-gradient(circle, #fa709a 0%, #fee140 100%);
  top: 50%;
  left: 50%;
  animation-delay: 14s;
}

@keyframes float-sphere {
  0%, 100% {
    transform: translate(0, 0) scale(1);
  }
  33% {
    transform: translate(50px, -30px) scale(1.1);
  }
  66% {
    transform: translate(-30px, 40px) scale(0.9);
  }
}

/* ==================== 主内容区 ==================== */
.main-content {
  position: relative;
  z-index: 1;
  display: flex;
  width: 100%;
  max-width: 1300px;
  margin: 0 auto;
  padding: 20px 40px;
  gap: 60px;
  align-items: center;
  height: 100vh;
  max-height: 900px;
}

/* ==================== 左侧品牌区 ==================== */
.brand-zone {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.brand-inner {
  max-width: 540px;
  width: 100%;
  animation: fade-slide-in 0.8s ease-out;
}

@keyframes fade-slide-in {
  from {
    opacity: 0;
    transform: translateX(-30px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

/* Logo区域 - 改进配色方案 */
.logo-section {
  display: flex;
  justify-content: center;
  margin-bottom: 44px;
}

.logo-wrapper {
  position: relative;
  display: inline-block;
}

/* 发光效果 */
.logo-glow {
  position: absolute;
  inset: -20px;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.3) 0%, transparent 70%);
  border-radius: 50%;
  filter: blur(30px);
  animation: glow-pulse 3s ease-in-out infinite;
  z-index: 0;
}

@keyframes glow-pulse {
  0%, 100% {
    opacity: 0.6;
    transform: scale(1);
  }
  50% {
    opacity: 1;
    transform: scale(1.1);
  }
}

/* Logo背景 - 使用半透明深蓝渐变，与主题协调且能看清Logo */
.logo-bg {
  width: 130px;
  height: 130px;
  /* 使用深蓝主题色，半透明效果 */
  background: linear-gradient(135deg, rgba(42, 82, 152, 0.4) 0%, rgba(30, 60, 114, 0.3) 100%);
  /* 添加磨砂玻璃效果 */
  backdrop-filter: blur(20px);
  border-radius: 32px;
  padding: 12px;
  box-shadow: 
    0 25px 60px rgba(0, 0, 0, 0.3),
    0 0 0 1px rgba(255, 255, 255, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.4);
  position: relative;
  z-index: 1;
  animation: logo-float 4s ease-in-out infinite;
  transition: transform 0.4s ease;
}

.logo-bg:hover {
  transform: scale(1.08) rotate(-3deg);
}

@keyframes logo-float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-8px);
  }
}

.logo-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 24px;
}

/* 标题区域 */
.title-section {
  text-align: center;
  margin-bottom: 40px;
}

.system-title {
  font-size: 46px;
  font-weight: 800;
  color: white;
  margin: 0 0 20px 0;
  letter-spacing: -1px;
  text-shadow: 0 4px 24px rgba(0, 0, 0, 0.25);
  font-family: 'PingFang SC', 'Helvetica Neue', 'Microsoft YaHei', sans-serif;
  line-height: 1.2;
}

.title-divider {
  width: 90px;
  height: 4px;
  background: linear-gradient(90deg, transparent, white, transparent);
  margin: 0 auto 20px;
  border-radius: 2px;
  box-shadow: 0 2px 15px rgba(255, 255, 255, 0.4);
}

.system-slogan {
  font-size: 17px;
  color: rgba(255, 255, 255, 0.95);
  margin: 0;
  font-weight: 500;
  letter-spacing: 1.5px;
  line-height: 1.5;
}

/* 特色标签 - 不同颜色主题 */
.features-row {
  display: flex;
  justify-content: center;
  gap: 14px;
  margin-bottom: 44px;
  flex-wrap: wrap;
}

.feature-tag {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 13px 22px;
  border-radius: 50px;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.3s ease;
  cursor: default;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.feature-primary {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.25), rgba(255, 255, 255, 0.15));
  color: white;
}

.feature-success {
  background: linear-gradient(135deg, rgba(72, 187, 120, 0.3), rgba(56, 161, 105, 0.2));
  color: white;
}

.feature-info {
  background: linear-gradient(135deg, rgba(66, 153, 225, 0.3), rgba(49, 130, 206, 0.2));
  color: white;
}

.feature-tag:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
}

.feature-primary:hover {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.35), rgba(255, 255, 255, 0.25));
}

.feature-success:hover {
  background: linear-gradient(135deg, rgba(72, 187, 120, 0.4), rgba(56, 161, 105, 0.3));
}

.feature-info:hover {
  background: linear-gradient(135deg, rgba(66, 153, 225, 0.4), rgba(49, 130, 206, 0.3));
}

.feature-icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
  stroke-width: 2.5px;
}

/* 机构信息 - 优化样式 */
.institution-info {
  padding-top: 36px;
  text-align: center;
}

.institution-line {
  width: 70%;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
  margin: 0 auto 24px;
}

.institution-name {
  font-size: 16px;
  color: white;
  margin: 0 0 10px 0;
  font-weight: 600;
  line-height: 1.6;
  letter-spacing: 0.5px;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.institution-abbr {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.85);
  margin: 0;
  font-weight: 500;
  letter-spacing: 1px;
}

/* ==================== 右侧表单区 ==================== */
.form-zone {
  flex: 0 0 480px;
  animation: fade-slide-in-right 0.8s ease-out;
}

@keyframes fade-slide-in-right {
  from {
    opacity: 0;
    transform: translateX(30px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.form-card {
  background: white;
  border-radius: 28px;
  padding: 44px 40px;
  box-shadow: 0 25px 70px rgba(0, 0, 0, 0.25);
}

/* 表单头部 */
.form-header {
  margin-bottom: 36px;
}

.form-title {
  font-size: 32px;
  font-weight: 700;
  color: #1a202c;
  margin: 0 0 10px 0;
  font-family: 'PingFang SC', 'Helvetica Neue', 'Microsoft YaHei', sans-serif;
}

.form-desc {
  font-size: 15px;
  color: #718096;
  margin: 0;
  font-weight: 500;
}

/* 表单样式 */
.login-form {
  margin: 0;
}

.field-group {
  width: 100%;
}

.field-label {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 10px;
  font-family: 'PingFang SC', 'Helvetica Neue', 'Microsoft YaHei', sans-serif;
}

.field-icon {
  font-size: 20px;
  color: #a0aec0;
  transition: color 0.3s ease;
}

/* 表单额外选项 */
.form-extra {
  margin-bottom: 28px;
}

.remember-check {
  font-size: 14px;
}

/* 提交按钮区域 */
.form-submit {
  margin-bottom: 0;
}

.submit-btn {
  width: 100%;
  height: 54px;
  border: none;
  border-radius: 14px;
  /* 深蓝商务风格按钮 */
  background: linear-gradient(135deg, #2a5298 0%, #1e3c72 100%);
  color: white;
  font-size: 17px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  font-family: 'PingFang SC', 'Helvetica Neue', 'Microsoft YaHei', sans-serif;
  box-shadow: 0 10px 28px rgba(42, 82, 152, 0.4);
}

.submit-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  transition: left 0.6s ease;
}

.submit-btn:hover::before {
  left: 100%;
}

.submit-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 14px 36px rgba(42, 82, 152, 0.5);
}

.submit-btn:active {
  transform: translateY(0);
}

.submit-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
}

.btn-inner,
.btn-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.btn-arrow {
  width: 20px;
  height: 20px;
  transition: transform 0.3s ease;
}

.submit-btn:hover .btn-arrow {
  transform: translateX(4px);
}

.loading-icon {
  font-size: 20px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* ==================== Element Plus 样式覆盖 ==================== */

/* 表单项间距 */
:deep(.el-form-item) {
  margin-bottom: 26px;
}

/* 输入框样式 */
:deep(.el-input__wrapper) {
  border-radius: 12px;
  background: #f7fafc;
  border: 2px solid #e2e8f0;
  box-shadow: none;
  transition: all 0.3s ease;
  padding: 14px 18px;
  min-height: 52px;
}

:deep(.el-input__wrapper:hover) {
  border-color: #cbd5e0;
  background: white;
}

:deep(.el-input__wrapper.is-focus) {
  border-color: #2a5298;
  background: white;
  box-shadow: 0 0 0 4px rgba(42, 82, 152, 0.1);
}

:deep(.el-input__wrapper.is-focus) .field-icon {
  color: #2a5298;
}

:deep(.el-input__inner) {
  font-size: 15px;
  color: #2d3748;
  font-weight: 500;
  font-family: 'PingFang SC', 'Helvetica Neue', 'Microsoft YaHei', sans-serif;
}

:deep(.el-input__inner::placeholder) {
  color: #cbd5e0;
  font-weight: 400;
}

/* 前缀图标位置 */
:deep(.el-input__prefix) {
  left: 18px;
}

/* 后缀图标 */
:deep(.el-input__suffix) {
  right: 18px;
}

:deep(.el-input__suffix-inner) {
  color: #a0aec0;
}

/* 复选框样式 */
:deep(.el-checkbox__input.is-checked .el-checkbox__inner) {
  background-color: #2a5298;
  border-color: #2a5298;
}

:deep(.el-checkbox__inner) {
  width: 18px;
  height: 18px;
  border-radius: 5px;
  border: 2px solid #cbd5e0;
  background-color: white;
  transition: all 0.3s ease;
}

:deep(.el-checkbox__inner:hover) {
  border-color: #2a5298;
}

:deep(.el-checkbox__label) {
  font-size: 14px;
  color: #4a5568;
  font-family: 'PingFang SC', 'Helvetica Neue', 'Microsoft YaHei', sans-serif;
  font-weight: 500;
  padding-left: 10px;
}

/* 错误提示 */
:deep(.el-form-item__error) {
  color: #e53e3e;
  background: #fff5f5;
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  margin-top: 8px;
  border: 1px solid #feb2b2;
}

:deep(.el-input__wrapper.is-error) {
  border-color: #fc8181 !important;
}

/* ==================== 响应式设计 ==================== */

/* 中等屏幕 */
@media (max-width: 1200px) {
  .main-content {
    gap: 40px;
    padding: 20px 30px;
  }
  
  .system-title {
    font-size: 40px;
  }
  
  .logo-bg {
    width: 120px;
    height: 120px;
  }
  
  .form-zone {
    flex: 0 0 440px;
  }
}

/* 平板 - 上下布局 */
@media (max-width: 1024px) {
  .login-wrapper {
    height: auto;
    min-height: 100vh;
  }
  
  .main-content {
    flex-direction: column;
    gap: 30px;
    padding: 30px 20px;
    height: auto;
    max-height: none;
  }
  
  .brand-zone {
    width: 100%;
  }
  
  .form-zone {
    flex: 0 0 auto;
    width: 100%;
    max-width: 480px;
  }
}

/* 手机 */
@media (max-width: 640px) {
  .main-content {
    padding: 24px 16px;
  }
  
  .system-title {
    font-size: 32px;
  }
  
  .system-slogan {
    font-size: 15px;
  }
  
  .logo-bg {
    width: 110px;
    height: 110px;
  }
  
  .features-row {
    gap: 10px;
  }
  
  .feature-tag {
    padding: 11px 18px;
    font-size: 13px;
  }
  
  .form-card {
    padding: 36px 28px;
    border-radius: 24px;
  }
  
  .form-title {
    font-size: 28px;
  }
  
  .form-desc {
    font-size: 14px;
  }
  
  .submit-btn {
    height: 52px;
    font-size: 16px;
  }
  
  .institution-name {
  font-size: 15px;
  }
}

/* 小屏手机 */
@media (max-width: 480px) {
  .form-card {
    padding: 32px 24px;
  }
  
  .system-title {
    font-size: 28px;
  }
  
  .form-title {
    font-size: 24px;
  }
}

/* 超小屏幕高度优化 */
@media (max-height: 700px) {
  .logo-section {
    margin-bottom: 32px;
  }
  
  .title-section {
    margin-bottom: 32px;
  }
  
  .features-row {
    margin-bottom: 32px;
  }
  
  .institution-info {
    padding-top: 28px;
  }
  
  .form-header {
    margin-bottom: 28px;
  }
}
</style>
