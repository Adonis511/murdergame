#!/usr/bin/env python3
"""
测试DM工具功能
演示线索展示和角色展示工具的使用
"""

import sys
import os

# 导入测试工具
from test_utils import setup_project_path, get_latest_game, get_project_root

# 设置项目路径
setup_project_path()

from dm_agent import DMAgent

def test_show_clue():
    """测试线索展示工具"""
    print("=" * 60)
    print("🔍 测试线索展示工具")
    print("=" * 60)
    
    dm_agent = DMAgent()
    
    # 模拟剧本数据
    script_data = {
        'title': '豪门谋杀案',
        'characters': ['李华', '王强', '张雪', '管家约翰'],
        'clues': [
            ['一把带血的匕首', '破碎的花瓶', '神秘的威胁信'],
            ['指纹证据', '监控录像', '证人证言'],
            ['遗嘱副本', '银行记录', '电话录音']
        ]
    }
    
    # 测试展示不同线索
    test_cases = [
        (1, 1, "第1章第1个线索"),
        (1, 2, "第1章第2个线索"),
        (2, 1, "第2章第1个线索"),
        (3, 3, "第3章第3个线索"),
        (5, 1, "不存在的章节"),
        (1, 5, "不存在的线索")
    ]
    
    for chapter, clue_index, description in test_cases:
        print(f"\n🎯 测试 {description}:")
        # 使用项目根目录构建base_path
        project_root = get_project_root()
        result = dm_agent.show_clue(
            chapter=chapter,
            clue_index=clue_index,
            script_data=script_data,
            base_path=project_root
        )
        
        if result['success']:
            print(f"✅ 成功!")
            print(f"   线索描述: {result['description']}")
            print(f"   图片路径: {result['image_url']}")
        else:
            print(f"❌ 失败: {result.get('error', '未知错误')}")

def test_show_character():
    """测试角色展示工具"""
    print("\n" + "=" * 60)
    print("👤 测试角色展示工具")
    print("=" * 60)
    
    dm_agent = DMAgent()
    
    # 模拟剧本数据
    script_data = {
        'title': '豪门谋杀案',
        'characters': ['李华', '王强', '张雪', '管家约翰']
    }
    
    # 测试展示不同角色
    test_cases = [
        ('李华', '主角'),
        ('王强', '嫌疑人'),
        ('张雪', '证人'),
        ('管家约翰', '管家'),
        ('不存在的角色', '无效角色')
    ]
    
    for character_name, description in test_cases:
        print(f"\n🎯 测试 {description}:")
        # 使用项目根目录构建base_path
        project_root = get_project_root()
        result = dm_agent.show_character(
            character_name=character_name,
            script_data=script_data,
            base_path=project_root
        )
        
        if result['success']:
            print(f"✅ 成功!")
            print(f"   角色名称: {result['character_name']}")
            print(f"   图片路径: {result['image_url']}")
        else:
            print(f"❌ 失败: {result.get('error', '未知错误')}")

