#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试脚本：验证新环境安装是否成功
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """测试所有必要的包是否能正常导入"""
    print("🔍 测试包导入...")
    
    try:
        # Flask 相关
        import flask
        print(f"✅ Flask {flask.__version__}")
        
        import flask_sqlalchemy
        print(f"✅ Flask-SQLAlchemy {flask_sqlalchemy.__version__}")
        
        import flask_login
        print(f"✅ Flask-Login {flask_login.__version__}")
        
        import flask_wtf
        print(f"✅ Flask-WTF {flask_wtf.__version__}")
        
        # 表单验证
        import wtforms
        print(f"✅ WTForms {wtforms.__version__}")
        
        import email_validator
        print(f"✅ email-validator {email_validator.__version__}")
        
        # AI 相关
        import openai
        print(f"✅ OpenAI {openai.__version__}")
        
        import requests
        print(f"✅ Requests {requests.__version__}")
        
        # 配置管理
        import dotenv
        print(f"✅ python-dotenv {dotenv.__version__}")
        
        print("\n🎉 所有必要包导入成功！")
        return True
        
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return False

def test_app_structure():
    """测试应用结构是否完整"""
    print("\n🔍 测试应用结构...")
    
    # 切换到父目录进行文件检查
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    required_files = [
        'app.py',
        'config.py', 
        'models.py',
        'ai_service.py',
        'dm_agent.py',
        'player_agent.py',
        'game.py',
        'game_api.py',
        'openai_utils.py',
        'agent_logger.py',
        'requirements.txt',
        'README.md'
    ]
    
    missing_files = []
    for file in required_files:
        file_path = os.path.join(parent_dir, file)
        if os.path.exists(file_path):
            print(f"✅ {file}")
        else:
            print(f"❌ {file}")
            missing_files.append(file)
    
    if missing_files:
        print(f"\n⚠️ 缺少文件: {missing_files}")
        return False
    else:
        print("\n🎉 应用结构完整！")
        return True

def test_app_initialization():
    """测试应用是否能正常初始化"""
    print("\n🔍 测试应用初始化...")
    
    try:
        from app import app
        from models import db, init_db
        
        # 测试应用配置
        print(f"✅ Flask应用创建成功")
        print(f"✅ 调试模式: {app.debug}")
        
        # 测试数据库初始化
        with app.app_context():
            db.create_all()
            print(f"✅ 数据库初始化成功")
        
        print("\n🎉 应用初始化成功！")
        return True
        
    except Exception as e:
        print(f"❌ 应用初始化失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始测试新环境安装...")
    print("=" * 50)
    
    tests = [
        ("包导入测试", test_imports),
        ("应用结构测试", test_app_structure),
        ("应用初始化测试", test_app_initialization)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        result = test_func()
        results.append(result)
    
    print("\n" + "=" * 50)
    print("📊 测试结果汇总:")
    
    success_count = sum(results)
    total_count = len(results)
    
    for i, (test_name, _) in enumerate(tests):
        status = "✅" if results[i] else "❌"
        print(f"   {status} {test_name}")
    
    if success_count == total_count:
        print(f"\n🎉 所有测试通过！({success_count}/{total_count})")
        print("✨ 环境配置完成，可以运行应用了！")
        print("\n📝 下一步:")
        print("   1. 运行: python app.py")
        print("   2. 访问: http://localhost:5000")
        print("   3. 注册账户并配置API密钥")
    else:
        print(f"\n⚠️ 部分测试失败 ({success_count}/{total_count})")
        print("请检查上述错误信息并修复问题")

if __name__ == '__main__':
    main()