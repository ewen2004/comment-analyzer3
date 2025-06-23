import os
import time
import math
import threading
import hashlib
import concurrent.futures
import requests
import pandas as pd
import urllib.parse as urlparse
import re
import json
import random

from settings.config import (
    COOKIE,
    HEADERS,
    MAX_WORKERS,
    BASE_DELAY,
    MIN_COMMENTS,
    SECONDARY_BATCH_SIZE,
    MAX_VIDEOS_PER_KEYWORD,
    MAX_COMMENTS_PER_VIDEO,
    MAX_TOTAL_COMMENTS,
)
from settings.config import Config

# 在文件顶部添加导入
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from concurrent.futures import ThreadPoolExecutor
import httplib2

import logging

# 设置日志记录器
logger = logging.getLogger(__name__)


# 添加YouTubeClient类
class YouTubeClient:
    def __init__(self, api_key, proxy_host=None, proxy_port=None):
        try:
            proxy_info = None
            if proxy_host and proxy_port:
                proxy_info = httplib2.ProxyInfo(
                    proxy_type=httplib2.socks.PROXY_TYPE_SOCKS5,  # 改为SOCKS5代理
                    proxy_host=proxy_host,
                    proxy_port=int(proxy_port)
                )
            # 增加超时和重试设置
            http = httplib2.Http(
                proxy_info=proxy_info,
                timeout=300,  # 30秒超时
                disable_ssl_certificate_validation=True  # 解决部分SSL问题
            )
            
            self.youtube = build(
                'youtube', 'v3',
                developerKey=api_key,
                http=http,
                cache_discovery=False,  # 避免警告
                static_discovery=False
            )
        except Exception as e:
            logger.error(f"初始化YouTube客户端失败: {str(e)}")
            raise

    def search_videos(self, query, max_results=3):
        try:
            request = self.youtube.search().list(
                part="snippet",
                q=query,
                type="video",
                maxResults=max_results,
                regionCode="US"  # 获取国际版结果
            )
            response = request.execute()
            
            video_ids = []
            for item in response['items']:
                if 'videoId' in item['id']:
                    video_ids.append({
                        'videoId': item['id']['videoId'],
                        'title': item['snippet']['title']
                    })
            return video_ids
        except Exception as e:
            logger.error(f"搜索YouTube视频失败: {str(e)}")
            return []

    def get_comments(self, video_id, max_comments=100):
        comments = []
        next_page_token = None
    
        while len(comments) < max_comments:
            try:
                response = self.youtube.commentThreads().list(
                    part="snippet",
                    videoId=video_id,
                    maxResults=min(100, max_comments - len(comments)),  # 每次最多100条
                    pageToken=next_page_token,
                    textFormat="plainText",
                    order="relevance"  # 按相关性排序
                ).execute()
            
                for item in response['items']:
                    top_comment = item['snippet']['topLevelComment']['snippet']
                    comments.append({
                        "content": top_comment['textDisplay'],
                        "username": top_comment['authorDisplayName'],
                        "like_count": top_comment['likeCount'],
                        "publish_time": top_comment['publishedAt'],
                        "is_secondary": False,
                        "platform": "youtube"  # 添加平台标识
                    })
                
                    # 获取部分回复（如果有）
                    if item['snippet']['totalReplyCount'] > 0 and len(comments) < max_comments:
                        replies = self.youtube.comments().list(
                            part="snippet",
                            parentId=item['id'],
                            maxResults=2  # 每条评论最多获取2条回复
                        ).execute()
                    
                        for reply in replies['items']:
                            comments.append({
                                "content": reply['snippet']['textDisplay'],
                                "username": reply['snippet']['authorDisplayName'],
                                "like_count": reply['snippet']['likeCount'],
                                "publish_time": reply['snippet']['publishedAt'],
                                "is_secondary": True,
                                "platform": "youtube"
                            })
                        
                next_page_token = response.get('nextPageToken')
                if not next_page_token:
                    break
                
                # 避免请求过于频繁
                time.sleep(1)
                
            except HttpError as e:
                if e.resp.status == 403:
                    logger.error("API配额已用完或评论已禁用")
                break
            except Exception as e:
                logger.error(f"获取评论时出错: {str(e)}")
                break
            
        return comments[:max_comments]

