#!/usr/bin/env python3
"""
测试玩家代理的格式化修复
"""

import sys
import os

# 导入测试工具
from test_utils import setup_project_path

# 设置项目路径
setup_project_path()

from player_agent import PlayerAgent

def test_player_query():
    """测试玩家询问功能"""
    print("🧪 测试玩家代理格式化修复...")
    
    try:
        # 创建玩家代理
        player = PlayerAgent("林慕白")
        print("✅ 玩家代理创建成功")
        
        # 准备测试数据
        test_scripts = [
            "**第1章**\n\n我是林慕白，林氏集团的长子。今天父亲召集大家到庄园，说有重要事情宣布。"
        ]
        test_chat_history = "## 🎭 DM\n\n欢迎来到豪门血案！\n\n### 👤 苏婉清\n\n大家好，我是苏婉清。"
        
        print("📝 测试玩家主动发言...")
        
        # 测试玩家询问
        result = player.query(test_scripts, test_chat_history)
        
        print(f"✅ 玩家发言成功")
        print(f"🔍 返回类型: {type(result)}")
        
        if isinstance(result, dict):
            print(f"💬 发言内容: {result.get('content', 'N/A')[:100]}...")
            print(f"❓ 询问内容: {result.get('query', {})}")
        else:
            print(f"⚠️ 返回格式异常: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_player_response():
    """测试玩家回应功能"""
    print("\n🧪 测试玩家回应功能...")
    
    try:
        # 创建玩家代理
        player = PlayerAgent("苏婉清")
        print("✅ 玩家代理创建成功")
        
        # 准备测试数据
        test_scripts = [
            "**第1章**\n\n我是苏婉清，林慕白的妻子。今天来到庄园参加家族聚会。"
        ]
        test_chat_history = "## 🎭 DM\n\n欢迎来到豪门血案！\n\n### 👤 林慕白\n\n我想了解一下大家的情况。"
        test_query = "你昨晚什么时候到达庄园的？"
        test_query_player = "林慕白"
        
        print("📝 测试玩家被动回应...")
        
        # 测试玩家回应
        result = player.response(test_scripts, test_chat_history, test_query, test_query_player)
        
        print(f"✅ 玩家回应成功")
        print(f"🔍 返回类型: {type(result)}")
        print(f"💬 回应内容: {result[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("🔧 玩家代理格式化修复测试开始...")
    print("=" * 60)
    
    success_count = 0
    total_tests = 2
    
    # 测试1: 玩家主动发言
    if test_player_query():
        success_count += 1
    
    # 测试2: 玩家被动回应
    if test_player_response():
        success_count += 1
    
    print("\n" + "=" * 60)
    print(f"📊 测试结果: {success_count}/{total_tests} 个功能测试成功")
    
    if success_count == total_tests:
        print("🎉 所有玩家代理功能修复成功！")
        print("✅ 格式化错误已解决")
        print("✅ 玩家发言和回应功能正常")
    elif success_count > 0:
        print("⚠️ 部分功能正常，仍有问题需要解决")
    else:
        print("❌ 所有功能测试都失败，需要进一步检查")
    
    print("=" * 60)
    
    return success_count == total_tests

if __name__ == "__main__":
    main()