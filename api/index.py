"""
Vercel Serverless 入口文件
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入Flask应用
from app import app

# Vercel需要的handler
def handler(request):
    """Vercel serverless handler"""
    return app(request.environ, lambda *args: None)

# 导出app供Vercel使用
app = app
