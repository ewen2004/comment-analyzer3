import requests
import random
import re
import json
import logging

from settings.config import Config
from settings.prompts import ANALYSIS_PROMPT, CHAT_PROMPT

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class CommentAnalyzer:
    def __init__(self):
        self.api_key = Config.DEEPSEEK_API_KEY
        # 使用正确的API URL
        self.api_url = Config.DEEPSEEK_API_URL
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        logger.info(f"初始化API URL: {self.api_url}")

    def compare_platforms(self, bilibili_comments, youtube_comments, bilibili_report, youtube_report, genre=''):
        """比较两个平台的评论并生成对比分析报告"""
        # 提取评论内容
        bilibili_texts = [
            f"{i + 1}. {comment['content']}"
            for i, comment in enumerate(bilibili_comments[:100])  # 限制评论数量
        ]
        youtube_texts = [
            f"{i + 1}. {comment['content']}"
            for i, comment in enumerate(youtube_comments[:10])  # 限制评论数量
        ]

        bilibili_str = "\n".join(bilibili_texts)
        youtube_str = "\n".join(youtube_texts)

        # 使用prompts.py中定义的COMPARE_PROMPT
        from settings.prompts import COMPARE_PROMPT

        formatted_prompt = COMPARE_PROMPT.format(
            bilibili_comments=bilibili_str,
            youtube_comments=youtube_str,
            genre=genre
        )

        logger.info("开始生成平台对比分析报告")

        try:
            response = self._call_deepseek_api(formatted_prompt)
            logger.info("成功获取API对比分析结果")

            # 清理响应内容
            cleaned_report = re.sub(
                r'<!--\s*系统数据区开始\s*-->[\s\S]*?<!--\s*系统数据区结束\s*-->',
                '',
                response
            )

            # 清理报告中出现的词频数据格式
            cleaned_report = re.sub(
                r'([^(（]*)\(([^)）]*次[^)）]*)\)',
                r'\1',
                cleaned_report
            )

            # 清理类似"关键词：季冠霖22次/声线18次"的格式
            cleaned_report = re.sub(
                r'([^\d]+)(\d+次)',
                r'\1',
                cleaned_report
            )

            # 清理斜杠分隔的词频列表
            cleaned_report = re.sub(
                r'([^/\d]+)\d+次/([^/\d]+)\d+次',
                r'\1、\2',
                cleaned_report
            )

            # 提取对比数据（可选，如果需要用于图表展示）
            sentiment_compare = self._extract_sentiment_compare(response)
            topics_compare = self._extract_topics_compare(response)

            return {
                "report": cleaned_report,
                "sentiment_compare": sentiment_compare,
                "topics_compare": topics_compare
            }
        except Exception as e:
            logger.error(f"生成对比分析报告时出错: {str(e)}")
            return {
                "report": f"对比分析失败: {str(e)}",
                "sentiment_compare": {},
                "topics_compare": {}
            }

    def analyze_comments(self, comments, genre='', platform='bilibili'):
        """分析评论并生成报告"""
        # 提取评论内容
        comment_texts = [
            f"{i + 1}. {comment['content']}"
            for i, comment in enumerate(comments[:100])  # 限制评论数量
        ]

        comments_str = "\n".join(comment_texts)

        # 使用prompts.py中定义的ANALYSIS_PROMPT
        formatted_prompt = ANALYSIS_PROMPT.format(
            comments=comments_str,
            platform=platform,
            genre=genre
        )

        logger.info(f"开始生成{platform}平台分析报告")

        try:
            response = self._call_deepseek_api(formatted_prompt)
            logger.info("成功获取API分析结果")

            # 清理响应内容
            cleaned_report = re.sub(
                r'<!--\s*系统数据区开始\s*-->[\s\S]*?<!--\s*系统数据区结束\s*-->',
                '',
                response
            )

            # 清理报告中出现的词频数据格式
            cleaned_report = re.sub(
                r'([^(（]*)\(([^)）]*次[^)）]*)\)',
                r'\1',
                cleaned_report
            )

            # 清理类似"关键词：季冠霖22次/声线18次"的格式
            cleaned_report = re.sub(
                r'([^\d]+)(\d+次)',
                r'\1',
                cleaned_report
            )

            # 清理斜杠分隔的词频列表
            cleaned_report = re.sub(
                r'([^/\d]+)\d+次/([^/\d]+)\d+次',
                r'\1、\2',
                cleaned_report
            )

            # 提取数据用于图表展示
            sentiment_data = self._extract_sentiment_data(response)
            topics_data = self._extract_topics_data(response)

            return {
                "report": cleaned_report,
                "sentiment_data": sentiment_data,
                "topics_data": topics_data
            }
        except Exception as e:
            logger.error(f"生成分析报告时出错: {str(e)}")
            return {
                "report": f"分析失败: {str(e)}",
                "sentiment_data": {"positive": 60, "negative": 20, "neutral": 20},
                "topics_data": {"数据提取错误": 20, "未分类主题": 10}
            }

    def _extract_sentiment_compare(self, report):
        """提取情感对比数据"""
        try:
            sentiment_compare = {
                "bilibili": {"positive": 0, "negative": 0, "neutral": 0},
                "youtube": {"positive": 0, "negative": 0, "neutral": 0}
            }

            # 匹配B站情感数据
            bilibili = re.search(r'哔哩哔哩[^%]*正面[：:]\s*(\d+)%[^%]*负面[：:]\s*(\d+)%[^%]*中性[：:]\s*(\d+)%', report)
            if bilibili:
                sentiment_compare["bilibili"]["positive"] = int(bilibili.group(1))
                sentiment_compare["bilibili"]["negative"] = int(bilibili.group(2))
                sentiment_compare["bilibili"]["neutral"] = int(bilibili.group(3))

            # 匹配YouTube情感数据
            youtube = re.search(r'YouTube[^%]*正面[：:]\s*(\d+)%[^%]*负面[：:]\s*(\d+)%[^%]*中性[：:]\s*(\d+)%', report)
            if youtube:
                sentiment_compare["youtube"]["positive"] = int(youtube.group(1))
                sentiment_compare["youtube"]["negative"] = int(youtube.group(2))
                sentiment_compare["youtube"]["neutral"] = int(youtube.group(3))

            # 验证数据合理性
            for platform in sentiment_compare:
                total = sum(sentiment_compare[platform].values())
                if total < 80 or total > 120:
                    logger.warning(f"{platform}情感分析总和异常({total}%)，使用默认值")
                    sentiment_compare[platform] = {"positive": 60, "negative": 20, "neutral": 20}

            return sentiment_compare
        except Exception as e:
            logger.error(f"提取情感对比数据时出错: {str(e)}")
            return {
                "bilibili": {"positive": 60, "negative": 20, "neutral": 20},
                "youtube": {"positive": 50, "negative": 30, "neutral": 20}
            }

    def _extract_topics_compare(self, report):
        """提取主题对比数据"""
        try:
            topics_compare = {
                "bilibili": {},
                "youtube": {},
                "common": {}  # 共同话题
            }

            # 尝试从系统数据区获取词频数据
            system_data = re.search(
                r'<!--\s*系统数据区开始\s*-->([\s\S]*?)<!--\s*系统数据区结束\s*-->',
                report
            )

            if system_data:
                system_text = system_data.group(1)

                # 提取B站关键词
                bilibili_section = re.search(r'哔哩哔哩关键词:([\s\S]*?)YouTube关键词:', system_text)
                if bilibili_section:
                    pairs = re.findall(r'-\s*([^：:]+)[：:]\s*(\d+)[次|个]?', bilibili_section.group(1))
                    for keyword, freq in pairs:
                        keyword = keyword.strip()
                        if keyword and len(keyword) > 1:
                            try:
                                topics_compare["bilibili"][keyword] = int(freq)
                            except ValueError:
                                topics_compare["bilibili"][keyword] = 10

                # 提取YouTube关键词
                youtube_section = re.search(r'YouTube关键词:([\s\S]*?)共同关键词:', system_text)
                if youtube_section:
                    pairs = re.findall(r'-\s*([^：:]+)[：:]\s*(\d+)[次|个]?', youtube_section.group(1))
                    for keyword, freq in pairs:
                        keyword = keyword.strip()
                        if keyword and len(keyword) > 1:
                            try:
                                topics_compare["youtube"][keyword] = int(freq)
                            except ValueError:
                                topics_compare["youtube"][keyword] = 10

                # 提取共同关键词
                common_section = re.search(r'共同关键词:([\s\S]*?)$', system_text)
                if common_section:
                    pairs = re.findall(r'-\s*([^：:]+)[：:]\s*(\d+)[次|个]?', common_section.group(1))
                    for keyword, freq in pairs:
                        keyword = keyword.strip()
                        if keyword and len(keyword) > 1:
                            try:
                                topics_compare["common"][keyword] = int(freq)
                            except ValueError:
                                topics_compare["common"][keyword] = 15

            # 如果没有足够的数据，尝试从报告文本中提取
            if not topics_compare["bilibili"] or not topics_compare["youtube"]:
                # 查找B站主题部分
                bilibili_section = re.search(r'哔哩哔哩[^:：]*关键词[^:：]*[：:]([\s\S]*?)(?:YouTube|油管)', report)
                if bilibili_section:
                    keywords = re.split(r'[,，、/\s]+', bilibili_section.group(1))
                    for i, kw in enumerate(keywords):
                        kw = kw.strip()
                        if kw and len(kw) > 1:
                            topics_compare["bilibili"][kw] = max(25 - i * 2, 10)

                # 查找YouTube主题部分
                youtube_section = re.search(r'YouTube[^:：]*关键词[^:：]*[：:]([\s\S]*?)(?:共同|相同|两个平台)', report)
                if youtube_section:
                    keywords = re.split(r'[,，、/\s]+', youtube_section.group(1))
                    for i, kw in enumerate(keywords):
                        kw = kw.strip()
                        if kw and len(kw) > 1:
                            topics_compare["youtube"][kw] = max(25 - i * 2, 10)

                # 查找共同主题部分
                common_section = re.search(r'(共同|相同)[^:：]*关键词[^:：]*[：:]([\s\S]*?)(?:\n\n|\Z)', report)
                if common_section:
                    keywords = re.split(r'[,，、/\s]+', common_section.group(2))
                    for i, kw in enumerate(keywords):
                        kw = kw.strip()
                        if kw and len(kw) > 1:
                            topics_compare["common"][kw] = max(30 - i * 2, 15)

            # 确保每个平台至少有一些关键词
            for platform in ["bilibili", "youtube", "common"]:
                if len(topics_compare[platform]) < 3:
                    if platform == "bilibili":
                        topics_compare[platform] = {"B站热门": 25, "B站讨论": 20, "B站特色": 15}
                    elif platform == "youtube":
                        topics_compare[platform] = {"YouTube热门": 25, "国际视角": 20, "YouTube特色": 15}
                    else:  # common
                        topics_compare[platform] = {"共同话题": 25, "通用讨论": 20, "跨平台": 15}

            # 限制每个平台最多显示10个主题
            for platform in topics_compare:
                if len(topics_compare[platform]) > 10:
                    sorted_topics = sorted(topics_compare[platform].items(), key=lambda x: x[1], reverse=True)
                    topics_compare[platform] = dict(sorted_topics[:10])

            return topics_compare
        except Exception as e:
            logger.error(f"提取主题对比数据时出错: {str(e)}")
            return {
                "bilibili": {"B站热门": 25, "B站讨论": 20, "B站特色": 15},
                "youtube": {"YouTube热门": 25, "国际视角": 20, "YouTube特色": 15},
                "common": {"共同话题": 25, "通用讨论": 20, "跨平台": 15}
            }

    def chat_with_ai(self, comments, report, question, genre: str = ''):
        """与 AI 交互"""
        try:
            comment_texts = [
                f"{i + 1}. {comment['content']}"
                for i, comment in enumerate(comments)
            ]
            comments_str = "\n".join(comment_texts[:100])
            prompt = CHAT_PROMPT.format(
                comments=comments_str,
                report=report,
                question=question,
                genre=genre
            )
            logger.info(f"开始聊天交互，问题: {question[:50]}...")
            return self._call_deepseek_api(prompt)
        except Exception as e:
            logger.error(f"聊天交互时出错: {str(e)}")
            return f"抱歉，无法完成对话。错误: {str(e)}"

    def _call_deepseek_api(self, prompt):
        """调用DeepSeek API并处理响应"""
        # DeepSeek模型名称可能需要根据实际API调整
        payload = {
            "model": "deepseek-chat",  # 根据DeepSeek的实际模型名称调整
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 2000
        }

        logger.info(f"发送请求到 {self.api_url}")
        logger.debug(f"请求内容前100字符: {json.dumps(payload, ensure_ascii=False)[:100]}...")

        try:
            # 打印完整请求信息
            print(f"发送到: {self.api_url}")
            print(f"请求头: {self.headers}")
            print(f"请求体: {json.dumps(payload, ensure_ascii=False)[:200]}...")

            resp = requests.post(self.api_url, headers=self.headers, json=payload, timeout=300)
            resp.encoding = 'utf-8'

            # 打印完整响应信息
            print(f"响应状态码: {resp.status_code}")
            print(f"响应内容: {resp.text[:200]}...")

            # 记录原始响应
            logger.debug(f"API原始响应: {resp.text[:500]}...")

            # 检查HTTP状态码
            resp.raise_for_status()

            # 解析JSON响应
            response_data = resp.json()

            # 打印解析后的响应结构
            print(
                f"响应数据结构: {json.dumps(response_data, ensure_ascii=False)[:200] if isinstance(response_data, dict) else '非字典类型'}...")

            # 根据DeepSeek API的响应格式提取文本内容
            if "choices" in response_data and len(response_data["choices"]) > 0:
                content = response_data["choices"][0]["message"]["content"]
                logger.info("成功从API响应中提取内容")
                return content
            else:
                error_msg = f"API响应格式不符合预期: {json.dumps(response_data, ensure_ascii=False)[:200]}"
                logger.error(error_msg)
                raise ValueError(error_msg)

        except requests.exceptions.RequestException as e:
            logger.error(f"API请求失败: {str(e)}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"响应状态码: {e.response.status_code}")
                logger.error(f"响应内容: {e.response.text[:500]}")
            raise Exception(f"API请求失败: {str(e)}")
        except json.JSONDecodeError as e:
            logger.error(f"无法解析JSON响应: {str(e)}")
            logger.error(f"原始响应: {resp.text[:500]}")
            raise Exception(f"无法解析API响应: {str(e)}")
        except Exception as e:
            logger.error(f"调用API时发生未知错误: {str(e)}")
            raise Exception(f"API调用错误: {str(e)}")

    def _extract_sentiment_data(self, report):
        try:
            sentiment_data = {"positive": 0, "negative": 0, "neutral": 0}

            m = re.search(r'正面[：:]\s*(\d+)%', report) or re.search(r'(\d+)%.*正面', report)
            if m: sentiment_data["positive"] = int(m.group(1))
            m = re.search(r'负面[：:]\s*(\d+)%', report) or re.search(r'(\d+)%.*负面', report)
            if m: sentiment_data["negative"] = int(m.group(1))
            m = re.search(r'中性[：:]\s*(\d+)%', report) or re.search(r'(\d+)%.*中性', report)
            if m: sentiment_data["neutral"] = int(m.group(1))

            total = sum(sentiment_data.values())
            if total < 80 or total > 120:
                logger.warning(f"情感分析总和异常({total}%)，使用默认值")
                sentiment_data = {"positive": 60, "negative": 20, "neutral": 20}

            return sentiment_data
        except Exception as e:
            logger.error(f"提取情感数据时出错: {str(e)}")
            return {"positive": 60, "negative": 20, "neutral": 20}

    def _extract_topics_data(self, report):
        try:
            topics_data = {}

            # 尝试从系统数据区获取词频数据
            system_data = re.search(
                r'<!--\s*系统数据区开始\s*-->([\s\S]*?)<!--\s*系统数据区结束\s*-->',
                report
            )

            if system_data:
                logger.info("找到系统数据区")
                system_text = system_data.group(1)
                # 提取关键词和频率
                pairs = re.findall(r'-\s*([^：:]+)[：:]\s*(\d+)[次|个]?', system_text)

                if pairs:
                    logger.info(f"从系统数据区提取到 {len(pairs)} 对关键词-频率")
                    for keyword, freq in pairs:
                        try:
                            clean_keyword = keyword.strip()
                            topics_data[clean_keyword] = int(freq)
                        except ValueError:
                            topics_data[clean_keyword] = 15  # 默认值
                else:
                    logger.warning("系统数据区未找到关键词-频率对")

            # 提取如"季冠霖22次/声线18次/资方15次"格式的数据
            if not topics_data:
                slash_separated = re.findall(r'([^/\d]+)(\d+)次', report)
                if slash_separated:
                    for keyword, freq in slash_separated:
                        keyword = keyword.strip()
                        if len(keyword) > 1:  # 避免单字符
                            try:
                                topics_data[keyword] = int(freq)
                            except ValueError:
                                pass

            # 提取如"关键词1：XX次"格式的数据
            if not topics_data:
                colon_separated = re.findall(r'-\s*([^：:]+)[：:]\s*(\d+)[次|个]?', report)
                for keyword, freq in colon_separated:
                    keyword = keyword.strip()
                    if len(keyword) > 1:
                        try:
                            topics_data[keyword] = int(freq)
                        except ValueError:
                            pass

            # 提取如"词(数字次)"格式的数据
            if not topics_data:
                parenthesis_format = re.findall(r'([^(（]+)[\(（](\d+)次[\)）]', report)
                for keyword, freq in parenthesis_format:
                    keyword = keyword.strip()
                    if len(keyword) > 1:
                        try:
                            topics_data[keyword] = int(freq)
                        except ValueError:
                            pass

            # 直接查找关键词列表部分
            if not topics_data:
                keyword_lists = re.findall(
                    r'关键词列表\(请严格按照以下格式，确保包含词频数字\)：\s*((?:-\s*[^:：]+[：:]\s*\d+[次]?\s*)+)',
                    report
                )

                for keyword_list in keyword_lists:
                    # 从列表中提取关键词和频率
                    pairs = re.findall(r'-\s*([^:：]+)[：:]\s*(\d+)[次]?', keyword_list)
                    for keyword, frequency in pairs:
                        keyword = keyword.strip()
                        try:
                            frequency = int(frequency)
                            # 累加同一关键词在不同主题中的频率
                            if keyword in topics_data:
                                topics_data[keyword] += frequency
                            else:
                                topics_data[keyword] = frequency
                        except ValueError:
                            logger.warning(f"无法解析关键词频率: {keyword}: {frequency}")

            # 如果无法找到结构化的关键词列表，尝试使用备选方法
            if not topics_data:
                # 在整个文本中查找可能的关键词频率对
                pairs = re.findall(r'(?:^|\n|\s)([^\n:：]+)[：:]\s*(\d+)[次]?(?:\s|$)', report)
                for keyword, frequency in pairs:
                    keyword = keyword.strip()
                    # 排除一些可能的误匹配
                    if len(keyword) > 1 and not re.search(r'情感|比例|占比|总体|百分|指数', keyword):
                        try:
                            frequency = int(frequency)
                            topics_data[keyword] = frequency
                        except ValueError:
                            pass

            # 如果数据太少，再尝试一种备选方法
            if len(topics_data) < 5:
                # 尝试找到主题分布部分
                section = re.search(r'一、主题分布图鉴([\s\S]*?)二、', report)
                if section:
                    text = section.group(1)
                    # 提取关键词部分
                    keywords_sections = re.findall(r'关键词：([^\n]+)', text)
                    for keywords_text in keywords_sections:
                        # 拆分关键词
                        keywords = re.split(r'[,，、+\s]+', keywords_text)
                        for i, kw in enumerate(keywords):
                            if kw and len(kw) > 1:
                                # 根据位置分配权重，前面的关键词权重高
                                topics_data[kw.strip()] = max(30 - i * 3, 10)

            # 确保有足够的数据，限制最多显示15个主题
            if len(topics_data) > 15:
                sorted_topics = sorted(topics_data.items(), key=lambda x: x[1], reverse=True)
                topics_data = dict(sorted_topics[:15])
            elif len(topics_data) < 3:
                logger.warning("提取到的主题词太少，使用默认值")
                topics_data = {"热门话题": 25, "用户讨论": 20, "核心观点": 15, "其他讨论": 10}

            logger.info(f"最终提取到的主题数据: {json.dumps(topics_data, ensure_ascii=False)}")
            return topics_data

        except Exception as e:
            logger.error(f"提取主题数据时出错: {str(e)}")
            return {"数据提取错误": 20, "未分类主题": 10}
