<template>
    <div>
        <el-card class="box-card">
            <div slot="header" class="clearfix">
                <span>账号管理</span>
            </div>
            <el-form :model="form" label-width="150px" ref="formRef">
                <!-- WeChat 配置 -->
                <el-form-item label="WeChat AppID">
                    <el-input v-model="form.wechat_appid" @focus="removeMask('wechat_appid')"
                        @blur="saveAndApplyMask('wechat_appid')" placeholder="请输入 WeChat AppID"></el-input>
                </el-form-item>
                <el-form-item label="WeChat Secret">
                    <el-input v-model="form.wechat_secret" @focus="removeMask('wechat_secret')"
                        @blur="saveAndApplyMask('wechat_secret')" placeholder="请输入 WeChat Secret"></el-input>
                </el-form-item>

                <!-- 小星球配置 -->
                <el-form-item label="星球 Access Token">
                    <el-input v-model="form.xing_qiu_access_token" @focus="removeMask('xing_qiu_access_token')"
                        @blur="saveAndApplyMask('xing_qiu_access_token')" placeholder="请输入 Access Token"></el-input>
                </el-form-item>
                <el-form-item label="星球 Session ID">
                    <el-input v-model="form.xing_qiu_session_id" @focus="removeMask('xing_qiu_session_id')"
                        @blur="saveAndApplyMask('xing_qiu_session_id')" placeholder="请输入 Session ID"></el-input>
                </el-form-item>
                <el-form-item label="星球 Group ID">
                    <el-input v-model="form.xing_qiu_group_id" @focus="removeMask('xing_qiu_group_id')"
                        @blur="saveAndApplyMask('xing_qiu_group_id')" placeholder="请输入 Group ID"></el-input>
                </el-form-item>

                <!-- 掘金配置 -->
                <el-form-item label="掘金 Session ID">
                    <el-input v-model="form.jue_jin_session_id" @focus="removeMask('jue_jin_session_id')"
                        @blur="saveAndApplyMask('jue_jin_session_id')" placeholder="请输入掘金 Session ID"></el-input>
                </el-form-item>

                <!-- 知乎配置 -->
                <el-form-item label="知乎 Cookie">
                    <el-input v-model="form.zhi_hu_cookie" @focus="removeMask('zhi_hu_cookie')"
                        @blur="saveAndApplyMask('zhi_hu_cookie')" placeholder="请输入知乎 Cookie"></el-input>
                </el-form-item>

                <!-- APIKEY配置 -->
                <el-form-item label="APIKEY">
                    <el-input v-model="form.apikey" @focus="removeMask('apikey')" @blur="saveAndApplyMask('apikey')"
                        placeholder="请输入 API Key"></el-input>
                </el-form-item>

                <!-- Prompt 配置 -->
                <el-form-item label="Prompt">
                    <el-input v-model="form.prompt"
                        placeholder='1.You are a professional news editor.\n2.Based on the provided link, title, and original content, assess the consistency of the content with the title.\n3.If the original content is consistent with the title, summarize the core content of the article;\n4.If the original content does not match the title, or if it is a page verification like Cloudflare, ignore the original content and base your summary solely on the title.\n5.Using the above rules, generate a new title and rehashed content from the provided title, link, and original content. The new content should be summarized in simplified Chinese and be approximately 350 Chinese characters long.\n6.Ensure the content is concise and accurate, while adhering to the required format. The content should follow the format below:\n标题: xxxx\n内容: xxxx.\n7.Ensure the generated content does not contain words like \"本文\" or \"文章\" or \"**\" or \"#\" and does not include any article links. Summarizing the gist of the article in the conclusion is not allowed.'></el-input>
                </el-form-item>

                <!-- Chat Model 配置为下拉框 -->
                <el-form-item label="Chat Model">
                    <el-select v-model="form.chat_model" placeholder="请选择 Chat Model">
                        <el-option v-for="model in chatModels" :key="model.value" :label="model.label"
                            :value="model.value"></el-option>
                    </el-select>
                </el-form-item>

                <!-- 保存按钮 -->
                <el-form-item>
                    <el-button type="primary" @click="saveConfig" :loading="loading">保存配置</el-button>
                </el-form-item>
            </el-form>
        </el-card>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import { usePlatformConfig } from '@/composables/usePlatform'; // 引入组合式函数

