#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试PlayerAgent功能
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from player_agent import PlayerAgent

def test_player_query():
    """测试玩家主动发言功能"""
    print("🎭 测试玩家主动发言功能")
    print("=" * 40)
    
    # 创建玩家
    player = PlayerAgent("李华")
    
    # 模拟剧本内容
    scripts = [
        """你是李华，一名成功的商人，今晚来到张家别墅参加聚会。
        你与死者张明有商业纠纷，他最近威胁要曝光你的商业秘密。
        你必须找出真正的凶手来洗清自己的嫌疑。
        你知道张明最近收到了威胁信，但你不是写信的人。""",
        
        """第二章：你发现了张明的日记，里面提到他怀疑有人要害他。
        日记中提到了一个神秘的约会，时间就在他死亡的前一天。
        你开始怀疑其他几个人，特别是那个一直很安静的王强。
        你需要通过交谈获取更多信息。"""
    ]
    
    # 模拟聊天历史
    chat_history = """## 交谈历史

**DM**: 欢迎各位来到豪门血案剧本杀！现在是第一轮交谈时间。

**王强**: 我觉得我们应该先分享一下昨晚各自在做什么。我昨晚一直在书房看书。

**张雪**: *看起来很紧张* 我...我昨晚很早就睡了，什么都不知道。

**刘远**: 各位，我们需要冷静分析。死者张明是在几点被发现的？

**DM**: 张明是在今早8点被管家发现在书房中死亡的。"""
    
    try:
        print(f"👤 玩家: {player.name}")
        print(f"📖 当前剧本章节数: {len(scripts)}")
        print("\n🗣️ 生成玩家发言...")
        
        # 生成玩家发言
        response = player.query(scripts, chat_history)
        
        print(f"\n💬 {player.name}的发言:")
        print("-" * 30)
        
        if isinstance(response, dict):
            print(f"📝 发言内容: {response.get('content', '无内容')}")
            
            queries = response.get('query', {})
            if queries:
                print(f"❓ 询问对象:")
                for person, question in queries.items():
                    print(f"   @{person}: {question}")
            else:
                print(f"❓ 询问对象: 无")
        else:
            print(f"⚠️ 非预期格式: {response}")
        
        print("-" * 30)
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        return False

def test_player_response():
    """测试玩家被动回应功能"""
    print("\n🎭 测试玩家被动回应功能")
    print("=" * 40)
    
    # 创建玩家
    player = PlayerAgent("王强")
    
    # 模拟剧本内容
    scripts = [
        """你是王强，张明的商业伙伴。你们最近因为一笔投资产生了分歧。
        昨晚你确实在书房，但你在查看一些重要文件。
        你发现张明可能在背着你做一些不光彩的交易。
        你有动机，但你不是凶手。你需要证明自己的清白。"""
    ]
    
    # 模拟聊天历史（包含对王强的询问）
    chat_history = """## 交谈历史

**DM**: 现在是询问环节。

**李华**: 王强，你昨晚说在书房看书，但是管家说他看到你的房间灯光一直在闪烁，你在做什么？

**张雪**: 是啊，王强，你能详细说说你昨晚的行程吗？从几点到几点在做什么？

**刘远**: 还有，你和张明最近有什么矛盾吗？我听说你们的合作出现了问题。"""
    
    try:
        print(f"👤 被询问玩家: {player.name}")
        print("\n🔍 检测到针对该玩家的询问...")
        print("\n🗣️ 生成玩家回应（基础示例）...")
        
        # 生成玩家回应（需要指定问题和提问者）
        default_query = "请详细说明你昨晚的行程和你与张明的关系。"
        default_player = "李华"
        response = player.response(scripts, chat_history, default_query, default_player)
        
        print(f"\n💬 {player.name}的回应:")
        print("-" * 30)
        print(response)
        print("-" * 30)
        
        # 测试不同的具体问题
        print("\n🔍 测试不同的具体问题...")
        specific_query = "你昨晚在书房具体在做什么？为什么灯光会闪烁？"
        query_player_name = "张雪"
        
        print(f"❓ 具体问题: {specific_query}")
        print(f"👤 提问者: {query_player_name}")
        print("\n🗣️ 生成针对性回应...")
        
        specific_response = player.response(scripts, chat_history, specific_query, query_player_name)
        
        print(f"\n💬 {player.name}的针对性回应:")
        print("-" * 30)
        print(specific_response)
        print("-" * 30)
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        return False

