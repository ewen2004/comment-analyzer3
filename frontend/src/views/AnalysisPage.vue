<template>
  <div class="analysis-container container">
    <el-page-header @back="goBack" title="返回首页" style="margin-bottom: 20px;">
      <template #content>
        <span class="page-title">关键词 {{ keyword }} 的评论分析</span>
      </template>
    </el-page-header>

    <!-- 添加平台切换器 -->
    <div class="platform-switcher" style="margin-bottom: 20px;">
      <el-radio-group v-model="currentPlatform" @change="switchPlatform">
        <el-radio-button label="bilibili">哔哩哔哩</el-radio-button>
        <el-radio-button label="youtube">YouTube</el-radio-button>
      </el-radio-group>
      <span style="margin-left: 10px; color: #606266;">
        当前平台: {{ currentPlatform === 'bilibili' ? '哔哩哔哩' : 'YouTube' }}
      </span>
    </div>

    <!-- 添加调试工具（仅开发环境显示） -->
    <div v-if="isDev" class="debug-tools">
      <el-button @click="debugData" size="small" type="info">
        调试数据
      </el-button>
      <el-button @click="forceReload" size="small" type="warning">
        强制重新加载
      </el-button>
    </div>

    <div v-if="loading" class="loading-box">
      <el-skeleton :rows="10" animated />
      <div class="loading-text">
        <el-icon class="is-loading"><Loading /></el-icon>
        <span>正在分析评论数据，请稍候...</span>
      </div>
    </div>

    <div v-else-if="error" class="error-box">
      <el-result
        icon="error"
        title="分析失败"
        :sub-title="error"
      >
        <template #extra>
          <el-button type="primary" @click="goBack">返回首页</el-button>
          <el-button @click="retryAnalysis">重试</el-button>
        </template>
      </el-result>
    </div>

    <div v-else class="content">
      <div class="report-section">
        <Report
          :report="report"
          :platform="currentPlatform"
          :keyword="keyword"
          :genre="genre"
        />
      </div>

      <div class="charts-section">
        <Charts
          :sentimentData="sentimentData"
          :topicsData="topicsData"
        />
      </div>

      <div class="chat-section">
        <ChatBox
          :keyword="keyword"
          @send-message="sendMessage"
          :messages="chatMessages"
          :loading="chatLoading"
        />
      </div>
    </div>
  </div>
</template>

<script>
import { Loading } from '@element-plus/icons-vue';
import { ElMessage } from 'element-plus';
import Report from '@/components/Report.vue';
import Charts from '@/components/Charts.vue';
import ChatBox from '@/components/ChatBox.vue';
import api from '@/api/index';

