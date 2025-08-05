#!/usr/bin/env python3
"""
DM发言系统演示
展示在实际游戏中如何使用DM发言功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from game import Game

def simulate_game_session():
    """模拟一个完整的游戏会话，展示DM发言的各种场景"""
    print("🎭 剧本杀DM发言系统演示")
    print("=" * 60)
    
    # 创建游戏（不生成图片，节省时间）
    print("📝 正在创建新游戏...")
    game = Game(script_path=None, generate_images=False)
    
    print(f"\n✅ 游戏创建成功!")
    print(f"🎯 剧本: {game.script.get('title', '未命名剧本')}")
    print(f"👥 角色: {', '.join(game.script.get('characters', []))}")
    print(f"📖 章节数: {game.get_total_chapters()}")
    
    # 模拟游戏流程
    chat_history = ""
    
    # 第1章开始
    print("\n" + "="*50)
    print("📖 第1章：游戏开始")
    print("="*50)
    
    dm_speech = game.start_chapter(1, chat_history)
    print(f"\n🎭 DM: {dm_speech}\n")
    
    # 模拟玩家对话
    chat_history += f"""
DM: {dm_speech}

李华: 大家好，我是李华。这次聚会真是让人意外...
王强: 是啊，没想到会发生这种事情。我们需要冷静分析。
张雪: 我觉得我们应该先检查一下现场，看看有什么线索。
李华: 同意，让我们分头行动，仔细寻找证据。
王强: 等等，在分开之前，我们是不是应该先说说自己昨晚的行踪？
"""
    
    print("💬 玩家对话:")
    print(chat_history.split("DM:")[1].strip())
    
    # DM穿插发言
    print("\n" + "-"*30)
    print("🎭 DM穿插发言示例")
    print("-"*30)
    
    dm_interject = game.dm_interject(
        chat_history=chat_history,
        trigger_reason="引导玩家进行更深入的调查",
        guidance="提醒玩家注意时间线和动机"
    )
    print(f"\n🎭 DM: {dm_interject}\n")
    
    # 继续模拟对话
    chat_history += f"""
DM: {dm_interject}

张雪: DM说得对，我们确实需要建立时间线。
李华: 我昨晚10点就回房间休息了，有人可以证明吗？
王强: 我和张雪一起在客厅聊天到11点半。
张雪: 是的，然后我们就各自回房了。
李华: 那案发时间是什么时候？
王强: 根据现场情况，应该是凌晨2点左右。
"""
    
    # 第1章结束
    print("📖 第1章即将结束...")
    dm_end_chapter = game.end_chapter(1, chat_history)
    print(f"\n🎭 DM: {dm_end_chapter}\n")
    
    # 第2章开始
    print("\n" + "="*50)
    print("📖 第2章：深入调查")
    print("="*50)
    
    dm_chapter2 = game.start_chapter(2, chat_history)
    print(f"\n🎭 DM: {dm_chapter2}\n")
    
    # 模拟更多对话和线索发现
    final_history = chat_history + f"""
DM: {dm_end_chapter}
DM: {dm_chapter2}

李华: 我在书房发现了一把刀！
王强: 什么？在哪里？
张雪: 这可能就是凶器！
李华: 刀上还有血迹，而且刀柄上有指纹。
王强: 我们需要对比指纹。还有别的发现吗？
张雪: 我在走廊发现了脚印，通向张三的房间。
李华: 等等，张三不是受害者吗？
王强: 对，所以凶手可能是从他房间逃跑的。
张雪: 或者凶手就住在那附近...
李华: 我觉得我们已经接近真相了！
王强: 经过推理，我认为凶手是管家！
张雪: 我也这么认为，证据都指向他。
"""
    
    # 游戏结束
    print("\n" + "="*50)
    print("🎉 游戏结束：真相大白")
    print("="*50)
    
    # 模拟游戏结束时的最终总结
    dm_final = game.end_game(
        chat_history=final_history,
        killer="管家约翰",
        truth_info="约翰发现主人要修改遗嘱，剥夺他的继承权，愤怒之下用古董匕首杀害了主人，并试图伪造现场。"
    )
    print(f"\n🎭 DM最终总结: {dm_final}\n")
    
    # 展示触发条件测试
    print("\n" + "="*50)
    print("🎯 DM发言触发条件演示")
    print("="*50)
    
    test_scenarios = [
        {
            "描述": "正常游戏对话",
            "历史": "玩家A: 我觉得线索很有用。玩家B: 是的，我们继续调查。",
            "消息数": 5
        },
        {
            "描述": "包含关键词的讨论",
            "历史": "玩家A: 我怀疑凶手就在这里！玩家B: 有什么证据支持你的推理？玩家C: 真相即将揭晓！",
            "消息数": 6
        },
        {
            "描述": "消息过多需要引导",
            "历史": "玩家们在讨论无关话题...",
            "消息数": 12
        }
    ]
    
    for scenario in test_scenarios:
        should_speak = game.should_dm_interject(
            chat_history=scenario["历史"],
            message_count_since_last_dm=scenario["消息数"]
        )
        status = "✅ 需要发言" if should_speak else "❌ 无需发言"
        print(f"{scenario['描述']}: {status}")
    
    print("\n" + "="*60)
    print("🎉 DM发言系统演示完成！")
    print("="*60)
    
    print(f"\n📊 游戏统计:")
    print(f"  游戏目录: {game.get_game_directory()}")
    print(f"  剧本标题: {game.script.get('title', '未命名剧本')}")
    print(f"  总章节数: {game.get_total_chapters()}")
    print(f"  角色数量: {len(game.script.get('characters', []))}")
    
    print(f"\n💡 功能特点:")
    print(f"  ✅ 智能章节引导发言")
    print(f"  ✅ 章节总结和过渡")
    print(f"  ✅ 游戏结束真相揭示")
    print(f"  ✅ 动态穿插发言")
    print(f"  ✅ 自动触发条件判断")
    print(f"  ✅ 上下文感知的个性化内容")

if __name__ == "__main__":
    simulate_game_session()