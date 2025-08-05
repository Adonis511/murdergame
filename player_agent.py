from openai import OpenAI
from config import Config
from typing import List
from openai_utils import create_openai_client
class PlayerAgent:
    def __init__(self, name):
        self.name = name
        self.base_sys_prompt = """
        你是一名剧本杀玩家"{player_name}"，你需要完成以下工作：
        
        【重要角色设定】
        - 你的角色名是"{player_name}"
        - 你只能询问剧本中明确存在的其他角色，绝对不可以询问或提及不存在的角色
        - 在询问时必须使用剧本中提供的确切角色名字，不可编造任何人名
        - 如果不确定某个角色是否存在，就不要询问该角色
        
        【游戏规则】
        1. 根据剧本内容，在交谈阶段完成自己的任务。比如，如果你需要找出杀人凶手，你需要追问怀疑对象来判断对方是否为凶手，如果你就是凶手，可能需要隐藏自己
        2. 交谈过程有多次发言机会，每次发言你可以选择询问一个或多个其他玩家问题，也可以选择不发言。这些发言会被所有玩家听到。
        3. 如果被其他玩家询问到，需要回答问题，这个回答会被所有其他玩家听到，但不占用发言次数。如果不怕对方怀疑误会自己，也可以不发言
        4. 每个人的剧本都由4-6个章节构成，如果每个章节阅读完剧本都会有多次交谈机会用于完成任务。只有在dm宣布开启下一阶段时，你和其他玩家才有机会接触后续章节内容
        
        【严格要求】
        - 绝对不能询问"李华"、"王强"或任何不在剧本中出现的角色
        - 只能基于剧本内容和交谈历史进行推理和询问
        - 询问时必须使用剧本中明确提到的角色的确切姓名
        """
        self.client = create_openai_client()
    
    def _get_system_prompt(self):
        """获取格式化后的系统提示词"""
        return self.base_sys_prompt.format(player_name=self.name)
    def query(self, scripts: List[str], chat_history: str) -> dict:
        '''
        主动发言方法
        scripts: 剧本内容列表，表中每一项包含一个章节本人拿到的剧本
        chat_history: 交谈历史，markdown，包含所有玩家和dm的发言，以及线索等要素
        return: 字典格式 {"content": "发言内容", "query": {"人名": "问题"}}
        '''
        try:
            # 构建玩家当前已知的完整剧本信息
            current_script = self._build_current_script(scripts)
            
            # 分析当前状况和决策
            user_prompt = self._build_user_prompt(current_script, chat_history)
            
            # 调用AI生成回复
            completion = self.client.chat.completions.create(
                model="qwen-plus",
                temperature=0.8,  # 稍高的温度让角色更有个性
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            response = completion.choices[0].message.content.strip()
            
            # 尝试解析JSON响应
            try:
                import json
                # 如果响应被包在```json代码块中，需要先提取
                if response.startswith("```json"):
                    json_start = response.find("{")
                    json_end = response.rfind("}") + 1
                    if json_start != -1 and json_end != 0:
                        response = response[json_start:json_end]
                elif response.startswith("```"):
                    # 移除可能的其他代码块标记
                    response = response.replace("```", "").strip()
                
                # 解析JSON
                response_data = json.loads(response)
                
                # 验证JSON格式
                if not isinstance(response_data, dict):
                    raise ValueError("响应不是有效的JSON对象")
                
                # 确保包含必要字段
                if 'content' not in response_data:
                    response_data['content'] = "**[保持沉默]**"
                if 'query' not in response_data:
                    response_data['query'] = {}
                
                # 验证query字段格式
                if not isinstance(response_data['query'], dict):
                    response_data['query'] = {}
                
                return response_data
                
            except (json.JSONDecodeError, ValueError) as e:
                print(f"⚠️ {self.name}的JSON解析失败: {e}")
                # 返回默认格式
                return {
                    "content": response if response else "**[保持沉默]**",
                    "query": {}
                }
            
        except Exception as e:
            print(f"❌ {self.name}发言生成失败: {str(e)}")
            return {
                "content": f"**[{self.name}思考中...]**",
                "query": {}
            }
    
    def _build_current_script(self, scripts: List[str]) -> str:
        """构建当前玩家已知的完整剧本"""
        if not scripts:
            return "暂无剧本内容"
        
        script_content = f"## {self.name}的剧本信息\n\n"
        
        for i, chapter in enumerate(scripts, 1):
            script_content += f"### 第{i}章\n\n{chapter}\n\n"
        
        return script_content
    
    def _extract_characters_from_script(self, script_content: str) -> str:
        """从剧本中提取角色列表"""
        import re
        
        # 尝试多种模式来提取角色名
        character_patterns = [
            r'角色：([^，。\n]+)',
            r'角色名：([^，。\n]+)', 
            r'扮演：([^，。\n]+)',
            r'你是([^，。\n]+)',
            r'你扮演([^，。\n]+)',
            r'身份：([^，。\n]+)',
            r'【([^】]+)】',  # 中文方括号
            r'\[([^\]]+)\]',  # 英文方括号
        ]
        
        characters = set()
        for pattern in character_patterns:
            matches = re.findall(pattern, script_content)
            for match in matches:
                # 清理和过滤
                char_name = match.strip()
                if len(char_name) > 1 and len(char_name) < 10:  # 合理的名字长度
                    if not any(word in char_name for word in ['章节', '线索', '剧本', '背景', '故事']):
                        characters.add(char_name)
        
        # 排除自己
        characters.discard(self.name)
        
        if characters:
            char_list = "\n".join([f"- {char}" for char in sorted(characters)])
            return f"{char_list}\n\n**注意**：只能询问上述列表中的角色，绝对不能询问或提及不在此列表中的任何人（如李华、王强等）！"
        else:
            return "- 暂时无法从剧本中识别出其他角色\n\n**注意**：在没有明确角色信息时，不要询问任何人！"
    
    def _build_user_prompt(self, current_script: str, chat_history: str) -> str:
        """构建用户提示词"""
        # 从剧本中提取角色列表
        character_list = self._extract_characters_from_script(current_script)
        
        prompt = f"""作为玩家"{self.name}"，请根据以下信息决定你的下一步行动：

{current_script}

## 当前交谈历史
{chat_history if chat_history.strip() else "暂无交谈历史"}

## 【重要】可询问的角色列表
根据剧本，你只能询问以下角色（绝对不能询问任何其他人）：
{character_list}

## 行动指南
请根据你的剧本内容和当前交谈情况，决定你的下一步行动：

1. **分析情况**：
   - 根据剧本，你的目标是什么？
   - 当前交谈中透露了哪些重要信息？
   - 谁的发言值得注意？

2. **决策选择**：
   - **询问**：如果需要获取信息，可以向其他玩家提问（只能询问上述角色列表中的角色）
   - **陈述**：如果需要分享信息或为自己辩护
   - **分析**：如果需要分析已知线索
   - **沉默**：如果当前不适合发言

3. **输出要求**：
   - 必须返回JSON格式，包含以下字段：
     - `content`: 你的发言内容（markdown格式）
     - `query`: 你要询问的问题（字典格式：{{"人名": "问题内容"}}）
   - 保持角色一致性，符合你的身份和性格
   - 发言要自然流畅，像真人玩家一样
   - 询问要具体明确，在query字段中指定询问对象

## 输出格式示例
```json
{{
  "content": "我觉得我们需要更仔细地分析一下昨晚的时间线。根据我了解的情况...",
  "query": {{
    "角色A": "你说你昨晚在书房看书，具体是几点到几点？",
    "角色B": "你有注意到最近的异常行为吗？"
  }}
}}
```

如果不询问任何人，query字段留空：
```json
{{
  "content": "**[保持沉默]**",
  "query": {{}}
}}
```

请直接输出JSON格式的响应，不要添加任何解释："""

        return prompt
    
    def response(self, scripts: List[str], chat_history: str, query: str, query_player: str) -> str:
        '''
        被动回应方法，当被其他玩家询问时使用
        scripts: 剧本内容列表，表中每一项包含一个章节本人拿到的剧本
        chat_history: 交谈历史，markdown，包含所有玩家和dm的发言，以及线索等要素
        query: 被问到的具体问题（必填）
        query_player: 提问的玩家姓名（必填）
        return: 你的markdown格式回应
        '''
        try:
            # 构建玩家当前已知的完整剧本信息
            current_script = self._build_current_script(scripts)
            
            # 构建回应提示词
            response_prompt = self._build_response_prompt(current_script, chat_history, query, query_player)
            
            # 调用AI生成回复
            completion = self.client.chat.completions.create(
                model="qwen-plus",
                temperature=0.7,  # 回应时温度稍低，更加谨慎
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": response_prompt}
                ]
            )
            
            response = completion.choices[0].message.content.strip()
            
            # 确保返回合理的内容
            if not response or response.lower() in ['无', '不回答', '沉默', '']:
                return "**[选择不回答]**"
            
            return response
            
        except Exception as e:
            print(f"❌ {self.name}回应生成失败: {str(e)}")
            return f"**[{self.name}无法回应...]**"
    
    def _build_response_prompt(self, current_script: str, chat_history: str, query: str, query_player: str) -> str:
        """构建回应提示词"""
        
        # 构建询问信息部分
        query_section = f"""
## 被询问的具体问题
**提问者**: {query_player}
**问题内容**: {query}
"""
        
        prompt = f"""作为玩家"{self.name}"，你被其他玩家询问了问题，请根据以下信息给出回应：

{current_script}

## 当前交谈历史
{chat_history if chat_history.strip() else "暂无交谈历史"}
{query_section}
## 回应指南
请针对具体问题给出回应，分析时考虑：

1. **理解问题**：
   - 问题的核心意图是什么？
   - 问题涉及你剧本中的哪些信息？
   - 提问者可能想要获得什么信息？

2. **分析情况**：
   - 你与提问者的关系如何？
   - 这个问题对你是否有威胁性？
   - 回答会暴露你的什么秘密？

3. **决策回应**：
   - **直接回答**：如果问题安全且有利于你
   - **部分透露**：说一些真话但隐瞒关键信息
   - **巧妙回避**：转移话题或模糊回应
   - **反向询问**：通过反问获取对方信息
   - **拒绝回答**：如果问题过于敏感

4. **回应要求**：
   - 保持角色一致性和性格特点
   - 根据你的剧本身份调整回应策略
   - 回应要自然流畅，像真实玩家的表达
   - 使用markdown格式增强表达效果
   - 针对具体问题给出有针对性的回答

请直接给出你的回应内容，如果选择不回答，请返回"**[选择不回答]**"："""

        return prompt
