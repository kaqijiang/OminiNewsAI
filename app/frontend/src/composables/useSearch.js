import { ref, onMounted, onUnmounted } from 'vue';
import { fetchStream } from '@/api/index.js'; // 确保这是正确的路径

export function useSearch() {
    const searchText = ref('');  // 用户输入
    const searchResult = ref('');  // 搜索结果

    const stream = ref(null);

    // 关闭搜索结果的函数
    const closeResults = (event) => {
        if (!event.target.closest('#text-display')) {
            searchResult.value = '';  // 清空搜索结果隐藏内容
        }
    };

    // 挂载时添加点击事件监听
    onMounted(() => {
        document.addEventListener('click', closeResults);
    });

    // 卸载时移除事件监听，并关闭可能打开的流
    onUnmounted(() => {
        document.removeEventListener('click', closeResults);
        if (stream.value && typeof stream.value.close === 'function') {
            stream.value.close();
        }
    });

    // 获取搜索结果，可能包括启动流
    const fetchSearchResult = () => {
        const item = searchText.value;
        console.log(`stream started for query: ${item}`);

        if (typeof item !== 'string') {
            console.error('Expected a string for the query, but got:', item);
            return;
        }

        // 如果有活动的流，关闭它
        if (stream.value && typeof stream.value.close === 'function') {
            stream.value.close();
        }

        // 更新搜索结果为“搜索中…”
        searchResult.value = '搜索中...';

        // 开始新的 SSE 流
        stream.value = fetchStream(
            item,
            (data) => {
                // 如果是接收到第一条消息，并且当前状态仍然是 '搜索中...'，则清空状态
                if (searchResult.value === '搜索中...') {
                    searchResult.value = '搜索结果：'; // 清空初始状态
                }
                // 累加接收到的消息并展示
                searchResult.value += (searchResult.value ? '\n' : '') + data.message;
                console.log(`收到消息: ${data.message}`);
            },
            (error) => {
                console.error('Failed to fetch stream:', error);
                searchResult.value = '加载失败，请重试。'; // 提供错误信息
                if (stream.value && typeof stream.value.close === 'function') {
                    stream.value.close();  // 在错误时关闭连接
                }
            }
        );
    };

    return {
        searchText,
        searchResult,
        fetchSearchResult
    };
}
