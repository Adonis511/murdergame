#!/usr/bin/env python3
"""
测试OpenAI客户端初始化修复
"""

import sys
import os

# 导入测试工具
from test_utils import setup_project_path

# 设置项目路径
setup_project_path()

def test_dm_agent_init():
    """测试DMAgent初始化"""
    print("🧪 测试DMAgent初始化...")
    
    try:
        from dm_agent import DMAgent
        dm_agent = DMAgent()
        print("✅ DMAgent初始化成功")
        return True
    except TypeError as e:
        if 'proxies' in str(e):
            print(f"❌ DMAgent初始化失败，仍有proxies参数问题: {e}")
        else:
            print(f"❌ DMAgent初始化失败: {e}")
        return False
    except Exception as e:
        print(f"⚠️ DMAgent初始化出现其他错误: {e}")
        return False

def test_player_agent_init():
    """测试PlayerAgent初始化"""
    print("\n🧪 测试PlayerAgent初始化...")
    
    try:
        from player_agent import PlayerAgent
        player_agent = PlayerAgent("测试角色")
        print("✅ PlayerAgent初始化成功")
        return True
    except TypeError as e:
        if 'proxies' in str(e):
            print(f"❌ PlayerAgent初始化失败，仍有proxies参数问题: {e}")
        else:
            print(f"❌ PlayerAgent初始化失败: {e}")
        return False
    except Exception as e:
        print(f"⚠️ PlayerAgent初始化出现其他错误: {e}")
        return False

def test_ai_service_init():
    """测试AIService初始化"""
    print("\n🧪 测试AIService初始化...")
    
    try:
        from ai_service import AIService
        ai_service = AIService()
        print("✅ AIService初始化成功")
        return True
    except TypeError as e:
        if 'proxies' in str(e):
            print(f"❌ AIService初始化失败，仍有proxies参数问题: {e}")
        else:
            print(f"❌ AIService初始化失败: {e}")
        return False
    except Exception as e:
        print(f"⚠️ AIService初始化出现其他错误: {e}")
        return False

def test_game_init():
    """测试Game类初始化（包含DMAgent）"""
    print("\n🧪 测试Game类初始化...")
    
    try:
        from game import Game
        # 创建游戏实例，不生成图片避免长时间等待
        game = Game(script_path=None, generate_images=False)
        print("✅ Game类初始化成功")
        
        # 测试一些基本方法
        total_chapters = game.get_total_chapters()
        print(f"✅ 总章节数: {total_chapters}")
        
        return True
    except TypeError as e:
        if 'proxies' in str(e):
            print(f"❌ Game类初始化失败，仍有proxies参数问题: {e}")
        else:
            print(f"❌ Game类初始化失败: {e}")
        return False
    except Exception as e:
        print(f"⚠️ Game类初始化出现其他错误: {e}")
        return False

def main():
    """主测试函数"""
    print("🔧 测试OpenAI客户端proxies参数修复...")
    print("=" * 60)
    
    success_count = 0
    total_tests = 4
    
    # 测试各个组件的初始化
    if test_dm_agent_init():
        success_count += 1
    
    if test_player_agent_init():
        success_count += 1
        
    if test_ai_service_init():
        success_count += 1
        
    if test_game_init():
        success_count += 1
    
    print("\n" + "=" * 60)
    print(f"📊 测试结果: {success_count}/{total_tests} 个组件初始化成功")
    
    if success_count == total_tests:
        print("🎉 所有OpenAI客户端初始化修复成功！")
        print("✅ proxies参数问题已解决")
        print("✅ 所有组件都可以正常初始化")
    elif success_count > 0:
        print("⚠️ 部分组件初始化成功，仍有问题需要解决")
    else:
        print("❌ 所有组件初始化都失败，需要进一步检查")
    
    print("=" * 60)
    
    return success_count == total_tests

if __name__ == "__main__":
    main()