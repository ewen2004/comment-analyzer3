<template>
  <div class="charts-container">
    <div class="chart-card">
      <h3>情感分析</h3>
      <div ref="sentimentChartRef" class="chart"></div>
    </div>

    <div class="chart-card">
      <h3>主题词分析</h3>
      <div ref="topicsChartRef" class="chart"></div>
    </div>
  </div>
</template>

<script>
import * as echarts from 'echarts'
import 'echarts-wordcloud'

export default {
  name: 'Charts',
  props: {
    sentimentData: {
      type: Object,
      default: () => ({
        positive: 0,
        negative: 0,
        neutral: 0
      })
    },
    topicsData: {
      type: Object,
      default: () => ({})
    }
  },
  data() {
    return {
      sentimentChart: null,
      topicsChart: null
    }
  },
  mounted() {
    // 等待DOM加载完成后初始化
    this.$nextTick(() => {
      this.initCharts()
    })

    // 监听窗口大小变化
    window.addEventListener('resize', this.handleResize)
  },
  beforeUnmount() {
    // 清理事件监听
    window.removeEventListener('resize', this.handleResize)

    // 销毁图表实例
    if (this.sentimentChart) {
      this.sentimentChart.dispose()
      this.sentimentChart = null
    }

    if (this.topicsChart) {
      this.topicsChart.dispose()
      this.topicsChart = null
    }
  },
  watch: {
    sentimentData: {
      handler(val) {
        if (val && this.sentimentChart) {
          this.renderSentimentChart()
        }
      },
      deep: true
    },
    topicsData: {
      handler(val) {
        if (val && this.topicsChart) {
          this.renderTopicsChart()
        }
      },
      deep: true
    }
  },
  methods: {
    initCharts() {
      if (this.$refs.sentimentChartRef) {
        this.sentimentChart = echarts.init(this.$refs.sentimentChartRef)
      }

      if (this.$refs.topicsChartRef) {
        this.topicsChart = echarts.init(this.$refs.topicsChartRef)
      }

      // 初始渲染
      if (this.sentimentData && this.sentimentChart) {
        this.renderSentimentChart()
      }

      if (this.topicsData && this.topicsChart) {
        this.renderTopicsChart()
      }
    },

    renderSentimentChart() {
      if (!this.sentimentChart || !this.sentimentData) return

      // 确保数据格式正确
      const sentimentData = this.sentimentData;

      const option = {
        tooltip: {
          trigger: 'item',
          formatter: '{b}: {c} ({d}%)'
        },
        legend: {
          orient: 'horizontal',
          bottom: 'bottom'
        },
        series: [
          {
            type: 'pie',
            radius: '70%',
            data: [
              { value: sentimentData.positive || 0, name: '正面', itemStyle: { color: '#67C23A' } },
              { value: sentimentData.negative || 0, name: '负面', itemStyle: { color: '#F56C6C' } },
              { value: sentimentData.neutral || 0, name: '中性', itemStyle: { color: '#909399' } }
            ],
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: 'rgba(0, 0, 0, 0.5)'
              }
            },
            label: {
              formatter: '{b}: {d}%'
            }
          }
        ]
      }

      this.sentimentChart.setOption(option)
    },

    renderTopicsChart() {
      console.log("渲染词云图，数据:", this.topicsData)
      if (!this.topicsChart || !this.topicsData) return

      const data = []
      // 将对象格式转换为词云所需的数组格式
      for (const [key, value] of Object.entries(this.topicsData)) {
        if (value > 0) { // 确保值为正
          data.push({ name: key, value })
        }
      }

      data.sort((a, b) => b.value - a.value);

      const option = {
        tooltip: {
          trigger: 'item',
          formatter: '{b}: {c}'
        },
        series: [{
          type: 'wordCloud',
          shape: 'circle',
          left: 'center',
          top: 'center',
          width: '90%',
          height: '90%',
          right: null,
          bottom: null,
          sizeRange: [12, 35],
          rotationRange: [-45, 45],
          rotationStep: 15,
          gridSize: 8,
          drawOutOfBound: false,
          textStyle: {
            fontFamily: 'sans-serif',
            fontWeight: 'bold',
            color: function(params) {
              const rank = data.findIndex(item => item.name === params.name);
              const saturation = Math.round(50 + 50 * (1 - Math.min(rank, 10) / 10));
              const lightness = Math.round(25 + 25 * (Math.min(rank, 10) / 10));
              return `hsl(${(rank * 30) % 360}, ${saturation}%, ${lightness}%)`;
            }
          },
          emphasis: {
            focus: 'self',
            textStyle: {
              shadowBlur: 10,
              shadowColor: '#333'
            }
          },
          data: data.length ? data : [{ name: '暂无数据', value: 1 }] // 提供默认数据避免空图表
        }]
      }

      this.topicsChart.setOption(option)
    },

    handleResize() {
      if (this.sentimentChart) {
        this.sentimentChart.resize()
      }
      if (this.topicsChart) {
        this.topicsChart.resize()
      }
    }
  }
}
</script>

<style scoped>
.charts-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.chart-card {
  background: white;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.chart-card h3 {
  margin-bottom: 15px;
  font-weight: 600;
  color: #303133;
}

.chart {
  height: 300px;
  width: 100%;
}
</style>
