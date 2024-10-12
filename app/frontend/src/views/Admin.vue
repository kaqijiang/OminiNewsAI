<template>
  <el-container style="height: 100vh">
    <el-header class="main-header">
      <div class="header-content">
        <div class="logo" @click="goHome" style="cursor: pointer">OMINAI</div>
        <div class="nav-links">
          <div class="current-time">{{ currentTime }}</div>
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
import useAdmin from '../composables/useAdmin.js';
import NewsList from './NewsList.vue';
import CarNewsList from './CarNewsList.vue';
import PublishRecords from './WelcomeItem.vue';
import AccountManagement from './Account.vue';
import { useRouter } from 'vue-router';

// 使用 useAdmin 组合式函数
const { currentComponent, handleSelect, currentTime } = useAdmin();
const router = useRouter();

// 定义返回首页的函数
const goHome = () => {
  router.push('/');  // 跳转到首页
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

.nav-links .current-time {
  color: rgb(118, 107, 209);
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
</style>