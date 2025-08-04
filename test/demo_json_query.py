#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
演示PlayerAgent的JSON格式输出功能
"""

import json
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from player_agent import PlayerAgent

def demo_json_output():
    """演示JSON格式输出"""
    print("🎮 PlayerAgent JSON格式演示")
    print("=" * 50)
    
    # 创建玩家
    player = PlayerAgent("李华")
    
    # 模拟剧本
    scripts = [
        """你是李华，死者张明的商业伙伴。你们最近因为项目投资产生了严重分歧，
        张明威胁要撤回投资并曝光你的一些商业秘密。你非常愤怒，但你不是凶手。
        你需要证明自己的清白，同时找出真正的凶手。
        你怀疑张明的女儿张雪知道一些内情，因为她最近行为很反常。"""
    ]
    
    # 模拟聊天历史
    chat_history = """## 交谈历史

**DM**: 各位，现在开始第一轮讨论。请大家分享昨晚的行程。

**王强**: 我昨晚一直在书房整理文件，大概从8点到11点。

**张雪**: *看起来很紧张* 我...我昨晚很早就休息了，什么都不知道。

**刘远**: 我是应张明先生邀请来调查威胁信的，昨晚我在检查房屋的安全设施。

**DM**: 现在轮到李华发言。"""
    
    try:
        print("🎭 角色: 李华（商业伙伴，有动机嫌疑人）")
        print("📚 剧本章节: 1")
        print("🗣️ 生成发言...")
        
        # 调用query方法
        result = player.query(scripts, chat_history)
        
        print("\n📄 AI返回的JSON结果:")
        print("=" * 30)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        print("=" * 30)
        
        # 解析和展示结果
        print("\n🔍 结果解析:")
        
        content = result.get('content', '')
        print(f"📝 发言内容:")
        print(f"   {content}")
        
        queries = result.get('query', {})
        if queries:
            print(f"\n❓ 询问对象 ({len(queries)}个):")
            for person, question in queries.items():
                print(f"   👤 @{person}: {question}")
        else:
            print(f"\n❓ 询问对象: 无")
        
        print(f"\n✅ JSON格式验证: {'通过' if isinstance(result, dict) else '失败'}")
        
        return True
        
    except Exception as e:
        print(f"❌ 演示失败: {str(e)}")
        return False

def demo_multiple_scenarios():
    """演示不同场景下的JSON输出"""
    print("\n🎯 多场景JSON输出演示")
    print("=" * 50)
    
    scenarios = [
        {
            "name": "张雪",
            "role": "受害者女儿，知情但害怕",
            "expected_behavior": "可能会询问其他人，试图获取信息确认自己的怀疑"
        },
        {
            "name": "王强", 
            "role": "最大嫌疑人，需要为自己辩护",
            "expected_behavior": "可能会质疑其他人，转移注意力"
        },
        {
            "name": "刘远",
            "role": "侦探，主导推理",
            "expected_behavior": "会询问多个人关键问题，推进案情分析"
        }
    ]
    
    base_script = "你需要根据当前情况决定发言策略。"
    base_history = "**DM**: 请大家继续讨论案情。"
    
    for scenario in scenarios:
        print(f"\n🎭 {scenario['name']} ({scenario['role']})")
        
        player = PlayerAgent(scenario['name'])
        
        try:
            result = player.query([base_script], base_history)
            
            if isinstance(result, dict):
                content_len = len(result.get('content', ''))
                query_count = len(result.get('query', {}))
                
                print(f"   📝 发言长度: {content_len}字符")
                print(f"   ❓ 询问数量: {query_count}个")
                print(f"   ✅ JSON格式: 正确")
            else:
                print(f"   ❌ JSON格式: 错误")
                
        except Exception as e:
            print(f"   ❌ 生成失败: {str(e)}")

def show_json_structure():
    """展示JSON结构说明"""
    print("\n📋 JSON输出结构说明")
    print("=" * 50)
    
    example = {
        "content": "我认为我们需要仔细分析时间线。根据我的了解...",
        "query": {
            "王强": "你说你在书房，有人能证明吗？",
            "张雪": "你父亲最近有什么异常行为吗？"
        }
    }
    
    print("📄 标准JSON格式:")
    print(json.dumps(example, ensure_ascii=False, indent=2))
    
    print("\n🔍 字段说明:")
    print("  content: 玩家的主要发言内容（markdown格式）")
    print("  query:   玩家要询问的问题")
    print("    - 键: 被询问者的姓名")  
    print("    - 值: 具体的问题内容")
    print("    - 如果不询问任何人，则为空字典 {}")
    
    print("\n💡 使用优势:")
    print("  ✅ 结构化数据，便于程序处理")
    print("  ✅ 明确区分发言和询问")
    print("  ✅ 支持同时询问多个玩家")
    print("  ✅ 便于实现游戏逻辑和UI显示")

def main():
    """主函数"""
    print("🚀 PlayerAgent JSON输出功能演示")
    print("🎮 新功能：query方法现在返回JSON格式")
    print("📝 包含content（发言）和query（询问）字段")
    print()
    
    # 演示基本功能
    success = demo_json_output()
    
    if success:
        # 演示多场景
        demo_multiple_scenarios()
        
        # 展示结构说明
        show_json_structure()
        
        print("\n🎉 演示完成！")
        print("💡 现在可以运行 'python test_player.py' 进行完整测试")
    else:
        print("\n⚠️ 基础演示失败，请检查配置")

if __name__ == "__main__":
    main()