"""
AI Agent调用日志记录模块
记录DM Agent和Player Agent的核心方法调用参数和结果
"""

import os
import json
import time
from datetime import datetime
from typing import Any, Dict, List


class AgentLogger:
    def __init__(self, log_dir: str = "log"):
        """
        初始化日志记录器
        
        Args:
            log_dir: 日志目录路径
        """
        self.log_dir = log_dir
        self.ensure_log_dir()
        
        # 创建当前会话的日志文件
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = os.path.join(log_dir, f"agent_calls_{timestamp}.log")
        
        # 初始化日志文件
        self._write_log_header()
    
    def ensure_log_dir(self):
        """确保日志目录存在"""
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
    
    def _write_log_header(self):
        """写入日志文件头部信息"""
        header = {
            "session_start": datetime.now().isoformat(),
            "description": "AI Agent方法调用日志",
            "format": "每行一个JSON对象，包含时间戳、代理类型、方法名、参数和结果"
        }
        
        with open(self.log_file, 'w', encoding='utf-8') as f:
            f.write(f"# {json.dumps(header, ensure_ascii=False, indent=2)}\n")
            f.write("# =" * 50 + "\n\n")
    
    def log_dm_speak(self, params: Dict[str, Any], result: Any = None, error: str = None):
        """
        记录DM Agent的speak方法调用
        
        Args:
            params: 输入参数字典
            result: 返回结果
            error: 错误信息（如果有）
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent_type": "DMAgent",
            "method": "speak",
            "params": self._sanitize_params(params),
            "success": error is None,
            "result": result if error is None else None,
            "error": error
        }
        
        self._write_log_entry(log_entry)
    
    def log_player_query(self, player_name: str, params: Dict[str, Any], result: Any = None, error: str = None):
        """
        记录Player Agent的query方法调用
        
        Args:
            player_name: 玩家角色名
            params: 输入参数字典
            result: 返回结果
            error: 错误信息（如果有）
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent_type": "PlayerAgent",
            "player_name": player_name,
            "method": "query",
            "params": self._sanitize_params(params),
            "success": error is None,
            "result": result if error is None else None,
            "error": error
        }
        
        self._write_log_entry(log_entry)
    
    def log_player_response(self, player_name: str, params: Dict[str, Any], result: Any = None, error: str = None):
        """
        记录Player Agent的response方法调用
        
        Args:
            player_name: 玩家角色名
            params: 输入参数字典
            result: 返回结果
            error: 错误信息（如果有）
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent_type": "PlayerAgent", 
            "player_name": player_name,
            "method": "response",
            "params": self._sanitize_params(params),
            "success": error is None,
            "result": result if error is None else None,
            "error": error
        }
        
        self._write_log_entry(log_entry)
    
    def _sanitize_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        清理参数，避免过长的文本内容影响日志可读性
        
        Args:
            params: 原始参数字典
            
        Returns:
            清理后的参数字典
        """
        sanitized = {}
        
        for key, value in params.items():
            if isinstance(value, str):
                # 如果字符串太长，截断并添加省略号
                if len(value) > 500:
                    sanitized[key] = value[:500] + "...[truncated]"
                else:
                    sanitized[key] = value
            elif isinstance(value, list):
                # 对列表中的字符串也进行截断
                sanitized_list = []
                for item in value:
                    if isinstance(item, str) and len(item) > 300:
                        sanitized_list.append(item[:300] + "...[truncated]")
                    else:
                        sanitized_list.append(item)
                sanitized[key] = sanitized_list
            else:
                sanitized[key] = value
                
        return sanitized
    
    def _write_log_entry(self, entry: Dict[str, Any]):
        """
        写入日志条目到文件
        
        Args:
            entry: 日志条目字典
        """
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception as e:
            print(f"⚠️ 写入Agent调用日志失败: {e}")


# 全局日志实例
_global_logger = None

def get_agent_logger() -> AgentLogger:
    """获取全局Agent日志记录器实例"""
    global _global_logger
    if _global_logger is None:
        _global_logger = AgentLogger()
    return _global_logger

def log_dm_speak_call(params: Dict[str, Any], result: Any = None, error: str = None):
    """便捷函数：记录DM speak调用"""
    get_agent_logger().log_dm_speak(params, result, error)

def log_player_query_call(player_name: str, params: Dict[str, Any], result: Any = None, error: str = None):
    """便捷函数：记录Player query调用"""
    get_agent_logger().log_player_query(player_name, params, result, error)

def log_player_response_call(player_name: str, params: Dict[str, Any], result: Any = None, error: str = None):
    """便捷函数：记录Player response调用"""
    get_agent_logger().log_player_response(player_name, params, result, error)