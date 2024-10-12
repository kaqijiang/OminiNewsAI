import { ref, computed } from 'vue';
import { ElMessage } from 'element-plus';
import {
  getCategoryALL,
  fetchAINews,
  fetchCarNews,
  fetchAllNews,
  updateNews,
  publishNews,
  generateNews,
  getLatestNews,
  deleteNews
} from '@/api/index.js';  // 假设封装的 API 方法放在 @/api/index.js 中

export function useNews(newsType = 'ai') {
  const newsList = ref([]);
  const typeFilter = ref(''); // 大类选择
  const subTypeFilter = ref(''); // 子类选择
  const categories = ref([]);  // 存储从接口获取的分类数据
  const subTypes = ref([]);  // 用于存储子类选项
  const dateFilter = ref('');
  const titleNotEmptyFilter = ref(false);
  const noPushFilter = ref(false);
  const times = ref([]);
  const loading = ref(false);
  const selectedRows = ref([]);
  const publishDialogVisible = ref(false);
  const selectedPlatforms = ref([]);
  const publishStatus = ref({});
  const platforms = ref(['微信', '知识星球', '掘金', '知乎']);

  const types = ref([]);
  // const group = ref([]);

  // const formatDate = (dateString) => {
  //   const date = new Date(dateString * 1000);  // 将秒转换为毫秒
  //   return date.toISOString().split('T')[0];  // 返回 YYYY-MM-DD 格式的日期
  // };

  // 格式化时间戳为易读的日期和时间
  const formatDate = (timestamp) => {
    const date = new Date(timestamp * 1000);
    const options = { month: 'long', day: 'numeric' };
    return date.toLocaleDateString(undefined, options);
  };

  // 加载分类数据并分组
  const loadCategories = async () => {
    try {
      const data = await getCategoryALL();
      const categoryMap = {};

      // 遍历数据并按照 `category_name` 分组
      data.forEach(item => {
        if (!categoryMap[item.category_name]) {
          categoryMap[item.category_name] = [];
        }
        // 如果子类有值，将其添加到对应的类别下
        if (item.category_value) {
          categoryMap[item.category_name].push(item.category_value);
        }
      });

      // 将结果映射到 `categories` 中，用于展示大类和子类
      categories.value = Object.keys(categoryMap).map(categoryName => ({
        name: categoryName,
        subcategories: categoryMap[categoryName]
      }));

    } catch (error) {
      ElMessage.error('加载分类数据失败');
    }
  };

  // 选择大类时，更新子类选项
  const onCategoryChange = (category) => {
    typeFilter.value = category;
    const selectedCategory = categories.value.find(cat => cat.name === category);
    subTypes.value = selectedCategory ? selectedCategory.subcategories : [];
    subTypeFilter.value = '';
  };

  // const loadNews = async () => {
  //   try {
  //     loading.value = true;
  //     let data;
  //     if (newsType === 'car') {
  //       group.value = 1
  //       data = await fetchCarNews();
  //     } else {
  //       group.value = 0
  //       data = await fetchAINews();
  //     }

  //     if (Array.isArray(data)) {
  //       newsList.value = data;
  //       types.value = [...new Set(data.map(news => news.type))];
  //       times.value = [...new Set(data.map(news => formatDate(news.create_time)))];
  //     } else {
  //       console.error('获取的数据不是数组:', data);
  //       newsList.value = [];
  //       types.value = [];
  //       times.value = [];
  //     }
  //   } catch (error) {
  //     ElMessage.error(error.message);
  //   } finally {
  //     loading.value = false;
  //   }
  // };
  const loadNews = async () => {
    try {
      loading.value = true;

      // 获取所有类型的资讯
      const data = await fetchAllNews(); // 假设你有一个 API 可以获取所有资讯

      if (Array.isArray(data)) {
        newsList.value = data;
        // 提取所有资讯的类型和日期
        types.value = [...new Set(data.map(news => news.type))];
        times.value = [...new Set(data.map(news => formatDate(news.create_time)))];
      } else {
        console.error('获取的数据不是数组:', data);
        newsList.value = [];
        types.value = [];
        times.value = [];
      }
    } catch (error) {
      ElMessage.error(error.message);
    } finally {
      loading.value = false;
    }
  };


  // const filteredNewsList = computed(() => {
  //   return newsList.value.filter(news => {
  //     const formattedDate = formatDate(news.create_time);
  //     const dateMatch = dateFilter.value ? formattedDate === dateFilter.value : true;
  //     const typeMatch = typeFilter.value ? news.type === typeFilter.value : true;
  //     const titleNotEmptyMatch = titleNotEmptyFilter.value ? (news.processed_title && news.processed_title.trim() !== '') : true;
  //     const noPushFilterMatch = noPushFilter.value ? (news.send !== 1) : true;

  //     return dateMatch && typeMatch && titleNotEmptyMatch && noPushFilterMatch;
  //   });
  // });
  // 过滤新闻列表
  const filteredNewsList = computed(() => {
    return newsList.value.filter(news => {
      const dateMatch = dateFilter.value ? formatDate(news.create_time) === dateFilter.value : true;

      // 处理大类和子类的匹配
      let typeMatch = true;
      if (typeFilter.value) {
        if (subTypeFilter.value) {
          // 如果选中子类，按子类匹配
          typeMatch = news.type === subTypeFilter.value;
        } else {
          // 如果没有选中子类，按该大类的所有子类匹配
          const selectedCategory = categories.value.find(cat => cat.name === typeFilter.value);
          typeMatch = selectedCategory ? selectedCategory.subcategories.includes(news.type) : true;
        }
      }

      const titleNotEmptyMatch = titleNotEmptyFilter.value ? news.processed_title : true;
      const noPushFilterMatch = noPushFilter.value ? news.send !== 1 : true;

      return dateMatch && typeMatch && titleNotEmptyMatch && noPushFilterMatch;
    });
  });

  const handleAction = async (row) => {
    loading.value = true;
    try {
      const updatedRow = await updateNews(row);
      const index = newsList.value.findIndex(news => news.id === row.id);
      if (index !== -1) {
        newsList.value[index] = updatedRow;
      }
      ElMessage.success('更新成功');
    } catch (error) {
      ElMessage.error(error.message);
    } finally {
      loading.value = false;
    }
  };

  const openPublishDialog = () => {
    publishDialogVisible.value = true;
  };


  const confirmPublish = async () => {

    const config = window.__ENV__;  // 使用全局注入的 config.js


    const platformsArray = selectedPlatforms.value || [];

    if (platformsArray.length === 0) {
      ElMessage.error('请选择至少一个发布平台');
      return;
    }

    // 设置选定平台的状态为 "正在发布"
    platformsArray.forEach(platform => {
      publishStatus.value[platform] = '正在发布';
    });

    try {

      const webSocketUrl = `${config.VITE_API_WS}/ws`;

      // 创建 WebSocket 连接
      const ws = new WebSocket(webSocketUrl);


      // WebSocket 接收到消息时更新发布状态
      ws.onmessage = (event) => {
        const message = event.data;
        const [platform, status, msg] = message.split(':');
        publishStatus.value[platform] = `${status}${msg ? `: ${msg}` : ''}`;
        console.log(`收到消息 ${platform}: ${status}: ${msg}`);
      };

      // 处理 WebSocket 关闭事件
      ws.onclose = () => {
        console.log('WebSocket 已关闭');
      };
      ws.onerror = function (event) {
        console.error("WebSocket 错误:", event);
      };


      // 调用发布 API
      await publishNews(selectedRows.value.map(row => row.id), platformsArray, typeFilter.value ? typeFilter.value : '');

      // 发布请求成功提示
      ElMessage.success('发布请求已发送');
    } catch (error) {
      // 出现错误时更新平台状态为 "失败"
      platformsArray.forEach(platform => {
        publishStatus.value[platform] = '失败';
      });
      ElMessage.error(`发布失败: ${error.message}`);
    }
  };

  const retryPublish = async (platform) => {
    const originalSelectedPlatforms = [...selectedPlatforms.value]; // 保存原有选择
    selectedPlatforms.value = [platform]; // 设置为仅包含重试的平台
    await confirmPublish(); // 调用不带参数的 confirmPublish
    selectedPlatforms.value = originalSelectedPlatforms; // 还原原有选择
  };


  const generateNewNews = async () => {
    loading.value = true;
    try {
      await generateNews();
      ElMessage.success('生成完毕');
      await loadNews();  // 重新获取新闻列表
    } catch (error) {
      ElMessage.error(error.message);
    } finally {
      loading.value = false;
    }
  };
  const resetPublishDialog = () => {
    publishDialogVisible.value = false;
    selectedPlatforms.value = []; // 重置选择的发布平台
    publishStatus.value = {}; // 重置发布状态
  };
  const fetchLatestNews = async () => {
    loading.value = true;
    try {
      await getLatestNews();
      ElMessage.success('获取完毕');
      await loadNews();  // 重新获取新闻列表
    } catch (error) {
      ElMessage.error(error.message);
    } finally {
      loading.value = false;
    }
  };

  const removeNews = async () => {
    loading.value = true;
    const newsIds = selectedRows.value.map(row => row.id);

    try {
      await deleteNews(newsIds);
      ElMessage.success('删除成功');
      await loadNews();  // 重新获取新闻列表
    } catch (error) {
      ElMessage.error(error.message);
    } finally {
      loading.value = false;
    }
  };

  const handleSelectionChange = (val) => {
    selectedRows.value = val;
  };

  const updateOrder = () => {
    console.log('Updated order:', selectedRows.value);
  };

  return {
    newsList,
    dateFilter,
    typeFilter,
    titleNotEmptyFilter,
    noPushFilter,
    types,
    times,
    filteredNewsList,
    handleAction,
    loading,
    handleSelectionChange,
    selectedRows,
    updateOrder,
    openPublishDialog,
    fetchLatestNews,
    loadNews,
    confirmPublish,
    retryPublish,
    generateNewNews,
    removeNews,
    formatDate,
    resetPublishDialog,
    publishDialogVisible,
    selectedPlatforms,
    publishStatus,
    platforms,
    onCategoryChange,
    loadCategories,
    categories,
    typeFilter,
    subTypeFilter,
    subTypes,
  };
}
