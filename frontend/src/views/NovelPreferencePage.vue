<template>
  <div class="preference-container container">
    <div class="preference-card">
      <div class="header-section">
        <h1 class="main-title">欢迎！你喜欢什么类型的小说？</h1>
        <div class="subtitle-wrapper">
          <el-tag size="small" effect="plain" type="info">欢迎来到我们的游乐园！</el-tag>
        </div>
      </div>

      <div class="content-section">
        <div class="options-grid">
          <el-radio-group v-model="selected" class="radio-card-group">
            <el-radio-button
              v-for="opt in options"
              :key="opt.value"
              :label="opt.value"
              class="radio-card-item"
            >
              <div class="radio-card-content">
                <div class="icon-box" :class="{ 'active': selected === opt.value }">
                  <!-- 使用Font Awesome图标替代Element Plus图标 -->
                  <i :class="opt.icon"></i>
                </div>
                <div class="option-info">
                  <div class="option-title">{{ opt.label }}</div>
                  <div class="option-desc">{{ opt.description }}</div>
                </div>
              </div>
            </el-radio-button>
          </el-radio-group>
        </div>

        <div class="action-section">
          <el-button
            type="primary"
            size="large"
            :disabled="!selected"
            @click="next"
            class="submit-button"
          >
            <i class="fas fa-arrow-right"></i>
            开始分析
          </el-button>

          <div class="additional-actions">
            <el-button
              type="info"
              plain
              size="small"
              @click="selected = null"
              :disabled="!selected"
            >
              重新选择
            </el-button>
            <el-button
              type="info"
              link
              size="small"
              @click="showInfo = true"
            >
              了解更多
            </el-button>
          </div>
        </div>
      </div>

      <div class="footer-section">
        <span class="copyright">© 2025 对我好一点</span>
        <div class="links">
          <el-link type="info" :underline="false"@click="showPrivacyPolicy = true">隐私政策</el-link>
          <el-divider direction="vertical" />
          <el-link type="info" :underline="false"@click="showTermsOfUse = true">使用条款</el-link>
          <el-divider direction="vertical" />
          <el-link type="info" :underline="false" @click="showHelpCenter = true">帮助中心</el-link>
        </div>
      </div>
    </div>
    <!-- 隐私政策对话框 -->
    <el-dialog
      v-model="showPrivacyPolicy"
      title="详见使用条款ʕ⸝⸝˙Ⱉ˙ʔ"
      width="500px"
      align-center
    >
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showPrivacyPolicy = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 使用条款对话框 -->
    <el-dialog
      v-model="showTermsOfUse"
      title="详见帮助中心ʕ˶'༥'˶ʔ"
      width="500px"
      align-center
    >
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showTermsOfUse = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 帮助中心对话框 -->
    <el-dialog
      v-model="showHelpCenter"
      title="哈哈没有∠( ᐛ 」∠)＿"
      width="500px"
      align-center
    >
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showHelpCenter = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>

    <el-dialog
      v-model="showInfo"
      title="哈哈没有⌓‿⌓"
      width="500px"
      align-center
    >
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showInfo = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
export default {
  name: 'NovelPreferencePage',
  data() {
    return {
      options: [
        {
          value: '古早玛丽苏霸总',
          label: '古早玛丽苏霸总',
          icon: 'fas fa-crown',
          description: '霸道总裁与灰姑娘的现代童话'
        },
        {
          value: '校园青春疼痛',
          label: '校园青春疼痛',
          icon: 'fas fa-school',
          description: '青涩岁月里的成长与伤痛'
        },
        {
          value: '江湖仗义侠客梦',
          label: '江湖仗义侠客梦',
          icon: 'fas fa-user-ninja',
          description: '刀光剑影中的侠义情仇'
        },
        {
          value: '星际科幻未来',
          label: '星际科幻未来',
          icon: 'fas fa-rocket',
          description: '探索未知宇宙的奇幻冒险'
        },
        {
          value: '非虚构纪实文学',
          label: '非虚构纪实文学',
          icon: 'fas fa-book',
          description: '真实事件的深度记录与思考'
        },
        {
          value: '意识流伍尔夫',
          label: '意识流伍尔夫',
          icon: 'fas fa-brain',
          description: '内心世界的哲学探索之旅'
        },
        {
          value: '悬疑推理烧脑',
          label: '悬疑推理烧脑',
          icon: 'fas fa-search',
          description: '层层谜团中的智力挑战'
        },
      ],
      selected: null,
      showPrivacyPolicy: false,
      showTermsOfUse: false,
      showHelpCenter: false,
      showInfo: false
    }
  },
  methods: {
    next() {
      if (this.selected) {
        this.$router.push({ name: 'Home', query: { genre: this.selected } })
      }
    }
  }
}
</script>

