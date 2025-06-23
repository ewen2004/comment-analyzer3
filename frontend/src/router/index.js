import { createRouter, createWebHistory } from 'vue-router';
import NovelPreferencePage from '@/views/NovelPreferencePage.vue';
import HomePage from '@/views/HomePage.vue';
import AnalysisPage from '@/views/AnalysisPage.vue';
import ComparisonPage from '@/views/ComparisonPage.vue';
// 支持的平台类型
const SUPPORTED_PLATFORMS = ['bilibili', 'youtube'];
const routes = [
  // 根路径重定向到偏好选择页
  {
    path: '/',
    redirect: '/preference'
  },
  // 小说偏好页
  {
    path: '/preference',
    name: 'Preference',
    component: NovelPreferencePage,
    meta: {
      title: '选择小说偏好'
    }
  },
  // HomePage 接收 genre 查询参数
  {
    path: '/home',
    name: 'Home',
    component: HomePage,
    props: route => ({
      genre: route.query.genre || '',
      platform: SUPPORTED_PLATFORMS.includes(route.query.platform?.toLowerCase()) 
        ? route.query.platform.toLowerCase() 
        : 'bilibili' // 默认值
    }),
    meta: {
      title: '首页'
    }
  },
  // 分析页面使用通用 keyword 参数
  {
    path: '/analysis/:keyword',
    name: 'Analysis',
    component: AnalysisPage,
    props: route => ({
      keyword: route.params.keyword,
      genre: route.query.genre || '',
      platform: SUPPORTED_PLATFORMS.includes(route.query.platform?.toLowerCase()) 
        ? route.query.platform.toLowerCase() 
        : 'bilibili' // 默认值
    }),
    meta: {
      title: '分析报告'
    },
    // 路由守卫 - 验证关键词
    beforeEnter: (to, from, next) => {
      if (!to.params.keyword || to.params.keyword.trim() === '') {
        next({ name: 'Home' }); // 如果关键词为空，重定向到首页
      } else {
        next();
      }
    }
  },
  // 对比分析页面 - 修改为
  {
    path: '/comparison/:keyword',  // 添加 :keyword 参数
    name: 'CompareAnalysis',      // 改为 CompareAnalysis 匹配代码中使用的名称
    component: ComparisonPage,
    props: route => ({            // 添加 props 函数处理参数
      keyword: route.params.keyword,
      genre: route.query.genre || ''
    }),
    meta: {
      title: '平台对比分析'
    }
  }
];

const router = createRouter({
  history: createWebHistory(import.meta.env.VITE_BASE_URL),
  routes,
  // 滚动行为
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition;
    } else {
      return { top: 0 };
    }
  }
});

// 设置页面标题
router.beforeEach((to, from, next) => {
  document.title = to.meta.title || '评论分析系统';
  next();
});

export default router;
