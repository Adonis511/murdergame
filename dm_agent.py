from ai_service import AIService
from openai import OpenAI
from config import Config
import json
import time
import requests
import os
from datetime import datetime
from typing import List
from openai_utils import create_openai_client
from agent_logger import log_dm_speak_call
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
        self.client = create_openai_client()
    def gen_script(self):
        print("start generating script")
        start = time.time()
        completion = self.client.chat.completions.create(
        model=Config.MODEL,
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
              is_interject: bool = False, **kwargs) -> dict:
        """
        生成DM发言，支持工具调用
        
        Args:
            chapter: 章节（从0开始）
            script: 剧本内容
            chat_history: 聊天历史记录
            is_chapter_end: 是否是章节结束
            is_game_end: 是否是游戏结束
            is_interject: 是否是穿插发言
            **kwargs: 其他参数，如killer、truth_info、trigger_reason、guidance等
            
        Returns:
            dict: 包含发言内容和可能的工具调用信息
        """
        print(f"🎭 DM正在准备发言...")
        
        # 记录输入参数到日志
        input_params = {
            'chapter': chapter,
            'script': script,
            'chat_history': chat_history,
            'is_chapter_end': is_chapter_end,
            'is_game_end': is_game_end,
            'is_interject': is_interject,
            'kwargs': kwargs
        }
        
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
                'dm': script,
                'clues': kwargs.get('clues', [])
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
                model=Config.MODEL,
                temperature=0.8,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            response = completion.choices[0].message.content.strip()
            print(f"✅ DM {speak_type} 发言生成完成")
            
            # 解析响应，检查是否包含工具调用
            result = self._parse_dm_response(response, script_data, kwargs.get('base_path', ''))
            
            # 记录成功结果到日志
            log_dm_speak_call(input_params, result)
            
            return result
            
        except Exception as e:
            print(f"❌ DM发言生成失败: {e}")
            error_result = {
                'speech': self._get_speak_fallback(speak_type, chapter + 1),
                'tools': [],
                'success': False,
                'error': str(e)
            }
            
            # 记录错误结果到日志
            log_dm_speak_call(input_params, None, str(e))
            
            return error_result
    
    def _parse_dm_response(self, response: str, script_data: dict, base_path: str = "") -> dict:
        """
        解析DM响应，提取发言内容和工具调用
        
        Args:
            response: AI生成的响应
            script_data: 剧本数据
            base_path: 基础路径
            
        Returns:
            dict: 包含发言和工具调用信息
        """
        try:
            # 尝试解析JSON格式的响应
            if response.strip().startswith('{') and response.strip().endswith('}'):
                parsed = json.loads(response)
                speech = parsed.get('speech', '')
                tool_calls = parsed.get('tools', [])
            else:
                # 如果不是JSON格式，检查是否包含工具调用标记
                speech = response
                tool_calls = []
                
                # 检查是否包含线索展示请求
                if '[SHOW_CLUE:' in response:
                    import re
                    clue_matches = re.findall(r'\[SHOW_CLUE:(\d+)-(\d+)\]', response)
                    for chapter, clue_index in clue_matches:
                        tool_calls.append({
                            'type': 'show_clue',
                            'chapter': int(chapter),
                            'clue_index': int(clue_index)
                        })
                        # 从发言中移除工具调用标记
                        speech = speech.replace(f'[SHOW_CLUE:{chapter}-{clue_index}]', '')
                
                # 检查是否包含角色展示请求
                if '[SHOW_CHARACTER:' in response:
                    import re
                    char_matches = re.findall(r'\[SHOW_CHARACTER:([^\]]+)\]', response)
                    for character_name in char_matches:
                        tool_calls.append({
                            'type': 'show_character',
                            'character_name': character_name
                        })
                        # 从发言中移除工具调用标记
                        speech = speech.replace(f'[SHOW_CHARACTER:{character_name}]', '')
            
            # 执行工具调用
            executed_tools = []
            for tool_call in tool_calls:
                if tool_call['type'] == 'show_clue':
                    result = self.show_clue(
                        tool_call['chapter'], 
                        tool_call['clue_index'], 
                        script_data, 
                        base_path
                    )
                    executed_tools.append(result)
                elif tool_call['type'] == 'show_character':
                    result = self.show_character(
                        tool_call['character_name'], 
                        script_data, 
                        base_path
                    )
                    executed_tools.append(result)
            
            return {
                'speech': speech.strip(),
                'tools': executed_tools,
                'success': True,
                'raw_response': response
            }
            
        except Exception as e:
            print(f"❌ 响应解析失败: {e}")
            return {
                'speech': response,
                'tools': [],
                'success': False,
                'error': str(e),
                'raw_response': response
            }
    
    def _build_speak_system_prompt(self, speak_type: str) -> str:
        """构建speak方法的系统提示词"""
        base_prompt = """你是一名专业的剧本杀DM（游戏主持人），负责引导整个游戏进程。
你的发言应该：
1. 营造悬疑紧张的氛围
2. 推进剧情发展  
3. 引导玩家思考和互动
4. 保持角色扮演的沉浸感
5. 语言生动有趣，富有感染力

## 可用工具
你可以在发言中使用以下工具来增强游戏体验：

1. **展示线索** - 当需要向玩家展示具体线索时使用
   格式: [SHOW_CLUE:章节号-线索编号] (例如: [SHOW_CLUE:1-1] 表示第1章第1个线索)
   
2. **展示角色** - 当需要介绍角色或展示角色信息时使用  
   格式: [SHOW_CHARACTER:角色名称] (例如: [SHOW_CHARACTER:张三])

## 工具使用原则
- **线索展示是DM的核心职责**，每次发言都应积极考虑展示线索
- 线索展示工具适用于：引入新线索、强调重要证据、回顾关键线索、推进推理
- 角色展示工具适用于：角色介绍、嫌疑人分析、角色回顾
- **强烈建议**：在章节开始、章节结束、穿插发言时优先展示相关线索
- 工具调用应该与你的发言内容自然结合
- 一次发言中可以使用多个工具，鼓励适度使用增强游戏体验

## 输出格式
直接输出你的发言内容，在需要使用工具的地方插入工具调用标记。
例如：
"现在让我们来看看在案发现场发现的第一个重要线索。[SHOW_CLUE:1-1] 这把匕首上的血迹..."
或者：
"让我为大家介绍一下我们的主要嫌疑人。[SHOW_CHARACTER:李华] 李华先生，您能解释一下..."
"""

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
你需要让每次穿插发言都富有变化和惊喜：

