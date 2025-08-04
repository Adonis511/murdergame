#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
演示PlayerAgent的response方法新API
展示必选参数query和query_player的用法
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from player_agent import PlayerAgent

def demo_response_api():
    """演示response方法的新API"""
    print("🎯 PlayerAgent.response() 新API演示")
    print("=" * 50)
    print("🔹 query和query_player参数现在是必选的")
    print("🔹 提供更精准的问题针对性回应")
    print()
    
    # 创建玩家
    player = PlayerAgent("王强")
    
    # 模拟剧本
    scripts = [
        """你是王强，张明的商业伙伴。昨晚你在书房查看一些重要的商业文件，
        发现张明可能在背着你做一些不光彩的交易。你很愤怒，但你不是凶手。
        你需要巧妙地回答问题，既不暴露自己知道的秘密，又要证明自己的清白。"""
    ]
    
    # 模拟聊天历史
    chat_history = """## 交谈历史
**DM**: 现在开始询问环节。

**刘远**: 各位，我需要了解昨晚的情况。

**张雪**: 我很担心父亲，希望大家能说实话。
"""
    
    # 演示不同问题的针对性回应
    questions = [
        {
            "query": "你昨晚在书房具体在做什么？为什么灯光一直闪烁？",
            "query_player": "李华",
            "description": "关于行踪的直接询问"
        },
        {
            "query": "你和张明最近的合作关系如何？有什么矛盾吗？",
            "query_player": "刘远",
            "description": "关于动机的调查询问"
        },
        {
            "query": "叔叔，你真的没有伤害我父亲吗？我很害怕...",
            "query_player": "张雪",
            "description": "来自受害者女儿的情感询问"
        },
        {
            "query": "昨晚11点你在哪里？有人能证明吗？",
            "query_player": "DM",
            "description": "官方的时间线询问"
        }
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"🎭 场景 {i}: {question['description']}")
        print(f"❓ 问题: {question['query']}")
        print(f"👤 提问者: {question['query_player']}")
        print()
        
        try:
            # 调用新的response API
            response = player.response(
                scripts, 
                chat_history, 
                query=question['query'], 
                query_player=question['query_player']
            )
            
            print(f"💬 {player.name}的回应:")
            print("-" * 40)
            print(response)
            print("-" * 40)
            print()
            
        except Exception as e:
            print(f"❌ 回应生成失败: {str(e)}")
            print()

def demo_api_comparison():
    """对比新旧API的差异"""
    print("📊 API对比演示")
    print("=" * 50)
    
    print("❌ 旧API（已弃用）:")
    print("```python")
    print("# 可选参数，可能导致回应不够精准")
    print("response = player.response(scripts, chat_history)")
    print("response = player.response(scripts, chat_history, query='', query_player='')")
    print("```")
    print()
    
    print("✅ 新API（当前版本）:")
    print("```python")
    print("# 必选参数，确保回应针对性")
    print("response = player.response(scripts, chat_history, ")
    print("                         query='具体问题', ")
    print("                         query_player='提问者姓名')")
    print("```")
    print()
    
    print("🎯 新API优势:")
    print("  ✅ 强制指定问题，避免模糊回应")
    print("  ✅ 明确提问者，考虑人际关系")
    print("  ✅ 提高回应质量和针对性")
    print("  ✅ 更符合剧本杀游戏逻辑")

def demo_error_handling():
    """演示错误处理"""
    print("\n⚠️ 错误处理演示")
    print("=" * 50)
    
    print("如果忘记传入必选参数，会产生TypeError:")
    print("```python")
    print("# 错误用法示例（会报错）:")
    print("# response = player.response(scripts, chat_history)  # 缺少参数")
    print("```")
    print()
    
    print("正确的调用方式:")
    print("```python")
    print("response = player.response(")
    print("    scripts=scripts,")
    print("    chat_history=chat_history,")
    print("    query='你的问题',")
    print("    query_player='提问者姓名'")
    print(")")
    print("```")

def main():
    """主函数"""
    print("🚀 PlayerAgent Response API 更新演示")
    print("📝 重要变更：query和query_player参数现在是必选的")
    print()
    
    # 演示新API用法
    demo_response_api()
    
    # API对比说明
    demo_api_comparison()
    
    # 错误处理说明
    demo_error_handling()
    
    print("\n🎉 演示完成！")
    print("💡 现在所有response调用都必须明确指定问题和提问者")
    print("📚 查看 test/README.md 获取更多使用说明")

if __name__ == "__main__":
    main()