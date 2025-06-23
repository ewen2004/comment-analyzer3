<template>
  <div class="chat-box">
    <h2>与AI助手交流</h2>
    <!-- 可选：展示当前分析的关键词 -->
    <p v-if="keyword" class="keyword-tip">
      正在分析关键词：<strong>{{ keyword }}</strong>
    </p>

    <div class="messages" ref="messagesContainer">
      <div
        v-for="(msg, index) in messages"
        :key="index"
        :class="['message', msg.role]"
      >
        <div class="message-content" v-html="formatMessage(msg.content)"></div>
      </div>

      <div v-if="loading" class="message assistant loading">
        <span class="loading-dots">
          <span></span>
          <span></span>
          <span></span>
        </span>
      </div>
    </div>

    <div class="input-area">
      <el-input
        v-model="inputMessage"
        type="textarea"
        :rows="2"
        placeholder="请输入您的问题..."
        :disabled="loading"
        @keydown.enter.exact.prevent="handleSend"
      />
      <el-button
        type="primary"
        :disabled="!inputMessage.trim() || loading"
        @click="handleSend"
      >
        发送
      </el-button>
    </div>
  </div>
</template>

<script>
import { marked } from "marked";

export default {
  name: "ChatBox",
  props: {
    // 改为通用的 keyword
    keyword: {
      type: String,
      required: true,
    },
    messages: {
      type: Array,
      default: () => [],
    },
    loading: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      inputMessage: "",
    };
  },
  watch: {
    messages() {
      this.$nextTick(() => {
        this.scrollToBottom();
      });
    },
  },
  methods: {
    handleSend() {
      if (!this.inputMessage.trim() || this.loading) return;
      //emit 消息内容，父组件里拿 keyword 发请求
      this.$emit("send-message", this.inputMessage);
      this.inputMessage = "";
    },
    formatMessage(content) {
      return marked(content);
    },
    scrollToBottom() {
      const container = this.$refs.messagesContainer;
      container.scrollTop = container.scrollHeight;
    },
  },
  mounted() {
    this.scrollToBottom();
  },
};
</script>

<style scoped>
.chat-box {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  height: 500px;
}

.messages {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 15px;
}

.message {
  max-width: 80%;
  padding: 10px 15px;
  border-radius: 10px;
  word-break: break-word;
}

.message.user {
  align-self: flex-end;
  background-color: #409eff;
  color: white;
}

.message.assistant {
  align-self: flex-start;
  background-color: #f2f6fc;
  color: #303133;
}

.message-content :deep(p) {
  margin: 0;
}

.message-content :deep(pre) {
  background: #f8f8f8;
  padding: 10px;
  border-radius: 5px;
  overflow-x: auto;
  margin: 10px 0;
}

.message-content :deep(code) {
  font-family: monospace;
}

.input-area {
  display: flex;
  gap: 10px;
}

.loading-dots {
  display: flex;
  gap: 4px;
}

.loading-dots span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #909399;
  display: inline-block;
  animation: bounce 1.4s infinite ease-in-out both;
}

.loading-dots span:nth-child(1) {
  animation-delay: -0.32s;
}

.loading-dots span:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes bounce {
  0%,
  80%,
  100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}
</style>
