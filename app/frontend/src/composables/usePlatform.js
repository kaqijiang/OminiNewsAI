import { ref } from 'vue';
import { ElMessage } from 'element-plus';
import { updatePlatformConfig, getByUserPlatformConfig } from '@/api/index.js'; // 导入 API 函数

export function usePlatformConfig() {
    const loading = ref(false);

    /**
     * 更新平台配置
     * @param {Object} configData - 平台配置数据对象
     * @returns {Promise<void>}
     */
    const updateConfig = async (configData) => {  // 这里把 `updatePlatformConfig` 改成 `updateConfig`
        loading.value = true;
        try {
            const result = await updatePlatformConfig(configData);
        } catch (error) {
            console.error('更新配置时出错:', error);
        } finally {
            loading.value = false;
        }
    };

    const getPlatformConfig = async (configData) => {  // 这里把 `updatePlatformConfig` 改成 `updateConfig`
        loading.value = true;
        try {
            const result = await getByUserPlatformConfig(configData);
            return result
        } catch (error) {
            console.error('更新配置时出错:', error);
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
