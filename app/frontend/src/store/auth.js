// modules/auth.js
const state = {
    token: null,
    user: null,
};

const mutations = {
    SET_TOKEN(state, token) {
        state.token = token;
    },
    SET_USER(state, user) {
        state.user = user;
    },
    LOGOUT(state) {
        state.token = null;
        state.user = null;
    }
};

const actions = {
    logout({ commit }) {
        commit('LOGOUT');
        localStorage.removeItem('accessToken');
        localStorage.removeItem('user');
    },
};

export default {
    namespaced: true, // 启用命名空间
    state,
    mutations,
    actions,
};