<style scoped>
/* 引入Font Awesome */
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css');

.preference-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  background-color: #f5f7fa;
}

.preference-card {
  width: 100%;
  max-width: 900px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.header-section {
  padding: 30px;
  background: linear-gradient(90deg, #409eff 0%, #a0cfff 100%);
  color: white;
  position: relative;
  overflow: hidden;
}

.header-section::after {
  content: '';
  position: absolute;
  top: -50px;
  right: -50px;
  width: 150px;
  height: 150px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
}

.main-title {
  font-size: 28px;
  font-weight: 600;
  margin: 0 0 15px 0;
  position: relative;
  z-index: 1;
}

.subtitle-wrapper {
  display: flex;
  align-items: center;
  font-size: 16px;
  position: relative;
  z-index: 1;
}

.content-section {
  padding: 30px;
}

.options-grid {
  margin-bottom: 30px;
}

.radio-card-group {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 16px;
  width: 100%;
}

.radio-card-item {
  height: auto;
  margin: 0;
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.3s ease;
}

/* Override Element Plus default radio styles */
.radio-card-item :deep(.el-radio-button__inner) {
  width: 100%;
  height: 100%;
  padding: 0;
  border-radius: 8px !important;
  border: 1px solid #e4e7ed;
  border-left: 1px solid #e4e7ed !important;
  display: block;
  text-align: left;
  transition: all 0.3s;
}

.radio-card-item:first-child :deep(.el-radio-button__inner) {
  border-left: 1px solid #e4e7ed !important;
}

.radio-card-item:hover :deep(.el-radio-button__inner) {
  border-color: #a0cfff;
  box-shadow: 0 0 0 1px #a0cfff;
  z-index: 1;
}

.radio-card-item :deep(.el-radio-button__original-radio:checked + .el-radio-button__inner) {
  background-color: #f5f7fa;
  color: inherit;
  border-color: #409eff;
  box-shadow: 0 0 0 1px #409eff;
}

.radio-card-content {
  display: flex;
  align-items: center;
  padding: 16px 20px;
}

.icon-box {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  background-color: #f5f7fa;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #909399;
  transition: all 0.3s;
  flex-shrink: 0;
}

.icon-box i {
  font-size: 18px;
}

.icon-box.active {
  background-color: #ecf5ff;
  color: #409eff;
}

.option-info {
  margin-left: 16px;
  flex: 1;
}

.option-title {
  font-size: 15px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
}

.option-desc {
  font-size: 12px;
  color: #909399;
  line-height: 1.4;
}

.action-section {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.submit-button {
  width: 100%;
  max-width: 400px;
  height: 48px;
  font-size: 16px;
  border-radius: 24px;
  margin-bottom: 16px;
  background: linear-gradient(90deg, #409eff 0%, #79bbff 100%);
  border: none;
  transition: all 0.3s;
}

.submit-button i {
  margin-right: 8px;
}

.submit-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(64, 158, 255, 0.2);
}

.submit-button:disabled {
  background: #a0cfff;
  opacity: 0.7;
}

.additional-actions {
  display: flex;
  gap: 16px;
}

.footer-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 30px;
  background-color: #f5f7fa;
  border-top: 1px solid #ebeef5;
  font-size: 12px;
  color: #909399;
}

.links {
  display: flex;
  align-items: center;
}

@media (max-width: 768px) {
  .radio-card-group {
    grid-template-columns: 1fr;
  }

  .footer-section {
    flex-direction: column;
    gap: 10px;
  }
}
</style>
