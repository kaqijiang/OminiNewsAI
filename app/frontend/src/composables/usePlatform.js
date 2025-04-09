import { ref } from "vue";
import { ElMessage } from "element-plus";
import { updatePlatformConfig, getByUserPlatformConfig } from "@/api/index.js"; // 导入 API 函数

export function usePlatformConfig() {
  const loading = ref(false);

  /**
   * 更新平台配置
   * @param {Object} configData - 平台配置数据对象
   * @returns {Promise<void>}
   */
  const updateConfig = async (configData) => {
    // 这里把 `updatePlatformConfig` 改成 `updateConfig`
    loading.value = true;
    try {
      const result = await updatePlatformConfig(configData);
    } catch (error) {
      console.error("更新配置时出错:", error);
    } finally {
      loading.value = false;
    }
  };

  const getPlatformConfig = async (configData) => {
    // 这里把 `updatePlatformConfig` 改成 `updateConfig`
    loading.value = true;
    try {
      const result = await getByUserPlatformConfig(configData);
      console.log("获取到的平台配置:", result);
      if (!result) {
        console.error("平台配置返回为空");
        throw new Error("平台配置返回为空");
      }
      return result;
    } catch (error) {
      console.error("获取平台配置时出错:", error);
      throw error;
    } finally {
      loading.value = false;
    }
  };

  return {
    updateConfig, // 返回改名后的 `updateConfig` 函数
    getPlatformConfig,
    loading,
  };
}
