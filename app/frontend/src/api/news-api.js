import store from "@/store"; // 确保引入 Vuex store

/**
 * 获取 Axios 实例
 * @returns {Object} Axios 实例
 */
const getApiClient = () => {
  const apiClient = store.state.config.apiClient; // 从 Vuex 获取 Axios 实例
  if (!apiClient) {
    throw new Error("Axios instance is not initialized");
  }
  return apiClient;
};

/**
 * 获取 AI 新闻列表
 * @returns {Promise<Object[]>} 返回 AI 新闻数据数组
 * @throws {Error} 如果请求失败，抛出错误
 */
export const fetchAINews = async () => {
  const apiClient = getApiClient(); // 获取 Axios 实例
  try {
    const response = await apiClient.get("/news/aiList");
    return response.data;
  } catch (error) {
    throw new Error("获取新闻列表错误");
  }
};

export const fetchAllNews = async () => {
  const apiClient = getApiClient(); // 获取 Axios 实例
  try {
    const response = await apiClient.get("/news/allList");
    return response.data;
  } catch (error) {
    throw new Error("获取新闻列表错误");
  }
};

/**
 * 获取汽车新闻列表
 * @returns {Promise<Object[]>} 返回汽车新闻数据数组
 * @throws {Error} 如果请求失败，抛出错误
 */
export const fetchCarNews = async () => {
  const apiClient = getApiClient(); // 获取 Axios 实例
  try {
    const response = await apiClient.get("/news/carList");
    return response.data;
  } catch (error) {
    throw new Error("获取新闻列表错误");
  }
};

/**
 * 更新新闻数据
 * @param {Object} row - 要更新的新闻数据对象
 * @returns {Promise<Object>} 返回更新后的新闻数据
 * @throws {Error} 如果请求失败，抛出错误
 */
export const updateNews = async (row) => {
  const apiClient = getApiClient(); // 获取 Axios 实例
  try {
    const response = await apiClient.get("/news/updateNews", {
      params: {
        id: row.id, // 使用 params 对象来传递查询参数
      },
    });
    return response.data;
  } catch (error) {
    throw new Error("更新数据失败");
  }
};

/**
 * 发布新闻
 * @param {number[]} newsIds - 要发布的新闻 ID 列表
 * @param {string[]} selectedPlatforms - 选择的发布平台列表
 * @param {string} type - 组信息
 * @returns {Promise<void>} 无返回值
 * @throws {Error} 如果请求失败，抛出错误
 */
export const publishNews = async (newsIds, selectedPlatforms, type) => {
  const apiClient = getApiClient(); // 获取 Axios 实例
  try {
    await apiClient.post("/news/publish", {
      news_ids: newsIds,
      platforms: selectedPlatforms,
      type: type,
    });
  } catch (error) {
    throw new Error("发布请求失败");
  }
};

/**
 * 生成新闻
 * @returns {Promise<void>} 无返回值
 * @throws {Error} 如果请求失败，抛出错误
 */
export const generateNews = async () => {
  const apiClient = getApiClient(); // 获取 Axios 实例
  try {
    await apiClient.get("/news/generateNews");
  } catch (error) {
    throw new Error("生成请求失败");
  }
};

/**
 * 获取最新新闻
 * @returns {Promise<void>} 无返回值
 * @throws {Error} 如果请求失败，抛出错误
 */
export const getLatestNews = async () => {
  const apiClient = getApiClient(); // 获取 Axios 实例
  try {
    await apiClient.get("/news/getLatestNews");
  } catch (error) {
    throw new Error("获取最新新闻失败");
  }
};

/**
 * 删除新闻
 * @param {number[]} newsIds - 要删除的新闻 ID 列表
 * @returns {Promise<void>} 无返回值
 * @throws {Error} 如果请求失败，抛出错误
 */
export const deleteNews = async (newsIds) => {
  const apiClient = getApiClient(); // 获取 Axios 实例
  try {
    const response = await apiClient.post("/news/delete", {
      ids: newsIds,
    });
    return response.data;
  } catch (error) {
    throw new Error("删除请求失败");
  }
};

/**
 * 更新平台配置
 * @param {Object} configData - 平台配置数据对象，例如 WeChat、XingQiu 等平台的配置
 * @returns {Promise<Object>} 返回更新后的配置数据
 * @throws {Error} 如果请求失败，抛出错误
 */
export const updatePlatformConfig = async (configData) => {
  const apiClient = getApiClient(); // 获取 Axios 实例

  // 过滤掉值为空的字段
  const filteredConfigData = Object.fromEntries(
    Object.entries(configData).filter(
      ([_, value]) => value !== "" && value !== undefined && value !== null
    )
  );

  try {
    const response = await apiClient.post(
      "/platforms/updateConfig",
      filteredConfigData
    );
    return response.data;
  } catch (error) {
    throw new Error("更新平台配置失败");
  }
};

/**
 * 根据用户获取平台配置
 * @returns {Promise<Object>} 返回平台配置数据
 * @throws {Error} 如果请求失败，抛出错误
 */
export const getByUserPlatformConfig = async () => {
  const apiClient = getApiClient(); // 获取 Axios 实例
  try {
    console.log("正在请求平台配置...");
    const response = await apiClient.get("/platforms/getByUser");
    console.log("平台配置API响应:", response);
    return response.data;
  } catch (error) {
    console.error("获取平台配置失败:", error);
    throw new Error("获取平台配置失败: " + (error.message || "未知错误"));
  }
};

/**
 * 获取平台配置
 * @returns {Promise<Object>} 返回平台配置数据
 * @throws {Error} 如果请求失败，抛出错误
 */
export const getPlatformConfig = async () => {
  const apiClient = getApiClient(); // 获取 Axios 实例
  try {
    const response = await apiClient.get("/platforms/getByUser");
    return response.data;
  } catch (error) {
    throw new Error("获取平台配置失败");
  }
};

export const getCategoryALL = async () => {
  const apiClient = getApiClient(); // 获取 Axios 实例
  try {
    const response = await apiClient.get("/newsCategories/all");
    return response.data;
  } catch (error) {
    throw new Error("获取分类列表错误");
  }
};