# 修改crawl_comments_by_keyword函数，添加platform参数
def crawl_comments_by_keyword(keyword: str, platform: str = "bilibili") -> pd.DataFrame:
    """主函数：按关键词搜索并爬取评论"""
    if platform.lower() == "youtube":
        logger.info(f"开始爬取YouTube视频评论，关键词: {keyword}")
        try:
            yt_client = YouTubeClient(
                Config.YOUTUBE_API_KEY,
                Config.YOUTUBE_PROXY_HOST,
                Config.YOUTUBE_PROXY_PORT
            )
            
            # 搜索视频
            videos = yt_client.search_videos(keyword)
            if not videos:
                logger.warning("没有找到相关YouTube视频")
                return pd.DataFrame()
            
            # 获取评论
            all_comments = []
            for video in videos[:3]:  # 最多3个视频
                logger.info(f"正在处理视频: {video['title']}")
                comments = yt_client.get_comments(video['videoId'], 100)
                all_comments.extend(comments)
                
                if len(all_comments) >= 200:  # 最多200条评论
                    break
                    
                # 视频间延迟
                time.sleep(2)
            
            df = pd.DataFrame(all_comments)
            
            # 统一数据格式并确保日期可序列化
            if not df.empty:
                df['publish_time'] = df['publish_time'].astype(str)  # 将Timestamp转换为字符串
                df = df.rename(columns={
                    'username': 'author',
                    'like_count': 'like'
                })
            
            logger.info(f"成功获取{len(df)}条YouTube评论")
            return df
            
        except Exception as e:
            logger.error(f"YouTube爬取失败: {str(e)}")
            return pd.DataFrame()
    else:
        # 原有的B站爬取逻辑
        logger.info(f"开始搜索B站关键词: {keyword}")
        vids = search_videos_by_keyword(keyword)
        logger.info(f"找到 {len(vids)} 个相关视频")
        sel = select_videos_by_ratio(vids)
        if not sel:
            logger.warning("没有找到符合条件的B站视频")
            return pd.DataFrame()
            
        counter = CommentCounter()
        all_comments = []
        
        for bvid, title in sel:
            try:
                wait_time = BASE_DELAY * 5 + random.random() * 10
                logger.info(f"等待 {wait_time:.2f} 秒后开始爬取视频《{title}》")
                time.sleep(wait_time)

                video_counter = CommentCounter()
                cmts = get_all_comments_optimized(bvid, title, video_counter)
                logger.info(f"视频《{title}》完成，成功获取 {len(cmts)} 条评论")

                all_comments.extend(cmts)
                counter.increment(len(cmts))

                if counter.get() >= MAX_TOTAL_COMMENTS:
                    logger.info("已达最大评论总数，停止爬取")
                    break

            except Exception as e:
                logger.error(f"视频《{title}》爬取异常：{e}")

        return pd.DataFrame(all_comments)



class CommentCounter:
    """线程安全的评论计数器"""

    def __init__(self):
        self.count = 0
        self.lock = threading.Lock()

    def increment(self, n=1):
        with self.lock:
            self.count += n
            return self.count

    def get(self):
        with self.lock:
            return self.count


def get_random_ua():
    """获取随机User-Agent"""
    ua_list = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
    ]
    return random.choice(ua_list)


