<template>
  <div class="login-container">
    <!-- 微动效背景 -->
    <div class="background-effects">
      <!-- 星空效果通过粒子实现 -->
      
      <!-- 粒子效果 -->
      <div class="particles">
        <div class="particle particle-1"></div>
        <div class="particle particle-2"></div>
        <div class="particle particle-3"></div>
        <div class="particle particle-4"></div>
        <div class="particle particle-5"></div>
        <div class="particle particle-6"></div>
        <div class="particle particle-7"></div>
        <div class="particle particle-8"></div>
        <div class="particle particle-9"></div>
        <div class="particle particle-10"></div>
        <div class="particle particle-11"></div>
        <div class="particle particle-12"></div>
        <div class="particle particle-13"></div>
        <div class="particle particle-14"></div>
        <div class="particle particle-15"></div>
        <div class="particle particle-16"></div>
        <div class="particle particle-17"></div>
        <div class="particle particle-18"></div>
        <div class="particle particle-19"></div>
        <div class="particle particle-20"></div>
        <div class="particle particle-21"></div>
        <div class="particle particle-22"></div>
        <div class="particle particle-23"></div>
        <div class="particle particle-24"></div>
        <div class="particle particle-25"></div>
        
        <!-- 明亮主星 -->
        <div class="particle bright-star bright-star-1"></div>
        <div class="particle bright-star bright-star-2"></div>
        <div class="particle bright-star bright-star-3"></div>
      </div>
    </div>
    
      <div class="login-card">
        <div class="login-header">
          <div class="logo">
            <img src="/images/logo.jpeg" alt="Logo" class="logo-image" />
          </div>
          <h2 class="title">科创部项目管理系统</h2>
          <p class="subtitle">请登录您的账户</p>
        </div>
      
      <el-form
        ref="loginFormRef"
        :model="loginForm"
        :rules="loginRules"
        class="login-form"
        size="large"
        @submit.prevent="handleLogin"
      >
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="请输入用户名"
            :prefix-icon="User"
            clearable
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        
        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            :prefix-icon="Lock"
            show-password
            clearable
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        
        <el-form-item>
          <div class="login-options">
            <el-checkbox v-model="rememberMe">
              记住登录状态
            </el-checkbox>
          </div>
        </el-form-item>
        
        <el-form-item>
          <el-button
            type="primary"
            class="login-button"
            :loading="loading"
            @click="handleLogin"
          >
            {{ loading ? '登录中...' : '登录' }}
          </el-button>
        </el-form-item>
      </el-form>
      
      <div class="login-footer">
        <p class="institution-full">天津大学浙江国际创新设计与智造研究院</p>
        <p class="institution-short">IDIM</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, Management } from '@element-plus/icons-vue'
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
.login-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 25%, #334155 50%, #475569 75%, #64748b 100%);
  padding: 20px;
  position: relative;
  overflow: hidden;
  
  /* 添加科技感深层渐变 */
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-image: 
      radial-gradient(circle at 20% 80%, rgba(34, 211, 238, 0.08) 0%, transparent 50%),
      radial-gradient(circle at 80% 20%, rgba(6, 182, 212, 0.06) 0%, transparent 50%),
      radial-gradient(circle at 40% 40%, rgba(14, 165, 233, 0.04) 0%, transparent 50%);
    animation: backgroundFloat 25s ease-in-out infinite;
    pointer-events: none;
  }
  
  /* 添加科技感光晕效果 */
  &::after {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: conic-gradient(
      from 0deg at 50% 50%,
      rgba(34, 211, 238, 0.02) 0deg,
      transparent 60deg,
      rgba(6, 182, 212, 0.015) 120deg,
      transparent 180deg,
      rgba(14, 165, 233, 0.02) 240deg,
      transparent 300deg,
      rgba(34, 211, 238, 0.015) 360deg
    );
    animation: rotate 60s linear infinite;
    pointer-events: none;
  }
}

@keyframes backgroundFloat {
  0%, 100% {
    transform: translate(0, 0) scale(1);
    opacity: 1;
  }
  33% {
    transform: translate(30px, -30px) scale(1.1);
    opacity: 0.8;
  }
  66% {
    transform: translate(-20px, 20px) scale(0.9);
    opacity: 0.9;
  }
}

