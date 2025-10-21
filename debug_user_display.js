// 调试用户显示问题的脚本
// 在浏览器控制台中运行

console.log('🔍 开始调试用户显示问题...');

// 1. 检查本地存储
console.log('📦 检查本地存储:');
console.log('localStorage:', localStorage);
console.log('sessionStorage:', sessionStorage);

// 2. 清除所有缓存
console.log('🧹 清除所有缓存...');
localStorage.clear();
sessionStorage.clear();

// 3. 检查Pinia store中的用户数据
console.log('🗄️ 检查Pinia用户存储:');
if (window.__VUE_DEVTOOLS_GLOBAL_HOOK__ && window.__VUE_DEVTOOLS_GLOBAL_HOOK__.apps) {
    const app = window.__VUE_DEVTOOLS_GLOBAL_HOOK__.apps[0];
    if (app && app._instance && app._instance.appContext.app.config.globalProperties.$pinia) {
        const pinia = app._instance.appContext.app.config.globalProperties.$pinia;
        console.log('Pinia stores:', pinia._s);
        
        // 查找用户store
        for (let [key, store] of pinia._s) {
            if (key.includes('user')) {
                console.log(`用户Store (${key}):`, store);
                if (store.users) {
                    console.log('用户列表:', store.users);
                    console.log('用户数量:', store.users.length);
                }
            }
        }
    }
}

// 4. 直接调用API检查
console.log('🌐 直接调用API检查用户数据:');
fetch('/api/users/', {
    method: 'GET',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token') || sessionStorage.getItem('token')}`
    }
})
.then(response => {
    console.log('API响应状态:', response.status);
    return response.json();
})
.then(data => {
    console.log('API返回数据:', data);
    if (data.success && data.data) {
        console.log('✅ 用户总数:', data.data.length);
        console.log('👥 用户列表:');
        data.data.forEach((user, index) => {
            console.log(`  ${index + 1}. ${user.name} (${user.username}) - ${user.position}`);
        });
        
        // 检查是否包含毕庆鹏
        const biqingpeng = data.data.find(u => u.name === '毕庆鹏');
        if (biqingpeng) {
            console.log('✅ 找到毕庆鹏:', biqingpeng);
        } else {
            console.log('❌ 未找到毕庆鹏用户');
        }
    } else {
        console.log('❌ API调用失败:', data.message);
    }
})
.catch(error => {
    console.log('❌ API调用出错:', error);
});

// 5. 建议的解决方案
console.log(`
🔧 解决方案建议:
1. 刷新页面: location.reload()
2. 清除缓存后刷新: localStorage.clear(); sessionStorage.clear(); location.reload()
3. 手动重新获取用户数据（如果有userStore.fetchUsers方法）
4. 检查网络请求是否被拦截或缓存
`);

console.log('🔍 调试完成！请查看上面的输出结果。');

