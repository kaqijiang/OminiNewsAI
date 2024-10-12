import store from '@/store';  // 确保引入 Vuex store

/**
 * 获取 Axios 实例
 * @returns {Object} Axios 实例
 */
const getApiClient = () => {
  const apiClient = store.state.config.apiClient;  // 从 Vuex 获取 Axios 实例
  if (!apiClient) {
    throw new Error('Axios instance is not initialized');
  }
  return apiClient;
};

/**
 * 获取分类列表
 * @returns {Promise<Object[]>} 返回分类数据数组
 * @throws {Error} 如果请求失败，抛出错误
 */
export const getCategoryList = async () => {
  const apiClient = getApiClient();  // 获取 Axios 实例
  try {
    const response = await apiClient.get('/newsCategories/list');
    return response.data.news_items;
  } catch (error) {
    throw new Error('获取分类列表错误');
  }
};

/**
 * 根据分类获取具体内容
 * @param {string} categoryName 分类名称 
 * @returns {Promise<Object[]>} 返回新闻数据数组
 * @throws {Error} 如果请求失败，抛出错误
 */
export const fetchNewsByCategory = async (categoryName) => {
  const apiClient = getApiClient();  // 获取 Axios 实例
  try {
    const response = await apiClient.get('/news/readNewsByCategory', {
      params: {
        category_name: categoryName
      }
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching news by category:', error);
    throw error;
  }
};

/**
 * 获取随机新闻
 * @returns {Promise<Object[]>} 返回随机新闻数据数组
 * @throws {Error} 如果请求失败，抛出错误
 */
export const getRandomNewsItems = async () => {
  const apiClient = getApiClient();  // 获取 Axios 实例
  try {
    const response = await apiClient.get('/news/hotNewsItems');
    return response.data;
  } catch (error) {
    console.error('Error fetching random news:', error);
    throw error;
  }
};

/**
 * 获取天气信息
 * @returns {Promise<Object>} 返回天气数据
 * @throws {Error} 如果请求失败，抛出错误
 */
export const getWeather = async () => {
  const apiClient = getApiClient();  // 获取 Axios 实例
  try {
    const response = await apiClient.get('/utils/weather');
    return response.data;
  } catch (error) {
    console.error('Error fetching weather:', error);
    throw error;
  }
};

/**
 * 登录
 * @param {string} username 用户名
 * @param {string} password 密码
 * @returns {Promise<Object>} 返回登录响应数据
 * @throws {Error} 如果请求失败，抛出错误
 */
export const login = async (username, password) => {
  const apiClient = getApiClient();  // 获取 Axios 实例
  try {
    // 构建表单数据
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);

    // 发送 POST 请求，并携带表单数据
    const response = await apiClient.post('/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });

    return response.data;
  } catch (error) {
    console.error('Error during login:', error);
    throw error;
  }
};

/**
 * 获取流式数据
 * @param {string} query 搜索关键词
 * @param {function} onMessage 消息处理回调
 * @param {function} onError 错误处理回调
 * @returns {EventSource} 返回流连接实例
 */
export const fetchStream = async (query, onMessage, onError) => {
  try {
    const config = window.__ENV__;  // 使用全局注入的 config.js
    const baseURL = `${config.VITE_API_URL}${config.VITE_API_VERSION}`;
    const url = `${baseURL}/utils/search?query=${encodeURIComponent(query)}`;
    const eventSource = new EventSource(url);

    let combinedMessage = '';  // 用于存储合并后的消息

    eventSource.onmessage = (event) => {
      const data = event.data;

      if (data.includes('[DONE]')) {
        console.log('Stream has ended with [DONE]');
        eventSource.close();  // 关闭连接
      } else {
        try {
          const parsedData = JSON.parse(data);
          combinedMessage += parsedData.message;  // 拼接消息
          onMessage({ message: combinedMessage });  // 更新整个消息
        } catch (e) {
          console.error('Failed to parse message as JSON', e);
        }
      }
    };

    eventSource.onerror = (error) => {
      console.error('Stream encountered an error:', error);
      onError(error);
      eventSource.close();  // 在错误时关闭连接
    };

    return eventSource;
  } catch (error) {
    console.error('Error fetching stream:', error);
    throw error;
  }
};
