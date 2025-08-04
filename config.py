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
    OPENAI_MODEL = os.environ.get('AI_MODEL') or 'gpt-3.5-turbo'
    OPENAI_MAX_TOKENS = int(os.environ.get('AI_MAX_TOKENS', '1000'))
    OPENAI_TEMPERATURE = float(os.environ.get('AI_TEMPERATURE', '0.7'))
    
    # 聊天功能配置
    CHAT_HISTORY_LIMIT = int(os.environ.get('CHAT_HISTORY_LIMIT', '50'))
    MAX_MESSAGE_LENGTH = int(os.environ.get('MAX_MESSAGE_LENGTH', '2000'))
    
    # WTF表单配置
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600  # 1小时

    # LLM配置
    API_BASE="https://dashscope.aliyuncs.com/compatible-mode/v1"
    API_KEY="sk-fb535aeda39f42d0b8f7039b98699374"