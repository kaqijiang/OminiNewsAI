// src/store/config.js
import createApiClient from '@/api/apiClient';

const state = {
    config: {},
    apiClient: null,  // 存储 Axios 实例
};

const mutations = {
    setConfig(state, config) {
        state.config = config;
    },
    setApiClient(state, apiClient) {
        state.apiClient = apiClient;
    }
};

const actions = {
    initializeConfig({ commit }, config) {
        commit('setConfig', config);

        // 调用 createApiClient 只创建一次 Axios 实例
        const apiClient = createApiClient(config);
        commit('setApiClient', apiClient);
    }
};

export default {
    namespaced: true,
    state,
    mutations,
    actions,
};
