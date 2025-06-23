import axios from 'axios';

const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api';
const api = axios.create({
  baseURL,
  timeout: 300000, // 5 分钟超时
});

// 请求拦截器
api.interceptors.request.use(
  config => {
    // 添加请求日志
    console.log(`发送请求: ${config.method.toUpperCase()} ${config.url}`, config.params || config.data);
    return config;
  },
  error => Promise.reject(error)
);

// 响应拦截器增强
api.interceptors.response.use(
  response => {
    console.log(`请求成功: ${response.config.url}`, response.data);
    return response.data;
  },
  error => {
    if (error.code === 'ECONNABORTED') {
      console.error('请求超时，请检查网络连接或稍后重试');
    } else {
      console.error('API 错误:', error.response?.data?.error || error.message);
      console.error('错误详情:', error.config?.url, error.response?.data);
    }
    return Promise.reject(error);
  }
);


export default {
  // 按关键词抓取评论
  fetchComments(keyword, genre, platform = 'bilibili') {
    console.log(`正在抓取${platform}评论，关键词: ${keyword}, 类型: ${genre}`);
    return api.post('/fetch-comments', { 
      keyword: keyword.trim(), 
      genre: genre ? genre.trim() : '', 
      platform: platform.toLowerCase() 
    });
  },

  // 获取关键词分析报告
  getAnalysisReport(keyword, genre, platform = 'bilibili') {
    console.log(`正在获取${platform}分析报告，关键词: ${keyword}, 类型: ${genre}`);
    return api.get(
      `/analysis-report/${encodeURIComponent(keyword)}`,
      { 
        params: { 
          genre: genre ? genre.trim() : '', 
          platform: platform.toLowerCase() 
        } 
      }
    );
  },

  // 与 DeepSeek 聊天接口
  chatWithDeepSeek(keyword, message, genre, platform = 'bilibili') {
    console.log(`聊天使用平台: ${platform}, 关键词: ${keyword}`);
    return api.post('/chat', { 
      keyword: keyword.trim(), 
      message: message.trim(), 
      genre: genre ? genre.trim() : '', 
      platform: platform.toLowerCase() 
    });
  },

  // 获取平台对比分析
  getCompareAnalysis(keyword, genre) {
    console.log(`获取平台对比分析，关键词: ${keyword}, 类型: ${genre}`);
    return api.get(
      `/compare-analysis/${encodeURIComponent(keyword)}`,
      { 
        params: { 
          genre: genre ? genre.trim() : ''
        } 
      }
    );
  },

  // 新增：检查平台数据状态
  checkPlatformDataStatus(keyword, genre, platform) {
    console.log(`检查${platform}数据状态，关键词: ${keyword}`);
    return api.get(
      `/check-platform-data/${encodeURIComponent(keyword)}`,
      { 
        params: { 
          genre: genre ? genre.trim() : '', 
          platform: platform.toLowerCase() 
        } 
      }
    );
  },

  // 新增：调试接口
  debugPlatformData(keyword, platform = 'youtube') {
    console.log(`调试${platform}数据，关键词: ${keyword}`);
    return api.get(
      `/debug-platform-data/${encodeURIComponent(keyword)}`,
      { 
        params: { 
          genre: genre ? genre.trim() : '', 
          platform: platform.toLowerCase() 
        } 
      }
    );
  }
};
