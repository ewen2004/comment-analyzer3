<template>
  <div class="keyword-input">
    <!-- 如果有 genre，展示用户的小说偏好 -->
    <p v-if="genre" class="genre-tip">
      您选择的小说类型：<strong>{{ genre }}</strong>
    </p>
    
    <!-- 添加平台选择器 -->
    <el-select
      v-model="platform"
      placeholder="选择平台"
      class="platform-select"
      :disabled="loading"
    >
      <el-option label="哔哩哔哩" value="bilibili" />
      <el-option label="YouTube" value="youtube" />
    </el-select>
    
    <el-input
      v-model="keyword"
      placeholder="请输入搜索关键词"
      :prefix-icon="Search"
      clearable
      :disabled="loading"
      @keyup.enter="onSubmit"
    />
    <el-button
      type="primary"
      @click="onSubmit"
      :loading="loading"
      :disabled="!isValid"
      size="large"
      style="margin-top: 15px; width: 100%"
    >
      开始分析
    </el-button>
    <p class="tip">示例: 小说, 科技, 教育等</p>
  </div>
</template>

<script>
import { Search } from '@element-plus/icons-vue'

export default {
  name: 'KeywordInput',
  props: {
    loading: {
      type: Boolean,
      default: false
    },
    // 接收小说类型偏好
    genre: {
      type: String,
      default: ''
    }
  },
  data() {
    return {
      keyword: '',
      platform: 'bilibili', // 新增平台选择
      Search
    }
  },
  computed: {
    isValid() {
      // 验证关键词非空
      return this.keyword.trim().length > 0
    }
  },
  methods: {
    onSubmit() {
      if (this.isValid && !this.loading) {
        this.$emit('submit', {
          keyword: this.keyword.trim(),
          platform: this.platform
        })
        this.keyword = ''
      }
    }
  }
}
</script>

<style scoped>
.keyword-input {
  display: flex;
  flex-direction: column;
  gap: 15px;
  max-width: 450px;
  margin: 0 auto;
}

.platform-select {
  width: 100%;
}

.tip {
  font-size: 12px;
  color: #909399;
  margin: 5px 0 0;
}
.genre-tip {
  font-size: 14px;
  color: #606266;
  text-align: left;
}
</style>