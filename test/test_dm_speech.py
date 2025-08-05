#!/usr/bin/env python3
"""
测试DM发言功能
演示不同场景下的DM发言生成
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game import Game

def test_chapter_start():
    """测试章节开始发言"""
    print("=" * 60)
    print("🎭 测试DM章节开始发言")
    print("=" * 60)
    
    # 创建游戏（不生成图片，节省时间）
    game = Game(script_path=None, generate_images=False)
    
    # 模拟聊天历史
    chat_history = ""
    
    # 测试第1章开始
    print("\n📖 第1章开始:")
    dm_speech = game.start_chapter(1, chat_history)
    print(f"DM: {dm_speech}")
    
    # 模拟一些聊天记录
    chat_history = """
玩家A: 大家好，我是李明，这次聚会真是太突然了...
玩家B: 是啊，没想到会发生这种事情。
玩家C: 我们需要仔细调查一下现场。
"""
    
    # 测试第2章开始
    print("\n📖 第2章开始:")
    dm_speech = game.start_chapter(2, chat_history)
    print(f"DM: {dm_speech}")
    
    return game, chat_history

def test_chapter_end(game, chat_history):
    """测试章节结束发言"""
    print("\n" + "=" * 60)
    print("🎭 测试DM章节结束发言")
    print("=" * 60)
    
    # 扩展聊天历史
    extended_history = chat_history + """
玩家A: 我在书房发现了一把刀！
玩家B: 什么？！在哪里发现的？
玩家C: 这可能就是凶器！
玩家A: 刀上还有血迹...
玩家B: 我们需要检查指纹。
玩家C: 大家都在案发时间做什么？
"""
    
    # 测试第1章结束
    print("\n📖 第1章结束:")
    dm_speech = game.end_chapter(1, extended_history)
    print(f"DM: {dm_speech}")
    
    return extended_history

def test_dm_interject(game, chat_history):
    """测试DM穿插发言"""
    print("\n" + "=" * 60)
    print("🎭 测试DM穿插发言")
    print("=" * 60)
    
    # 测试场景1：提供引导
    print("\n🎯 场景1: 玩家需要引导")
    guidance_history = chat_history + """
玩家A: 我不知道该怎么办了...
玩家B: 线索太少了。
玩家C: 感觉陷入了死胡同。
"""
    
    dm_speech = game.dm_interject(
        chat_history=guidance_history,
        trigger_reason="玩家需要引导",
        guidance="提示玩家注意之前忽略的线索"
    )
    print(f"DM: {dm_speech}")
    
    # 测试场景2：推进剧情
    print("\n⏰ 场景2: 推进游戏进程")
    progress_history = chat_history + """
玩家A: 我觉得凶手就是张三！
玩家B: 不对，应该是李四！
玩家C: 你们都错了，明明是王五！
玩家A: 我们来投票吧！
玩家B: 等等，还有什么证据吗？
"""
    
    dm_speech = game.dm_interject(
        chat_history=progress_history,
        trigger_reason="需要推进投票流程",
        guidance="引导玩家进行最终推理"
    )
    print(f"DM: {dm_speech}")

def test_game_end(game, chat_history):
    """测试游戏结束发言"""
    print("\n" + "=" * 60)
    print("🎭 测试DM游戏结束发言")
    print("=" * 60)
    
    # 完整的游戏历史
    final_history = chat_history + """
玩家A: 经过仔细推理，我认为凶手是管家！
玩家B: 我同意，所有证据都指向他。
玩家C: 是的，动机、机会、手段都有。
DM: 请说出你们的最终推理...
玩家A: 管家因为遗产纠纷杀害了主人。
玩家B: 他利用对房屋的熟悉逃脱了监控。
玩家C: 凶器就是那把古董匕首。
"""
    
    # 提供真相信息
    killer = "管家约翰"
    truth_info = "约翰因为发现主人要修改遗嘱，剥夺他的继承权，在愤怒之下用古董匕首杀害了主人，并精心伪造了现场。"
    
    print("\n🎉 游戏结束:")
    dm_speech = game.end_game(
        chat_history=final_history,
        killer=killer,
        truth_info=truth_info
    )
    print(f"DM: {dm_speech}")

def test_interject_trigger(game):
    """测试DM发言触发条件"""
    print("\n" + "=" * 60)
    print("🎭 测试DM发言触发条件")
    print("=" * 60)
    
    # 测试不同的聊天情况
    test_cases = [
        {
            "name": "包含关键词的聊天",
            "history": "玩家A: 我怀疑凶手就在我们中间！玩家B: 有什么线索吗？玩家C: 需要更多证据来推理真相。",
            "count": 5
        },
        {
            "name": "消息数量触发",
            "history": "普通聊天内容...",
            "count": 15
        },
        {
            "name": "偏离主题的聊天",
            "history": "玩家A: 无话可说了。玩家B: 我也不知道该说什么。",
            "count": 3
        }
    ]
    
    for case in test_cases:
        should_interject = game.should_dm_interject(
            chat_history=case["history"],
            message_count_since_last_dm=case["count"]
        )
        
        print(f"\n📋 {case['name']}: {'✅ 需要DM发言' if should_interject else '❌ 不需要DM发言'}")
        print(f"   消息数: {case['count']}")
        print(f"   聊天内容: {case['history'][:50]}...")

def main():
    """主测试函数"""
    print("🎭 DM发言功能测试")
    print("=" * 60)
    
    try:
        # 测试章节开始发言
        game, chat_history = test_chapter_start()
        
        # 测试章节结束发言
        extended_history = test_chapter_end(game, chat_history)
        
        # 测试穿插发言
        test_dm_interject(game, extended_history)
        
        # 测试游戏结束发言
        test_game_end(game, extended_history)
        
        # 测试触发条件
        test_interject_trigger(game)
        
        print("\n" + "=" * 60)
        print("🎉 所有DM发言功能测试完成！")
        print("=" * 60)
        
        print(f"\n💡 游戏信息:")
        print(f"   游戏目录: {game.get_game_directory()}")
        print(f"   当前章节: {game.get_current_chapter()}")
        print(f"   总章节数: {game.get_total_chapters()}")
        print(f"   角色数量: {len(game.script.get('characters', []))}")
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()