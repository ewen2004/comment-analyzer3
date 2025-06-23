<template>
  <div class="comparison-page">
    <h1>海内外评论对比分析</h1>

    <div class="keyword-info">
      关键词: <strong>{{ keyword }}</strong>
      <button @click="goBack" class="back-button">返回首页</button>
    </div>

    <div class="platform-status">
      <div class="platform" :class="{ active: hasBilibiliData }">
        <span class="platform-icon">B站</span>
        哔哩哔哩
        <span v-if="hasBilibiliData" class="status success">已获取</span>
        <span v-else class="status pending">未获取</span>
      </div>
      <div class="platform" :class="{ active: hasYoutubeData }">
        <span class="platform-icon">YT</span>
        YouTube
        <span v-if="hasYoutubeData" class="status success">已获取</span>
        <span v-else class="status pending">未获取</span>
      </div>
    </div>

    <div v-if="!hasBilibiliData || !hasYoutubeData" class="notice">
      <p>请先获取两个平台的评论数据再进行对比分析</p>
      <div class="actions">
        <button
          v-if="!hasBilibiliData"
          @click="fetchComments('bilibili')"
          :disabled="loading"
        >
          获取哔哩哔哩评论
        </button>
        <button
          v-if="!hasYoutubeData"
          @click="fetchComments('youtube')"
          :disabled="loading"
        >
          获取YouTube评论
        </button>
        <!-- 强制获取YouTube数据按钮 -->
        <button
          v-if="!hasYoutubeData && !loading"
          @click="forceFetchYoutubeData"
        >
          强制重新获取YouTube数据
        </button>
        <!-- 查看单平台分析按钮 -->
        <button
          v-if="hasBilibiliData"
          @click="viewSinglePlatformAnalysis('bilibili')"
        >
          查看B站分析结果
        </button>
        <button
          v-if="hasYoutubeData"
          @click="viewSinglePlatformAnalysis('youtube')"
        >
          查看YouTube分析结果
        </button>
      </div>
    </div>

    <div v-else-if="!hasComparisonReport && !loading" class="notice">
      <button @click="generateComparisonReport" :disabled="loading">
        生成对比报告
      </button>
    </div>

    <div v-if="loading" class="loading">
      <p>{{ loadingMessage }}</p>
    </div>

    <div v-if="error" class="error-message">
      {{ error }}
      <button @click="clearError" class="clear-error">清除</button>
    </div>

    <div v-if="debugInfo" class="debug-info">
      <h3>调试信息</h3>
      <pre>{{ debugInfo }}</pre>
      <button @click="debugInfo = null" class="clear-debug">关闭</button>
    </div>

    <ComparisonReport v-if="comparisonReport" :report="comparisonReport" />

    <!-- 引入 ChatBox 组件并传递必要的 props -->
    <ChatBox
      v-if="comparisonReport"
      :keyword="keyword"
      :messages="chatMessages"
      @send-message="handleSendMessage"
      :loading="chatLoading"
    />
  </div>
</template>

<script>
import api from "@/api";
import ComparisonReport from "@/components/ComparisonReport.vue";
import ChatBox from "@/components/ChatBox.vue";
import { ElMessage } from "element-plus";

