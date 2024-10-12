<template>
    <div v-if="isModalVisible" class="ttp-modal-wrapper ttp-login-modal modal-show modal-anime-show">
        <div class="ttp-modal-mask"></div>
        <div role="dialog" aria-modal="true" aria-label="登录管理后台" class="ttp-modal">
            <div class="ttp-modal-header">
                <span class="ttp-modal-title">登录</span>
                <button type="button" aria-label="关闭弹窗" class="ttp-modal-close-btn" @click="closeLoginModal">
                    <i></i>
                </button>
            </div>
            <div class="ttp-modal-body">
                <div id="login_modal_ele">
                    <div class="web-login-container">
                        <article class="web-login">
                            <article class="web-login-union">
                                <div class="web-login-union__login">
                                    <div class="web-login-union__login__form">
                                        <div class="web-login-union__login__form__content">
                                            <article class="web-login-mobile-code">
                                                <div class="web-login-mobile-code__mobile-input-wrapper">
                                                    <div class="web-login-normal-input">
                                                        <input name="normal-input" type="text"
                                                            class="web-login-normal-input__input first-focus-el"
                                                            placeholder="请输入账号" autocomplete="username" maxlength="50"
                                                            tabindex="0" aria-label="请输入账号" v-model="username">
                                                    </div>
                                                </div>
                                                <div class="web-login-mobile-code__code-input-wrapper">
                                                    <div class="web-login-button-input">
                                                        <div class="web-login-button-input__input-wrapper send-input">
                                                            <input name="button-input" type="password"
                                                                class="web-login-button-input__input"
                                                                placeholder="请输入密码" autocomplete="current-password"
                                                                maxlength="50" tabindex="0" aria-label="请输入密码"
                                                                v-model="password">
                                                        </div>
                                                    </div>
                                                </div>
                                                <div v-if="errorMessage" class="web-login-error" role="alert"
                                                    aria-relevant="all" tabindex="0" aria-live="assertive"
                                                    aria-atomic="true">
                                                    {{ errorMessage }}
                                                </div>
                                                <div class="web-login-mobile-code__button-wrapper">
                                                    <button type="submit" class="web-login-button"
                                                        :class="{ 'web-login-button__disabled': !username || !password }"
                                                        :disabled="!username || !password"
                                                        @click.prevent="handleLogin">登录</button>
                                                </div>
                                            </article>
                                        </div>
                                    </div>
                                </div>
                            </article>
                        </article>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref } from 'vue';
import { useStore } from 'vuex';
import { useRouter } from 'vue-router';
import { login, getPlatformConfig } from "@/api/index.js";
import { defineExpose } from 'vue';

const isModalVisible = ref(false);
const username = ref('');
const password = ref('');
const errorMessage = ref('');

const store = useStore();
const router = useRouter();

const openLoginModal = () => {
    isModalVisible.value = true;
};

const closeLoginModal = () => {
    isModalVisible.value = false;
};

const handleLogin = async () => {
    if (!username.value || !password.value) {
        errorMessage.value = '信息不能为空';
        return;
    }

    try {
        const response = await login(username.value, password.value);

        const { access_token, user } = response;

        if (!access_token || !user) {
            throw new Error('登录数据无效');
        }

        store.dispatch('user/login', { access_token, user });  // 注意 'user/' 前缀

        console.log('更新后的状态:', store.state);

        closeLoginModal();
        router.push('/admin');
    } catch (error) {
        errorMessage.value = '登录失败，请检查账号或密码';
    }
};

// 暴露方法供外部调用
defineExpose({
    openLoginModal,
    closeLoginModal
});
</script>

<style scoped>
.web-login-button__disabled {
    background-color: #ccc;
    cursor: not-allowed;
}
</style>
