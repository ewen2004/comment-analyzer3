<template>
  <div class="home-container container">
    <div class="header">
      <h1 class="title">
        评论分析平台
        <span class="subtitle">海内外评论分析工具</span>
      </h1>
    </div>

    <el-card class="input-card">
      <div class="input-section">
        <h2 class="section-title">开始分析</h2>
        <p class="section-desc">
          输入关键词，我们将为您分析相关视频的评论，生成深度洞察报告
        </p>

        <KeywordInput
          @submit="onKeywordSubmit"
          :loading="loading"
          :genre="selectedGenre"
        />
      </div>
    </el-card>

    <!-- 添加平台状态指示器 -->
    <div class="platforms-status" v-if="currentKeyword">
      <h3>分析状态</h3>
      <div class="platform-indicators">
        <el-tag
          :type="platformsAnalyzed.bilibili ? 'success' : 'info'"
          effect="plain"
          class="platform-tag"
        >
          哔哩哔哩 {{ platformsAnalyzed.bilibili ? '✓' : '待分析' }}
        </el-tag>
        <el-tag
          :type="platformsAnalyzed.youtube ? 'success' : 'info'"
          effect="plain"
          class="platform-tag"
        >
          YouTube {{ platformsAnalyzed.youtube ? '✓' : '待分析' }}
        </el-tag>
      </div>
    </div>

    <div class="history-section" v-if="!loading && recentKeywords.length > 0">
      <h3>最近分析</h3>
      <el-space wrap>
        <el-tag
          v-for="item in recentKeywords"
          :key="item.keyword"
          class="history-tag"
          @click="goToAnalysis(item.keyword, item.platform)"
          effect="light"
        >
          {{ item.keyword }} ({{ item.platform === 'bilibili' ? '哔哩哔哩' : 'YouTube' }})
        </el-tag>
      </el-space>
    </div>

    <!-- 添加对比分析入口 -->
    <div class="compare-section" v-if="hasCompletedAnalysis">
      <el-divider content-position="center">平台对比分析</el-divider>
      <p class="compare-tip">已完成两个平台的评论抓取，可以进行对比分析</p>
      <el-button
        type="primary"
        @click="startCompareAnalysis"
        icon="Connection"
      >
        开始平台对比分析
      </el-button>
    </div>
  </div>
</template>

<script>
import { ElMessage } from 'element-plus';
import KeywordInput from '@/components/KeywordInput.vue';
import api from '@/api/index';

