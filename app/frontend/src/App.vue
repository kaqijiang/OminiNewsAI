<template>
  <div id="app">
    <router-view></router-view>
  </div>
</template>

<script>
import { useStore } from 'vuex';

export default {
  name: 'App',
  created() {
    const store = useStore();
    store.dispatch('user/restoreAuthState'); // 恢复鉴权状态时使用命名空间
  }
}
</script>

<style>
/* 添加全局样式 */
</style>
