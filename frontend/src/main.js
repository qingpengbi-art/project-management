import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import 'element-plus/theme-chalk/dark/css-vars.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'

// 导入dayjs和所需插件
import dayjs from 'dayjs'
import isoWeek from 'dayjs/plugin/isoWeek'
import weekOfYear from 'dayjs/plugin/weekOfYear'
import weekYear from 'dayjs/plugin/weekYear'
import advancedFormat from 'dayjs/plugin/advancedFormat'
import localeData from 'dayjs/plugin/localeData'

import App from './App.vue'
import router from './router'
import './styles/main.scss'

// 扩展dayjs插件
dayjs.extend(isoWeek)
dayjs.extend(weekOfYear)
dayjs.extend(weekYear)
dayjs.extend(advancedFormat)
dayjs.extend(localeData)

const app = createApp(App)

// 注册Element Plus图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(createPinia())

// 初始化认证状态
import { useAuthStore } from '@/stores/auth'
const authStore = useAuthStore()
authStore.initAuth()

app.use(router)
app.use(ElementPlus, {
  locale: zhCn
})

// 配置全局消息提示
app.config.globalProperties.$message = ElMessage

app.mount('#app')
