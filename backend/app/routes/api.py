import os
import re
import json
import logging
from flask import Blueprint, request, jsonify

from app.services.crawler import crawl_comments_by_keyword
from app.services.analyzer import CommentAnalyzer
from settings.config import DATA_DIR
from settings.config import Config

# 设置日志
logger = logging.getLogger(__name__)

api_bp = Blueprint('api', __name__)


# 修改fetch_comments路由
@api_bp.route('/fetch-comments', methods=['POST'])
def fetch_comments():
    data = request.json or {}
    keyword = data.get('keyword', '').strip()
    genre = data.get('genre', '').strip()
    platform = data.get('platform', 'bilibili').strip().lower()

    # 平台验证
    if platform not in Config.SUPPORTED_PLATFORMS:
        logger.error(f"不支持的平台类型: {platform}")
        return jsonify({
            'success': False,
            'error': f'不支持的平台类型: {platform}。请使用: {", ".join(Config.SUPPORTED_PLATFORMS)}'
        }), 400

    if not keyword:
        logger.error("缺少关键词参数")
        return jsonify({
            'success': False,
            'data': None,
            'error': 'Missing keyword parameter'
        }), 400

    try:
        # 用关键词调用爬虫，返回 DataFrame
        logger.info(f"开始获取 {platform} 平台的评论，关键词: {keyword}")
        df = crawl_comments_by_keyword(keyword, platform)

        if df.empty:
            logger.warning(f"未获取到{platform}评论数据")
            return jsonify({
                'success': False,
                'data': None,
                'error': f'无法获取{platform}评论数据，可能限制了访问。请稍后再试或更换关键词。'
            }), 429
        # 确保所有数据都可序列化
        comments = df.to_dict(orient='records')
        safe_key = keyword.replace(' ', '_')
        dir_path = os.path.join(DATA_DIR, safe_key)
        os.makedirs(dir_path, exist_ok=True)

        comments_path = os.path.join(dir_path, f'comments_{platform}.json')
        with open(comments_path, 'w', encoding='utf-8') as f:
            json.dump(comments, f, ensure_ascii=False, indent=2, default=str)  # 添加default=str处理不可序列化对象

        logger.info(f"成功获取{len(comments)}条{platform}评论，保存至 {comments_path}")

        # 获取评论后立即进行分析
        try:
            logger.info(f"开始分析 {platform} 平台评论")
            analyzer = CommentAnalyzer()
            result = analyzer.analyze_comments(comments, genre, platform)  # 明确传递平台参数

            # 保存分析结果
            report_path = os.path.join(dir_path, f'report_{platform}.json')
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            logger.info(f"成功生成 {platform} 平台分析报告，保存至 {report_path}")
        except Exception as analysis_error:
            logger.error(f"分析 {platform} 评论时出错: {str(analysis_error)}")
            # 评论获取成功，但分析失败，仍然返回成功状态

        return jsonify({
            'success': True,
            'data': {
                'message': f'{platform}评论获取成功',
                'keyword': keyword,
                'platform': platform,
                'count': len(comments),
                'commentsPath': comments_path
            },
            'error': None
        }), 200

    except Exception as e:
        logger.error(f"抓取{platform}评论时出错: {str(e)}")
        error_message = str(e)

        if "412" in error_message and "Precondition Failed" in error_message:
            return jsonify({
                'success': False,
                'data': None,
                'error': 'B站拒绝访问（412 Precondition Failed）。请等待一段时间后再试。'
            }), 429

        if "quotaExceeded" in error_message:
            return jsonify({
                'success': False,
                'data': None,
                'error': 'YouTube API配额已用完。请稍后再试或联系管理员。'
            }), 429

        if "API key" in error_message and "invalid" in error_message:
            return jsonify({
                'success': False,
                'data': None,
                'error': 'YouTube API密钥无效。请检查配置或联系管理员。'
            }), 401

        return jsonify({
            'success': False,
            'data': None,
            'error': error_message
        }), 500


