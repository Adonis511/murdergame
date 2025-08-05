#!/usr/bin/env python3
"""
测试所有模块导入是否正常
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """测试所有主要模块的导入"""
    print("🧪 测试模块导入...")
    
    try:
        from game import Game
        print("✅ game模块导入成功")
    except ImportError as e:
        print(f"❌ game模块导入失败: {e}")
        return False
    
    try:
        from dm_agent import DMAgent
        print("✅ dm_agent模块导入成功")
    except ImportError as e:
        print(f"❌ dm_agent模块导入失败: {e}")
        return False
    
    try:
        from player_agent import PlayerAgent
        print("✅ player_agent模块导入成功")
    except ImportError as e:
        print(f"❌ player_agent模块导入失败: {e}")
        return False
    
    # 测试基本实例化
    try:
        dm = DMAgent()
        print("✅ DMAgent实例化成功")
    except Exception as e:
        print(f"⚠️ DMAgent实例化失败: {e}")
    
    try:
        player = PlayerAgent("测试角色")
        print("✅ PlayerAgent实例化成功")
    except Exception as e:
        print(f"⚠️ PlayerAgent实例化失败: {e}")
    
    print("\n🎉 所有核心模块导入测试完成!")
    return True

if __name__ == "__main__":
    test_imports()