#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
演示新的文件存储结构
"""

import sys
import os
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game import Game

def demo_directory_structure():
    """演示新的目录结构"""
    print("🎮 新文件存储结构演示")
    print("=" * 60)
    
    print("🔄 变更说明:")
    print("✅ DMAgent不再保存文件，仅返回数据")
    print("✅ Game类统一管理所有文件存储")
    print("✅ 使用带时间戳的游戏目录")
    print("✅ 规范化的文件命名")
    
    print("\n📁 新目录结构:")
    print("```")
    print("log/")
    print("└── YYMMDDhhmmss/              # 游戏会话目录")
    print("    ├── script.json            # 剧本文件")
    print("    ├── game_info.json         # 游戏信息和统计")
    print("    └── imgs/                  # 图片目录")
    print("        ├── 角色名1.png")
    print("        ├── 角色名2.png")
    print("        ├── clue-ch1-1.png     # 第1章第1个线索")
    print("        ├── clue-ch1-2.png     # 第1章第2个线索")
    print("        ├── clue-ch2-1.png     # 第2章第1个线索")
    print("        └── ...")
    print("```")
    
    return True

def demo_quick_game():
    """演示快速创建游戏（不生成图片）"""
    print("\n🚀 快速游戏创建演示（不生成图片）")
    print("=" * 60)
    
    try:
        print("🎭 创建游戏（仅剧本，不生成图片）...")
        game = Game(generate_images=False)
        
        print(f"\n✅ 游戏创建完成!")
        print(f"📖 剧本标题: {game.script.get('title')}")
        print(f"👥 角色: {', '.join(game.script.get('characters', []))}")
        print(f"📂 游戏目录: {game.get_game_directory()}")
        
        # 显示实际创建的文件
        game_dir = game.get_game_directory()
        if os.path.exists(game_dir):
            print(f"\n📋 实际创建的文件:")
            for item in os.listdir(game_dir):
                item_path = os.path.join(game_dir, item)
                if os.path.isfile(item_path):
                    size = os.path.getsize(item_path)
                    print(f"  📄 {item} ({size} bytes)")
                elif os.path.isdir(item_path):
                    sub_files = os.listdir(item_path) if os.path.exists(item_path) else []
                    print(f"  📁 {item}/ ({len(sub_files)} files)")
        
        return True
        
    except Exception as e:
        print(f"❌ 演示失败: {str(e)}")
        return False

def show_file_examples():
    """显示文件内容示例"""
    print("\n📄 文件内容示例")
    print("=" * 60)
    
    print("### script.json 结构:")
    print("```json")
    print("{")
    print('  "title": "豪门谋杀案",')
    print('  "theme": "豪门谋杀案",')
    print('  "characters": ["张明", "李华", "王强", "张雪"],')
    print('  "张明": ["第一章剧本", "第二章剧本", ...],')
    print('  "李华": ["第一章剧本", "第二章剧本", ...],')
    print('  "dm": ["DM指引1", "DM指引2", ...],')
    print('  "character_image_prompts": {')
    print('    "张明": "50岁商人，穿深色西装...",')
    print('    "李华": "45岁伙伴，穿灰色西装..."')
    print('  },')
    print('  "clue_image_prompts": [')
    print('    ["第1章线索1提示词", "第1章线索2提示词"],')
    print('    ["第2章线索1提示词", "第2章线索2提示词"]')
    print('  ]')
    print("}")
    print("```")
    
    print("\n### game_info.json 结构:")
    print("```json")
    print("{")
    print('  "game_directory": "log/250108123456",')
    print('  "script_title": "豪门谋杀案",')
    print('  "characters": ["张明", "李华", "王强", "张雪"],')
    print('  "generation_summary": {')
    print('    "characters": {"total": 4, "success": 4, "success_rate": "100.0%"},')
    print('    "clues": {"total": 6, "success": 6, "success_rate": "100.0%"}')
    print('  },')
    print('  "file_structure": {')
    print('    "script": "script.json",')
    print('    "images_dir": "imgs/",')
    print('    "character_images": ["张明.png", "李华.png", ...],')
    print('    "clue_images": ["clue-ch1-1.png", "clue-ch1-2.png", ...]')
    print('  },')
    print('  "creation_time": "2025-01-08 12:34:56"')
    print("}")
    print("```")

def show_migration_benefits():
    """显示迁移到新结构的好处"""
    print("\n🎯 新结构的优势")
    print("=" * 60)
    
    print("📈 组织性改进:")
    print("  ✅ 每个游戏会话有独立目录")
    print("  ✅ 所有相关文件集中管理")
    print("  ✅ 文件命名规范化和可预测")
    print("  ✅ 游戏信息和统计自动记录")
    
    print("\n🔧 技术改进:")
    print("  ✅ DMAgent职责单一化（只生成，不存储）")
    print("  ✅ Game类统一管理存储逻辑")
    print("  ✅ 支持游戏会话的完整追踪")
    print("  ✅ 便于备份和分享游戏资源")
    
    print("\n👥 用户体验改进:")
    print("  ✅ 清晰的目录结构，易于浏览")
    print("  ✅ 完整的游戏信息记录")
    print("  ✅ 支持游戏会话的重新加载")
    print("  ✅ 便于游戏资源的管理和分发")

def main():
    """主函数"""
    print("🎉 新文件存储结构演示")
    print("📅 更新日期: 2025-01-08")
    print()
    
    # 演示目录结构
    demo_directory_structure()
    
    # 演示快速游戏创建
    demo_quick_game()
    
    # 显示文件示例
    show_file_examples()
    
    # 显示迁移优势
    show_migration_benefits()
    
    print("\n🎊 演示完成!")
    print("💡 现在可以运行 'python test/test_game.py' 进行完整测试")
    print("📚 查看 test/README.md 获取详细使用说明")

if __name__ == "__main__":
    main()