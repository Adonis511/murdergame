from ai_service import AIService
from openai import OpenAI
from config import Config
import json
import time
import requests
import os
from datetime import datetime
from typing import List
class DMAgent:
    def __init__(self):
        # self.name = name
        # self.description = description
        # self.goals = goals
        # self.constraints = constraints
        # self.tools = tools
        self.system_prompt = """你是一名专业的剧本杀DM，负责创作完整的剧本杀剧本。

你需要完成以下工作：
1. 编写一个完整的剧本杀剧本，涉及4-6个角色，包含谋杀悬疑情节
2. 为每个角色创建分章节的剧本，剧本应该像写小说一样生动形象地展开，每章节每个人的剧本体量不少于500字
3. 创建DM专用的上帝视角剧本，用于推进游戏
4. 设计每阶段的线索和图像提示词
5. 创建角色图像生成提示词

重要要求：
- 必须返回纯JSON格式，不要用markdown代码块包装
- 确保JSON格式正确，可以直接解析
- 所有中文内容要完整清晰"""
        self.client = OpenAI(
            base_url=Config.API_BASE,
            api_key=Config.API_KEY,
        )
    def gen_script(self):
        print("start generating script")
        start = time.time()
        completion = self.client.chat.completions.create(
        model="qwen-plus",
        temperature=0.7,
        messages=[
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": """请创作一个剧本杀剧本，主题为豪门谋杀案。

创作步骤：
1. 设计4-6个角色，为他们取名
2. 创建DM章节（上帝视角）
3. 为每个角色创建分章节剧本
4. 设计线索和图像提示词

输出格式要求（纯JSON，不要markdown包装）：
{
  "title": "剧本标题",
  "theme": "剧本主题",
  "characters": ["角色1姓名", "角色2姓名", "角色3姓名", "角色4姓名"],
  "角色1姓名": ["第一章剧本内容", "第二章剧本内容", "第三章剧本内容"],
  "角色2姓名": ["第一章剧本内容", "第二章剧本内容", "第三章剧本内容"],
  "角色3姓名": ["第一章剧本内容", "第二章剧本内容", "第三章剧本内容"],
  "角色4姓名": ["第一章剧本内容", "第二章剧本内容", "第三章剧本内容"],
  "dm": ["DM第一章指引", "DM第二章指引", "DM第三章指引", "真相揭露"],
  "clues": [["第一章线索1", "第一章线索2"], ["第二章线索1", "第二章线索2"], ["第三章线索1", "第三章线索2"]],
  "clue_image_prompts": [["第一章线索1图像提示", "第一章线索2图像提示"], ["第二章线索1图像提示", "第二章线索2图像提示"]],
  "character_image_prompts": {
    "角色1姓名": "角色1的AI绘图提示词",
    "角色2姓名": "角色2的AI绘图提示词",
    "角色3姓名": "角色3的AI绘图提示词",
    "角色4姓名": "角色4的AI绘图提示词"
  }
}

请直接输出JSON，不要添加任何解释或markdown格式。"""},
            ],
        )
        end = time.time()
        print(f"script generated in {end - start} seconds")
        
        # 获取AI响应内容
        response_content = completion.choices[0].message.content
        print("Raw response preview:", response_content[:200])
        
        try:
            # 尝试解析JSON
            # 如果响应被包在```json代码块中，需要先提取
            if response_content.strip().startswith("```json"):
                # 提取JSON内容
                json_start = response_content.find("{")
                json_end = response_content.rfind("}") + 1
                if json_start != -1 and json_end != 0:
                    json_content = response_content[json_start:json_end]
                else:
                    json_content = response_content
            else:
                json_content = response_content
            
            # 解析JSON
            script_data = json.loads(json_content)
            
            print(f"✅ 剧本生成成功！")
            return script_data
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON解析失败: {e}")
            print(f"原始响应内容: {response_content[:200]}...")
            
            # 尝试手动修复JSON格式
            try:
                # 移除可能的markdown代码块标记
                cleaned_content = response_content.replace("```json", "").replace("```", "").strip()
                script_data = json.loads(cleaned_content)
                
                print(f"✅ JSON修复成功！")
                return script_data
                
            except Exception as repair_error:
                print(f"❌ JSON修复也失败: {repair_error}")
                return None

    def gen_image(self, prompt: str, size: str = "512*512"):
        """
        使用阿里云百炼通义万象2.2生成图片
        
        Args:
            prompt: 图片生成的提示词
            size: 图片尺寸，默认"512*512"
            
        Returns:
            dict: 包含图片URL和相关信息的字典
        """
        print(f"🎨 开始生成图片: {prompt[:50]}...")
        start_time = time.time()
        
        try:
            # 第一步：提交图片生成任务
            task_id = self._submit_image_task(prompt, size)
            if not task_id:
                return None
                
            print(f"📋 任务已提交，ID: {task_id}")
            
            # 第二步：轮询获取结果
            result = self._poll_image_result(task_id)
            if not result:
                return None
                
            end_time = time.time()
            print(f"⏱️ 图片生成完成，耗时: {end_time - start_time:.2f}秒")
            
            # 第三步：处理结果
            if result.get('task_status') == 'SUCCEEDED':
                results = result.get('results', [])
                if results:
                    image_info = results[0]
                    image_url = image_info.get('url')
                    actual_prompt = image_info.get('actual_prompt', prompt)
                    
                    print(f"✅ 图片生成成功!")
                    print(f"🔗 图片URL: {image_url}")
                    print(f"📝 实际提示词: {actual_prompt[:100]}...")
                    
                    return {
                        'success': True,
                        'url': image_url,
                        'original_prompt': prompt,
                        'actual_prompt': actual_prompt,
                        'task_id': task_id,
                        'generation_time': end_time - start_time
                    }
                else:
                    print("❌ 未找到生成结果")
                    return None
            else:
                # 处理失败情况
                error_code = result.get('code', 'Unknown')
                error_message = result.get('message', '未知错误')
                print(f"❌ 图片生成失败: {error_code} - {error_message}")
                return {
                    'success': False,
                    'error_code': error_code,
                    'error_message': error_message,
                    'task_id': task_id
                }
                
        except Exception as e:
            print(f"❌ 图片生成异常: {str(e)}")
            return None
    
    def speak(self, chapter: int, script: List[str], chat_history: str = "", 
              is_chapter_end: bool = False, is_game_end: bool = False, 
              is_interject: bool = False, **kwargs) -> str:
        """
        生成DM发言
        
        Args:
            chapter: 章节（从0开始）
            script: 剧本内容
            chat_history: 聊天历史记录
            is_chapter_end: 是否是章节结束
            is_game_end: 是否是游戏结束
            is_interject: 是否是穿插发言
            **kwargs: 其他参数，如killer、truth_info、trigger_reason、guidance等
            
        Returns:
            str: DM发言内容
        """
        print(f"🎭 DM正在准备发言...")
        
        try:
            # 确定发言类型
            if is_game_end:
                speak_type = "game_end"
            elif is_chapter_end:
                speak_type = "chapter_end"
            elif is_interject:
                speak_type = "interject"
            else:
                speak_type = "chapter_start"
            
            # 构建剧本数据字典
            script_data = {
                'title': kwargs.get('title', '剧本杀游戏'),
                'characters': kwargs.get('characters', []),
                'dm': script
            }
            
            # 构建系统提示词
            system_prompt = self._build_speak_system_prompt(speak_type)
            
            # 构建用户提示词
            user_prompt = self._build_speak_user_prompt(
                speak_type, chapter + 1, len(script), script_data, 
                chat_history, **kwargs
            )
            
            # 生成DM发言
            completion = self.client.chat.completions.create(
                model="qwen-plus",
                temperature=0.8,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            response = completion.choices[0].message.content.strip()
            print(f"✅ DM {speak_type} 发言生成完成")
            return response
            
        except Exception as e:
            print(f"❌ DM发言生成失败: {e}")
            return self._get_speak_fallback(speak_type, chapter + 1)
    
    def _build_speak_system_prompt(self, speak_type: str) -> str:
        """构建speak方法的系统提示词"""
        base_prompt = """你是一名专业的剧本杀DM（游戏主持人），负责引导整个游戏进程。
你的发言应该：
1. 营造悬疑紧张的氛围
2. 推进剧情发展  
3. 引导玩家思考和互动
4. 保持角色扮演的沉浸感
5. 语言生动有趣，富有感染力"""

        if speak_type == "chapter_start":
            return base_prompt + """

当前任务：章节开始发言
- 简要回顾前情（如果不是第一章）
- 介绍本章节的背景设定
- 引导玩家进入角色状态
- 设置本章节的主要任务或目标
- 营造适当的氛围"""

        elif speak_type == "chapter_end":
            return base_prompt + """

当前任务：章节结束发言
- 总结本章节的关键事件
- 点评玩家的表现和发现的线索
- 为下一章节做铺垫（如果不是最后一章）
- 保持悬念和期待感"""

        elif speak_type == "game_end":
            return base_prompt + """

当前任务：游戏结束总结发言
- 揭示完整真相和所有秘密
- 总结整个游戏的精彩瞬间
- 点评每个玩家的表现
- 对推理过程进行分析
- 给出最终的感谢和总结"""

        elif speak_type == "interject":
            return base_prompt + """

当前任务：游戏过程中的穿插发言
- 根据当前对话情况进行适当引导
- 提供必要的提示或澄清
- 控制游戏节奏
- 适时推进剧情
- 简短而有效，不要过度干预"""

        return base_prompt

    def _build_speak_user_prompt(self, speak_type: str, current_chapter: int, 
                                total_chapters: int, script_data: dict, 
                                chat_history: str, **kwargs) -> str:
        """构建speak方法的用户提示词"""
        
        # 基础信息
        title = script_data.get('title', '剧本杀游戏')
        characters = script_data.get('characters', [])
        dm_script = script_data.get('dm', [])
        
        # 当前章节信息
        current_dm_content = ""
        if current_chapter <= len(dm_script):
            current_dm_content = dm_script[current_chapter - 1] if dm_script else "本章节内容"
        
        base_info = f"""## 剧本信息
**剧本标题**: {title}
**角色列表**: {', '.join(characters) if characters else '游戏角色'}
**当前章节**: 第{current_chapter}章 (共{total_chapters}章)
**当前章节内容**: {current_dm_content}
"""

        if speak_type == "chapter_start":
            prompt = base_info + f"""

## 发言场景
这是第{current_chapter}章开始时的DM发言。

## 聊天历史
{chat_history if chat_history else "（游戏刚开始，暂无聊天记录）"}

## 发言要求
请作为DM为第{current_chapter}章开场，内容应该：
1. {"欢迎玩家并介绍游戏背景" if current_chapter == 1 else f"简要回顾第{current_chapter-1}章的关键情况"}
2. 介绍第{current_chapter}章的场景和任务
3. 引导玩家开始本章节的互动
4. 字数控制在200-400字之间
"""

        elif speak_type == "chapter_end":
            prompt = base_info + f"""

## 发言场景
这是第{current_chapter}章结束时的DM总结发言。

## 本章聊天历史
{chat_history}

## 发言要求
请作为DM为第{current_chapter}章做总结，内容应该：
1. 总结本章节玩家的主要发现和互动
2. 点评重要的推理和线索发现
3. {f"为第{current_chapter+1}章做铺垫" if current_chapter < total_chapters else "为最终真相揭示做准备"}
4. 字数控制在300-500字之间
"""

        elif speak_type == "game_end":
            # 获取真相信息
            killer = kwargs.get('killer', '凶手身份待确认')
            truth_info = kwargs.get('truth_info', '最终真相待揭示')
            
            prompt = base_info + f"""

## 发言场景
这是整个游戏结束时的最终总结发言。

## 完整游戏历史
{chat_history}

## 真相信息
**凶手**: {killer}
**真相**: {truth_info}

## 发言要求
请作为DM为整个游戏做最终总结，内容应该：
1. 完整揭示真相和所有秘密
2. 解释关键线索和推理逻辑
3. 点评每个玩家的精彩表现
4. 总结整个游戏的亮点时刻
5. 表达对玩家参与的感谢
6. 字数控制在500-800字之间
"""

        elif speak_type == "interject":
            trigger_reason = kwargs.get('trigger_reason', '游戏进程需要')
            guidance = kwargs.get('guidance', '')
            
            prompt = base_info + f"""

## 发言场景
在第{current_chapter}章进行过程中的穿插发言。

## 触发原因
{trigger_reason}

## 当前对话情况
{chat_history[-1000:] if len(chat_history) > 1000 else chat_history}

## 特殊指导要求
{guidance}

## 发言要求
请作为DM进行简短的穿插发言，内容应该：
1. 针对当前情况进行适当引导
2. {"提供必要的提示或澄清" if guidance else "推进游戏进程"}
3. 保持游戏的流畅性
4. 字数控制在100-200字之间
"""

        return prompt

    def _get_speak_fallback(self, speak_type: str, current_chapter: int) -> str:
        """获取speak方法的备用发言"""
        fallback_speeches = {
            "chapter_start": f"欢迎各位来到第{current_chapter}章！让我们继续深入这个扑朔迷离的案件。请各位仔细观察，认真思考，真相就在你们中间...",
            "chapter_end": f"第{current_chapter}章到此结束。各位的表现都很精彩，一些重要的线索已经浮现。让我们期待接下来的发展...",
            "game_end": "经过激烈的推理和讨论，真相终于大白于天下！感谢各位的精彩演出，这真是一场难忘的推理之旅！",
            "interject": "请各位继续，我在这里静静观察着你们的推理过程..."
        }
        return fallback_speeches.get(speak_type, "DM发言暂时无法生成，请继续游戏。")

    def _submit_image_task(self, prompt: str, size: str) -> str:
        """提交图片生成任务"""
        url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis"
        
        headers = {
            'X-DashScope-Async': 'enable',
            'Authorization': f'Bearer {Config.API_KEY}',
            'Content-Type': 'application/json'
        }
        
        data = {
            "model": "wan2.2-t2i-flash",
            "input": {
                "prompt": prompt
            },
            "parameters": {
                "size": size,
                "n": 1
            }
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            task_id = result.get('output', {}).get('task_id')
            
            if task_id:
                return task_id
            else:
                print(f"❌ 提交任务失败: {result}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 网络请求失败: {str(e)}")
            return None
        except json.JSONDecodeError as e:
            print(f"❌ 响应解析失败: {str(e)}")
            return None
    
    def _poll_image_result(self, task_id: str, max_wait_time: int = 300, poll_interval: int = 5) -> dict:
        """轮询获取图片生成结果"""
        url = f"https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}"
        
        headers = {
            'Authorization': f'Bearer {Config.API_KEY}'
        }
        
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            try:
                response = requests.get(url, headers=headers, timeout=30)
                response.raise_for_status()
                
                result = response.json()
                output = result.get('output', {})
                task_status = output.get('task_status')
                
                print(f"🔄 任务状态: {task_status}")
                
                if task_status == 'SUCCEEDED':
                    return output
                elif task_status == 'FAILED':
                    return output
                elif task_status in ['PENDING', 'RUNNING']:
                    # 继续等待
                    time.sleep(poll_interval)
                    continue
                else:
                    print(f"⚠️ 未知任务状态: {task_status}")
                    time.sleep(poll_interval)
                    continue
                    
            except requests.exceptions.RequestException as e:
                print(f"❌ 轮询请求失败: {str(e)}")
                time.sleep(poll_interval)
                continue
            except json.JSONDecodeError as e:
                print(f"❌ 响应解析失败: {str(e)}")
                time.sleep(poll_interval)
                continue
        
        print(f"⏰ 等待超时 ({max_wait_time}秒)")
        return None
    

def test_image_generation():
    """测试图片生成功能"""
    print("\n🎨 测试图片生成功能")
    print("=" * 50)
    
    dm_agent = DMAgent()
    
    # 测试提示词
    test_prompts = [
        "一间豪华的书房，深色木质书桌，昏暗的灯光，神秘的氛围",
        "一把古典的匕首，银色刀刃，精美雕刻的手柄",
        "一封威胁信，破旧的纸张，红色印章"
    ]
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n🖼️ 测试 {i}/{len(test_prompts)}: {prompt}")
        
        result = dm_agent.gen_image(prompt)
        
        if result and result.get('success'):
            print(f"✅ 生成成功!")
            print(f"📁 本地文件: {result.get('local_path', '未保存')}")
        elif result:
            print(f"❌ 生成失败: {result.get('error_message', '未知错误')}")
        else:
            print(f"❌ 生成失败: 未知错误")
        
        # 添加延迟避免频率限制
        if i < len(test_prompts):
            print("⏳ 等待5秒...")
            time.sleep(5)

if __name__ == "__main__":
    import sys
    
    print("🎭 DMAgent 功能测试")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "script":
            print("📝 测试剧本生成...")
            dm_agent = DMAgent()
            result = dm_agent.gen_script()
            if result:
                print("✅ 剧本生成成功!")
            else:
                print("❌ 剧本生成失败!")
        elif sys.argv[1] == "image":
            print("🎨 测试图片生成...")
            test_image_generation()
        elif sys.argv[1] == "all":
            print("🔄 测试所有功能...")
            dm_agent = DMAgent()
            
            print("\n1️⃣ 测试剧本生成...")
            script_result = dm_agent.gen_script()
            
            if script_result and script_result.get('character_image_prompts'):
                print("\n2️⃣ 测试角色图片生成...")
                character_prompts = script_result['character_image_prompts']
                
                for character, prompt in list(character_prompts.items())[:2]:  # 只测试前2个角色
                    print(f"\n🎭 为角色 {character} 生成图片...")
                    image_result = dm_agent.gen_image(prompt)
                    
                    if image_result and image_result.get('success'):
                        print(f"✅ {character} 图片生成成功!")
                    else:
                        print(f"❌ {character} 图片生成失败!")
                    
                    time.sleep(3)  # 避免频率限制
        else:
            print("❓ 未知参数。使用方法:")
            print("  python dm_agent.py script  # 只测试剧本生成")
            print("  python dm_agent.py image   # 只测试图片生成")
            print("  python dm_agent.py all     # 测试所有功能")
    else:
        print("📝 默认测试剧本生成...")
        dm_agent = DMAgent()
        result = dm_agent.gen_script()
        if result:
            print("✅ 剧本生成成功!")
            print("💡 提示：使用 'python dm_agent.py image' 测试图片生成功能")
        else:
            print("❌ 剧本生成失败!")