@api_bp.route('/compare-analysis/<keyword>', methods=['GET'])
def compare_analysis(keyword):
    genre = request.args.get('genre', '').strip()

    # 处理关键词中的特殊字符
    safe_key = re.sub(r'[\\/*?:"<>|]', '', keyword).replace(' ', '_')
    dir_path = os.path.join(DATA_DIR, safe_key)

    # 检查两个平台的评论是否都存在
    bilibili_comments_path = os.path.join(dir_path, 'comments_bilibili.json')
    youtube_comments_path = os.path.join(dir_path, 'comments_youtube.json')

    if not os.path.exists(bilibili_comments_path):
        logger.error(f"未找到哔哩哔哩评论文件: {bilibili_comments_path}")
        return jsonify({
            'success': False,
            'data': None,
            'error': '需要先获取哔哩哔哩平台的评论数据'
        }), 404

    if not os.path.exists(youtube_comments_path):
        logger.error(f"未找到YouTube评论文件: {youtube_comments_path}")
        return jsonify({
            'success': False,
            'data': None,
            'error': '需要先获取YouTube平台的评论数据'
        }), 404

    try:
        # 读取两个平台的评论
        with open(bilibili_comments_path, 'r', encoding='utf-8') as f:
            bilibili_comments = json.load(f)
        with open(youtube_comments_path, 'r', encoding='utf-8') as f:
            youtube_comments = json.load(f)

        # 检查是否已有对比分析报告
        compare_report_path = os.path.join(dir_path, 'compare_report.json')

        if not os.path.exists(compare_report_path):
            logger.info(f"生成新的对比分析报告: {compare_report_path}")

            analyzer = CommentAnalyzer()
            compare_result = analyzer.compare_platforms(
                bilibili_comments,
                youtube_comments,
                "", "",  # 可以传空字符串，因为我们不需要单独的报告
                genre
            )

            # 验证结果
            if not compare_result or not isinstance(compare_result, dict):
                logger.error(f"对比分析返回的结果无效: {compare_result}")
                return jsonify({
                    'success': False,
                    'data': None,
                    'error': '对比分析返回的结果无效'
                }), 500

            # 保存对比报告
            with open(compare_report_path, 'w', encoding='utf-8') as f:
                json.dump(compare_result, f, ensure_ascii=False, indent=2)
        else:
            logger.info(f"使用现有对比分析报告: {compare_report_path}")
            with open(compare_report_path, 'r', encoding='utf-8') as f:
                compare_result = json.load(f)

        return jsonify({
            'success': True,
            'data': {
                'report': compare_result.get('report'),
                'sentimentCompare': compare_result.get('sentiment_compare'),
                'topicsCompare': compare_result.get('topics_compare')
            },
            'error': None
        }), 200

    except Exception as e:
        logger.error(f"生成对比分析报告时出错: {str(e)}")
        return jsonify({
            'success': False,
            'data': None,
            'error': str(e)
        }), 500


@api_bp.route('/analysis-report/<keyword>', methods=['GET'])
def get_analysis_report(keyword):
    genre = request.args.get('genre', '').strip()
    platform = request.args.get('platform', 'bilibili').strip().lower()

    # 平台验证
    if platform not in Config.SUPPORTED_PLATFORMS:
        return jsonify({
            'success': False,
            'error': f'不支持的平台类型: {platform}。请使用: {", ".join(Config.SUPPORTED_PLATFORMS)}'
        }), 400

    # 处理关键词中的特殊字符
    safe_key = re.sub(r'[\\/*?:"<>|]', '', keyword).replace(' ', '_')
    dir_path = os.path.join(DATA_DIR, safe_key)

    # 根据平台使用不同的文件名
    comments_path = os.path.join(dir_path, f'comments_{platform}.json')
    report_path = os.path.join(dir_path, f'report_{platform}.json')

    logger.info(f"查找评论文件: {comments_path} (平台: {platform})")

    if not os.path.exists(comments_path):
        logger.error(f"评论文件不存在: {comments_path}")
        return jsonify({
            'success': False,
            'data': None,
            'error': 'Comments not found for this keyword'
        }), 404

    try:
        if not os.path.exists(report_path):
            logger.info(f"生成新的分析报告: {report_path} (平台: {platform})")
            with open(comments_path, 'r', encoding='utf-8') as f:
                comments = json.load(f)

            analyzer = CommentAnalyzer()
            result = analyzer.analyze_comments(comments, genre, platform)  # 传入platform参数

            # 添加结果验证
            if not result or not isinstance(result, dict):
                logger.error(f"分析结果无效: {result}")
                return jsonify({
                    'success': False,
                    'data': None,
                    'error': f'分析返回的结果无效，平台: {platform}'
                }), 500

            # 确保目录存在
            os.makedirs(dir_path, exist_ok=True)
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
        else:
            logger.info(f"使用现有分析报告: {report_path}")
            with open(report_path, 'r', encoding='utf-8') as f:
                result = json.load(f)

        return jsonify({
            'success': True,
            'data': {
                'report': result.get('report'),  # 使用正确的键名
                'sentimentData': result.get('sentiment_data'),
                'topicsData': result.get('topics_data'),
                'commentCount': result.get('comment_count', 0)
            },
            'error': None
        }), 200

    except Exception as e:
        logger.error(f"生成分析报告时出错: {str(e)}")
        return jsonify({
            'success': False,
            'data': None,
            'error': str(e)
        }), 500


