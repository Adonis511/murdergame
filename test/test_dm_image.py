#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试DMAgent的图片生成功能
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dm_agent import DMAgent
import time

def test_single_image():
    """测试单张图片生成"""
    print("🖼️ 测试单张图片生成")
    print("=" * 40)
    
    dm_agent = DMAgent()
    
    # 测试提示词
    prompt = "一间豪华的书房，深色木质书桌上放着一本打开的古书，昏暗的台灯光线，神秘的氛围，高清摄影风格"
    
    print(f"📝 提示词: {prompt}")
    print("🎨 开始生成...")
    
    try:
        result = dm_agent.gen_image(prompt)
        
        if result and result.get('success'):
            print("✅ 图片生成成功!")
            print(f"🔗 图片URL: {result.get('url')}")
            print(f"📁 本地文件: {result.get('local_path')}")
            print(f"⏱️ 生成时间: {result.get('generation_time', 0):.2f}秒")
            print(f"📋 任务ID: {result.get('task_id')}")
            return True
        elif result:
            print("❌ 图片生成失败!")
            print(f"错误代码: {result.get('error_code')}")
            print(f"错误信息: {result.get('error_message')}")
            return False
        else:
            print("❌ 图片生成失败: 未知错误")
            return False
            
    except Exception as e:
        print(f"❌ 测试异常: {str(e)}")
        return False

def test_character_images():
    """测试角色图片生成"""
    print("\n🎭 测试角色图片生成")
    print("=" * 40)
    
    dm_agent = DMAgent()
    
    # 模拟角色图像提示词
    character_prompts = {
        "张明": "一位50岁的成功商人，穿着深色西装，严肃的表情，在豪华办公室中，商务摄影风格",
        "李华": "一位45岁的商业伙伴，穿着灰色西装，略显紧张的神情，在会议室中，职业摄影风格",
        "王强": "一位40岁的朋友，穿着休闲西装，沉思的表情，在书房中，肖像摄影风格"
    }
    
    success_count = 0
    total_count = len(character_prompts)
    
    for character, prompt in character_prompts.items():
        print(f"\n👤 角色: {character}")
        print(f"📝 提示词: {prompt}")
        
        try:
            result = dm_agent.gen_image(prompt)
            
            if result and result.get('success'):
                print(f"✅ {character} 图片生成成功!")
                print(f"📁 文件: {result.get('local_path')}")
                success_count += 1
            else:
                print(f"❌ {character} 图片生成失败!")
                if result:
                    print(f"   错误: {result.get('error_message')}")
            
            # 避免频率限制
            if character != list(character_prompts.keys())[-1]:
                print("⏳ 等待3秒...")
                time.sleep(3)
                
        except Exception as e:
            print(f"❌ {character} 生成异常: {str(e)}")
    
    print(f"\n📊 测试结果: {success_count}/{total_count} 成功")
    return success_count == total_count

def test_clue_images():
    """测试线索图片生成"""
    print("\n🔍 测试线索图片生成")
    print("=" * 40)
    
    dm_agent = DMAgent()
    
    # 模拟线索图像提示词
    clue_prompts = [
        "一把古典的银色匕首，精美雕刻的手柄，放在暗红色天鹅绒上，特写镜头",
        "一封威胁信，破旧的纸张上写着红色字迹，蜡封印章，复古风格",
        "一个打碎的花瓶碎片，散落在大理石地板上，犯罪现场摄影风格"
    ]
    
    success_count = 0
    total_count = len(clue_prompts)
    
    for i, prompt in enumerate(clue_prompts, 1):
        print(f"\n🔍 线索 {i}: {prompt[:30]}...")
        
        try:
            result = dm_agent.gen_image(prompt)
            
            if result and result.get('success'):
                print(f"✅ 线索图片 {i} 生成成功!")
                print(f"📁 文件: {result.get('local_path')}")
                success_count += 1
            else:
                print(f"❌ 线索图片 {i} 生成失败!")
                if result:
                    print(f"   错误: {result.get('error_message')}")
            
            # 避免频率限制
            if i < total_count:
                print("⏳ 等待3秒...")
                time.sleep(3)
                
        except Exception as e:
            print(f"❌ 线索图片 {i} 生成异常: {str(e)}")
    
    print(f"\n📊 测试结果: {success_count}/{total_count} 成功")
    return success_count == total_count

def test_error_handling():
    """测试错误处理"""
    print("\n⚠️ 测试错误处理")
    print("=" * 40)
    
    dm_agent = DMAgent()
    
    # 测试空提示词
    print("📝 测试空提示词...")
    result = dm_agent.gen_image("")
    
    if result and not result.get('success'):
        print("✅ 空提示词正确处理")
    else:
        print("⚠️ 空提示词处理异常")
    
    # 测试非常长的提示词
    print("\n📝 测试超长提示词...")
    long_prompt = "一个非常详细的场景描述，" * 100  # 创建一个很长的提示词
    result = dm_agent.gen_image(long_prompt)
    
    if result:
        if result.get('success'):
            print("✅ 超长提示词处理成功")
        else:
            print(f"⚠️ 超长提示词被拒绝: {result.get('error_message')}")
    else:
        print("⚠️ 超长提示词处理异常")

def check_environment():
    """检查环境配置"""
    print("🔧 检查环境配置")
    print("=" * 40)
    
    from config import Config
    
    # 检查API_KEY
    if hasattr(Config, 'API_KEY') and Config.API_KEY:
        print("✅ API_KEY 已配置")
        print(f"   密钥: {Config.API_KEY[:10]}...{Config.API_KEY[-4:]}")
    else:
        print("❌ API_KEY 未配置")
        return False
    
    # 检查网络连接
    try:
        import requests
        response = requests.get("https://dashscope.aliyuncs.com", timeout=5)
        print("✅ 网络连接正常")
    except Exception as e:
        print(f"❌ 网络连接失败: {str(e)}")
        return False
    
    # 检查目录权限
    try:
        os.makedirs("images", exist_ok=True)
        test_file = "images/test_permissions.txt"
        with open(test_file, "w") as f:
            f.write("test")
        os.remove(test_file)
        print("✅ 目录权限正常")
    except Exception as e:
        print(f"❌ 目录权限问题: {str(e)}")
        return False
    
    return True

def main():
    """主函数"""
    print("🎨 DMAgent 图片生成功能测试")
    print("=" * 50)
    
    # 检查环境
    if not check_environment():
        print("❌ 环境检查失败，无法继续测试")
        return
    
    print("\n🚀 开始功能测试...")
    
    # 统计测试结果
    test_results = []
    
    # 测试单张图片生成
    test_results.append(test_single_image())
    
    # 测试角色图片生成
    test_results.append(test_character_images())
    
    # 测试线索图片生成
    test_results.append(test_clue_images())
    
    # 测试错误处理
    test_error_handling()
    
    # 总结
    success_count = sum(test_results)
    total_count = len(test_results)
    
    print(f"\n📊 测试总结:")
    print(f"   成功: {success_count}/{total_count}")
    print(f"   状态: {'✅ 全部通过' if success_count == total_count else '⚠️ 部分失败'}")
    
    print(f"\n💡 使用说明:")
    print(f"   图片保存在: images/ 目录")
    print(f"   支持的尺寸: 1024*1024, 512*512 等")
    print(f"   单次生成时间: 10-30秒")
    print(f"   建议间隔: 3-5秒 (避免频率限制)")

if __name__ == "__main__":
    main()