@keyframes rotate {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

/* 微动效背景样式 */
.background-effects {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  z-index: 0;
}

/* 星空效果通过粒子系统实现 */

/* 专注于粒子动画营造星空感 */

/* 粒子效果 */
.particles {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
}

.particle {
  position: absolute;
  background: rgba(34, 211, 238, 0.9);
  border-radius: 50%;
  opacity: 0;
  animation-timing-function: ease-in-out;
  animation-iteration-count: infinite;
  box-shadow: 
    0 0 15px rgba(34, 211, 238, 0.8),
    0 0 30px rgba(34, 211, 238, 0.4),
    0 0 45px rgba(34, 211, 238, 0.2);
}

/* 不同大小的粒子 - 增强版 */
.particle-1, .particle-2, .particle-3 {
  width: 3px;
  height: 3px;
}

.particle-4, .particle-5, .particle-6 {
  width: 4px;
  height: 4px;
}

.particle-7, .particle-8, .particle-9 {
  width: 2px;
  height: 2px;
}

.particle-10, .particle-11 {
  width: 5px;
  height: 5px;
}

.particle-12, .particle-13 {
  width: 2.5px;
  height: 2.5px;
}

.particle-14, .particle-15 {
  width: 3.5px;
  height: 3.5px;
}

/* 粒子位置和动画 */
.particle-1 {
  top: 20%;
  left: 15%;
  animation: floatParticle1 15s infinite;
  animation-delay: 0s;
}

.particle-2 {
  top: 40%;
  right: 20%;
  animation: floatParticle2 18s infinite;
  animation-delay: 2s;
}

.particle-3 {
  bottom: 25%;
  left: 25%;
  animation: floatParticle3 20s infinite;
  animation-delay: 4s;
}

.particle-4 {
  top: 70%;
  right: 30%;
  animation: floatParticle4 16s infinite;
  animation-delay: 1s;
}

.particle-5 {
  top: 30%;
  left: 60%;
  animation: floatParticle5 22s infinite;
  animation-delay: 3s;
}

.particle-6 {
  bottom: 40%;
  right: 10%;
  animation: floatParticle6 19s infinite;
  animation-delay: 5s;
}

.particle-7 {
  top: 80%;
  left: 40%;
  animation: floatParticle7 14s infinite;
  animation-delay: 1.5s;
}

.particle-8 {
  top: 10%;
  right: 40%;
  animation: floatParticle8 17s infinite;
  animation-delay: 3.5s;
}

.particle-9 {
  bottom: 60%;
  left: 80%;
  animation: floatParticle9 21s infinite;
  animation-delay: 2.5s;
}

.particle-10 {
  top: 50%;
  left: 30%;
  animation: floatParticle10 23s infinite;
  animation-delay: 4.5s;
}

.particle-11 {
  top: 15%;
  left: 70%;
  animation: floatParticle1 21s infinite;
  animation-delay: 2.5s;
}

.particle-12 {
  bottom: 60%;
  right: 5%;
  animation: floatParticle2 16s infinite;
  animation-delay: 4.5s;
}

.particle-13 {
  top: 65%;
  left: 10%;
  animation: floatParticle3 19s infinite;
  animation-delay: 1.8s;
}

.particle-14 {
  top: 35%;
  right: 50%;
  animation: floatParticle4 23s infinite;
  animation-delay: 3.2s;
}

.particle-15 {
  bottom: 10%;
  left: 80%;
  animation: floatParticle5 18s infinite;
  animation-delay: 5.5s;
}

/* 新增粒子样式 */
.particle-16, .particle-17, .particle-18 {
  width: 1.5px;
  height: 1.5px;
}

.particle-19, .particle-20, .particle-21 {
  width: 2.8px;
  height: 2.8px;
}

.particle-22, .particle-23 {
  width: 4.5px;
  height: 4.5px;
}

.particle-24, .particle-25 {
  width: 1.8px;
  height: 1.8px;
}

/* 新增粒子位置 */
.particle-16 {
  top: 8%;
  left: 25%;
  animation: floatParticle1 22s infinite;
  animation-delay: 1.2s;
}

.particle-17 {
  top: 45%;
  right: 8%;
  animation: floatParticle2 19s infinite;
  animation-delay: 3.8s;
}

.particle-18 {
  bottom: 35%;
  left: 5%;
  animation: floatParticle3 25s infinite;
  animation-delay: 2.1s;
}

.particle-19 {
  top: 75%;
  right: 45%;
  animation: floatParticle4 17s infinite;
  animation-delay: 4.2s;
}

.particle-20 {
  top: 25%;
  left: 85%;
  animation: floatParticle5 20s infinite;
  animation-delay: 1.8s;
}

.particle-21 {
  bottom: 55%;
  right: 25%;
  animation: floatParticle1 24s infinite;
  animation-delay: 3.5s;
}

.particle-22 {
  top: 55%;
  left: 45%;
  animation: floatParticle2 21s infinite;
  animation-delay: 2.8s;
}

.particle-23 {
  bottom: 20%;
  right: 60%;
  animation: floatParticle3 18s infinite;
  animation-delay: 4.8s;
}

.particle-24 {
  top: 85%;
  left: 15%;
  animation: floatParticle4 23s infinite;
  animation-delay: 1.5s;
}

.particle-25 {
  top: 12%;
  right: 35%;
  animation: floatParticle5 19s infinite;
  animation-delay: 3.2s;
}

/* 明亮主星样式 */
.bright-star {
  width: 6px;
  height: 6px;
  background: rgba(34, 211, 238, 1);
  box-shadow: 
    0 0 20px rgba(34, 211, 238, 1),
    0 0 40px rgba(34, 211, 238, 0.8),
    0 0 60px rgba(34, 211, 238, 0.6),
    0 0 80px rgba(34, 211, 238, 0.4);
}

.bright-star-1 {
  top: 18%;
  left: 75%;
  animation: brightStarTwinkle1 4s infinite;
}

.bright-star-2 {
  bottom: 25%;
  right: 20%;
  animation: brightStarTwinkle2 5s infinite;
}

.bright-star-3 {
  top: 65%;
  left: 20%;
  animation: brightStarTwinkle3 3.5s infinite;
}

/* 粒子浮动动画 - 增强版 */
@keyframes floatParticle1 {
  0%, 100% { transform: translate(0, 0); opacity: 0; }
  10% { opacity: 1; }
  25% { opacity: 0.3; }
  50% { transform: translate(40px, -60px); opacity: 0.9; }
  75% { opacity: 0.2; }
  90% { opacity: 0.8; }
}

@keyframes floatParticle2 {
  0%, 100% { transform: translate(0, 0); opacity: 0; }
  15% { opacity: 0.9; }
  30% { opacity: 0.4; }
  50% { transform: translate(-50px, -40px); opacity: 1; }
  70% { opacity: 0.3; }
  85% { opacity: 0.7; }
}

@keyframes floatParticle3 {
  0%, 100% { transform: translate(0, 0); opacity: 0; }
  20% { opacity: 0.7; }
  50% { transform: translate(30px, -80px); opacity: 0.5; }
  80% { opacity: 0.4; }
}

@keyframes floatParticle4 {
  0%, 100% { transform: translate(0, 0); opacity: 0; }
  12% { opacity: 0.9; }
  50% { transform: translate(-35px, -70px); opacity: 0.6; }
  88% { opacity: 0.2; }
}

@keyframes floatParticle5 {
  0%, 100% { transform: translate(0, 0); opacity: 0; }
  18% { opacity: 0.5; }
  50% { transform: translate(60px, -50px); opacity: 0.9; }
  82% { opacity: 0.3; }
}

@keyframes floatParticle6 {
  0%, 100% { transform: translate(0, 0); opacity: 0; }
  25% { opacity: 0.8; }
  50% { transform: translate(-40px, -90px); opacity: 0.4; }
  75% { opacity: 0.6; }
}

@keyframes floatParticle7 {
  0%, 100% { transform: translate(0, 0); opacity: 0; }
  14% { opacity: 0.6; }
  50% { transform: translate(25px, -45px); opacity: 0.8; }
  86% { opacity: 0.2; }
}

@keyframes floatParticle8 {
  0%, 100% { transform: translate(0, 0); opacity: 0; }
  16% { opacity: 0.7; }
  50% { transform: translate(-55px, -35px); opacity: 0.5; }
  84% { opacity: 0.4; }
}

@keyframes floatParticle9 {
  0%, 100% { transform: translate(0, 0); opacity: 0; }
  22% { opacity: 0.9; }
  50% { transform: translate(45px, -75px); opacity: 0.6; }
  78% { opacity: 0.3; }
}

@keyframes floatParticle10 {
  0%, 100% { transform: translate(0, 0); opacity: 0; }
  24% { opacity: 0.4; }
  50% { transform: translate(-30px, -55px); opacity: 0.8; }
  76% { opacity: 0.5; }
}

/* 明亮主星闪烁动画 */
@keyframes brightStarTwinkle1 {
  0%, 100% { 
    opacity: 0.6; 
    transform: scale(1);
    box-shadow: 
      0 0 20px rgba(34, 211, 238, 0.8),
      0 0 40px rgba(34, 211, 238, 0.6),
      0 0 60px rgba(34, 211, 238, 0.4);
  }
  50% { 
    opacity: 1; 
    transform: scale(1.3);
    box-shadow: 
      0 0 30px rgba(34, 211, 238, 1),
      0 0 60px rgba(34, 211, 238, 0.8),
      0 0 90px rgba(34, 211, 238, 0.6),
      0 0 120px rgba(34, 211, 238, 0.4);
  }
}

@keyframes brightStarTwinkle2 {
  0%, 100% { 
    opacity: 0.7; 
    transform: scale(1);
  }
  25% { 
    opacity: 0.3; 
    transform: scale(0.8);
  }
  50% { 
    opacity: 1; 
    transform: scale(1.4);
  }
  75% { 
    opacity: 0.4; 
    transform: scale(1.1);
  }
}

@keyframes brightStarTwinkle3 {
  0%, 100% { 
    opacity: 0.5; 
    transform: scale(1) rotate(0deg);
  }
  33% { 
    opacity: 1; 
    transform: scale(1.2) rotate(120deg);
  }
  66% { 
    opacity: 0.3; 
    transform: scale(0.9) rotate(240deg);
  }
}

.login-card {
  width: 100%;
  max-width: 420px;
  /* 毛玻璃效果 */
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(25px);
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  box-shadow: 
    0 30px 60px rgba(0, 0, 0, 0.15),
    0 20px 40px rgba(0, 0, 0, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.25);
  padding: 48px;
  position: relative;
  z-index: 10;
  
  /* 增加内部光泽效果 */
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.6), transparent);
    border-radius: 20px 20px 0 0;
  }
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.logo {
  margin-bottom: 16px;
}