def search_videos_by_keyword(query: str, max_results: int = 30):
    """搜索视频并返回视频信息列表"""
    encoded = urlparse.quote(query)
    url = (
        f"https://api.bilibili.com/x/web-interface/search/type"
        f"?search_type=video&keyword={encoded}&page=1&page_size={max_results}"
    )
    try:
        headers = HEADERS.copy()
        headers['Cookie'] = COOKIE
        headers['User-Agent'] = get_random_ua()
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"搜索视频失败：{e}")
        return []
    if data.get("code") != 0:
        print(f"搜索API返回错误：{data.get('message')}")
        return []

    videos = []
    for item in data["data"]["result"]:
        play = item.get("play", 0)
        review = item.get("review", 0)
        videos.append({
            "bvid": item["bvid"],
            "title": item["title"],
            "play": play,
            "review": review,
            "comment_ratio": review / play if play > 0 else float("inf"),
        })
    return videos


def select_videos_by_ratio(videos):
    """筛选评论数适中的视频，避免过多评论触发反爬"""
    # 筛选评论数在MIN_COMMENTS和3000之间的视频
    candidates = [v for v in videos if MIN_COMMENTS <= v["review"] <= 3000]
    if not candidates:
        # 如果没有满足条件的视频，降低要求
        candidates = sorted(videos, key=lambda v: v["review"])
        # 过滤掉评论数太多的视频
        candidates = [v for v in candidates if v["review"] <= 5000][:5]

    # 按评论数从小到大排序，避免一次获取太多评论
    sorted_vs = sorted(candidates, key=lambda v: v["review"])
    return [(v["bvid"], v["title"]) for v in sorted_vs[:3]]  # 选择前3个


def get_video_aid(bvid: str):
    """BV号转AV号"""
    url = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"
    try:
        headers = HEADERS.copy()
        headers['Cookie'] = COOKIE
        headers['User-Agent'] = get_random_ua()
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"获取AV号失败：{e}")
        return None
    if data.get("code") != 0:
        print(f"获取视频信息失败：{data.get('message')}")
        return None
    return data["data"]["aid"]


def get_comments_page(oid, next_page="0"):
    """使用更简单的API获取评论"""
    url = (
        f"https://api.bilibili.com/x/v2/reply"
        f"?pn=1&type=1&oid={oid}&sort=2&nohot=1&ps=20"
    )

    if next_page and next_page != "0":
        url += f"&next={next_page}"

    headers = HEADERS.copy()
    headers['Cookie'] = COOKIE
    headers['User-Agent'] = get_random_ua()
    headers['Referer'] = f"https://www.bilibili.com/video/av{oid}"

    try:
        # 更长的延迟
        time.sleep(BASE_DELAY * 2 + random.random() * 3)
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"获取评论页失败：{e}")
        return {}


def get_secondary_comments(oid, root_rpid, max_pages=2):
    """获取二级评论，限制页数"""
    all_replies = []

    for page in range(1, max_pages + 1):
        url = (
            f"https://api.bilibili.com/x/v2/reply/reply"
            f"?oid={oid}&type=1&root={root_rpid}&pn={page}&ps=10"
        )

        headers = HEADERS.copy()
        headers['Cookie'] = COOKIE
        headers['User-Agent'] = get_random_ua()

        try:
            time.sleep(BASE_DELAY + random.random() * 2)
            resp = requests.get(url, headers=headers, timeout=10)
            resp.raise_for_status()
            data = resp.json()

            if data.get("code") != 0:
                print(f"获取二级评论失败: {data.get('message')}")
                break

            replies = data.get("data", {}).get("replies", [])
            if not replies:
                break

            all_replies.extend(replies)

            # 如果返回的评论数小于请求的数量，说明已经到最后一页
            if len(replies) < 10:
                break

        except Exception as e:
            print(f"获取二级评论异常: {e}")
            break

    return all_replies