export default {
  name: 'AnalysisPage',
  components: {
    Report,
    Charts,
    ChatBox,
    Loading
  },
  props: {
    keyword: {
      type: String,
      required: true
    },
    genre: {
      type: String,
      default: ''
    },
    platform: {
      type: String,
      default: 'bilibili'
    }
  },
  data() {
    return {
      currentPlatform: this.platform, // 初始化为 props 中的 platform
      loading: true,
      error: '',
      report: null,
      sentimentData: null,
      topicsData: null,
      chatMessages: [],
      chatLoading: false,
      isDev: import.meta.env.DEV // 开发环境标志
    };
  },
  mounted() {
    console.log(`页面加载，平台: ${this.platform}, 关键词: ${this.keyword}`);
    this.currentPlatform = this.platform; // 确保初始平台与 props 一致
    this.fetchAnalysisReport();
  },
  watch: {
    // 监听路由参数变化
    platform(newPlatform, oldPlatform) {
      if (newPlatform !== oldPlatform) {
        console.log(`平台参数变化: ${oldPlatform} -> ${newPlatform}`);
        this.currentPlatform = newPlatform;
        this.fetchAnalysisReport();
      }
    }
  },
  methods: {
    // 平台切换方法
    switchPlatform(platform) {
      console.log(`手动切换平台: ${this.currentPlatform} -> ${platform}`);
      this.currentPlatform = platform;

      // 更新路由参数但不重新加载组件
      this.$router.replace({
        name: this.$route.name,
        params: { keyword: this.keyword },
        query: {
          genre: this.genre,
          platform: platform
        }
      });

      // 重新加载数据
      this.fetchAnalysisReport();
    },

    async fetchAnalysisReport(forceRefresh = false) {
      this.loading = true;
      this.error = '';

      try {
        // 使用当前选择的平台
        const platform = this.currentPlatform;
        console.log(`开始获取${platform}平台分析报告, 关键词: ${this.keyword}`);

        // 检查数据状态
        const statusCheck = await api.checkPlatformDataStatus(this.keyword, this.genre, platform);
        console.log(`${platform}数据状态检查:`, statusCheck);

        let needFetchComments = !statusCheck?.data?.commentsFileExists || forceRefresh;
        let needAnalysis = !statusCheck?.data?.reportFileExists || forceRefresh;

        // 如果需要，先获取评论
        if (needFetchComments) {
          console.log(`${platform}评论文件不存在或强制刷新，开始获取`);
          const commentsResponse = await api.fetchComments(this.keyword, this.genre, platform);
          console.log(`${platform}评论获取响应:`, commentsResponse);

          if (!commentsResponse || !commentsResponse.success) {
            throw new Error(commentsResponse?.error || `获取${platform}评论失败`);
          }

          // 添加延迟确保文件写入完成
          console.log(`等待5秒确保${platform}评论文件写入完成`);
          await new Promise(resolve => setTimeout(resolve, 5000));
        } else {
          console.log(`${platform}评论文件已存在，无需重新获取`);
        }

        // 确保分析报告存在或重新生成
        if (needAnalysis) {
          console.log(`${platform}分析报告不存在或强制刷新，重新获取`);
        } else {
          console.log(`${platform}分析报告已存在，直接获取`);
        }

        // 获取分析报告
        const response = await api.getAnalysisReport(this.keyword, this.genre, platform);
        console.log(`${platform}分析报告响应:`, response);

        // 确保数据存在
        if (!response || !response.success) {
          throw new Error(response?.error || '服务器返回数据格式不正确');
        }

        // 正确解析嵌套的数据结构
        const data = response.data;
        this.report = data.report;
        this.sentimentData = data.sentimentData || { positive: 0, negative: 0, neutral: 0 };
        this.topicsData = data.topicsData || {};

        // 添加初始对话消息
        if (this.chatMessages.length === 0) {
          this.chatMessages.push({
            role: 'assistant',
            content: `我已经分析完${platform === 'bilibili' ? '哔哩哔哩' : 'YouTube'}评论，你可以向我询问更多细节问题。`,
          });
        }
        ElMessage.success(`${platform === 'bilibili' ? '哔哩哔哩' : 'YouTube'}数据分析完成`);
      } catch (err) {
        console.error(`${this.currentPlatform}数据获取或分析错误:`, err);
        this.error = `获取${this.currentPlatform === 'bilibili' ? '哔哩哔哩' : 'YouTube'}数据失败: ` + (err.response?.data?.error || err.message);
        ElMessage.error(this.error);
      } finally {
        this.loading = false;
      }
    },

    // 调试功能
    debugData() {
      console.log('当前分析状态:', {
        platform: this.currentPlatform,
        keyword: this.keyword,
        hasReport: !!this.report,
        reportLength: this.report ? this.report.length : 0,
        sentimentData: this.sentimentData,
        topicsData: this.topicsData
      });

      // 调用API检查数据
      api.debugPlatformData(this.keyword, this.currentPlatform)
        .then(response => {
          console.log('后端数据状态:', response);
          ElMessage.info('调试信息已输出到控制台');
        })
        .catch(error => {
          console.error('调试请求失败:', error);
        });
    },

    forceReload() {
      ElMessage.warning('强制重新加载分析数据');
      this.report = null;
      this.sentimentData = null;
      this.topicsData = null;
      this.fetchAnalysisReport(true); // 传入true表示强制刷新
    },

    async sendMessage(message) {
      if (!message.trim() || this.chatLoading) return;

      this.chatMessages.push({ role: 'user', content: message });
      this.chatLoading = true;

      try {
        const response = await api.chatWithDeepSeek(this.keyword, message, this.genre, this.currentPlatform);

        if (response && response.data && response.data.reply) {
          this.chatMessages.push({ role: 'assistant', content: response.data.reply });
        } else {
          throw new Error('获取回复失败');
        }
      } catch (err) {
        console.error('聊天请求错误:', err);
        ElMessage.error('获取回复失败: ' + (err.response?.data?.error || err.message));
        this.chatMessages.push({
          role: 'assistant',
          content: '抱歉，获取回复时出现错误。请稍后再试。'
        });
      } finally {
        this.chatLoading = false;
      }
    },

    goBack() {
      this.$router.push({
        name: 'Home',
        query: {
          genre: this.genre,
          platform: this.currentPlatform
        }
      });
    },

    retryAnalysis() {
      this.fetchAnalysisReport();
    }
  }
};
</script>

<style scoped>
.analysis-container {
  padding: 20px 0;
}

.page-title {
  font-size: 18px;
  font-weight: 600;
}

.platform-switcher {
  margin-bottom: 20px;
}

.debug-tools {
  margin: 10px 0;
  padding: 8px;
  background-color: #fdf6ec;
  border-radius: 4px;
  display: flex;
  gap: 10px;
}

.loading-box {
  padding: 30px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.loading-text {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 20px;
  color: #909399;
  gap: 10px;
}

.error-box {
  padding: 30px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.content {
  display: grid;
  grid-template-columns: 1fr;
  gap: 20px;
}

@media (min-width: 992px) {
  .content {
    grid-template-columns: 3fr 2fr;
  }

  .report-section {
    grid-column: 1;
    grid-row: 1;
  }

  .charts-section {
    grid-column: 2;
    grid-row: 1;
  }

  .chat-section {
    grid-column: 1 / 3;
    grid-row: 2;
  }
}
</style>
