# 项目简介

本项目的目标是为广泛用户提供一个便捷 API 工具，使其能够快速获取海内外关于任何特定话题的优质评论数据，主要评论采集平台为 YouTube、Bilibili 并对这些数据进行对比分析。通过这种方式，我们希望为用户提供更全面的视角，打破信息茧房，拓宽认知边界。

为了打破算法偏见，爬虫除了捕获高播放视频的评论，同时筛选出播评比，即评论数量/播放数量这一比值较高的数据，这样的评论数据可认为是主流舆论下的小圈层中坚意见，算是打破信息茧房的思路尝试。

评论数据分析上使用 Deepseek 进行不同平台的分析、以及对比分析，并做了许多有趣的尝试。页面结构如下：

## 页面模块
| 页面                 | 模块                                                        |
|----------------------|-------------------------------------------------------------|
| 用户兴趣页           | 写作风格选择模块、平台关键词输入模块                        |
| B站评论分析页面      | 评论分析报告模块、可视化模块、AI小助手模块                 |
| youtube评论分析页面 | 评论分析报告模块、可视化模块、AI小助手模块                 |
| 对比分析页面         | 对比分析模块、新媒体推文模块、AI小助手模块                 |

本科课程作业，诸多不完备之处敬请谅解，
## 运行方式

1. 先运行后端 `main.py` 文件。
2. 在 `Windows` 中按下 `Windows + R` 打开运行窗口，输入 `cmd` 打开命令行，通过 `cd` 命令切换到前端文件夹 `frontend`，并执行以下命令：

   ```bash
   cd path\to\your\project\frontend
   npm run dev

## 注意事项

- **DEEPSEEK 官方 API 获取**：[https://api-docs.deepseek.com/zh-cn/](https://api-docs.deepseek.com/zh-cn/)
  
- 根据你的需要，在 `backend/settings/config.py` 中修改爬虫参数：
  - `MAX_WORKERS`
  - `BASE_DELAY`
  - `MIN_COMMENTS`
  - `SECONDARY_BATCH_SIZE`
  - `MAX_TOTAL_COMMENTS`
  - `MAX_VIDEOS_PER_KEYWORD`
  - `MAX_COMMENTS_PER_VIDEO`

- 访问 YouTube 的爬虫需要通过梯子实现，我使用免费的 [v2free](https://v2free.net/user)，下载地址及使用方法见网页内部。如果你使用的是自己的梯子，只需在 `backend/settings/config.py` 中修改 `YOUTUBE_API_KEY`、`YOUTUBE_PROXY_HOST`、`YOUTUBE_PROXY_PORT`。

- `comment_texts[:800]`：限制只取前 800 条评论内容，拼成字符串，也就是最多把 800 条评论送进模型的提示。

- **B 站 Cookie**：可通过环境变量 `BILIBILI_COOKIE`，或默认从项目根下的 `bili_cookie.txt` 文件读取。
 ## 页面预览
页面预览可在imges目录下查看