.logo-image {
  width: 64px;
  height: 64px;
  object-fit: contain;
  border-radius: 8px;
  background: linear-gradient(135deg, #0f172a 0%, #334155 50%, #475569 100%);
  padding: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
  border: 1px solid rgba(34, 211, 238, 0.2);
}

.title {
  font-size: 32px;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.95);
  margin: 0 0 12px 0;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  font-family: 'PingFang SC', 'Helvetica Neue', 'Microsoft YaHei', sans-serif;
}

.subtitle {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.8);
  margin: 0;
  font-weight: 400;
}

/* 外部机构信息样式已移除，现在在登录框内部显示 */

.login-form {
  margin-bottom: 24px;
}

.login-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.login-button {
  width: 100%;
  height: 52px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 12px;
  background: linear-gradient(135deg, #0ea5e9 0%, #06b6d4 25%, #0891b2 50%, #0e7490 75%, #155e75 100%);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  font-family: 'PingFang SC', 'Helvetica Neue', 'Microsoft YaHei', sans-serif;
  box-shadow: 
    0 8px 32px rgba(0, 0, 0, 0.12),
    inset 0 1px 0 rgba(255, 255, 255, 0.4);
  
  /* 添加光泽效果 */
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
    transition: left 0.5s;
  }
  
  &:hover {
    background: linear-gradient(135deg, #38bdf8 0%, #22d3ee 25%, #06b6d4 50%, #0891b2 75%, #0e7490 100%);
    border-color: rgba(255, 255, 255, 0.4);
    transform: translateY(-3px);
    box-shadow: 
      0 12px 40px rgba(14, 165, 233, 0.4),
      0 8px 24px rgba(6, 182, 212, 0.3),
      inset 0 1px 0 rgba(255, 255, 255, 0.3);
    
    &::before {
      left: 100%;
    }
  }
  
  &:active {
    transform: translateY(-1px);
    box-shadow: 
      0 6px 20px rgba(0, 0, 0, 0.15),
      inset 0 1px 0 rgba(255, 255, 255, 0.5);
  }
}

.login-footer {
  text-align: center;
  border-top: 1px solid rgba(255, 255, 255, 0.2);
  padding-top: 24px;
  margin-top: 24px;
}

.login-footer .institution-full {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.7);
  margin: 8px 0;
  line-height: 1.5;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
  font-weight: 400;
  font-family: 'PingFang SC', 'Helvetica Neue', 'Microsoft YaHei', sans-serif;
}

