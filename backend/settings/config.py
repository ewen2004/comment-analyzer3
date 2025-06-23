import os
from dotenv import load_dotenv
import json

# 加载环境变量
load_dotenv()

# 定义基础路径常量
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, 'backend', 'data')

# 直接在这里设置COOKIE
COOKIE = "SESSDATA=315cc9cb%2C1763344680%2C8c115%2A51CjAsCHI6obdPu8ReuhlWhxAOT4NgeeMdBxZENt3lbdcKyK-72fpA1LmimIF9fRcucLISVjM1QnNsbmV4UEJiNGtJWHZqM3dhcENzUVJKTFhld1B0dE9vbHZYN1FHdU9RZERCWTZxeDhOXzhUeWpfV3dQR2RXdkxzWXRYaW5lQlAxR0lmSnNFNEVBIIEC;bili_jct=6d52c9cab1a78a9dedef304f3fb3d313;DedeUserID=660221512;buvid3=350696D3-2593-ED40-3BC1-52C7F2381F2622055infoc;"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    "Referer": "https://www.bilibili.com/",
    "Cookie": COOKIE,  # 必须加上这一行
}

MAX_WORKERS = 2
BASE_DELAY = 2.0
MIN_COMMENTS = 10
SECONDARY_BATCH_SIZE = 20
MAX_TOTAL_COMMENTS = 2000
MAX_VIDEOS_PER_KEYWORD = 4  # 每个关键词最多爬取2个视频
MAX_COMMENTS_PER_VIDEO = 200  # 每个视频最多爬取1000条评论


class Config:
    """应用配置类"""

    # 基础配置
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev_secret_key')

    # API 配置
    DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', '')
    # 在 Config 类中添加
    #DEEPSEEK_BASE_URL = os.getenv('DEEPSEEK_API_URL', 'https://api.deepseek.com/v1')
    DEEPSEEK_API_URL = os.getenv('DEEPSEEK_API_URL', 'https://api.deepseek.com/v1/chat/completions')
    # YouTube配置
    YOUTUBE_API_KEY = 'AIzaSyBOrvX8-tYtw3TtwWyY5brxLgy0Nnb0S64'  # 直接使用你的API key
    YOUTUBE_PROXY_HOST = '127.0.0.1'  # V2Ray默认本地代理
    YOUTUBE_PROXY_PORT = 10808  # V2Ray默认socks5端口
    # 代理验证设置
    YOUTUBE_TIMEOUT = 30  # 请求超时时间(秒)
    YOUTUBE_MAX_RESULTS = 100  # 最大返回结果数
    # 数据存储路径
    BASE_DIR = BASE_DIR
    DATA_DIR = DATA_DIR

    # Cookie 配置
    BILI_COOKIE = COOKIE
    SUPPORTED_PLATFORMS = ['bilibili', 'youtube']  # 明确支持的平台列表