// 用于存储表单数据
const form = ref({
    wechat_appid: '',
    wechat_secret: '',
    xing_qiu_access_token: '',
    xing_qiu_session_id: '',
    xing_qiu_group_id: '',
    jue_jin_session_id: '',
    zhi_hu_cookie: '',
    apikey: '',
    prompt: '',
    chat_model: ''
});

// Chat Model 下拉框的选项
const chatModels = ref([
    { value: 'gemma2-9b-it', label: 'gemma2-9b-it - 8k - $0.2 - 0.25s' },
    { value: 'llama-3.1-70b-versatile', label: 'llama-3.1-70b-versatile-128k - $0.79 - 0.41s' },
    { value: 'llama3-70b-8192', label: 'llama3-70b-8192 - 8k - $0.79 - 0.24s' },
    { value: 'llama-3.1-8b-instant', label: 'llama-3.1-8b-instant - 128k - $0.08 - 0.39s' }
]);

// 从 usePlatformConfig 组合式函数中解构出 updateConfig, getPlatformConfig 和 loading
const { updateConfig, getPlatformConfig, loading } = usePlatformConfig();

// 存储初始值，用于恢复遮掩
const originalValues = {};

// 添加星号的方法（中间部分替换为星号）
const maskMiddle = (str) => {
    if (!str || str.length < 6) return str; // 对长度小于6的字符串不进行处理
    const visibleChars = 3; // 显示头尾的字符数
    const maskedLength = str.length - 2 * visibleChars; // 需要用星号替代的字符数
    const maskedPart = '*'.repeat(maskedLength); // 替换部分为星号
    return str.slice(0, visibleChars) + maskedPart + str.slice(-visibleChars); // 拼接结果
};

// 取消遮掩，显示原始数据
const removeMask = (key) => {
    form.value[key] = originalValues[key];
};

// 保存用户输入并应用星号遮掩
const saveAndApplyMask = (key) => {
    originalValues[key] = form.value[key]; // 更新 originalValues
    applyMask(key); // 应用遮掩
};

// 重新应用星号遮掩
const applyMask = (key) => {
    form.value[key] = maskMiddle(originalValues[key]);
};

// 获取平台配置数据并初始化表单
const loadPlatformConfig = async () => {
    try {
        const platformConfig = await getPlatformConfig(); // 调用 API 获取数据
        console.log(platformConfig)
        if (platformConfig) {
            form.value = platformConfig
            // 保存原始值并应用遮掩
            for (const key in form.value) {
                originalValues[key] = form.value[key]; // 存储原始值
                applyMask(key); // 应用遮掩
            }
        }
    } catch (error) {
        ElMessage.error('无法加载平台配置，请重试');
    }
};

// 在页面加载时获取配置数据
onMounted(() => {
    loadPlatformConfig();
});

// 保存配置的函数，调用 API 更新配置
const saveConfig = async () => {
    const configData = {}; // 用于存储要发送到后端的真实数据

    // 遍历 originalValues，确保传递的是未被遮掩的值
    for (const key in originalValues) {
        configData[key] = originalValues[key]; // 保存真实的原始值
    }

    // 检查是否有值被修改，如果所有值都是空的则不保存
    const hasValue = Object.values(configData).some(value => value && value.trim() !== '');
    if (!hasValue) {
        ElMessage.warning('没有修改任何配置');
        return;
    }

    try {
        await updateConfig(configData); // 调用组合式函数更新配置
        ElMessage.success('配置已成功保存！');
    } catch (error) {
        ElMessage.error('配置保存失败，请重试');
    }
};
</script>


<style scoped>
.el-form {
    margin-top: 30px;
}

.box-card {
    margin: 20px;
}
</style>
