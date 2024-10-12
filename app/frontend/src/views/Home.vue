<template>
    <div id="root">
        <div class="home-container new-style">
            <!-- 固定头部 -->
            <div class="fix-header common-component-wrapper" style="display: none; transform: translate(0px, 64px);">
                <div>
                    <a class="logo" aria-label="ominiai徽标" href="https://www.ominiai.cn/" rel="nofollow"></a>
                    <div class="feed-m-nav">
                        <ul class="feed-default-nav">
                            <li v-for="(channel, index) in categoryList" :key="index" tabindex="0" role="button"
                                :aria-label="channel" @click="changeChannel(channel)">
                                <div class="show-monitor">
                                    <div class="feed-default-nav-item">{{ channel }}</div>
                                </div>
                            </li>
                        </ul>
                    </div>
                    <div style="flex: 1 1 0%; min-width: 40px;"></div>
                    <!-- <div class="search-wrapper red">
                        <div class="search">
                            <input type="text" placeholder="问AI" aria-label="搜索" @keyup.enter="fetchSearchResult"
                                v-model="searchText">
                            <button type="button" aria-label="搜索" @click="fetchSearchResult">
                                <i></i><span>搜索</span>
                            </button>
                        </div>
                    </div> -->
                    <a class="login-button" rel="nofollow" @click="openLogin">登录</a>
                </div>
            </div>

            <!-- 横幅 -->
            <div class="show-monitor show-monitor-block">
                <div role="banner" aria-label="背景大图">
                    <div class="home-banner-wrapper">
                        <div class="home-banner" :style="{ transform: 'translate3d(0px, 0.5px, 0px)' }">
                            <div class="video-poster" :style="{ backgroundImage: 'url(' + bannerImage + ')' }"></div>
                            <video :src="bannerVideo" muted loop playsinline preload="auto" autoplay></video>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 头部 -->
            <div role="banner" aria-label="头部" class="toutiao-header">
                <div class="header-left"></div>
                <div class="header-right common-component-wrapper">
                    <div role="button" tabindex="0" class="weather-wrapper">
                        <div class="weather-abstract">
                            <span class="time">{{ weather.date + ' ' }}</span>
                            <span>{{ weather.city }}</span>
                            <i :class="['weather-icon', weather.iconClass]" aria-hidden="true"
                                :title="weather.description"></i>
                            <span class="city_state">{{ weather.description }}</span>
                            <span class="city_temperature">{{ weather.temperature }}</span>
                            <span class="air">{{ weather.airQuality }}</span>
                        </div>
                        <div role="dialog" aria-modal="true" aria-label="天气"
                            class="weather-hover ttp-popup-container popup-anime-hide popup-hide">
                            <div class="w-header">
                                <i class="header-bg"></i>
                                <button type="button" class="change weather-change-button">切换</button>
                                <span class="time">{{ weather.date }}</span>
                            </div>
                            <ul class="days-weather">
                                <li class="day">
                                    <span class="time">{{ weather.date + ' ' }}</span>
                                    <i :class="['weather-icon', weather.todayIconClass]"></i>
                                    <span class="temperature"><em>{{ weather.todayLow }}</em> ~ {{ weather.todayHigh
                                        }}</span>
                                </li>
                            </ul>
                        </div>
                    </div>
                    <a class="login-button" rel="nofollow" @click="openLogin">登录</a>
                </div>
            </div>

            <!-- 搜索区 -->
            <div role="search" class="search-container new-style">
                <div class="search-wrapper main-search white">
                    <a class="logo" aria-label="OMINIAI" href="https://www.ominiai.cn/" rel="nofollow"></a>
                    <div class="search">
                        <input type="text" placeholder="" aria-label="搜索" v-model="searchText"
                            @keyup.enter="fetchSearchResult" autofocus>
                        <button type="button" aria-label="搜索" @click="fetchSearchResult">
                            <i></i><span>搜索</span>
                        </button>
                    </div>
                    <div v-show="searchResult" class="show-monitor" style="width: 100%">
                        <div id="text-display" class="text-display" @click.stop>
                            <p id="search-result" v-text="searchResult"></p>
                        </div>
                        <!-- <div role="region" aria-label="热搜" class="hot-word">
                            <span class="hot">热搜：</span>
                            <div class="show-monitor" v-for="(item, index) in hotSearches" :key="index">
                                <span tabindex="0" role="link" class="words">{{ item }}</span>
                            </div>
                        </div> -->
                    </div>
                </div>

            </div>
            <!-- 主内容 -->
            <div class="main-content">
                <div role="main" class="left-container">
                    <div class="show-monitor">
                        <div>
                            <div class="ttp-feed-module">
                                <div class="main-nav-wrapper" style="margin-bottom:8px">
                                    <div class="feed-m-nav">
                                        <ul class="feed-default-nav">
                                            <li v-for="(item, index) in categoryList" :key="index" tabindex="0"
                                                role="button" :aria-label="item" @click="changeChannel(item)">
                                                <div class="show-monitor">
                                                    <div class="feed-default-nav-item"
                                                        :class="{ active: selectedChannel === item }">
                                                        {{ item }}
                                                    </div>
                                                </div>
                                            </li>

                                        </ul>
                                    </div>
                                </div>
                                <div>
                                    <div class="feed-card-wrapper feed-card-article-wrapper"
                                        v-for="(article, index) in newsListData" :key="index">
                                        <div class="feed-card-article multi-cover">
                                            <div class="feed-card-article-l">
                                                <!-- 1. 显示文章序号 -->
                                                <span class="article-index">{{ index + 1 }}.</span>

                                                <!-- 2. 显示处理后的标题，点击跳转到原文 -->
                                                <a class="feed-card-article-title" :href="article.source_url"
                                                    rel="nofollow" target="_blank" :title="article.title">
                                                    {{ article.processed_title }}
                                                </a>

                                                <!-- 3. 显示内容 -->
                                                <div class="article-content">
                                                    {{ article.processed_content }}
                                                </div>

                                                <!-- 4. 显示时间和来源 -->
                                                <div class="article-meta">
                                                    <span class="article-time">{{ formatDate(article.create_time)
                                                        }}</span> |
                                                    <span class="article-source">{{ article.type }}</span>
                                                    <!-- |<span class="article-source">{{ '内容由AI总结，点击标题跳转原文' }}</span> -->
                                                </div>
                                            </div>
                                            <div class="feed-card-article-r">
                                                <!-- 如果存在图片链接，显示图片 -->
                                                <img v-if="article.image" :src="article.image" alt="文章封面"
                                                    class="cover-image">
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="right-container">
                    <div class="show-monitor">
                        <div class="home-hotboard">
                            <div style="position: static;">
                                <div class="ttp-hot-board">
                                    <div class="title-bar">
                                        <h2 class="title">资讯热榜</h2><button type="button" class="refresh"
                                            @click="getRandomNewsItems">换一换</button>
                                    </div>
                                    <ol>
                                        <li v-for="(article, index) in hotNewsListData" :key="index">
                                            <!-- <a class="feed-card-article-title" :href="article.source_url" rel="nofollow"
                                                target="_blank" :title="article.title">
                                                {{ article.processed_title }}
                                            </a> -->
                                            <a :aria-label="article.description" class="article-item"
                                                :href="article.source_url" target="_blank" rel="noopener nofollow">
                                                <span class="news-index" :class="'num-' + (index + 1)">{{ index + 1
                                                    }}</span>
                                                <p class="news-title" :title="article.title">{{
                                                    article.processed_title }}</p>
                                                <i class="news-icon" :class="article.iconClass"></i>
                                            </a>
                                        </li>
                                    </ol>
                                </div>
                                <div class="download-app-banner">
                                    <div class="download-app-banner-left">
                                        <div class="download-app-banner-title">关注视频号&公众号</div>
                                        <div class="download-app-banner-desc">了解最新AI资讯</div>
                                    </div>
                                    <div class="download-app-banner-right"
                                        style="background-image:url(https://image.ominiai.cn/ai.png)">
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <!-- <div class="show-monitor" style="display: none;">
                        <div role="complementary" aria-label="热门视频" class="hot-video">
                            <div>
                                <div class="pane-header">
                                    <h2 class="header icon-video">热门视频</h2>
                                    <button type="button" class="right" aria-label="换一换热门视频" @click="changeVideos">
                                        <img src="https://lf-dw.toutiaostatic.com/obj/toutiao-duanwai/toutiao/toutiao_web_pc/svgs/rotate_new.3094a784.svg"
                                            style="transform:rotate(0deg)" alt="">
                                        <span>换一换</span>
                                    </button>
                                </div>
                                <div class="video-list hot-video-list">
                                    <div class="video-item" v-for="(video, index) in hotVideos" :key="index">
                                        <a tabindex="-1" aria-hidden="true" class="left-img" :href="video.link"
                                            target="_blank" rel="noopener nofollow">
                                            <img class="pic" :src="video.cover" alt="封面" loading="lazy">
                                            <p class="number" :class="'num' + (index + 1)">{{ index + 1 }}</p>
                                            <p class="duration">{{ video.duration }}</p>
                                        </a>
                                        <div class="right-content">
                                            <a class="title" :title="video.title" :href="video.link" target="_blank"
                                                rel="noopener nofollow">{{ video.title }}</a>
                                            <p class="desc">
                                                <span>{{ video.views }}次观看</span>
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div> -->
                    <div role="contentinfo" aria-label="公司执照" class="company-wrapper" style="margin-top: 20px;">
                        <p> © <!-- -->2024<!-- --> OMINIAI 资讯由AI总结生成，点击标题可跳转原文</p><br />
                        <a href="https://api.ominiai.cn" target="_blank"> API 由 OMINIAI 支持</a>
                    </div>
                </div>
            </div>
            <!-- <div class="ttp-toolbar">
                <ul class="tool-container">
                    <li tabindex="0" role="button" aria-label="刷新" class="tool-item refresh">刷新</li>
                    <li tabindex="0" role="button" aria-label="回到顶部" class="tool-item top" style="display: block; opacity:1;" @click="scrollToTop">顶部
                    </li>
                </ul>
            </div> -->

            <div role="contentinfo" aria-label="footer" class="footer-wrapper" style=" text-align: center;">
                <span></span>
            </div>
        </div>
    </div>
    <LoginModal ref="loginModal" />


