#!/usr/bin/env python3
"""
生产模式启动服务器
"""
import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入app
from app import app

if __name__ == '__main__':
    print("=" * 50)
    print("🎮 扭曲画猜 - 生产模式")
    print("=" * 50)
    print("访问: http://localhost:5000")
    print("=" * 50)
    # 禁用调试，这样不会重新加载
    app.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False)
