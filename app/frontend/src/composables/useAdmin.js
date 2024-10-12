// src/composables/useAdmin.js
import { ref, onMounted, onUnmounted } from 'vue';

export default function useAdmin() {
  const currentComponent = ref('NewsList');
  const currentTime = ref(new Date().toLocaleString());

  const updateTime = () => {
    currentTime.value = new Date().toLocaleString();
  };

  let timer;
  onMounted(() => {
    timer = setInterval(updateTime, 1000);
  });

  onUnmounted(() => {
    clearInterval(timer);
  });


  const handleSelect = (key) => {
  console.log('handleSelect triggered with key:', key);
  if (key === '1') {
    currentComponent.value = 'NewsList';
  } else if (key === '2') {
    currentComponent.value = 'CarNewsList';
  } else if (key === '3') {
    currentComponent.value = 'AccountManagement';
  } else if (key === '6') {  // 对应菜单中的 index="6"
    currentComponent.value = 'PublishRecords';
  }
};


  return {
    currentComponent,
    handleSelect,
    currentTime,
  };
}
