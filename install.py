#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
聊天应用安装脚本 - 自动安装依赖和配置环境
"""

import subprocess
import sys
import os

def install_requirements():
    """安装Python依赖包"""
    print("🔧 开始安装Python依赖包...")
    
    try:
        # 升级pip
        print("📦 升级pip...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        
        # 安装依赖
        print("📦 安装项目依赖...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        
        print("✅ 依赖安装完成!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖安装失败: {e}")
        return False
    except FileNotFoundError:
        print("❌ 找不到requirements.txt文件")
        return False

def create_env_file():
    """创建环境配置文件"""
    env_content = """# OpenAI API配置
OPENAI_API_KEY=sk-fb535aeda39f42d0b8f7039b98699374

# Flask配置
SECRET_KEY=your-secret-key-here-change-in-production
FLASK_DEBUG=True

# 数据库配置
DATABASE_URL=sqlite:///chat_app.db

# AI聊天配置
AI_MODEL=gpt-3.5-turbo
AI_MAX_TOKENS=1000
AI_TEMPERATURE=0.7

# 系统配置
CHAT_HISTORY_LIMIT=50
MAX_MESSAGE_LENGTH=2000
"""
    
    try:
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        print("✅ .env配置文件创建完成")
        return True
    except Exception as e:
        print(f"❌ 创建.env文件失败: {e}")
        return False

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 7):
        print(f"❌ Python版本过低: {sys.version}")
        print("需要Python 3.7或更高版本")
        return False
    
    print(f"✅ Python版本检查通过: {sys.version.split()[0]}")
    return True

def check_files():
    """检查必要文件"""
    required_files = [
        'app.py',
        'models.py', 
        'config.py',
        'ai_service.py',
        'requirements.txt'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ 缺少以下必要文件:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        return False
    
    print("✅ 文件检查完成")
    return True

def test_installation():
    """测试安装是否成功"""
    print("🧪 测试安装...")
    
    try:
        # 测试关键模块导入
        import flask
        import flask_login
        import flask_sqlalchemy
        import openai
        
        print("✅ 关键模块导入成功")
        
        # 测试配置加载
        from config import Config
        print("✅ 配置文件加载成功")
        
        # 测试AI服务
        from ai_service import ai_service
        print("✅ AI服务模块加载成功")
        
        return True
        
    except ImportError as e:
        print(f"❌ 模块导入失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def main():
    """主安装流程"""
    print("🎯 聊天应用安装向导")
    print("=" * 40)
    
    # 检查Python版本
    if not check_python_version():
        sys.exit(1)
    
    # 检查文件
    if not check_files():
        sys.exit(1)
    
    # 创建环境配置文件
    if not os.path.exists('.env'):
        print("📝 创建环境配置文件...")
        create_env_file()
    else:
        print("✅ .env文件已存在")
    
    # 安装依赖
    if not install_requirements():
        print("\n❌ 安装失败，请手动运行以下命令:")
        print("pip install -r requirements.txt")
        sys.exit(1)
    
    # 测试安装
    if not test_installation():
        print("\n❌ 安装测试失败，可能需要手动检查")
        sys.exit(1)
    
    print("\n🎉 安装完成!")
    print("=" * 40)
    print("现在可以运行以下命令启动应用:")
    print("python app.py")
    print("")
    print("或使用启动脚本:")
    print("python run.py")
    print("")
    print("访问地址:")
    print("http://localhost:5000")
    print("")
    print("默认账户:")
    print("管理员 - admin / admin123")
    print("测试用户 - test / test123")

if __name__ == "__main__":
    main()