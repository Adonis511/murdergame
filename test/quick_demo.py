#!/usr/bin/env python3
"""
快速AI游戏演示脚本
用于快速验证AI系统的基本功能
"""

import sys
import os

# 导入测试工具
from test_utils import setup_project_path

# 设置项目路径
setup_project_path()

from test_ai_game_simulation import AIGameSimulator

def quick_demo():
    """快速演示AI游戏功能"""
    print("🎮 AI剧本杀游戏快速演示")
    print("=" * 50)
    
    # 检查是否有现有游戏
    log_dir = "log"
    existing_games = []
    
    if os.path.exists(log_dir):
        for item in os.listdir(log_dir):
            game_path = os.path.join(log_dir, item)
            if os.path.isdir(game_path):
                existing_games.append(game_path)
    
    if existing_games:
        # 使用最新的游戏
        latest_game = max(existing_games, key=os.path.getmtime)
        print(f"📂 找到现有游戏: {latest_game}")
        
        try:
            simulator = AIGameSimulator(latest_game)
            print(f"✅ 游戏加载成功")
            print(f"🎭 剧本: {simulator.game.script.get('title', '未命名')}")
            print(f"👥 角色: {', '.join(simulator.character_names)}")
            print(f"📖 章节: {simulator.total_chapters}")
            
            # 简单测试：只模拟第一章
            print(f"\n🧪 快速测试第1章...")
            chapter_result = simulator.simulate_chapter_discussion(1)
            
            if chapter_result:
                print(f"\n✅ 演示成功!")
                print(f"🤖 AI代理工作正常")
                print(f"🎭 DM系统运行正常")
                print(f"💬 角色互动正常")
            else:
                print(f"\n⚠️ 演示过程中出现问题")
                
        except Exception as e:
            print(f"❌ 演示失败: {e}")
    else:
        print(f"📂 未找到现有游戏，将生成新游戏进行演示...")
        
        try:
            simulator = AIGameSimulator(None)
            print(f"✅ 新游戏生成成功")
            print(f"🎭 剧本: {simulator.game.script.get('title', '未命名')}")
            print(f"👥 角色: {', '.join(simulator.character_names)}")
            print(f"📖 章节: {simulator.total_chapters}")
            print(f"📂 保存路径: {simulator.game.game_dir}")
            
            # 简单测试：只模拟第一章
            print(f"\n🧪 快速测试第1章...")
            chapter_result = simulator.simulate_chapter_discussion(1)
            
            if chapter_result:
                print(f"\n✅ 演示成功!")
                print(f"🤖 AI代理工作正常")
                print(f"🎭 DM系统运行正常")
                print(f"💬 角色互动正常")
                print(f"💾 游戏已保存到: {simulator.game.game_dir}")
            else:
                print(f"\n⚠️ 演示过程中出现问题")
                
        except Exception as e:
            print(f"❌ 演示失败: {e}")
    
    print("\n" + "=" * 50)
    print("💡 如需完整测试，请运行:")
    print("   python test_ai_game_simulation.py")
    print("=" * 50)

if __name__ == "__main__":
    quick_demo()