export default {
  name: 'HomePage',
  components: {
    KeywordInput
  },
  data() {
    return {
      loading: false,
      keyword: '',
      selectedGenre: '',
      recentKeywords: [],
      // 记录哪些平台已经分析过
      platformsAnalyzed: {
        bilibili: false,
        youtube: false
      },
      // 当前正在分析的关键词
      currentKeyword: ''
    };
  },
  computed: {
    hasCompletedAnalysis() {
      return this.platformsAnalyzed.bilibili && this.platformsAnalyzed.youtube &&
             this.currentKeyword !== '';
    }
  },
  mounted() {
    this.loadRecentKeywords();
    this.loadPlatformsAnalyzed();

    // 从URL参数中获取genre
    const genre = this.$route.query.genre;
    if (genre) {
      this.selectedGenre = genre;
    }

    // 从URL参数中获取platform
    const platform = this.$route.query.platform;
    if (platform && ['bilibili', 'youtube'].includes(platform)) {
      this.platformsAnalyzed[platform] = true;
    }
  },
  methods: {
    async onKeywordSubmit(data) {
      this.keyword = data.keyword;
      const platform = data.platform;
      this.loading = true;
      this.currentKeyword = this.keyword;

      try {
        // 保存关键词到本地存储
        this.saveKeyword(this.keyword, platform);

        // 先获取评论数据
        await api.fetchComments(this.keyword, this.selectedGenre, platform);

        // 标记该平台已分析完成
        this.platformsAnalyzed[platform] = true;
        // 保存平台分析状态
        this.savePlatformsAnalyzed();

        // 转到分析页面
        this.$router.push({
          name: 'Analysis',
          params: { keyword: this.keyword },
          query: {
            genre: this.selectedGenre,
            platform: platform
          }
        });
      } catch (error) {
        console.error('获取评论失败:', error);
        ElMessage.error(error.response?.data?.error || '获取评论失败，请稍后重试');
      } finally {
        this.loading = false;
      }
    },

    goToAnalysis(keyword, platform = 'bilibili') {
      this.currentKeyword = keyword;
      this.$router.push({
        name: 'Analysis',
        params: { keyword },
        query: {
          genre: this.selectedGenre,
          platform: platform
        }
      });
    },

    saveKeyword(keyword, platform) {
      try {
        // 获取现有的关键词历史
        let history = localStorage.getItem('recentKeywords');
        let keywords = history ? JSON.parse(history) : [];

        // 检查是否已存在相同关键词和平台
        const existingIndex = keywords.findIndex(
          item => item.keyword === keyword && item.platform === platform
        );

        if (existingIndex !== -1) {
          // 如果存在，删除旧的
          keywords.splice(existingIndex, 1);
        }

        // 添加到数组开头
        keywords.unshift({
          keyword,
          platform,
          timestamp: new Date().toISOString()
        });

        // 限制历史记录数量
        keywords = keywords.slice(0, 10);

        // 保存回本地存储
        localStorage.setItem('recentKeywords', JSON.stringify(keywords));

        // 更新组件中的历史记录
        this.loadRecentKeywords();
      } catch (e) {
        console.error('保存关键词历史失败:', e);
      }
    },

    loadRecentKeywords() {
      try {
        const history = localStorage.getItem('recentKeywords');
        if (history) {
          this.recentKeywords = JSON.parse(history);
        }
      } catch (e) {
        console.error('加载关键词历史失败:', e);
        this.recentKeywords = [];
      }
    },

    // 新增：保存平台分析状态
    savePlatformsAnalyzed() {
      try {
        if (this.currentKeyword) {
          localStorage.setItem(
            `platforms_${this.currentKeyword}`,
            JSON.stringify(this.platformsAnalyzed)
          );
        }
      } catch (e) {
        console.error('保存平台状态失败:', e);
      }
    },

    // 新增：加载平台分析状态
    loadPlatformsAnalyzed() {
      try {
        const keyword = this.$route.params.keyword;
        if (keyword) {
          this.currentKeyword = keyword;
          const savedStatus = localStorage.getItem(`platforms_${keyword}`);
          if (savedStatus) {
            this.platformsAnalyzed = JSON.parse(savedStatus);
          }
        }
      } catch (e) {
        console.error('加载平台状态失败:', e);
      }
    },

    startCompareAnalysis() {
      if (!this.currentKeyword) {
        ElMessage.warning('请先输入关键词进行分析');
        return;
      }

      if (!this.hasCompletedAnalysis) {
        ElMessage.warning('请先完成两个平台的评论分析');
        return;
      }

      this.$router.push({
        name: 'CompareAnalysis',
        params: { keyword: this.currentKeyword },
        query: { genre: this.selectedGenre }
      });
    }
  }
};
</script>

<style scoped>
.home-container {
  padding: 40px 0;
  max-width: 900px;
  margin: 0 auto;
}

.header {
  text-align: center;
  margin-bottom: 40px;
}

.title {
  font-size: 2.5rem;
  margin-bottom: 10px;
  color: #303133;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.subtitle {
  font-size: 1rem;
  font-weight: normal;
  color: #909399;
  margin-top: 10px;
}

.input-card {
  margin-bottom: 30px;
}

.section-title {
  font-size: 1.5rem;
  margin-bottom: 10px;
  color: #303133;
}

.section-desc {
  color: #606266;
  margin-bottom: 20px;
}

.genre-section {
  margin: 30px 0;
  text-align: center;
}

/* 新增：平台状态样式 */
.platforms-status {
  margin: 20px 0;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 8px;
}

.platform-indicators {
  display: flex;
  gap: 10px;
  margin-top: 10px;
}

.platform-tag {
  padding: 8px 12px;
}

.history-section {
  margin-top: 40px;
}

.history-tag {
  cursor: pointer;
  margin: 5px;
  font-size: 14px;
  padding: 6px 12px;
}

.compare-section {
  margin-top: 40px;
  text-align: center;
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.compare-tip {
  color: #67c23a;
  margin-bottom: 15px;
}
</style>