@api_bp.route('/chat', methods=['POST'])
def chat_with_deepseek():
    data = request.json or {}
    keyword = data.get('keyword', '').strip()
    message = data.get('message', '').strip()
    genre = data.get('genre', '').strip()
    platform = data.get('platform', '').strip().lower()  # 获取平台参数

    # 平台验证（对于非对比平台）
    if platform and platform != 'compare' and platform not in Config.SUPPORTED_PLATFORMS:
        return jsonify({
            'success': False,
            'error': f'不支持的平台类型: {platform}。请使用: {", ".join(Config.SUPPORTED_PLATFORMS)} 或 compare'
        }), 400

    if not keyword or not message:
        return jsonify({
            'success': False,
            'data': None,
            'error': 'Missing required parameters'
        }), 400

    # 处理关键词中的特殊字符
    safe_key = re.sub(r'[\\/*?:"<>|]', '', keyword).replace(' ', '_')
    dir_path = os.path.join(DATA_DIR, safe_key)

    # 根据平台参数决定使用哪些文件
    if platform == 'compare':
        # 处理对比分析场景
        bilibili_comments_path = os.path.join(dir_path, 'comments_bilibili.json')
        youtube_comments_path = os.path.join(dir_path, 'comments_youtube.json')
        # 修正报告路径保持一致
        compare_report_path = os.path.join(dir_path, 'compare_report.json')

        if not os.path.exists(compare_report_path):
            logger.error(f"未找到对比分析报告: {compare_report_path}")
            return jsonify({
                'success': False,
                'data': None,
                'error': 'Comparison analysis data not found'
            }), 404

        try:
            with open(bilibili_comments_path, 'r', encoding='utf-8') as f:
                bilibili_comments = json.load(f)
            with open(youtube_comments_path, 'r', encoding='utf-8') as f:
                youtube_comments = json.load(f)
            with open(compare_report_path, 'r', encoding='utf-8') as f:
                analysis_result = json.load(f)

            # 合并两个平台的评论，优先使用较多的那个
            comments = bilibili_comments if len(bilibili_comments) >= len(youtube_comments) else youtube_comments

            analyzer = CommentAnalyzer()
            reply = analyzer.chat_with_ai(
                comments,
                analysis_result.get('report'),
                message,
                genre
            )

            return jsonify({
                'success': True,
                'data': {
                    'reply': reply
                },
                'error': None
            }), 200

        except Exception as e:
            logger.error(f"AI聊天时出错: {str(e)}")
            return jsonify({
                'success': False,
                'data': None,
                'error': str(e)
            }), 500
    else:
        # 处理单平台分析场景
        if not platform:
            platform = 'bilibili'  # 默认使用B站
            logger.info(f"未指定平台，默认使用: {platform}")

        comments_path = os.path.join(dir_path, f'comments_{platform}.json')
        report_path = os.path.join(dir_path, f'report_{platform}.json')

        if not os.path.exists(comments_path) or not os.path.exists(report_path):
            logger.error(f"未找到 {platform} 平台的分析数据")
            return jsonify({
                'success': False,
                'data': None,
                'error': f'Analysis data for {platform} not found'
            }), 404

        try:
            with open(comments_path, 'r', encoding='utf-8') as f:
                comments = json.load(f)
            with open(report_path, 'r', encoding='utf-8') as f:
                analysis_result = json.load(f)

            analyzer = CommentAnalyzer()
            reply = analyzer.chat_with_ai(
                comments,
                analysis_result.get('report'),
                message,
                genre
            )

            return jsonify({
                'success': True,
                'data': {
                    'reply': reply
                },
                'error': None
            }), 200

        except Exception as e:
            logger.error(f"AI聊天时出错: {str(e)}")
            return jsonify({
                'success': False,
                'data': None,
                'error': str(e)
            }), 500