def test_specific_query_response():
    """测试指定问题和提问者的回应功能"""
    print("\n🎯 测试指定问题回应功能")
    print("=" * 40)
    
    scenarios = [
        {
            "name": "张雪",
            "script": "你是张雪，受害者张明的女儿。你知道父亲最近收到威胁信，但你一直瞒着家人。你很害怕，但不想让其他人知道。",
            "query": "你父亲最近有什么异常行为吗？",
            "query_player": "刘远",
            "expected": "应该表现出紧张，可能会隐瞒一些信息"
        },
        {
            "name": "李华",
            "script": "你是李华，张明的商业伙伴。你们因为投资分歧产生矛盾，张明威胁要曝光你的商业秘密。你很愤怒但不是凶手。",
            "query": "你和张明的合作关系如何？最近有什么问题吗？",
            "query_player": "王强",
            "expected": "可能会承认矛盾，但否认杀人动机"
        },
        {
            "name": "王强",
            "script": "你是王强，张明的朋友。你发现了张明的一些不法行为，正在纠结是否举报。昨晚你在书房查看相关证据。",
            "query": "昨晚你在书房做什么？为什么不开灯？",
            "query_player": "张雪",
            "expected": "应该会回避敏感信息，可能找借口"
        }
    ]
    
    base_history = """## 交谈历史
**DM**: 现在开始询问环节，请大家轮流提问。
"""
    
    success_count = 0
    
    for scenario in scenarios:
        print(f"\n🎭 测试场景: {scenario['name']}")
        print(f"❓ 问题: {scenario['query']}")
        print(f"👤 提问者: {scenario['query_player']}")
        print(f"📝 预期行为: {scenario['expected']}")
        
        try:
            player = PlayerAgent(scenario['name'])
            
            # 使用不同问题的回应
            general_query = "你有什么想说的吗？"
            general_player = "DM"
            general_response = player.response([scenario['script']], base_history, general_query, general_player)
            print(f"\n💬 一般性回应 (问题: {general_query}):")
            print(f"   {general_response[:100]}..." if len(general_response) > 100 else f"   {general_response}")
            
            # 指定具体问题的回应
            specific_response = player.response(
                [scenario['script']], 
                base_history, 
                scenario['query'], 
                scenario['query_player']
            )
            print(f"\n🎯 针对性回应 (问题: {scenario['query']}):")
            print(f"   {specific_response[:100]}..." if len(specific_response) > 100 else f"   {specific_response}")
            
            # 比较两种回应的差异
            if general_response != specific_response:
                print(f"✅ 两种回应有差异，说明针对性效果良好")
            else:
                print(f"⚠️ 两种回应相同，可能问题设计需要调整")
                
            success_count += 1
            
        except Exception as e:
            print(f"❌ 测试失败: {str(e)}")
    
    print(f"\n📊 测试结果: {success_count}/{len(scenarios)} 成功")
    return success_count == len(scenarios)

def test_different_scenarios():
    """测试不同场景下的表现"""
    print("\n🎭 测试不同角色场景")
    print("=" * 40)
    
    scenarios = [
        {
            "name": "张雪",
            "role": "受害者的女儿，知道一些秘密",
            "script": """你是张雪，死者张明的女儿。你知道父亲最近很焦虑，经常深夜不睡。
            你偷听到他在和某人打电话，提到"如果你敢曝光，我们就同归于尽"。
            你怀疑父亲卷入了什么危险的事情，但你不确定凶手是谁。
            你很害怕，不知道该相信谁。""",
            "history": """**DM**: 请张雪分享一下对父亲最近状况的观察。"""
        },
        {
            "name": "刘远",
            "role": "侦探角色，需要主导推理",
            "script": """你是刘远，一名退休的警察，现在是私家侦探。
            你是应张明邀请来调查他收到的威胁信的。
            你已经初步分析了现场，发现了一些可疑的线索。
            你的任务是引导大家分析案情，找出真凶。""",
            "history": """**李华**: 我觉得我们需要更系统地分析这个案件，刘远，你有什么专业建议吗？"""
        }
    ]
    
    for scenario in scenarios:
        print(f"\n🎯 场景: {scenario['name']} - {scenario['role']}")
        
        player = PlayerAgent(scenario['name'])
        
        try:
            response = player.query([scenario['script']], scenario['history'])
            print(f"💬 {scenario['name']}:")
            
            if isinstance(response, dict):
                content = response.get('content', '无内容')
                content_preview = content[:80] + "..." if len(content) > 80 else content
                print(f"   📝 {content_preview}")
                
                queries = response.get('query', {})
                if queries:
                    print(f"   ❓ 询问: {len(queries)}个对象")
            else:
                print(f"   ⚠️ 格式异常: {str(response)[:50]}...")
            
        except Exception as e:
            print(f"❌ {scenario['name']} 生成失败: {str(e)}")

def main():
    """主函数"""
    print("🎮 PlayerAgent 测试工具")
    print("=" * 50)
    
    success_count = 0
    
    # 测试主动发言
    if test_player_query():
        success_count += 1
    
    # 测试被动回应
    if test_player_response():
        success_count += 1
    
    # 测试指定问题回应功能
    if test_specific_query_response():
        success_count += 1
    
    # 测试不同场景
    test_different_scenarios()
    success_count += 1
    
    print(f"\n📊 测试总结:")
    print(f"   成功: {success_count}/4")
    print(f"   状态: {'✅ 全部通过' if success_count == 4 else '⚠️ 部分失败'}")
    
    print(f"\n💡 使用方法:")
    print(f"```python")
    print(f"# 创建玩家")
    print(f"player = PlayerAgent('玩家名称')")
    print(f"")
    print(f"# 主动发言（返回JSON格式）")
    print(f"result = player.query(scripts, chat_history)")
    print("# result = {'content': '发言内容', 'query': {'张三': '你昨晚在哪里？'}}")
    print("")
    print("# 获取发言内容")
    print("content = result['content']")
    print("")
    print("# 获取询问对象")
    print("queries = result['query']")
    print("for person, question in queries.items():")
    print("    print(f'询问 {person}: {question}')")
    print("")
    print("# 被动回应（字符串格式，必须指定问题和提问者）")
    print("response = player.response(scripts, chat_history, query='具体问题', query_player='提问者')")
    print("")
    print("# 示例：")
    print("response = player.response(scripts, chat_history, ")
    print("                         query='你昨晚在做什么？',")
    print("                         query_player='李华')")
    print(f"```")

if __name__ == "__main__":
    main()