export default {
  components: {
    ComparisonReport,
    ChatBox,
  },
  data() {
    return {
      keyword: "",
      genre: "",
      loading: false,
      loadingMessage: "",
      error: null,
      debugInfo: null,
      hasBilibiliData: false,
      hasYoutubeData: false,
      hasComparisonReport: false,
      comparisonReport: null,
      chatMessages: [
        {
          role: "assistant",
          content:
            "我已经完成了两个平台的对比分析，你可以向我询问更多细节问题。",
        },
      ], // 初始欢迎消息
      chatLoading: false,
    };
  },
  created() {
    // 获取路由参数中的 keyword 和 genre
    this.keyword = this.$route.params.keyword || "";
    this.genre = this.$route.query.genre || "";

    if (!this.keyword) {
      this.error = "未提供关键词，请返回首页重新开始";
      return;
    }

    this.checkExistingData();
  },
  methods: {
    goBack() {
      this.$router.push({
        name: "Home",
        query: { genre: this.genre },
      });
    },

    clearError() {
      this.error = null;
    },

    viewSinglePlatformAnalysis(platform) {
      this.$router.push({
        name: "Analysis",
        params: { keyword: this.keyword },
        query: {
          genre: this.genre,
          platform: platform,
        },
      });
    },

    async checkExistingData() {
      this.loading = true;
      this.loadingMessage = "检查平台数据状态...";

      try {
        // 检查B站和YouTube数据
        const bilibiliStatus = await api.checkPlatformDataStatus(
          this.keyword,
          this.genre,
          "bilibili"
        );
        this.hasBilibiliData = bilibiliStatus?.data?.reportFileExists || false;

        const youtubeStatus = await api.checkPlatformDataStatus(
          this.keyword,
          this.genre,
          "youtube"
        );
        this.hasYoutubeData = youtubeStatus?.data?.reportFileExists || false;

        if (this.hasBilibiliData && this.hasYoutubeData) {
          const compareResponse = await api.getCompareAnalysis(
            this.keyword,
            this.genre
          );
          if (compareResponse && compareResponse.success) {
            this.hasComparisonReport = true;
            this.comparisonReport = compareResponse.data.report;
            ElMessage.success("成功获取平台对比分析报告");
          }
        }
      } catch (e) {
        this.error =
          "检查数据状态失败: " + (e.response?.data?.error || e.message);
      } finally {
        this.loading = false;
      }
    },

    async handleSendMessage(message) {
      if (!message.trim() || this.chatLoading) return;

      this.chatMessages.push({ role: "user", content: message });
      this.chatLoading = true;

      try {
        const response = await api.chatWithDeepSeek(
          this.keyword,
          message,
          this.genre,
          "compare"
        );

        if (response && response.data && response.data.reply) {
          this.chatMessages.push({
            role: "assistant",
            content: response.data.reply,
          });
        } else {
          throw new Error("获取回复失败");
        }
      } catch (err) {
        console.error("聊天请求错误:", err);
        ElMessage.error(
          "获取回复失败: " + (err.response?.data?.error || err.message)
        );
        this.chatMessages.push({
          role: "assistant",
          content: "抱歉，获取回复时出现错误。请稍后再试。",
        });
      } finally {
        this.chatLoading = false;
      }
    },

    async generateComparisonReport() {
      if (!this.hasBilibiliData || !this.hasYoutubeData) {
        this.error = "需要先获取两个平台的评论数据";
        return;
      }

      this.loading = true;
      this.loadingMessage = "正在生成平台对比分析报告...";
      this.error = null;

      try {
        const response = await api.getCompareAnalysis(this.keyword, this.genre);
        if (response && response.success) {
          this.hasComparisonReport = true;
          this.comparisonReport = response.data.report;
          ElMessage.success("平台对比分析报告生成成功");
        } else {
          this.error = response?.error || "生成对比报告失败";
        }
      } catch (e) {
        this.error = "生成对比报告失败";
      } finally {
        this.loading = false;
      }
    },
  },
};
</script>
<style scoped>
.comparison-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

h1 {
  text-align: center;
  margin-bottom: 20px;
}

.keyword-info {
  text-align: center;
  margin-bottom: 20px;
  font-size: 1.1em;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 15px;
}

.back-button {
  background-color: #f5f5f5;
  color: #333;
  border: 1px solid #ddd;
  padding: 5px 10px;
  font-size: 0.9em;
}

.platform-status {
  display: flex;
  justify-content: space-around;
  margin-bottom: 30px;
}

.platform {
  display: flex;
  align-items: center;
  padding: 15px 25px;
  border-radius: 8px;
  background-color: #f5f5f5;
  gap: 10px;
}

.platform.active {
  background-color: #e1f5fe;
  border-left: 4px solid #03a9f4;
}

.platform-icon {
  display: inline-block;
  width: 30px;
  height: 30px;
  line-height: 30px;
  text-align: center;
  border-radius: 50%;
  background-color: #ddd;
  font-weight: bold;
}

.status {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.8em;
}

.status.success {
  background-color: #c8e6c9;
  color: #2e7d32;
}

.status.pending {
  background-color: #ffecb3;
  color: #ff8f00;
}

.notice {
  text-align: center;
  margin: 30px 0;
  padding: 20px;
  background-color: #f5f5f5;
  border-radius: 8px;
}

.actions {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 15px;
}

button {
  padding: 10px 15px;
  border: none;
  border-radius: 4px;
  background-color: #1976d2;
  color: white;
  cursor: pointer;
  transition: background-color 0.3s;
}

button:hover {
  background-color: #1565c0;
}

button:disabled {
  background-color: #bbdefb;
  cursor: not-allowed;
}

.loading {
  text-align: center;
  padding: 20px;
  background-color: #e3f2fd;
  border-radius: 8px;
  margin: 20px 0;
}

.error-message {
  text-align: center;
  padding: 15px;
  background-color: #ffebee;
  color: #c62828;
  border-radius: 8px;
  margin: 20px 0;
  position: relative;
}

.clear-error {
  position: absolute;
  right: 10px;
  top: 10px;
  background-color: transparent;
  color: #c62828;
  padding: 2px 8px;
  font-size: 0.8em;
}

.debug-info {
  background-color: #f1f8e9;
  border: 1px solid #dcedc8;
  border-radius: 8px;
  padding: 15px;
  margin: 20px 0;
  position: relative;
  max-height: 300px;
  overflow: auto;
}

.debug-info h3 {
  margin-top: 0;
  color: #558b2f;
}

.debug-info pre {
  white-space: pre-wrap;
  font-size: 0.9em;
}

.clear-debug {
  position: absolute;
  right: 10px;
  top: 10px;
  background-color: transparent;
  color: #558b2f;
  padding: 2px 8px;
  font-size: 0.8em;
}
</style>
