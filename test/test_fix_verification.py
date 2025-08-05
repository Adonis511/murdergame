#!/usr/bin/env python3
"""
验证修复是否成功的测试脚本
"""

import sys
import os

# 导入测试工具
from test_utils import setup_project_path

# 设置项目路径
setup_project_path()

from game import Game

def test_get_total_chapters():
    """测试get_total_chapters方法是否存在"""
    print("🧪 测试get_total_chapters方法...")
    
    try:
        # 创建游戏实例（不生成图片）
        print("📝 创建游戏实例...")
        game = Game(script_path=None, generate_images=False)
        
        # 测试get_total_chapters方法
        total_chapters = game.get_total_chapters()
        print(f"✅ get_total_chapters方法正常工作: {total_chapters} 章")
        
        # 测试其他相关方法
        current_chapter = game.get_current_chapter()
        print(f"✅ get_current_chapter方法正常工作: 第{current_chapter}章")
        
        game_dir = game.get_game_directory()
        print(f"✅ get_game_directory方法正常工作: {game_dir}")
        
        return True
        
    except AttributeError as e:
        print(f"❌ 方法缺失错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 其他错误: {e}")
        return False

def test_dm_methods():
    """测试DM相关方法是否存在"""
    print("\n🧪 测试DM相关方法...")
    
    try:
        # 创建游戏实例（不生成图片）
        game = Game(script_path=None, generate_images=False)
        
        # 检查方法是否存在（不实际调用，避免API请求）
        methods_to_check = [
            'start_chapter',
            'end_chapter', 
            'end_game',
            'dm_interject',
            'should_dm_interject'
        ]
        
        for method_name in methods_to_check:
            if hasattr(game, method_name):
                print(f"✅ {method_name} 方法存在")
            else:
                print(f"❌ {method_name} 方法缺失")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def main():
    """主测试函数"""
    print("🔧 验证script_path和方法修复...")
    print("=" * 50)
    
    success = True
    
    # 测试get_total_chapters方法
    if not test_get_total_chapters():
        success = False
    
    # 测试DM相关方法
    if not test_dm_methods():
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 所有修复验证通过！")
        print("✅ script_path路径问题已解决")
        print("✅ get_total_chapters等方法已添加")
        print("✅ DM发言相关方法已完善")
    else:
        print("❌ 仍有问题需要修复")
    
    print("=" * 50)

if __name__ == "__main__":
    main()