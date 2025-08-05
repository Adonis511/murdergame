#!/usr/bin/env python3
"""
测试工具函数
提供统一的路径处理和项目根目录获取功能
"""

import os
import sys

def get_project_root():
    """
    获取项目根目录的绝对路径
    
    Returns:
        str: 项目根目录的绝对路径
    """
    # 获取当前文件所在目录（test目录）
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 上一级目录就是项目根目录
    project_root = os.path.dirname(current_dir)
    return project_root

def get_log_path(timestamp_dir):
    """
    获取log目录下指定时间戳目录的绝对路径
    
    Args:
        timestamp_dir (str): 时间戳目录名，如 "250805110930"
        
    Returns:
        str: 完整的游戏会话目录路径
    """
    project_root = get_project_root()
    return os.path.join(project_root, "log", timestamp_dir)

def setup_project_path():
    """
    设置项目路径，确保可以导入项目模块
    """
    project_root = get_project_root()
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

def list_available_games():
    """
    列出log目录下所有可用的游戏会话
    
    Returns:
        list: 可用的游戏会话目录列表
    """
    project_root = get_project_root()
    log_dir = os.path.join(project_root, "log")
    
    if not os.path.exists(log_dir):
        return []
    
    available_games = []
    for item in os.listdir(log_dir):
        item_path = os.path.join(log_dir, item)
        if os.path.isdir(item_path):
            # 检查是否包含script.json文件
            script_file = os.path.join(item_path, "script.json")
            if os.path.exists(script_file):
                available_games.append(item)
    
    return sorted(available_games)

def get_latest_game():
    """
    获取最新的游戏会话目录路径
    
    Returns:
        str or None: 最新游戏会话的完整路径，如果没有则返回None
    """
    available_games = list_available_games()
    if not available_games:
        return None
    
    # 最新的游戏（按时间戳排序）
    latest_game = available_games[-1]
    return get_log_path(latest_game)

def validate_game_path(game_path):
    """
    验证游戏路径是否有效
    
    Args:
        game_path (str): 游戏目录路径
        
    Returns:
        dict: 验证结果，包含是_valid、missing_files等信息
    """
    if not os.path.exists(game_path):
        return {
            'is_valid': False,
            'error': f'游戏目录不存在: {game_path}',
            'missing_files': []
        }
    
    required_files = ['script.json']
    optional_files = ['game_info.json']
    optional_dirs = ['imgs']
    
    missing_files = []
    existing_files = []
    existing_dirs = []
    
    # 检查必需文件
    for file_name in required_files:
        file_path = os.path.join(game_path, file_name)
        if os.path.exists(file_path):
            existing_files.append(file_name)
        else:
            missing_files.append(file_name)
    
    # 检查可选文件
    for file_name in optional_files:
        file_path = os.path.join(game_path, file_name)
        if os.path.exists(file_path):
            existing_files.append(file_name)
    
    # 检查可选目录
    for dir_name in optional_dirs:
        dir_path = os.path.join(game_path, dir_name)
        if os.path.exists(dir_path) and os.path.isdir(dir_path):
            existing_dirs.append(dir_name)
    
    is_valid = len(missing_files) == 0
    
    return {
        'is_valid': is_valid,
        'missing_files': missing_files,
        'existing_files': existing_files,
        'existing_dirs': existing_dirs,
        'game_path': game_path
    }

if __name__ == "__main__":
    # 测试工具函数
    print("🧰 测试工具函数演示")
    print("=" * 50)
    
    print(f"📁 项目根目录: {get_project_root()}")
    
    available_games = list_available_games()
    print(f"\n🎮 可用游戏会话: {len(available_games)} 个")
    for game in available_games:
        print(f"   - {game}")
    
    if available_games:
        latest_game = get_latest_game()
        print(f"\n🕐 最新游戏会话: {latest_game}")
        
        # 验证最新游戏
        validation = validate_game_path(latest_game)
        if validation['is_valid']:
            print(f"✅ 游戏会话有效")
            print(f"   存在文件: {', '.join(validation['existing_files'])}")
            if validation['existing_dirs']:
                print(f"   存在目录: {', '.join(validation['existing_dirs'])}")
        else:
            print(f"❌ 游戏会话无效: {validation['error']}")
            if validation['missing_files']:
                print(f"   缺少文件: {', '.join(validation['missing_files'])}")
    else:
        print("\n⚠️ 没有找到可用的游戏会话")