<template>
  <div>
    <el-header class="main-header">
      <div class="filter-bar">
        <!-- 大类选择 -->
        <el-select v-model="typeFilter" placeholder="选择大类" clearable @change="onCategoryChange">
          <el-option v-for="category in categories" :key="category.name" :label="category.name"
            :value="category.name" />
        </el-select>

        <!-- 子类选择 -->
        <el-select v-model="subTypeFilter" placeholder="选择子类" clearable>
          <el-option v-for="subcategory in subTypes" :key="subcategory" :label="subcategory" :value="subcategory" />
        </el-select>

        <!-- 日期选择 -->
        <el-select v-model="dateFilter" placeholder="选择日期" clearable>
          <el-option v-for="time in times" :key="time" :label="time" :value="time"></el-option>
        </el-select>

        <!-- 标题不为空的筛选 -->
        <el-checkbox v-model="titleNotEmptyFilter">标题不为空</el-checkbox>

        <!-- 未发布的筛选 -->
        <el-checkbox v-model="noPushFilter">未发布</el-checkbox>

        <div class="button-group">
          <el-button type="info" @click="fetchLatestNews">
            获取信息
            <el-icon>
              <Pointer />
            </el-icon>
          </el-button>
          <el-button type="info" @click="generateNewNews">
            生成信息
            <el-icon>
              <Pointer />
            </el-icon>
          </el-button>
          <el-button type="danger" @click="removeNews" :disabled="!selectedRows.length">
            删除
            <el-icon>
              <Delete />
            </el-icon>
          </el-button>
          <el-button type="primary" @click="publishDialogVisible = true" :disabled="!selectedRows.length">
            发布
            <el-icon>
              <Upload />
            </el-icon>
          </el-button>
        </div>
      </div>
    </el-header>
    <div class="content-container" v-loading="loading">
      <div class="news-table-container">
        <el-table :data="filteredNewsList" class="news-table row-grey" style="width: 100%" height="calc(100vh - 160px)"
          @selection-change="handleSelectionChange">
          <el-table-column type="selection" width="55"></el-table-column>
          <el-table-column prop="id" label="ID" width="50">
            <template v-slot="scope">
              <span :class="{ 'strikethrough': scope.row.send === 1 }">{{ scope.row.id }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="title" label="原始标题" width="150"></el-table-column>
          <el-table-column prop="processed_title" label="标题" width="150">
            <template v-slot="scope">
              <span :class="{ 'strikethrough': scope.row.send === 1 }">{{ scope.row.processed_title }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="source_url" label="链接" min-width="200">
          </el-table-column>
          <el-table-column prop="processed_content" label="内容" width="700"></el-table-column>
          <el-table-column prop="create_time" label="日期" width="100">
            <template v-slot="scope">
              {{ formatDate(scope.row.create_time) }}
            </template>
          </el-table-column>
          <el-table-column prop="type" label="类型" width="100"></el-table-column>
          <el-table-column label="操作" width="80">
            <template v-slot="scope">
              <el-button circle @click="handleAction(scope.row)" :disabled="scope.row.send === 1">
                <el-icon>
                  <Refresh />
                </el-icon>
              </el-button>
            </template>
          </el-table-column>
        </el-table>
        <div v-if="filteredNewsList.length === 0" class="no-content">
          <p>没有匹配的内容</p>
        </div>
      </div>
      <div class="selected-articles">
        <div class="draggable-title">选中的文章</div>
        <VueDraggableNext v-model="selectedRows" @end="updateOrder">
          <div v-for="(row, index) in selectedRows" :key="row.id" class="draggable-item">
            <p class="truncate">{{ index + 1 }}.{{ row.processed_title }}</p>
          </div>
        </VueDraggableNext>
      </div>
    </div>

    <!-- 添加发布平台选择区域 -->
    <div v-if="publishDialogVisible" class="publish-platforms">
      <div class="dialog-header">
        <h3>选择发布平台</h3>
        <el-button class="close-button" @click="resetPublishDialog">
          <el-icon>
            <Close />
          </el-icon>
        </el-button>
      </div>
      <!-- 选择发布平台 -->
      <el-checkbox-group v-model="selectedPlatforms">
        <div class="platforms-container">
          <div v-for="platform in platforms" :key="platform" class="platform-item">
            <el-checkbox :label="platform">{{ platform }}</el-checkbox>
            <div class="retry-button" v-if="publishStatus[platform]">
              <el-tooltip :content="publishStatus[platform] || ''" placement="top">
                <div
                  style="font-size: medium; height: 30px;  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                  {{ publishStatus[platform] || '' }}
                </div>
              </el-tooltip>
              <el-button v-if="publishStatus[platform]?.includes('失败')" @click="retryPublish(platform)">
                重试
              </el-button>
            </div>
          </div>
        </div>
      </el-checkbox-group>

      <div class="dialog-footer">
        <el-button @click="resetPublishDialog">取消</el-button>
        <el-button type="primary" @click="confirmPublish">确定</el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useNews } from '@/composables/useNews';
import { Refresh, Upload, Delete } from '@element-plus/icons-vue';
import { ElMessage } from 'element-plus';
import { VueDraggableNext } from 'vue-draggable-next';
const {
  typeFilter,
  subTypeFilter,
  categories,
  subTypes,
  loadCategories,
  onCategoryChange,
  filteredNewsList,
  selectedRows,
  loadNews,
  updateOrder,
  handleSelectionChange,
  fetchLatestNews,
  generateNewNews,
  removeNews,
  confirmPublish,
  handleAction,
  platforms,
  publishStatus,
  retryPublish,
  formatDate,
  selectedPlatforms,
  publishDialogVisible,
  resetPublishDialog,
  loading,
  dateFilter,
  titleNotEmptyFilter,
  noPushFilter,
  times
} = useNews('ai');

// 加载分类和新闻数据
onMounted(() => {
  loadCategories();
  loadNews();
});

</script>


<style scoped>
.strikethrough {
  text-decoration: line-through;
}

.main-header {
  position: sticky;
  top: 0;
  z-index: 1;
  width: 100%;
  background-color: #f5f5f5;
  padding: 10px 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.filter-bar {
  display: flex;
  align-items: center;
}

.filter-bar .el-select,
.filter-bar .el-date-picker {
  flex: 0.2;
  /* 每个元素占据相同的份额 */
  margin-right: 20px;
}

.button-group {
  margin-left: auto;
}

.button-group .el-button {
  margin-left: 10px;
}

.filter-bar .el-select:last-child {
  margin-right: 0;
}

.content-container {
  display: flex;
  height: calc(100vh - 160px);
}

.news-table-container {
  flex: 3;
  height: 100%;
  overflow: auto;
}

.news-table .el-table__header-wrapper {
  position: sticky;
  top: 0;
  z-index: 2;
  background-color: #fff;
  font-size: 12px;
}

.no-content {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 50px;
  color: #999;
  font-size: 18px;
}

.selected-articles {
  flex: 0.3;
  margin-left: 20px;
  overflow: auto;
}

.draggable-title {
  height: 42px;
  line-height: 42px;
  padding-left: 10px;
  border-bottom: 1px solid #ebeef5;
  /* 保持与表头一致 */
  color: #909399;
}

.draggable-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px;
  margin-bottom: 5px;
  background-color: #fff;
  /* 保持与表头一致 */
  border-bottom: 1px solid #ebeef5;
  /* 保持与表头一致 */
  cursor: grab;
}

.draggable-item:active {
  cursor: grabbing;
}

.truncate {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 150px;
  /* 根据需要调整宽度 */
}

/* 新添加的发布平台选择区域样式 */
.publish-platforms {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: white;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  z-index: 1000;
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.publish-platforms h3 {
  margin: 0;
  padding: 10px 10px 30px 0px;
  /* 调整 padding 以垂直居中 */
}

.publish-platforms .close-button {
  font-size: 18px;
  padding: 10px 10px 30px 0px;
  /* 调整 padding 以垂直居中 */
  background: none;
  border: none;
  cursor: pointer;
  line-height: 1;
  /* 确保没有额外的行高 */
}

.publish-platforms .platforms-container {
  display: flex;
  flex-wrap: wrap;
}

.publish-platforms .platform-item {
  display: inline-block;
  margin-right: 40px;
  text-align: center;
  width: 100px;
  /* 设置明确的宽度 */
  height: 100px;
  /* 设置明确的高度 */
  position: relative;
  /* 确保子元素相对于父元素定位 */
}

.retry-button {
  margin-top: 25px;
  overflow: hidden;
  line-height: 15px;
}

.publish-platforms .dialog-footer {
  display: flex;
  justify-content: flex-end;
  margin-top: 40px;
}
</style>
