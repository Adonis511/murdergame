import openai
import json
from typing import List, Dict, Optional
from config import Config

class AIService:
    """AI聊天服务类"""
    
    def __init__(self, user=None):
        """初始化AI服务"""
        self.max_tokens = Config.OPENAI_MAX_TOKENS
        self.temperature = Config.OPENAI_TEMPERATURE
        
        # 如果提供了用户，使用用户的API配置
        if user and hasattr(user, 'api_key') and user.api_key:
            try:
                self.client = openai.OpenAI(
                    api_key=user.api_key,
                    base_url=user.api_base or Config.API_BASE
                )
                self.model = user.model or Config.MODEL
                print(f"✅ 使用用户 {user.username} 的API配置")
            except Exception as e:
                print(f"⚠️ 使用用户API配置失败: {e}")
                # 如果用户配置失败，使用默认配置
                self.client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
                self.model = Config.MODEL
        else:
            # 使用默认配置
            try:
                from models import SystemConfig
                api_key = SystemConfig.get_config('api_key') or Config.API_KEY
                api_base = SystemConfig.get_config('api_base') or Config.API_BASE
                
                self.client = openai.OpenAI(
                    api_key=api_key,
                    base_url=api_base
                )
                self.model = SystemConfig.get_config('model') or Config.MODEL
                print("⚠️ 使用全局API配置")
            except Exception as e:
                # 如果无法从数据库读取，使用默认配置
                print(f"⚠️ 从数据库读取API配置失败，使用默认配置: {e}")
                self.client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
                self.model = Config.MODEL
        
        # 系统提示词
        self.system_prompt = """你是一个友好、有帮助的AI助手。你的回答应该：
1. 准确、有用、富有洞察力
2. 支持Markdown格式输出
3. 在适当的时候使用代码块、列表、强调等格式
4. 保持对话的连贯性和上下文理解
5. 用中文回答（除非用户特别要求其他语言）

请根据用户的消息提供有帮助的回复。"""
    
    def generate_response(self, user_message: str, chat_history: List[Dict] = None) -> str:
        """
        生成AI回复
        
        Args:
            user_message (str): 用户消息
            chat_history (List[Dict], optional): 聊天历史记录
            
        Returns:
            str: AI生成的回复
        """
        try:
            # 构建消息列表
            messages = [{"role": "system", "content": self.system_prompt}]
            
            # 添加聊天历史（最近几条）
            if chat_history:
                for msg in chat_history[-10:]:  # 只保留最近10条消息作为上下文
                    if msg.get('message_type') == 'user':
                        messages.append({"role": "user", "content": msg.get('content', '')})
                    elif msg.get('message_type') == 'bot':
                        messages.append({"role": "assistant", "content": msg.get('content', '')})
            
            # 添加当前用户消息
            messages.append({"role": "user", "content": user_message})
            
            # 调用OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
            
            # 提取回复内容
            ai_reply = response.choices[0].message.content.strip()
            
            return ai_reply
            
        except openai.RateLimitError:
            return "**API调用频率限制**\n\n抱歉，当前API调用过于频繁，请稍后再试。"
            
        except openai.AuthenticationError:
            return "**API认证错误**\n\n抱歉，OpenAI API密钥无效或已过期。请检查配置。"
            
        except openai.APIError as e:
            return f"**API服务错误**\n\n抱歉，OpenAI服务暂时不可用：{str(e)}"
            
        except Exception as e:
            return f"**系统错误**\n\n抱歉，生成回复时发生错误：{str(e)}"
    
    def generate_smart_response(self, user_message: str, user_info: Dict = None) -> str:
        """
        生成智能回复（包含用户信息上下文）
        
        Args:
            user_message (str): 用户消息
            user_info (Dict, optional): 用户信息
            
        Returns:
            str: AI生成的回复
        """
        try:
            # 构建增强的系统提示词
            enhanced_prompt = self.system_prompt
            
            if user_info:
                enhanced_prompt += f"\n\n当前用户信息：昵称是{user_info.get('nickname', '用户')}，这是有帮助的上下文信息。"
            
            messages = [
                {"role": "system", "content": enhanced_prompt},
                {"role": "user", "content": user_message}
            ]
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"**生成回复失败**\n\n抱歉，无法生成智能回复：{str(e)}"
    
    def analyze_message_intent(self, message: str) -> Dict:
        """
        分析消息意图
        
        Args:
            message (str): 用户消息
            
        Returns:
            Dict: 分析结果
        """
        try:
            prompt = f"""请分析以下用户消息的意图，返回JSON格式：
消息："{message}"

请返回：
{{
    "intent": "意图类型（问题/聊天/请求帮助/代码相关等）",
    "confidence": "置信度(0-1)",
    "keywords": ["关键词列表"],
    "suggested_response_type": "建议回复类型（详细解答/简短回复/代码示例等）"
}}"""

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.3
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            return {
                "intent": "unknown",
                "confidence": 0.5,
                "keywords": [],
                "suggested_response_type": "standard",
                "error": str(e)
            }
    
    def test_connection(self) -> Dict:
        """
        测试AI服务连接
        
        Returns:
            Dict: 测试结果
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            
            return {
                "status": "success",
                "message": "AI服务连接正常",
                "model": self.model,
                "response": response.choices[0].message.content
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"AI服务连接失败：{str(e)}",
                "model": self.model
            }

# 创建全局AI服务实例
ai_service = AIService()