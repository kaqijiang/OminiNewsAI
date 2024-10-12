import { createRouter, createWebHistory } from 'vue-router';
import Home from '@/views/Home.vue';
import Admin from '@/views/Admin.vue';
import store from '../store'; // 假设你使用 Vuex 进行状态管理

// 路由配置
const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/admin',
    name: 'Admin',
    component: Admin,
    meta: { requiresAuth: true, requiresAdmin: true },  // 需要鉴权和管理员权限
  }
];

// 创建路由实例
const router = createRouter({
  history: createWebHistory(),
  routes
});

router.beforeEach(async (to, from, next) => {
  await store.dispatch('user/restoreAuthState'); // 注意命名空间 'user/'


  const isAuthenticated = store.getters['user/isAuthenticated'];  // 检查用户是否已登录
  const user = store.state.user.user;  // 获取用户信息

  if (to.matched.some(record => record.meta.requiresAuth)) {
    // 需要登录验证
    if (!isAuthenticated) {
      next('/');  // 如果没有登录，重定向到登录页面
    } else if (to.matched.some(record => record.meta.requiresAdmin)) {
      // 需要管理员权限
      if (user && user.is_superuser) {
        next();  // 如果是管理员，允许访问
      } else {
        next('/');  // 如果不是管理员，重定向到首页或其他页面
      }
    } else {
      next();  // 已登录，且不需要管理员权限，直接放行
    }
  } else {
    next();  // 对于不需要鉴权的页面，直接放行
  }
});

export default router;