def test_speak_with_tools():
    """测试speak方法的工具集成"""
    print("\n" + "=" * 60)
    print("🎭 测试speak方法工具集成")
    print("=" * 60)
    
    dm_agent = DMAgent()
    
    # 模拟完整的剧本数据
    script_data = {
        'title': '豪门谋杀案',
        'characters': ['李华', '王强', '张雪', '管家约翰'],
        'dm': [
            'DM第一章: 案件发生，现场调查',
            'DM第二章: 证据收集，嫌疑人询问',
            'DM第三章: 真相揭露'
        ],
        'clues': [
            ['一把带血的匕首', '破碎的花瓶', '神秘的威胁信'],
            ['指纹证据', '监控录像', '证人证言'],
            ['遗嘱副本', '银行记录', '电话录音']
        ]
    }
    
    # 测试不同类型的发言
    test_scenarios = [
        {
            'name': '第1章开始',
            'params': {
                'chapter': 0,
                'script': script_data['dm'],
                'chat_history': '',
                'is_chapter_end': False,
                'is_game_end': False,
                'title': script_data['title'],
                'characters': script_data['characters'],
                'clues': script_data['clues']
            }
        },
        {
            'name': '第1章结束',
            'params': {
                'chapter': 0,
                'script': script_data['dm'],
                'chat_history': '玩家A: 我找到了一把刀！\n玩家B: 这可能是凶器！',
                'is_chapter_end': True,
                'is_game_end': False,
                'title': script_data['title'],
                'characters': script_data['characters'],
                'clues': script_data['clues']
            }
        },
        {
            'name': '游戏结束',
            'params': {
                'chapter': 2,
                'script': script_data['dm'],
                'chat_history': '完整的游戏历史...',
                'is_chapter_end': False,
                'is_game_end': True,
                'killer': '管家约翰',
                'truth_info': '约翰因为遗嘱问题杀害了主人',
                'title': script_data['title'],
                'characters': script_data['characters'],
                'clues': script_data['clues']
            }
        }
    ]
    
    for scenario in test_scenarios:
        print(f"\n🎬 场景: {scenario['name']}")
        print("-" * 40)
        
        try:
            result = dm_agent.speak(**scenario['params'])
            
            print(f"✅ 发言生成成功!")
            print(f"📝 DM发言: {result['speech'][:200]}...")
            
            if result['tools']:
                print(f"\n🛠️ 使用的工具:")
                for i, tool in enumerate(result['tools'], 1):
                    if tool['success']:
                        if tool['tool_type'] == 'show_clue':
                            print(f"   {i}. 展示线索: 第{tool['chapter']}章第{tool['clue_index']}个 - {tool['description']}")
                            print(f"      图片: {tool['image_url']}")
                        elif tool['tool_type'] == 'show_character':
                            print(f"   {i}. 展示角色: {tool['character_name']}")
                            print(f"      图片: {tool['image_url']}")
                    else:
                        print(f"   {i}. 工具调用失败: {tool.get('error', '未知错误')}")
            else:
                print("🔧 本次发言未使用工具")
                
        except Exception as e:
            print(f"❌ 发言生成失败: {e}")

def test_tool_parsing():
    """测试工具调用解析"""
    print("\n" + "=" * 60)
    print("🔧 测试工具调用解析")
    print("=" * 60)
    
    dm_agent = DMAgent()
    
    script_data = {
        'characters': ['李华', '王强'],
        'clues': [['匕首', '花瓶']]
    }
    
    test_responses = [
        "现在让我们看看第一个线索。[SHOW_CLUE:1-1] 这把匕首很关键。",
        "让我介绍一下嫌疑人。[SHOW_CHARACTER:李华] 李华先生昨晚的行踪很可疑。",
        "我们发现了两个重要证据。[SHOW_CLUE:1-1] 还有 [SHOW_CLUE:1-2] 这些都很重要。",
        "普通的发言，没有工具调用。",
        "混合发言 [SHOW_CHARACTER:王强] 和线索 [SHOW_CLUE:1-1] 一起展示。"
    ]
    
    for i, response in enumerate(test_responses, 1):
        print(f"\n🧪 测试 {i}: {response[:50]}...")
        result = dm_agent._parse_dm_response(response, script_data)
        
        print(f"   解析后发言: {result['speech']}")
        print(f"   工具数量: {len(result['tools'])}")
        for j, tool in enumerate(result['tools'], 1):
            if tool['success']:
                if tool['tool_type'] == 'show_clue':
                    print(f"   工具{j}: 线索 {tool['chapter']}-{tool['clue_index']}")
                elif tool['tool_type'] == 'show_character':
                    print(f"   工具{j}: 角色 {tool['character_name']}")

def main():
    """主测试函数"""
    print("🧪 DM工具功能测试")
    print("=" * 60)
    
    try:
        # 测试线索展示工具
        test_show_clue()
        
        # 测试角色展示工具  
        test_show_character()
        
        # 测试工具调用解析
        test_tool_parsing()
        
        # 测试speak方法工具集成
        print("\n⚠️ 注意: speak方法测试需要AI API连接，可能需要较长时间...")
        user_input = input("是否继续测试speak方法? (y/N): ").strip().lower()
        
        if user_input == 'y':
            test_speak_with_tools()
        else:
            print("⏭️ 跳过speak方法测试")
        
        print("\n" + "=" * 60)
        print("🎉 DM工具功能测试完成!")
        print("=" * 60)
        
        print(f"\n💡 功能总结:")
        print(f"  ✅ 线索展示工具 - 展示指定章节的线索图片和描述")
        print(f"  ✅ 角色展示工具 - 展示角色图片信息") 
        print(f"  ✅ 智能工具调用 - AI自动决定使用哪些工具")
        print(f"  ✅ 工具调用解析 - 支持多种格式的工具调用")
        print(f"  ✅ 结构化返回 - 返回发言内容和工具调用结果")
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()