<template>
  <div class="report-card">
    <!-- 添加平台标识 -->
    <div class="platform-badge" :class="{'bilibili': platform === 'bilibili', 'youtube': platform === 'youtube'}">
      {{ platformLabel }}
    </div>

    <h2>评论分析报告</h2>

    <div v-if="report" class="report-content" v-html="formattedReport"></div>
    <div v-else class="no-data">暂无报告数据</div>

    <!-- 添加对比分析按钮 -->
    <div class="comparison-link" v-if="showComparisonButton">
      <el-button
        type="primary"
        @click="goToComparisonPage"
        size="small"
        icon="Connection"
      >
        查看平台对比分析
      </el-button>
    </div>
  </div>
</template>

<script>
import { marked } from 'marked'
import { ElMessage } from 'element-plus'

export default {
  name: 'Report',
  props: {
    // 后端分析生成的 Markdown 报告
    report: {
      type: String,
      default: null
    },
    // 添加平台属性
    platform: {
      type: String,
      default: 'bilibili'
    },
    // 关键词
    keyword: {
      type: String,
      required: true
    },
    // 类型
    genre: {
      type: String,
      default: ''
    }
  },
  computed: {
    platformLabel() {
      return this.platform === 'bilibili' ? '哔哩哔哩' : 'YouTube';
    },
    formattedReport() {
      marked.setOptions({
        breaks: true,
        gfm: true,
        headerIds: false,
        sanitize: false
      })
      return this.report ? marked(this.report) : ''
    },
    // 判断是否显示对比按钮
    showComparisonButton() {
      // 检查另一个平台的数据是否存在
      const otherPlatform = this.platform === 'bilibili' ? 'youtube' : 'bilibili';
      // 从localStorage或其他方式检查另一个平台数据是否存在
      try {
        const platformStatus = JSON.parse(localStorage.getItem(`platforms_${this.keyword}`) || '{}');
        return platformStatus[otherPlatform];
      } catch (e) {
        console.error('获取平台状态失败:', e);
        return false;
      }
    }
  },
  methods: {
    goToComparisonPage() {
      try {
        // 记录当前平台状态
        const platformStatus = JSON.parse(localStorage.getItem(`platforms_${this.keyword}`) || '{}');
        platformStatus[this.platform] = true;
        localStorage.setItem(`platforms_${this.keyword}`, JSON.stringify(platformStatus));

        // 跳转到对比页面
        this.$router.push({
          name: 'CompareAnalysis', // 确保与路由名称匹配
          params: { keyword: this.keyword },
          query: { genre: this.genre }
        });
      } catch (e) {
        console.error('跳转到对比页面失败:', e);
        ElMessage.error('跳转失败: ' + e.message);
      }
    }
  },
  // 组件挂载时记录当前平台状态
  mounted() {
    try {
      const platformStatus = JSON.parse(localStorage.getItem(`platforms_${this.keyword}`) || '{}');
      platformStatus[this.platform] = true;
      localStorage.setItem(`platforms_${this.keyword}`, JSON.stringify(platformStatus));
    } catch (e) {
      console.error('记录平台状态失败:', e);
    }
  }
}
</script>

<style scoped>
.report-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  position: relative;
}

/* 平台徽章样式 */
.platform-badge {
  position: absolute;
  top: 20px;
  right: 20px;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
  color: white;
}

.platform-badge.bilibili {
  background-color: #00a1d6;
}

.platform-badge.youtube {
  background-color: #ff0000;
}

.report-content {
  line-height: 1.6;
  margin-top: 15px;
}

.report-content :deep(h1),
.report-content :deep(h2),
.report-content :deep(h3) {
  margin-top: 1.5em;
  margin-bottom: 0.5em;
  font-weight: 600;
}

.report-content :deep(h1) {
  font-size: 1.8em;
}

.report-content :deep(h2) {
  font-size: 1.5em;
}

.report-content :deep(h3) {
  font-size: 1.3em;
}

.report-content :deep(ul),
.report-content :deep(ol) {
  padding-left: 20px;
  margin: 10px 0;
}

.report-content :deep(li) {
  margin-bottom: 5px;
}

.report-content :deep(p) {
  margin: 10px 0;
}

.report-content :deep(blockquote) {
  border-left: 4px solid #e0e0e0;
  padding-left: 15px;
  color: #666;
  margin: 10px 0;
}

.no-data {
  color: #909399;
  text-align: center;
  padding: 40px 0;
}

/* 添加新的样式 */
.comparison-link {
  margin-top: 20px;
  text-align: center;
}
</style>
