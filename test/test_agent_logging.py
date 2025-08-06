#!/usr/bin/env python3
"""
测试Agent日志记录功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent_logger import get_agent_logger, log_dm_speak_call, log_player_query_call, log_player_response_call
import json

def test_agent_logging():
    """测试Agent日志功能"""
    print("🧪 开始测试Agent日志记录功能...")
    
    # 获取日志记录器
    logger = get_agent_logger()
    print(f"📁 日志文件路径: {logger.log_file}")
    
    # 测试DM speak调用记录
    dm_params = {
        'chapter': 1,
        'script': ['第一章剧本内容...'],
        'chat_history': '玩家1: 你好大家\n玩家2: 我是嫌疑人吗？',
        'is_chapter_end': False,
        'is_game_end': False,
        'is_interject': True
    }
    
    dm_result = {
        'speech': '现在让我们分析一下当前的线索...',
        'tools': [{'type': 'SHOW_CLUE', 'args': ['1-1']}],
        'success': True
    }
    
    print("📝 记录DM speak调用...")
    log_dm_speak_call(dm_params, dm_result)
    
    # 测试Player query调用记录
    player_params = {
        'scripts': ['第一章剧本：我是警察...'],
        'chat_history': 'DM: 欢迎来到游戏\n玩家A: 大家好',
        'method': 'query'
    }
    
    player_result = {
        'content': '我觉得这个案子很可疑，需要更多线索。',
        'query': {'玩家B': '你昨晚在哪里？', '玩家C': '你有不在场证明吗？'}
    }
    
    print("📝 记录Player query调用...")
    log_player_query_call('玩家A', player_params, player_result)
    
    # 测试Player response调用记录
    response_params = {
        'scripts': ['第一章剧本：我是医生...'],
        'chat_history': '之前的对话记录...',
        'query': '你昨晚在哪里？',
        'query_player': '玩家A',
        'method': 'response'
    }
    
    response_result = '我昨晚在医院值班，有同事可以证明。'
    
    print("📝 记录Player response调用...")
    log_player_response_call('玩家B', response_params, response_result)
    
    # 测试错误记录
    print("📝 记录错误调用...")
    log_dm_speak_call({'test': 'error_test'}, None, "测试错误记录")
    
    print("✅ Agent日志记录测试完成！")
    print(f"📄 请查看日志文件: {logger.log_file}")

if __name__ == "__main__":
    test_agent_logging()