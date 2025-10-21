<template>
  <div class="login-wrapper">
    <!-- 
      配色方案选择：修改 class 即可切换
      - theme-modern (现代科技风 - 蓝紫渐变) 推荐！
      - theme-vibrant (活力橙粉风 - 橙粉渐变)
      - theme-elegant (优雅深蓝风 - 深蓝渐变)
      - theme-fresh (清新绿蓝风 - 绿蓝渐变)
    -->
    <div class="color-scheme theme-modern">
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
            <!-- Logo区域 -->
            <div class="logo-section">
              <div class="logo-wrapper">
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
            
            <!-- 特色标签 -->
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
            
            <!-- 底部机构信息 -->
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
            <div class="form-header">
              <h2 class="form-title">账号登录</h2>
              <p class="form-desc">欢迎使用科创部项目管理系统</p>
            </div>
            
            <div class="login-form">
              <!-- 用户名 -->
              <div class="field-group">
                <label class="field-label">用户名</label>
                <input type="text" placeholder="请输入用户名" class="form-input" />
              </div>
              
              <!-- 密码 -->
              <div class="field-group">
                <label class="field-label">密码</label>
                <input type="password" placeholder="请输入密码" class="form-input" />
              </div>
              
              <!-- 记住我 -->
              <div class="form-extra">
                <label class="checkbox-label">
                  <input type="checkbox" checked />
                  <span>记住登录状态</span>
                </label>
              </div>
              
              <!-- 登录按钮 -->
              <button class="submit-btn">
                <span>登录</span>
                <svg class="btn-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* ==================== 配色方案 ==================== */

