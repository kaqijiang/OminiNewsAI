const state = {
    user: null,
    token: null,
};

const mutations = {
    setUser(state, user) {
        state.user = user;
    },
    setToken(state, token) {
        state.token = token;
    },
};

const actions = {
    login({ commit }, { access_token, user }) {
        // 保存 token 和 user 信息到 Vuex
        commit('setToken', access_token);
        commit('setUser', user);

        // 将 token 和 user 信息保存到 localStorage
        localStorage.setItem('accessToken', access_token);
        localStorage.setItem('user', JSON.stringify(user)); // 将 user 对象序列化为字符串
    },
    logout({ commit }) {
        // 清除 Vuex 中的 token 和 user 信息
        commit('setToken', null);
        commit('setUser', null);

        // 从 localStorage 中移除 token 和 user 信息
        localStorage.removeItem('accessToken');
        localStorage.removeItem('user');
    },
    restoreAuthState({ commit }) {
        // 从 localStorage 中恢复 token 和 user 信息
        const accessToken = localStorage.getItem('accessToken');
        const user = JSON.parse(localStorage.getItem('user')); // 将字符串解析为对象

        if (accessToken && user) {
            // 将恢复的信息提交到 Vuex
            commit('setToken', accessToken);
            commit('setUser', user);
        }
    }
};



const getters = {
    isAuthenticated: state => !!state.token,
    getUser: state => state.user,
};

export default {
    namespaced: true,  // 确保命名空间启用
    state,
    mutations,
    actions,
    getters,
};
