import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    """应用配置类"""
    
    # Flask基础配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here-change-in-production'
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///chat_app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # OpenAI API配置
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY') or 'sk-fb535aeda39f42d0b8f7039b98699374'
    MODEL = os.environ.get('OPENAI_MODEL') or 'qwen-plus-0806'
    MODEL_T2I = os.environ.get('MODEL_T2I') or 'wan2.2-t2i-flash'
    OPENAI_MAX_TOKENS = int(os.environ.get('AI_MAX_TOKENS', '1000'))
    OPENAI_TEMPERATURE = float(os.environ.get('AI_TEMPERATURE', '0.7'))
    
    # 聊天功能配置
    CHAT_HISTORY_LIMIT = int(os.environ.get('CHAT_HISTORY_LIMIT', '50'))
    MAX_MESSAGE_LENGTH = int(os.environ.get('MAX_MESSAGE_LENGTH', '2000'))
    
    # WTF表单配置
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600  # 1小时

    # LLM配置
    API_BASE = os.environ.get('API_BASE') or "https://dashscope.aliyuncs.com/compatible-mode/v1"
    API_KEY = os.environ.get('API_KEY') or "sk-fb535aeda39f42d0b8f7039b98699374"
    
    # 剧本杀游戏流程配置
    GAME_PLAYER_SPEAK_TIME = int(os.environ.get('GAME_PLAYER_SPEAK_TIME', '180'))  # 玩家发言阶段时间(秒) - 默认3分钟
    GAME_PLAYER_ANSWER_TIME = int(os.environ.get('GAME_PLAYER_ANSWER_TIME', '60'))  # 玩家回答阶段时间(秒) - 默认1分钟
    GAME_CHAPTER_CYCLES = int(os.environ.get('GAME_CHAPTER_CYCLES', '3'))  # 每章节循环次数 - 默认3次
    GAME_DM_SPEAK_DELAY = int(os.environ.get('GAME_DM_SPEAK_DELAY', '2'))  # DM发言延迟(秒) - 默认2秒
    GAME_AI_RESPONSE_DELAY = int(os.environ.get('GAME_AI_RESPONSE_DELAY', '3'))  # AI玩家回应延迟(秒) - 默认3秒
    
    # 默认剧本路径配置（如果为None或路径无效则使用AI生成）
    DEFAULT_SCRIPT_PATH = os.environ.get('DEFAULT_SCRIPT_PATH', 'log/250805154217')  # 例如: 'log/250805151240'