def process_comment(reply, bvid, is_secondary=False):
    """结构化单条评论"""
    return {
        "video_bvid": bvid,
        "comment_id": reply["rpid"],
        "username": reply["member"]["uname"],
        "content": reply["content"]["message"],
        "publish_time": pd.to_datetime(reply["ctime"], unit="s")
        .strftime("%Y-%m-%d %H:%M:%S"),
        "like_count": reply["like"],
        "ip_region": (
            reply.get("reply_control", {}).get("location", "未知")[5:]
            if reply.get("reply_control") else "未知"
        ),
        "is_secondary": is_secondary
    }


def get_all_comments_optimized(bvid, title, counter: CommentCounter):
    """获取单视频评论，逐页获取而非并发"""
    comments = []
    oid = get_video_aid(bvid)
    if not oid:
        return comments

    # 获取首页评论
    next_page = "0"
    max_pages = 5  # 限制最大爬取页数

    for page in range(max_pages):
        if counter.get() >= MAX_COMMENTS_PER_VIDEO:
            print(f"视频《{title}》已达到单视频评论上限")
            break

        # 获取评论页
        data = get_comments_page(oid, next_page)

        if data.get("code") != 0:
            print(f"获取第{page + 1}页评论失败: {data.get('message')}")
            break

        # 处理评论
        if "data" in data and "replies" in data["data"] and data["data"]["replies"]:
            for reply in data["data"]["replies"]:
                if counter.get() >= MAX_COMMENTS_PER_VIDEO:
                    break

                comments.append(process_comment(reply, bvid))
                counter.increment()

                # 随机处理部分评论的二级回复
                if random.random() < 0.3 and reply.get("rcount", 0) > 0:
                    sec_replies = get_secondary_comments(oid, reply["rpid"], max_pages=1)
                    for sec_reply in sec_replies:
                        if counter.get() >= MAX_COMMENTS_PER_VIDEO:
                            break
                        comments.append(process_comment(sec_reply, bvid, True))
                        counter.increment()

            print(f"已获取视频《{title}》第{page + 1}页评论，当前共{len(comments)}条")

            # 获取下一页的cursor
            if "cursor" in data["data"] and "next" in data["data"]["cursor"]:
                next_page = str(data["data"]["cursor"]["next"])
                if next_page == "0":  # 已到最后一页
                    break
            else:
                break  # 没有下一页数据

            # 页间延迟
            wait_time = BASE_DELAY * 3 + random.random() * 5
            print(f"等待 {wait_time:.2f} 秒后获取下一页")
            time.sleep(wait_time)
        else:
            print(f"页面无评论数据")
            break

    return comments


'''def crawl_comments_by_keyword(keyword: str) -> pd.DataFrame:
    """主函数：按关键词搜索并爬取评论"""
    print(f"开始搜索关键词: {keyword}")
    vids = search_videos_by_keyword(keyword)
    print(f"找到 {len(vids)} 个相关视频")

    sel = select_videos_by_ratio(vids)
    if not sel:
        print("没有找到符合条件的视频")
        return pd.DataFrame()

    print(f"选择了 {len(sel)} 个视频进行爬取")
    counter = CommentCounter()
    all_comments = []

    # 一个视频一个视频地爬
    for bvid, title in sel:
        try:
            # 视频间随机等待
            wait_time = BASE_DELAY * 5 + random.random() * 10
            print(f"等待 {wait_time:.2f} 秒后开始爬取视频《{title}》")
            time.sleep(wait_time)

            # 单视频计数器
            video_counter = CommentCounter()
            cmts = get_all_comments_optimized(bvid, title, video_counter)
            print(f"视频《{title}》完成，成功获取 {len(cmts)} 条评论")

            all_comments.extend(cmts)
            counter.increment(len(cmts))

            if counter.get() >= MAX_TOTAL_COMMENTS:
                print("已达最大评论总数，停止爬取")
                break

        except Exception as e:
            print(f"视频《{title}》爬取异常：{e}")

    #df = pd.DataFrame(all_comments)
    print(f"总共爬取 {len(pd.DataFrame(all_comments))} 条评论")
    return pd.DataFrame(all_comments)
'''