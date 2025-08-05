#!/usr/bin/env python3
"""
测试修复后的Game类
测试加载现有游戏目录和创建新游戏的功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game import Game

def test_create_new_game():
    """测试创建新游戏"""
    print("=" * 50)
    print("测试1: 创建新游戏")
    print("=" * 50)
    
    try:
        # 创建新游戏（不生成图片，节省时间）
        game = Game(script_path=None, generate_images=False)
        
        print(f"\n✅ 新游戏创建成功!")
        print(f"📂 游戏目录: {game.get_game_directory()}")
        
        # 检查文件结构
        script_file = os.path.join(game.game_dir, "script.json")
        info_file = os.path.join(game.game_dir, "game_info.json")
        imgs_dir = os.path.join(game.game_dir, "imgs")
        
        print(f"\n📋 文件结构检查:")
        print(f"   script.json: {'✅' if os.path.exists(script_file) else '❌'}")
        print(f"   game_info.json: {'✅' if os.path.exists(info_file) else '❌'}")
        print(f"   imgs/ 目录: {'✅' if os.path.exists(imgs_dir) else '❌'}")
        
        return game.game_dir
        
    except Exception as e:
        print(f"❌ 创建新游戏失败: {e}")
        return None

def test_load_existing_game(game_dir):
    """测试加载现有游戏"""
    print("\n" + "=" * 50)
    print("测试2: 加载现有游戏")
    print("=" * 50)
    
    if not game_dir:
        print("❌ 没有可用的游戏目录")
        return
    
    try:
        # 加载现有游戏
        game = Game(script_path=game_dir, generate_images=False)
        
        print(f"\n✅ 现有游戏加载成功!")
        print(f"📂 游戏目录: {game.get_game_directory()}")
        print(f"🎭 剧本标题: {game.script.get('title', '未命名剧本')}")
        print(f"👥 角色数量: {len(game.script.get('characters', []))}")
        
        # 检查图片加载情况
        char_images = game.get_all_character_images()
        clue_images = game.get_all_clue_images()
        
        print(f"\n🖼️ 图片加载情况:")
        print(f"   角色图片: {len([img for img in char_images.values() if img and img.get('success')])} 个")
        total_clues = sum(len(chapter_clues) for chapter_clues in clue_images.values())
        loaded_clues = sum(sum(1 for clue in chapter_clues if clue['image_result'] and clue['image_result'].get('success')) 
                          for chapter_clues in clue_images.values())
        print(f"   线索图片: {loaded_clues}/{total_clues} 个")
        
    except Exception as e:
        print(f"❌ 加载现有游戏失败: {e}")

def test_invalid_path():
    """测试无效路径"""
    print("\n" + "=" * 50)
    print("测试3: 无效路径处理")
    print("=" * 50)
    
    try:
        # 尝试加载不存在的目录
        game = Game(script_path="nonexistent_directory")
        print("❌ 应该报错但没有报错")
    except ValueError as e:
        print(f"✅ 正确捕获错误: {e}")
    except Exception as e:
        print(f"⚠️ 意外错误类型: {e}")

def main():
    """主测试函数"""
    print("🧪 开始测试修复后的Game类...")
    
    # 测试1: 创建新游戏
    new_game_dir = test_create_new_game()
    
    # 测试2: 加载现有游戏
    if new_game_dir:
        test_load_existing_game(new_game_dir)
    
    # 测试3: 无效路径处理
    test_invalid_path()
    
    print("\n" + "=" * 50)
    print("🎯 测试完成!")
    
    if new_game_dir:
        print(f"\n💡 提示: 你可以使用以下路径测试加载现有游戏:")
        print(f"   game = Game(script_path='{new_game_dir}')")
    
    print("=" * 50)

if __name__ == "__main__":
    main()