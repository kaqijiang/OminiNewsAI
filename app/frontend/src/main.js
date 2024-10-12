// src/main.js
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

async function initApp() {
    try {
        // 动态加载 config.js
        if (typeof window.__ENV__ === 'undefined') {
            throw new Error('Config is not defined');
        }

        const config = window.__ENV__;  // 直接使用 window.__ENV__ 访问动态注入的配置

        // 使用 Vuex Action 初始化配置和 API 客户端
        store.dispatch('config/initializeConfig', config);

        const app = createApp(App);
        for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
            app.component(key, component);
        }

        app.use(ElementPlus).use(store).use(router).mount('#app');
    } catch (error) {
        console.error('Failed to initialize app:', error);
    }
}

initApp();
