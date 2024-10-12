import axios from 'axios';
import store from '@/store';  // 确保正确引入 Vuex store
import router from '@/router';  // 引入 Vue Router

// 创建并配置 Axios 实例
function createApiClient(config) {
    if (!config.VITE_API_URL || !config.VITE_API_VERSION) {
        console.error("API URL or Version is not defined in the config");
        return null; // 防止 Axios 实例被错误创建
    }

    const apiClient = axios.create({
        baseURL: `${config.VITE_API_URL}${config.VITE_API_VERSION}`, // 使用存储的配置信息
        timeout: 30000,
        headers: {
            'Content-Type': 'application/json'
        }
    });

    // 请求拦截器 - 在每个请求发送前自动添加 token
    apiClient.interceptors.request.use(
        (config) => {
            const token = store.getters['user/isAuthenticated'] ? store.state.user.token : localStorage.getItem('accessToken');
            if (token) {
                config.headers['Authorization'] = `Bearer ${token}`;
            }
            return config;
        },
        (error) => Promise.reject(error)
    );

    // 响应拦截器 - 处理 401 和 403 错误，并重定向到首页
    apiClient.interceptors.response.use(
        (response) => response,
        (error) => {
            if (error.response) {
                const { status } = error.response;
                if (status === 401 || status === 403) {
                    store.dispatch('auth/logout');  // 确保清除登录状态
                    router.push('/');  // 重定向到首页
                }
            }
            return Promise.reject(error);
        }
    );

    return apiClient;
}

export default createApiClient;