.login-footer .institution-short {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.8);
  margin: 4px 0 0 0;
  font-weight: 600;
  letter-spacing: 2px;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
  font-family: 'Arial', 'Helvetica', sans-serif;
}

/* 响应式设计 */
@media (max-width: 480px) {
  .login-container {
    padding: 16px;
  }
  
  .login-card {
    padding: 24px;
    max-width: 100%;
  }
  
  .title {
    font-size: 24px;
  }
  
  .subtitle {
    font-size: 14px;
  }
  
  .logo-image {
    width: 56px;
    height: 56px;
    padding: 6px;
  }
  
  .login-footer .institution-full {
    font-size: 12px;
  }
  
  .login-footer .institution-short {
    font-size: 14px;
    letter-spacing: 1px;
  }
}

/* 输入框样式优化 */
:deep(.el-input__wrapper) {
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: 
    0 4px 16px rgba(0, 0, 0, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.4);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  padding: 8px 14px;
  min-height: 38px;
}

:deep(.el-input__wrapper:hover) {
  background: rgba(255, 255, 255, 0.95);
  border-color: rgba(255, 255, 255, 0.5);
  box-shadow: 
    0 6px 20px rgba(0, 0, 0, 0.15),
    inset 0 1px 0 rgba(255, 255, 255, 0.6);
  transform: translateY(-2px);
}

