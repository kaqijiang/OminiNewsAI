// src/store/index.js
import { createStore } from 'vuex';
import user from './user';
import auth from './auth';
import config from './config';  // 引入 config 模块

export default createStore({
  modules: {
    user,  // 注册 user 模块
    auth,  // 注册 auth 模块
    config  // 注册 config 模块
  }
});