</template>

<script setup>
import { ref, onMounted } from 'vue';
import useHome from '@/composables/useHome';
import { LoginModal } from '@/components';
import { useSearch } from '@/composables/useSearch'; // 确保正确导入 useSearch

// 使用 useSearch 中的状态和方法
const {
    searchText,
    searchResult,
    fetchSearchResult
} = useSearch();

const loading = ref(true);
const loginModal = ref(null);

// 使用 useHome 中的状态和方法
const {
    categoryList,
    getCategoryList,
    newsListData,
    selectedChannel,
    changeChannel,
    getRandomNewsItems,
    hotNewsListData,
    bannerImage,
    bannerVideo,
    weather,
    fetchWeather,
    hotSearches
} = useHome();

const openLogin = () => {
    if (loginModal.value) {
        loginModal.value.openLoginModal();
    }
};

// 格式化时间戳为易读的日期和时间
const formatDate = (timestamp) => {
    const date = new Date(timestamp * 1000);
    const options = { month: 'long', day: 'numeric' };
    return date.toLocaleDateString(undefined, options);
};

// 挂载时初始化数据
onMounted(async () => {
    loading.value = true;
    await getCategoryList();
    await getRandomNewsItems();
    await fetchWeather();

    if (categoryList.value.length > 0) {
        changeChannel(categoryList.value[0]);
    }
    loading.value = false;
});

</script>


<style scoped>
.article-index {
    font-weight: bold;
    margin-right: 8px;
}

.article-meta {
    margin-top: 10px;
    font-size: 0.9em;
    color: #888;
}

.article-time,
.article-source {
    margin-right: 5px;
}

.article-content {
    margin-top: 10px;
    color: #333;
    font-size: 1em;
    line-height: 1.6;
}

.text-display {
    margin-top: 20px;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 4px;
    background-color: #fff;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    height: 300px;
    overflow-y: auto;
}


.text-display p {
    margin: 0;
    color: #333;
}
</style>