**发言内容多样化要求：**
- 🎭 角色视角：以不同角色的视角描述当前情况
- 🔍 线索引导：巧妙引入新线索或重新审视已知线索  
- 🌟 剧情推进：推动故事向前发展，揭示新的情节点
- 💡 思路启发：给玩家提供新的推理思路或怀疑方向
- 🎪 氛围渲染：通过环境描写、心理描述增强沉浸感
- ⚡ 意外转折：适时抛出意想不到的信息或发现

**线索公布策略：**
- 每个章节必须逐步公布该章节的线索，不要一次性全部公布
- 在章节最后一轮讨论之前，确保该章节所有重要线索都已展示
- 根据玩家讨论的热度和方向，适时引入相关线索
- 用悬疑的方式展示线索，增加戏剧张力

**发言风格变化：**
- 有时像旁白叙述，有时像现场直播
- 可以模拟证人描述、警方报告、新闻播报等不同风格
- 适时加入环境音效描述、心理活动描述
- 保持语言生动有趣，避免单调重复

记住：你是游戏的灵魂，每一句话都应该让玩家更加投入游戏世界！"""

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
        
        # 构建可用线索信息
        clues = script_data.get('clues', [])
        available_clues = ""
        for i, chapter_clues in enumerate(clues[:current_chapter], 1):
            if chapter_clues:
                clue_list = []
                for j, clue in enumerate(chapter_clues, 1):
                    clue_list.append(f"  {i}-{j}: {clue}")
                available_clues += f"第{i}章线索:\n" + "\n".join(clue_list) + "\n"
        
        base_info = f"""## 剧本信息