:deep(.el-input__wrapper.is-focus) {
  background: rgba(255, 255, 255, 0.98);
  border-color: rgba(255, 255, 255, 0.8);
  box-shadow: 
    0 0 0 3px rgba(255, 255, 255, 0.3),
    0 8px 25px rgba(0, 0, 0, 0.2),
    inset 0 1px 0 rgba(255, 255, 255, 0.8);
  transform: translateY(-3px);
}

:deep(.el-input__inner) {
  font-size: 15px;
  color: #2c3e50;
  font-weight: 500;
  font-family: 'PingFang SC', 'Helvetica Neue', 'Microsoft YaHei', sans-serif;
}

:deep(.el-input__inner::placeholder) {
  color: #5a6c7d;
  font-weight: 400;
}

/* 复选框样式优化 */
:deep(.el-checkbox__input.is-checked .el-checkbox__inner) {
  background-color: #667eea;
  border-color: #667eea;
}

:deep(.el-checkbox__input.is-checked .el-checkbox__inner::after) {
  border-color: #ffffff;
  border-width: 2px;
}

:deep(.el-checkbox__inner) {
  border-radius: 4px;
  border-color: rgba(255, 255, 255, 0.6);
  background-color: rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
  width: 16px;
  height: 16px;
}

:deep(.el-checkbox__inner:hover) {
  border-color: rgba(255, 255, 255, 0.8);
  background-color: rgba(255, 255, 255, 0.3);
}

:deep(.el-checkbox__label) {
  font-size: 14px;
  color: #ffffff;
  font-family: 'PingFang SC', 'Helvetica Neue', 'Microsoft YaHei', sans-serif;
  font-weight: 500;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

/* 表单验证错误提示样式 */
:deep(.el-form-item__error) {
  color: #ffffff;
  background-color: rgba(220, 53, 69, 0.9);
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  text-shadow: none;
  box-shadow: 0 2px 8px rgba(220, 53, 69, 0.3);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

/* 错误状态输入框边框 */
:deep(.el-input__wrapper.is-error) {
  border-color: rgba(220, 53, 69, 0.8);
  box-shadow: 
    0 0 0 2px rgba(220, 53, 69, 0.2),
    0 4px 16px rgba(0, 0, 0, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.4);
}
</style>
