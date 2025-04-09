<template>
  <div v-if="!isAuthenticated">
    <!-- 未登录状态，显示登录界面 -->
    <div class="login-container">
      <div class="login-card">
        <h2 class="login-title">登录管理后台</h2>
        <el-form :model="loginForm" ref="loginFormRef" label-width="0" class="login-form">
          <el-form-item prop="username" :rules="[{ required: true, message: '请输入账号', trigger: 'blur' }]">
            <el-input v-model="loginForm.username" placeholder="请输入账号" prefix-icon="User"></el-input>
          </el-form-item>
          <el-form-item prop="password" :rules="[{ required: true, message: '请输入密码', trigger: 'blur' }]">
            <el-input v-model="loginForm.password" type="password" placeholder="请输入密码" prefix-icon="Lock" show-password></el-input>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleLogin" :loading="loginLoading" class="login-button">登录</el-button>
          </el-form-item>
        </el-form>
        <p v-if="loginError" class="login-error">{{ loginError }}</p>
        <p class="back-to-home">
          <el-button link @click="goHome">返回首页</el-button>
        </p>
      </div>
    </div>
  </div>
  <el-container v-else style="height: 100vh">
    <!-- 已登录状态，显示管理后台 -->
    <el-header class="main-header">
      <div class="header-content">
        <div class="logo" @click="goHome" style="cursor: pointer">OMINAI</div>
        <div class="nav-links">
          <div class="current-time">{{ currentTime }}</div>
          <el-button link @click="handleLogout" class="logout-button">退出登录</el-button>
        </div>
      </div>
    </el-header>
    <el-container>
      <el-aside width="160px">
        <el-menu default-active="1" class="el-menu-vertical-demo" @select="handleSelect" text-color="#fff"
          background-color="#545c64" active-text-color="#ffd04b">
          <el-menu-item index="1">
            <i class="el-icon-menu"></i>
            <span slot="title">资讯列表</span>
          </el-menu-item>
          <!-- <el-menu-item index="2">
            <i class="el-icon-menu"></i>
            <span slot="title">汽车资讯</span>
          </el-menu-item> -->
          <el-menu-item index="3">
            <i class="el-icon-menu"></i>
            <span slot="title">账号管理</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      <el-container>
        <el-main class="main-content">
          <component :is="CurrentComponent"></component>
        </el-main>
      </el-container>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed } from 'vue';  // 从 'vue' 导入 computed
import { useStore } from 'vuex';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import useAdmin from '../composables/useAdmin.js';
import NewsList from './NewsList.vue';
import CarNewsList from './CarNewsList.vue';
import PublishRecords from './WelcomeItem.vue';
import AccountManagement from './Account.vue';
import { login } from '@/api/home-api';

// 使用 Vuex store
const store = useStore();
const isAuthenticated = computed(() => store.getters['user/isAuthenticated']);

// 登录表单
const loginForm = ref({
  username: '',
  password: ''
});
const loginFormRef = ref(null);
const loginLoading = ref(false);
const loginError = ref('');

// 使用 useAdmin 组合式函数
const { currentComponent, handleSelect, currentTime } = useAdmin();
const router = useRouter();

// 定义返回首页的函数
const goHome = () => {
  router.push('/');  // 跳转到首页
};

// 登录处理函数
const handleLogin = async () => {
  if (!loginForm.value.username || !loginForm.value.password) {
    loginError.value = '请输入账号和密码';
    return;
  }

  try {
    loginLoading.value = true;
    const response = await login(loginForm.value.username, loginForm.value.password);

    const { access_token, user } = response;

    if (!access_token || !user) {
      throw new Error('登录数据无效');
    }

    store.dispatch('user/login', { access_token, user });
    ElMessage.success('登录成功');
    loginError.value = '';
  } catch (error) {
    console.error('登录失败:', error);
    loginError.value = '登录失败，请检查账号或密码';
  } finally {
    loginLoading.value = false;
  }
};

// 退出登录
const handleLogout = () => {
  store.dispatch('user/logout');
  ElMessage.success('已退出登录');
  // 保留在当前页面，由于现在未认证，会显示登录表单
};

// 定义所有组件
const components = {
  NewsList,
  CarNewsList,
  PublishRecords,
  AccountManagement,
};

// 使用 computed 返回当前组件
const CurrentComponent = computed(() => components[currentComponent.value] || NewsList);

</script>

<style>
body {
  font-family: Arial, sans-serif;
  margin: 0;
  padding: 0;
  /* background-color: #f8f9fa; */
  color: #343a40;
  height: 100vh;
  /* overflow: hidden; */
}

#app {
  display: flex;
  flex-direction: column;
  height: 100vh;
  max-width: 2500px;
  min-width: 1200px;
  width: 100%;
  margin: 0;
  padding: 0;
}

.el-container {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.el-header {
  background-color: #f5f5f5;
  padding: 20px;
  border-bottom: 1px solid #ddd;
  box-sizing: border-box;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  height: 64px;
}

.logo {
  font-size: 20px;
  font-weight: bold;
}

.nav-links {
  display: flex;
  align-items: center;
}

.current-time {
  color: rgb(118, 107, 209);
  margin-right: 20px;
}

.logout-button {
  color: #f56c6c;
}

.el-aside {
  background-color: #545c64;
  padding: 0;
  border-right: 1px solid #ddd;
  flex: 0 0 auto;
  height: calc(100vh - 60px);
  /* 减去 header 的高度 */
  overflow: auto;
}

.el-aside .el-menu {
  border-right: 0;
}

.el-menu-item {
  border-bottom: 0.5px solid #555362;
}

.main-content {
  flex: 1;
  overflow: auto;
  background-color: #fff;
  padding: 20px;
}

.footer {
  background-color: #f5f5f5;
  padding: 20px;
  border-top: 1px solid #ddd;
  text-align: center;
}

/* 登录页面样式 */
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f0f2f5;
}

.login-card {
  width: 400px;
  padding: 40px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.login-title {
  text-align: center;
  margin-bottom: 30px;
  color: #409EFF;
}

.login-form {
  margin-bottom: 20px;
}

.login-button {
  width: 100%;
}

.login-error {
  color: #f56c6c;
  font-size: 14px;
  text-align: center;
  margin-top: 10px;
}

.back-to-home {
  text-align: center;
  margin-top: 20px;
}
</style>