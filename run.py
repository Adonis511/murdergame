#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
聊天应用启动脚本（支持AI功能）
"""

import sys
import os

def check_dependencies():
    """检查依赖包"""
    required_packages = [
        'flask',
        'flask_login', 
        'flask_sqlalchemy',
        'openai',
        'python-dotenv'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ 缺少以下依赖包:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n请运行以下命令安装:")
        print("python install.py")
        print("或者:")
        print("pip install -r requirements.txt")
        return False
    
    return True

def test_ai_connection():
    """测试AI服务连接"""
    try:
        from ai_service import ai_service
        result = ai_service.test_connection()
        
        if result['status'] == 'success':
            print(f"✅ AI服务连接正常 (模型: {result['model']})")
        else:
            print(f"⚠️  AI服务连接异常: {result['message']}")
            print("   应用仍可正常使用，但AI功能可能受限")
        
        return True
        
    except Exception as e:
        print(f"⚠️  AI服务测试失败: {e}")
        print("   应用仍可正常使用，但AI功能可能受限")
        return False

def main():
    """主函数"""
    print("🎯 AI聊天应用启动器")
    print("=" * 35)
    
    # 检查Python版本
    if sys.version_info < (3, 7):
        print("❌ 错误: 需要Python 3.7或更高版本")
        print(f"当前版本: {sys.version}")
        sys.exit(1)
    print(f"✅ Python版本检查通过: {sys.version.split()[0]}")
    
    # 检查必要文件
    required_files = ['app.py', 'models.py', 'config.py', 'ai_service.py']
    for file_path in required_files:
        if not os.path.exists(file_path):
            print(f"❌ 缺少文件: {file_path}")
            sys.exit(1)
    print("✅ 文件检查完成")
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    print("✅ 依赖检查完成")
    
    # 测试AI服务
    test_ai_connection()
    
    # 启动应用
    try:
        print("\n🚀 启动AI聊天应用...")
        print("=" * 50)
        print("📱 聊天界面: http://localhost:5000/chat")
        print("🔑 登录页面: http://localhost:5000/login")
        print("📝 注册页面: http://localhost:5000/register")
        print("🔧 API状态: http://localhost:5000/api/status")
        print("🤖 AI测试: http://localhost:5000/api/ai/test")
        print("📋 应用首页: http://localhost:5000/")
        print("=" * 50)
        print("🔐 默认账户:")
        print("   管理员 - 用户名: admin, 密码: admin123")
        print("   测试用户 - 用户名: test, 密码: test123")
        print("=" * 50)
        print("🤖 AI功能:")
        print("   模型: GPT-3.5-turbo")
        print("   支持上下文对话")
        print("   支持Markdown格式输出")
        print("=" * 50)
        print("按 Ctrl+C 停止服务器\n")
        
        from app import app
        app.run(host='0.0.0.0', port=5000, debug=True)
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("请运行: python install.py")
    except Exception as e:
        print(f"❌ 启动失败: {e}")

if __name__ == "__main__":
    main()