@api_bp.route('/check-platform-data/<keyword>', methods=['GET'])
def check_platform_data(keyword):
    genre = request.args.get('genre', '').strip()
    platform = request.args.get('platform', '').strip().lower()

    # 平台验证
    if platform not in Config.SUPPORTED_PLATFORMS:
        return jsonify({
            'success': False,
            'error': f'不支持的平台类型: {platform}。请使用: {", ".join(Config.SUPPORTED_PLATFORMS)}'
        }), 400

    safe_key = re.sub(r'[\\/*?:"<>|]', '', keyword).replace(' ', '_')
    dir_path = os.path.join(DATA_DIR, safe_key)

    comments_path = os.path.join(dir_path, f'comments_{platform}.json')
    report_path = os.path.join(dir_path, f'report_{platform}.json')

    result = {
        'platform': platform,
        'keyword': keyword,
        'commentsFileExists': os.path.exists(comments_path),
        'reportFileExists': os.path.exists(report_path),
        'fileInfo': {}
    }

    if os.path.exists(comments_path):
        file_stats = os.stat(comments_path)
        try:
            with open(comments_path, 'r', encoding='utf-8') as f:
                comments = json.load(f)
                result['fileInfo']['comments'] = {
                    'count': len(comments),
                    'sizeBytes': file_stats.st_size,
                    'lastModified': file_stats.st_mtime
                }
        except Exception as e:
            result['fileInfo']['comments'] = {
                'error': str(e),
                'sizeBytes': file_stats.st_size
            }

    if os.path.exists(report_path):
        file_stats = os.stat(report_path)
        try:
            with open(report_path, 'r', encoding='utf-8') as f:
                report = json.load(f)
                result['fileInfo']['report'] = {
                    'sizeBytes': file_stats.st_size,
                    'lastModified': file_stats.st_mtime,
                    'hasReport': 'report' in report and bool(report['report'])
                }
        except Exception as e:
            result['fileInfo']['report'] = {
                'error': str(e),
                'sizeBytes': file_stats.st_size
            }

    return jsonify({
        'success': True,
        'data': result,
        'error': None
    }), 200


@api_bp.route('/debug-platform-data/<keyword>', methods=['GET'])
def debug_platform_data(keyword):
    platform = request.args.get('platform', 'youtube').strip().lower()

    # 平台验证
    if platform not in Config.SUPPORTED_PLATFORMS:
        return jsonify({
            'success': False,
            'error': f'不支持的平台类型: {platform}。请使用: {", ".join(Config.SUPPORTED_PLATFORMS)}'
        }), 400

    safe_key = re.sub(r'[\\/*?:"<>|]', '', keyword).replace(' ', '_')
    dir_path = os.path.join(DATA_DIR, safe_key)

    comments_path = os.path.join(dir_path, f'comments_{platform}.json')
    report_path = os.path.join(dir_path, f'report_{platform}.json')

    if not os.path.exists(comments_path):
        logger.error(f"未找到{platform}评论文件: {comments_path}")
        return jsonify({
            'success': False,
            'data': None,
            'error': f'未找到{platform}评论文件'
        }), 404

    try:
        with open(comments_path, 'r', encoding='utf-8') as f:
            comments = json.load(f)

        report_data = None
        if os.path.exists(report_path):
            try:
                with open(report_path, 'r', encoding='utf-8') as f:
                    report_data = json.load(f)
            except Exception as e:
                logger.error(f"读取报告文件出错: {str(e)}")

        # 返回前10条评论样本
        sample = comments[:10] if len(comments) > 10 else comments

        return jsonify({
            'success': True,
            'data': {
                'totalComments': len(comments),
                'sample': sample,
                'hasReport': report_data is not None,
                'reportInfo': {
                    'hasContent': report_data is not None and 'report' in report_data and bool(report_data['report']),
                    'keys': list(report_data.keys()) if report_data else []
                } if report_data else None,
                'filePath': comments_path
            },
            'error': None
        }), 200
    except Exception as e:
        logger.error(f"调试平台数据时出错: {str(e)}")
        return jsonify({
            'success': False,
            'data': None,
            'error': f'读取文件时出错: {str(e)}'
        }), 500


@api_bp.route('/debug-analyzer-status', methods=['GET'])
def debug_analyzer_status():
    """返回分析器的当前状态和配置"""
    try:
        analyzer = CommentAnalyzer()
        return jsonify({
            'success': True,
            'data': {
                'supported_platforms': Config.SUPPORTED_PLATFORMS,
                'api_keys_configured': {
                    'deepseek': bool(Config.DEEPSEEK_API_KEY),
                    'youtube': bool(Config.YOUTUBE_API_KEY)
                },
                'data_directory': DATA_DIR,
                'analyzer_version': getattr(analyzer, 'VERSION', 'unknown')
            },
            'error': None
        }), 200
    except Exception as e:
        logger.error(f"获取分析器状态时出错: {str(e)}")
        return jsonify({
            'success': False,
            'data': None,
            'error': f'获取分析器状态时出错: {str(e)}'
        }), 500