**剧本标题**: {title}
**角色列表**: {', '.join(characters) if characters else '游戏角色'}
**当前章节**: 第{current_chapter}章 (共{total_chapters}章)
**当前章节内容**: {current_dm_content}

## 可展示的线索 (使用 [SHOW_CLUE:章节-编号])
{available_clues if available_clues else "暂无可展示线索"}

## 可展示的角色 (使用 [SHOW_CHARACTER:角色名])
{', '.join(characters) if characters else '暂无角色信息'}
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
4. 适当时可以展示角色介绍或新线索
5. 字数控制在200-400字之间

**工具使用建议**: {"必须展示主要角色，并强烈建议展示第1章的关键线索以引导玩家" if current_chapter == 1 else f"必须展示第{current_chapter}章的新线索，推荐展示重要角色"}
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
4. 适当时可以回顾关键线索或角色
5. 字数控制在300-500字之间

**工具使用建议**: 强烈建议展示本章发现的关键线索以加深印象，必要时展示重要嫌疑人角色
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
6. 适当时展示关键证据或凶手角色
7. 字数控制在500-800字之间

**工具使用建议**: 强烈建议展示凶手角色，以及最关键的证据线索，增强真相揭示的视觉效果
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
4. 必要时可以展示相关线索或角色信息
5. 字数控制在100-200字之间

**工具使用建议**: 优先考虑展示能推进当前讨论的关键线索，必要时展示相关角色信息
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
    
    def show_clue(self, chapter: int, clue_index: int, script_data: dict, base_path: str = "") -> dict:
        """
        展示指定章节的线索
        
        Args:
            chapter: 章节号（从1开始）
            clue_index: 线索索引（从1开始）
            script_data: 剧本数据
            base_path: 基础路径，用于构建图片URL
            
        Returns:
            dict: 包含线索信息的字典
        """
        try:
            # 获取线索描述
            clues = script_data.get('clues', [])
            if chapter <= len(clues) and clue_index <= len(clues[chapter - 1]):
                clue_description = clues[chapter - 1][clue_index - 1]
            else:
                clue_description = "线索描述未找到"
            
            # 构建图片路径
            image_filename = f"clue-ch{chapter}-{clue_index}.png"
            if base_path:
                image_url = f"{base_path}/imgs/{image_filename}"
            else:
                image_url = f"imgs/{image_filename}"
            
            return {
                'success': True,
                'chapter': chapter,
                'clue_index': clue_index,
                'description': clue_description,
                'image_url': image_url,
                'image_filename': image_filename,
                'tool_type': 'show_clue'
            }
            
        except Exception as e:
            print(f"❌ 展示线索失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'tool_type': 'show_clue'
            }

    def show_character(self, character_name: str, script_data: dict, base_path: str = "") -> dict:
        """
        展示指定角色信息
        
        Args:
            character_name: 角色名称
            script_data: 剧本数据
            base_path: 基础路径，用于构建图片URL
            
        Returns:
            dict: 包含角色信息的字典
        """
        try:
            # 检查角色是否存在
            characters = script_data.get('characters', [])
            if character_name not in characters:
                return {
                    'success': False,
                    'error': f"角色 {character_name} 不存在",
                    'tool_type': 'show_character'
                }
            
            # 构建图片路径
            image_filename = f"{character_name}.png"
            if base_path:
                image_url = f"{base_path}/imgs/{image_filename}"
            else:
                image_url = f"imgs/{image_filename}"
            
            return {
                'success': True,
                'character_name': character_name,
                'image_url': image_url,
                'image_filename': image_filename,
                'tool_type': 'show_character'
            }
            
        except Exception as e:
            print(f"❌ 展示角色失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'tool_type': 'show_character'
            }

    def _submit_image_task(self, prompt: str, size: str) -> str:
        """提交图片生成任务"""
        url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis"
        
        headers = {
            'X-DashScope-Async': 'enable',
            'Authorization': f'Bearer {Config.API_KEY}',
            'Content-Type': 'application/json'
        }
        
        data = {
            "model": Config.MODEL_T2I,
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