/* 方案1：现代科技风 - 蓝紫渐变 (推荐！) */
.theme-modern {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.theme-modern .gradient-sphere {
  opacity: 0.35;
}

.theme-modern .sphere-1 {
  background: radial-gradient(circle, #f093fb 0%, #f5576c 100%);
}

.theme-modern .sphere-2 {
  background: radial-gradient(circle, #4facfe 0%, #00f2fe 100%);
}

.theme-modern .sphere-3 {
  background: radial-gradient(circle, #43e97b 0%, #38f9d7 100%);
}

.theme-modern .logo-bg {
  background: linear-gradient(135deg, rgba(79, 70, 229, 0.3) 0%, rgba(99, 102, 241, 0.25) 100%);
}

.theme-modern .submit-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  box-shadow: 0 10px 28px rgba(102, 126, 234, 0.4);
}

.theme-modern .submit-btn:hover {
  box-shadow: 0 14px 36px rgba(102, 126, 234, 0.5);
}

/* 方案2：活力橙粉风 - 橙粉渐变 */
.theme-vibrant {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.theme-vibrant .gradient-sphere {
  opacity: 0.3;
}

.theme-vibrant .sphere-1 {
  background: radial-gradient(circle, #ffecd2 0%, #fcb69f 100%);
}

.theme-vibrant .sphere-2 {
  background: radial-gradient(circle, #ff9a9e 0%, #fad0c4 100%);
}

.theme-vibrant .sphere-3 {
  background: radial-gradient(circle, #a18cd1 0%, #fbc2eb 100%);
}

.theme-vibrant .logo-bg {
  background: linear-gradient(135deg, rgba(245, 87, 108, 0.3) 0%, rgba(240, 147, 251, 0.25) 100%);
}

.theme-vibrant .submit-btn {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  box-shadow: 0 10px 28px rgba(245, 87, 108, 0.4);
}

.theme-vibrant .submit-btn:hover {
  box-shadow: 0 14px 36px rgba(245, 87, 108, 0.5);
}

/* 方案3：优雅深蓝风 - 深蓝渐变 */
.theme-elegant {
  background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
}

.theme-elegant .gradient-sphere {
  opacity: 0.4;
}

.theme-elegant .sphere-1 {
  background: radial-gradient(circle, #4facfe 0%, #00f2fe 100%);
}

.theme-elegant .sphere-2 {
  background: radial-gradient(circle, #43e97b 0%, #38f9d7 100%);
}

.theme-elegant .sphere-3 {
  background: radial-gradient(circle, #fa709a 0%, #fee140 100%);
}

.theme-elegant .logo-bg {
  background: linear-gradient(135deg, rgba(42, 82, 152, 0.4) 0%, rgba(30, 60, 114, 0.3) 100%);
}

.theme-elegant .submit-btn {
  background: linear-gradient(135deg, #2a5298 0%, #1e3c72 100%);
  box-shadow: 0 10px 28px rgba(42, 82, 152, 0.4);
}

.theme-elegant .submit-btn:hover {
  box-shadow: 0 14px 36px rgba(42, 82, 152, 0.5);
}

/* 方案4：清新绿蓝风 - 绿蓝渐变 */
.theme-fresh {
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
}

.theme-fresh .gradient-sphere {
  opacity: 0.35;
}

.theme-fresh .sphere-1 {
  background: radial-gradient(circle, #a8edea 0%, #fed6e3 100%);
}

.theme-fresh .sphere-2 {
  background: radial-gradient(circle, #4facfe 0%, #00f2fe 100%);
}

.theme-fresh .sphere-3 {
  background: radial-gradient(circle, #ffecd2 0%, #fcb69f 100%);
}

.theme-fresh .logo-bg {
  background: linear-gradient(135deg, rgba(56, 239, 125, 0.3) 0%, rgba(17, 153, 142, 0.25) 100%);
}

.theme-fresh .submit-btn {
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
  box-shadow: 0 10px 28px rgba(17, 153, 142, 0.4);
}

.theme-fresh .submit-btn:hover {
  box-shadow: 0 14px 36px rgba(17, 153, 142, 0.5);
}

/* ==================== 基础样式 ==================== */
.login-wrapper {
  min-height: 100vh;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.color-scheme {
  width: 100%;
  height: 100%;
  position: absolute;
  top: 0;
  left: 0;
}

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
  animation: float-sphere 20s ease-in-out infinite;
}

.sphere-1 {
  width: 600px;
  height: 600px;
  top: -200px;
  left: -200px;
  animation-delay: 0s;
}

.sphere-2 {
  width: 500px;
  height: 500px;
  bottom: -150px;
  right: -150px;
  animation-delay: 7s;
}

.sphere-3 {
  width: 450px;
  height: 450px;
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

.logo-section {
  display: flex;
  justify-content: center;
  margin-bottom: 44px;
}

.logo-wrapper {
  position: relative;
  display: inline-block;
}

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

.logo-bg {
  width: 130px;
  height: 130px;
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
}

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
}

.feature-icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

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
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.institution-abbr {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.85);
  margin: 0;
  font-weight: 500;
}

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

.login-form {
  margin: 0;
}

.field-group {
  margin-bottom: 26px;
}

.field-label {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 10px;
  font-family: 'PingFang SC', 'Helvetica Neue', 'Microsoft YaHei', sans-serif;
}

.form-input {
  width: 100%;
  border-radius: 12px;
  background: #f7fafc;
  border: 2px solid #e2e8f0;
  padding: 14px 18px;
  min-height: 52px;
  font-size: 15px;
  color: #2d3748;
  transition: all 0.3s ease;
}

.form-input:hover {
  border-color: #cbd5e0;
  background: white;
}

.form-input:focus {
  outline: none;
  border-color: #667eea;
  background: white;
  box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
}

.form-extra {
  margin-bottom: 28px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
  color: #4a5568;
  font-weight: 500;
  cursor: pointer;
}

.submit-btn {
  width: 100%;
  height: 54px;
  border: none;
  border-radius: 14px;
  color: white;
  font-size: 17px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  font-family: 'PingFang SC', 'Helvetica Neue', 'Microsoft YaHei', sans-serif;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
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
}

.btn-arrow {
  width: 20px;
  height: 20px;
  transition: transform 0.3s ease;
}

.submit-btn:hover .btn-arrow {
  transform: translateX(4px);
}
</style>
