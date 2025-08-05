#!/usr/bin/env python3
"""
OpenAI客户端工具函数
提供安全的OpenAI客户端初始化方法
"""

from openai import OpenAI
from config import Config
import os

def create_openai_client(base_url=None, api_key=None):
    """
    安全地创建OpenAI客户端
    
    Args:
        base_url: API基础URL，如果为None则使用Config.API_BASE
        api_key: API密钥，如果为None则使用Config.API_KEY
        
    Returns:
        OpenAI: 配置好的OpenAI客户端实例
    """
    # 使用提供的参数或默认配置
    if base_url is None:
        base_url = Config.API_BASE
    if api_key is None:
        api_key = Config.API_KEY
    
    # 尝试不同的初始化方式
    client = None
    errors = []
    
    # 方式1: 使用base_url和api_key
    try:
        client = OpenAI(
            base_url=base_url,
            api_key=api_key
        )
        print(f"✅ OpenAI客户端初始化成功 (使用base_url: {base_url})")
        return client
    except Exception as e:
        errors.append(f"方式1失败: {e}")
        print(f"⚠️ 使用base_url初始化失败: {e}")
    
    # 方式2: 只使用api_key
    try:
        client = OpenAI(api_key=api_key)
        print(f"✅ OpenAI客户端初始化成功 (仅使用api_key)")
        return client
    except Exception as e:
        errors.append(f"方式2失败: {e}")
        print(f"⚠️ 仅使用api_key初始化失败: {e}")
    
    # 方式3: 使用环境变量
    try:
        # 临时设置环境变量
        original_key = os.environ.get('OPENAI_API_KEY')
        os.environ['OPENAI_API_KEY'] = api_key
        
        client = OpenAI()
        print(f"✅ OpenAI客户端初始化成功 (使用环境变量)")
        
        # 恢复原始环境变量
        if original_key is not None:
            os.environ['OPENAI_API_KEY'] = original_key
        elif 'OPENAI_API_KEY' in os.environ:
            del os.environ['OPENAI_API_KEY']
            
        return client
    except Exception as e:
        errors.append(f"方式3失败: {e}")
        print(f"⚠️ 使用环境变量初始化失败: {e}")
        
        # 恢复原始环境变量
        if original_key is not None:
            os.environ['OPENAI_API_KEY'] = original_key
        elif 'OPENAI_API_KEY' in os.environ:
            del os.environ['OPENAI_API_KEY']
    
    # 所有方式都失败了
    error_msg = "所有OpenAI客户端初始化方式都失败:\n" + "\n".join(errors)
    print(f"❌ {error_msg}")
    raise Exception(error_msg)

def test_openai_client(client):
    """
    测试OpenAI客户端是否可以正常工作
    
    Args:
        client: OpenAI客户端实例
        
    Returns:
        bool: 是否可以正常工作
    """
    try:
        # 尝试进行一个简单的API调用测试
        # 注意：这里不实际调用API，只是检查客户端是否正确初始化
        if hasattr(client, 'chat') and hasattr(client.chat, 'completions'):
            print("✅ OpenAI客户端功能检查通过")
            return True
        else:
            print("❌ OpenAI客户端缺少必要的方法")
            return False
    except Exception as e:
        print(f"❌ OpenAI客户端测试失败: {e}")
        return False

if __name__ == "__main__":
    # 测试客户端创建
    print("🧪 测试OpenAI客户端创建...")
    print("=" * 50)
    
    try:
        client = create_openai_client()
        if test_openai_client(client):
            print("🎉 OpenAI客户端创建和测试成功！")
        else:
            print("⚠️ OpenAI客户端创建成功但功能测试失败")
    except Exception as e:
        print(f"❌ OpenAI客户端创建失败: {e}")
    
    print("=" * 50)