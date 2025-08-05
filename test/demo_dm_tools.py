#!/usr/bin/env python3
"""
DM工具功能演示
展示线索展示和角色展示工具的实际应用
"""

import sys
import os

# 导入测试工具
from test_utils import setup_project_path, get_project_root

# 设置项目路径
setup_project_path()

from dm_agent import DMAgent

def demo_tools():
    """演示DM工具功能"""
    print("🎭 DM工具功能演示")
    print("=" * 60)
    
    # 创建DM代理
    dm_agent = DMAgent()
    
    # 模拟一个完整的剧本数据
    script_data = {
        'title': '翠湖山庄谋杀案',
        'characters': ['富豪张三', '管家李四', '医生王五', '秘书赵六'],
        'dm': [
            '第一章：暴风雨夜，张三在书房被发现死亡',
            '第二章：警方到达，开始调查各种线索',
            '第三章：嫌疑人逐个询问，真相浮出水面'
        ],
        'clues': [
            ['一把带血的古董匕首', '破碎的威士忌酒杯', '撕碎的遗嘱草稿'],
            ['管家的指纹在门把手上', '监控显示医生11点离开', '秘书的证词有矛盾'],
            ['银行记录显示大额转账', '威胁信件藏在保险箱', '真正的遗嘱在暗格中']
        ]
    }
    
    print(f"📖 剧本: {script_data['title']}")
    print(f"👥 角色: {', '.join(script_data['characters'])}")
    print(f"📄 章节数: {len(script_data['dm'])}")
    
    # 演示1: 线索展示工具
    print("\n" + "="*50)
    print("🔍 演示1: 线索展示工具")
    print("="*50)
    
    print("\n📋 可用线索:")
    for chapter, clues in enumerate(script_data['clues'], 1):
        print(f"第{chapter}章:")
        for i, clue in enumerate(clues, 1):
            print(f"  {chapter}-{i}: {clue}")
    
    # 展示几个关键线索
    key_clues = [(1, 1), (1, 3), (3, 2)]
    for chapter, clue_index in key_clues:
        print(f"\n🔍 展示线索 {chapter}-{clue_index}:")
        # 使用项目根目录构建base_path
        project_root = get_project_root()
        result = dm_agent.show_clue(
            chapter=chapter,
            clue_index=clue_index,
            script_data=script_data,
            base_path=project_root
        )
        
        if result['success']:
            print(f"✅ 线索描述: {result['description']}")
            print(f"📁 图片路径: {result['image_url']}")
            print(f"🖼️ 文件名: {result['image_filename']}")
        else:
            print(f"❌ 展示失败: {result.get('error')}")
    
    # 演示2: 角色展示工具
    print("\n" + "="*50)
    print("👤 演示2: 角色展示工具")
    print("="*50)
    
    for character in script_data['characters']:
        print(f"\n👤 展示角色: {character}")
        # 使用项目根目录构建base_path
        project_root = get_project_root()
        result = dm_agent.show_character(
            character_name=character,
            script_data=script_data,
            base_path=project_root
        )
        
        if result['success']:
            print(f"✅ 角色名称: {result['character_name']}")
            print(f"📁 图片路径: {result['image_url']}")
            print(f"🖼️ 文件名: {result['image_filename']}")
        else:
            print(f"❌ 展示失败: {result.get('error')}")
    
    # 演示3: 工具调用解析
    print("\n" + "="*50)
    print("🔧 演示3: 工具调用解析")
    print("="*50)
    
    test_speeches = [
        "现在让我们来查看第一个重要线索。[SHOW_CLUE:1-1] 这把古董匕首上的血迹告诉我们凶手就在现场...",
        "让我为大家介绍主要嫌疑人。[SHOW_CHARACTER:管家李四] 李四先生，您昨晚的行踪能详细说明一下吗？",
        "我们发现了两个关键证据：[SHOW_CLUE:1-1] 以及这份撕碎的文件 [SHOW_CLUE:1-3]。这两个线索相互印证...",
        "经过调查，我们锁定了真凶。[SHOW_CHARACTER:医生王五] 王五医生，请解释一下您的动机。[SHOW_CLUE:3-1] 这笔转账记录说明了一切！"
    ]
    
    for i, speech in enumerate(test_speeches, 1):
        print(f"\n🎬 测试发言 {i}:")
        print(f"原始内容: {speech}")
        
        # 使用项目根目录构建base_path
        project_root = get_project_root()
        result = dm_agent._parse_dm_response(speech, script_data, project_root)
        
        print(f"\n📝 解析后发言: {result['speech']}")
        print(f"🛠️ 工具调用数量: {len(result['tools'])}")
        
        for j, tool in enumerate(result['tools'], 1):
            if tool['success']:
                if tool['tool_type'] == 'show_clue':
                    print(f"   工具{j}: 展示线索 第{tool['chapter']}章第{tool['clue_index']}个")
                    print(f"          描述: {tool['description']}")
                    print(f"          图片: {tool['image_url']}")
                elif tool['tool_type'] == 'show_character':
                    print(f"   工具{j}: 展示角色 {tool['character_name']}")
                    print(f"          图片: {tool['image_url']}")
            else:
                print(f"   工具{j}: 调用失败 - {tool.get('error')}")
    
    # 演示4: speak方法的完整功能
    print("\n" + "="*50)
    print("🎤 演示4: speak方法完整功能")
    print("="*50)
    
    print("⚠️ 注意: 以下演示需要AI API连接")
    user_input = input("是否继续演示speak方法? (y/N): ").strip().lower()
    
    if user_input == 'y':
        print("\n🎭 DM第1章开场发言（AI生成）:")
        try:
            result = dm_agent.speak(
                chapter=0,
                script=script_data['dm'],
                chat_history="",
                title=script_data['title'],
                characters=script_data['characters'],
                clues=script_data['clues'],
                base_path=get_project_root()
            )
            
            print(f"\n📝 DM发言:")
            print(result['speech'])
            
            if result['tools']:
                print(f"\n🛠️ AI自动使用的工具:")
                for i, tool in enumerate(result['tools'], 1):
                    if tool['success']:
                        if tool['tool_type'] == 'show_clue':
                            print(f"   {i}. 展示线索: {tool['description']}")
                        elif tool['tool_type'] == 'show_character':
                            print(f"   {i}. 展示角色: {tool['character_name']}")
                    else:
                        print(f"   {i}. 工具失败: {tool.get('error')}")
            else:
                print("\n🔧 AI选择不使用工具")
                
        except Exception as e:
            print(f"❌ AI发言生成失败: {e}")
            print("💡 可能是API配置问题，请检查config.py中的API设置")
    else:
        print("⏭️ 跳过AI发言演示")
    
    print("\n" + "="*60)
    print("🎉 DM工具功能演示完成!")
    print("="*60)
    
    print(f"\n📋 功能总结:")
    print(f"✅ 线索展示工具:")
    print(f"   - 根据章节和索引展示具体线索")
    print(f"   - 返回线索描述和图片路径")
    print(f"   - 支持错误处理和验证")
    
    print(f"\n✅ 角色展示工具:")
    print(f"   - 根据角色名称展示角色信息")
    print(f"   - 返回角色图片路径")
    print(f"   - 验证角色是否存在")
    
    print(f"\n✅ 智能工具调用:")
    print(f"   - AI自动决定是否使用工具")
    print(f"   - 支持多种工具调用格式")
    print(f"   - 自动解析和执行工具调用")
    
    print(f"\n✅ 增强的speak方法:")
    print(f"   - 返回结构化数据(发言+工具)")
    print(f"   - 支持所有原有发言类型")
    print(f"   - 与工具系统无缝集成")
    
    print(f"\n💡 使用建议:")
    print(f"   - 工具调用格式: [SHOW_CLUE:章节-索引] 或 [SHOW_CHARACTER:角色名]")
    print(f"   - AI会根据上下文智能选择使用工具")
    print(f"   - 返回数据包含发言内容和工具调用结果")
    print(f"   - 支持错误处理和回退机制")

if __name__ == "__main__":
    demo_tools()