import os
import sys
import logging
from flask import Flask, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS


# 确保backend包可被导入
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入配置
from settings.config import Config

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 初始化Flask应用
app = Flask(__name__)
app.config['SECRET_KEY'] = Config.SECRET_KEY
app.config['DEBUG'] = Config.DEBUG

# 允许跨域请求
CORS(app)

# 设置请求限制
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)
limiter.init_app(app)

# 全局错误处理
@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({
        'success': False,
        'data': None,
        'error': f"请求过于频繁，请稍后再试。{str(e)}"
    }), 429

@app.errorhandler(500)
def internal_error(e):
    logger.error(f"服务器内部错误: {str(e)}")
    return jsonify({
        'success': False,
        'data': None,
        'error': "服务器内部错误，请稍后再试"
    }), 500

@app.errorhandler(404)
def not_found(e):
    return jsonify({
        'success': False,
        'data': None,
        'error': "请求的资源不存在"
    }), 404

# 检查必要的环境变量
required_vars = ['DEEPSEEK_API_KEY']
missing_vars = [var for var in required_vars if not getattr(Config, var, None)]
if missing_vars:
    logger.error(f"缺少必要的环境变量: {', '.join(missing_vars)}")
    print(f"Error: Missing required environment variables: {', '.join(missing_vars)}")
    sys.exit(1)

# 检查数据目录并创建
if not os.path.exists(Config.DATA_DIR):
    try:
        os.makedirs(Config.DATA_DIR, exist_ok=True)
        logger.info(f"创建数据目录: {Config.DATA_DIR}")
    except Exception as e:
        logger.error(f"创建数据目录失败: {str(e)}")
        sys.exit(1)

# 注册蓝图
from app.routes.api import api_bp
app.register_blueprint(api_bp, url_prefix='/api')

# 健康检查接口
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'success': True,
        'data': {
            'status': 'ok',
            'version': '1.0'
        },
        'error': None
    })

if __name__ == '__main__':
    logger.info("应用启动中...")
    app.run(host='0.0.0.0', port=5000, debug=Config.DEBUG)
