import { ref } from "vue";
import {
  getCategoryList as fetchCategoryList,
  fetchNewsByCategory,
  getRandomNewsItems as fetchHotNewsList,
  getWeather,
} from "@/api/index.js";

export default function useHome() {
  const categoryList = ref([]); // 存储分类列表
  const newsListData = ref([]); // 存储新闻数据
  const hotNewsListData = ref([]);
  const selectedChannel = ref(""); // 存储当前选中的频道
  const currentPage = ref(1); // 当前页码
  const pageSize = ref(20); // 每页显示数量
  const total = ref(0); // 总数据量
  const loading = ref(false); // 加载状态
  const hasMore = ref(true); // 是否还有更多数据

  const bannerImage = ref(
    "https://lf3-static.bytednsdoc.com/obj/eden-cn/uldnupqplm/fangchunzhijiantupian.jpg"
  );
  const bannerVideo = ref(
    "https://lf3-static.bytednsdoc.com/obj/eden-cn/uldnupqplm/fangchunzhijianshipin.mp4"
  );

  const hotVideos = ref([
    {
      title: "郑钦文日夜兼程回国参会，年轻一代正以平视姿态，展现中国自信",
      link: "https://www.toutiao.com/video/7407572516094345766/",
      cover:
        "https://p3-sign.toutiaoimg.com/tos-cn-i-dy/2f1a1aae53a9444b8b6a464a3b9a5616~tplv-pk90l89vgd-crop-center-v4:576:324.jpeg?_iz=31127&from=ttvideo.headline&lk3s=06827d14&x-expires=1725518539&x-signature=t5YU8fte6ZfE%2FdFHG%2FpfXyUwIm0%3D",
      duration: "05:54",
      views: "104万",
    },
    // 更多视频数据
  ]);

  // 获取当前日期，并格式化为 '08月29日 周四' 形式
  const formatDate = () => {
    const now = new Date();
    const month = now.getMonth() + 1; // 月份从0开始，所以要加1
    const day = now.getDate();
    const weekDay = ["周日", "周一", "周二", "周三", "周四", "周五", "周六"][
      now.getDay()
    ];

    return `${month.toString().padStart(2, "0")}月${day.toString().padStart(2, "0")}日 ${weekDay}`;
  };

  const weather = ref({
    city: "北京",
    description: "阴",
    temperature: "28℃",
    airQuality: "优",
    iconClass: "weather-icon-white-2",
    date: formatDate(),
    todayIconClass: "weather-icon-2",
    todayLow: "22℃",
    todayHigh: "30℃",
  });

  const fetchWeather = async () => {
    try {
      const data = await getWeather();
      if (
        !data?.error ||
        (typeof data.error === "string" &&
          !data.error.includes("无法获取地理位置信息"))
      ) {
        data.date = formatDate(); // 强制格式化日期
        weather.value = data;
      }
    } catch (error) {
      console.error("Error fetching weather:", error);
    }
  };
  const hotSearches = ref([
    "男子感染鹦鹉热高烧不退进ICU",
    "韩国国会正式通过具荷拉法",
  ]);

  const getCategoryList = async () => {
    categoryList.value = await fetchCategoryList();
  };

  const getRandomNewsItems = async () => {
    hotNewsListData.value = await fetchHotNewsList();
  };

  const fetchNewsByPage = async (isLoadMore = false) => {
    if (
      !selectedChannel.value ||
      loading.value ||
      (!isLoadMore && !hasMore.value)
    )
      return;

    loading.value = true;
    try {
      const skip = (currentPage.value - 1) * pageSize.value;
      console.log(
        `Fetching news for ${selectedChannel.value}, skip=${skip}, limit=${pageSize.value}`
      );

      const response = await fetchNewsByCategory(
        selectedChannel.value,
        skip,
        pageSize.value
      );

      console.log("API response:", response);

      if (!response || !response.data) {
        console.error("Invalid response format:", response);
        return;
      }

      console.log(
        `Received ${response.data.length} news items, total: ${response.total}`
      );

      if (isLoadMore) {
        // 加载更多时，追加数据但限制最大显示条数
        const combinedData = [...newsListData.value, ...response.data];
        console.log(`Combined data length: ${combinedData.length}`);

        // 限制最多显示40条数据
        const maxItemsToShow = 40;
        newsListData.value = combinedData.slice(-maxItemsToShow);
        console.log(
          `Final data length after limiting: ${newsListData.value.length}`
        );
      } else {
        // 首次加载或切换频道时，替换数据
        newsListData.value = response.data;
        console.log(
          `Setting initial data length: ${newsListData.value.length}`
        );
      }

      total.value = response.total || 0;
      hasMore.value = newsListData.value.length < total.value;
      console.log(
        `Has more data: ${hasMore.value}, Current page: ${currentPage.value}`
      );

      if (hasMore.value) {
        currentPage.value += 1;
      }
    } catch (error) {
      console.error("Error fetching news by page:", error);
    } finally {
      loading.value = false;
    }
  };

  const loadMore = () => {
    if (!loading.value && hasMore.value) {
      fetchNewsByPage(true);
    }
  };

  const changeChannel = async (channelName) => {
    selectedChannel.value = channelName;
    currentPage.value = 1;
    hasMore.value = true;
    await fetchNewsByPage();
  };

  // 返回状态和方法，以便在组件中使用
  return {
    categoryList,
    getCategoryList,
    newsListData,
    hotNewsListData,
    selectedChannel,
    changeChannel,
    getRandomNewsItems,
    weather,
    fetchWeather,
    bannerImage,
    bannerVideo,
    hotSearches,
    loading,
    hasMore,
    loadMore,
  };
}
