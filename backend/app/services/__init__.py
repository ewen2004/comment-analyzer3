from settings.config import Config  # 使用相对导入

class CommentAnalyzer:
    def __init__(self):
        self.api_key = Config.DEEPSEEK_API_KEY
        self.base_url = Config.DEEPSEEK_API_URL  # 添加基础URL定义
        self.api_url = f"{self.base_url}"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
