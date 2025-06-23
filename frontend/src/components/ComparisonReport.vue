<template>
  <div class="comparison-report-card">
    <!-- 添加对比标识 -->
    <div class="comparison-badge">
      平台对比分析
    </div>

    <h2>平台对比分析报告</h2>

    <div v-if="report" class="report-content" v-html="formattedReport"></div>
    <div v-else class="no-data">暂无对比报告数据</div>
  </div>
</template>

<script>
import { marked } from 'marked'

export default {
  name: 'ComparisonReport',
  props: {
    report: {
      type: String,
      default: null
    }
  },
  computed: {
    formattedReport() {
      marked.setOptions({
        breaks: true,
        gfm: true,
        headerIds: false,
        sanitize: false
      })
      return this.report ? marked(this.report) : ''
    }
  }
}
</script>

<style scoped>
.comparison-report-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  position: relative;
  margin-bottom: 30px;
}

.comparison-badge {
  position: absolute;
  top: 20px;
  right: 20px;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
  color: white;
  background-color: #673ab7;
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
</style>
