from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import hashlib
import json

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """用户模型"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), nullable=True, index=True)  # 移除unique约束，允许邮箱重复
    password_hash = db.Column(db.String(255), nullable=False)
    nickname = db.Column(db.String(80), nullable=True)
    avatar = db.Column(db.String(255), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    login_count = db.Column(db.Integer, default=0)
    
    # 用户级API配置
    api_key = db.Column(db.Text, nullable=True)
    api_base = db.Column(db.String(500), default='https://dashscope.aliyuncs.com/compatible-mode/v1')
    model = db.Column(db.String(100), default='qwen-plus-0806')
    model_t2i = db.Column(db.String(100), default='wan2.2-t2i-flash')
    api_configured_at = db.Column(db.DateTime, nullable=True)
    
    # 关联聊天消息
    messages = db.relationship('ChatMessage', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def __init__(self, username, email, password, nickname=None):
        self.username = username
        self.email = email
        self.set_password(password)
        self.nickname = nickname or username
        self.avatar = self.generate_avatar()
    
    def set_password(self, password):
        """设置密码哈希"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """检查密码"""
        return check_password_hash(self.password_hash, password)
    
    def generate_avatar(self):
        """生成头像URL（使用Gravatar）"""
        if self.email:
            email_hash = hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()
            return f"https://www.gravatar.com/avatar/{email_hash}?d=identicon&s=80"
        # 如果没有邮箱，使用用户名生成默认头像
        username_hash = hashlib.md5(self.username.lower().encode('utf-8')).hexdigest()
        return f"https://www.gravatar.com/avatar/{username_hash}?d=identicon&s=80"
    
    def update_login_info(self):
        """更新登录信息"""
        self.last_login = datetime.utcnow()
        self.login_count += 1
        db.session.commit()
    
    def has_valid_api_config(self):
        """检查用户是否有有效的API配置"""
        if not self.api_key:
            return False, '未配置API Key'
        
        # 简单验证API Key格式（阿里云百炼通常以sk-开头）
        if not self.api_key.startswith('sk-'):
            return False, 'API Key格式无效'
        
        if len(self.api_key) < 20:
            return False, 'API Key长度过短'
        
        return True, 'API配置有效'
    
    def update_api_config(self, api_key, api_base=None, model=None, model_t2i=None):
        """更新用户的API配置"""
        self.api_key = api_key
        if api_base:
            self.api_base = api_base
        if model:
            self.model = model
        if model_t2i:
            self.model_t2i = model_t2i
        self.api_configured_at = datetime.utcnow()
        db.session.commit()
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'nickname': self.nickname,
            'avatar': self.avatar,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'login_count': self.login_count
        }
    
    def __repr__(self):
        return f'<User {self.username}>'

class ChatMessage(db.Model):
    """聊天消息模型"""
    __tablename__ = 'chat_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    message_type = db.Column(db.String(20), default='user')  # user, bot, system
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    is_deleted = db.Column(db.Boolean, default=False)
    session_id = db.Column(db.String(255), nullable=True)  # 用于区分不同的聊天会话
    
    def __init__(self, user_id, content, message_type='user', session_id=None):
        self.user_id = user_id
        self.content = content
        self.message_type = message_type
        self.session_id = session_id
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'content': self.content,
            'message_type': self.message_type,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'user': {
                'username': self.user.username,
                'nickname': self.user.nickname,
                'avatar': self.user.avatar
            } if self.user else None
        }
    
    def __repr__(self):
        return f'<ChatMessage {self.id} by {self.user.username}>'

class LoginLog(db.Model):
    """登录日志模型"""
    __tablename__ = 'login_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    username = db.Column(db.String(80), nullable=False)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.Text, nullable=True)
    success = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    failure_reason = db.Column(db.String(255), nullable=True)
    
    def __init__(self, username, ip_address=None, user_agent=None, success=False, user_id=None, failure_reason=None):
        self.username = username
        self.ip_address = ip_address
        self.user_agent = user_agent
        self.success = success
        self.user_id = user_id
        self.failure_reason = failure_reason
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'ip_address': self.ip_address,
            'success': self.success,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'failure_reason': self.failure_reason
        }

def init_db(app):
    """初始化数据库"""
    db.init_app(app)
    
    with app.app_context():
        # 创建所有表
        db.create_all()
        
        # 创建默认管理员用户（如果不存在）
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(
                username='admin',
                email='admin@example.com',
                password='admin123',
                nickname='管理员'
            )
            admin_user.is_admin = True
            db.session.add(admin_user)
            
            # 创建测试用户（无邮箱测试）
            test_user = User(
                username='test',
                email=None,  # 测试无邮箱注册
                password='test123',
                nickname='测试用户'
            )
            db.session.add(test_user)
            
            db.session.commit()
            print("✅ 默认用户已创建:")
            print("   管理员 - 用户名: admin, 密码: admin123")
            print("   测试用户 - 用户名: test, 密码: test123")
        
        print("✅ 数据库初始化完成")


class SystemConfig(db.Model):
    """系统配置模型"""
    __tablename__ = 'system_configs'
    
    id = db.Column(db.Integer, primary_key=True)
    config_key = db.Column(db.String(100), unique=True, nullable=False, index=True)
    config_value = db.Column(db.Text, nullable=True)
    config_type = db.Column(db.String(50), default='string')  # string, json, integer, boolean
    description = db.Column(db.Text, nullable=True)
    is_encrypted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    def __init__(self, config_key, config_value, config_type='string', description=None, is_encrypted=False):
        self.config_key = config_key
        self.config_value = config_value
        self.config_type = config_type
        self.description = description
        self.is_encrypted = is_encrypted
    
    def get_value(self):
        """获取配置值，根据类型进行转换"""
        if not self.config_value:
            return None
        
        try:
            if self.config_type == 'json':
                return json.loads(self.config_value)
            elif self.config_type == 'integer':
                return int(self.config_value)
            elif self.config_type == 'boolean':
                return self.config_value.lower() in ('true', '1', 'yes')
            else:
                return self.config_value
        except (json.JSONDecodeError, ValueError):
            return self.config_value
    
    def set_value(self, value):
        """设置配置值，根据类型进行转换"""
        if value is None:
            self.config_value = None
        elif self.config_type == 'json':
            self.config_value = json.dumps(value, ensure_ascii=False)
        else:
            self.config_value = str(value)
        
        self.updated_at = datetime.utcnow()
    
    @staticmethod
    def get_config(key, default=None):
        """获取配置值的静态方法"""
        config = SystemConfig.query.filter_by(config_key=key).first()
        if config:
            return config.get_value()
        return default
    
    @staticmethod
    def set_config(key, value, config_type='string', description=None, user_id=None):
        """设置配置值的静态方法"""
        config = SystemConfig.query.filter_by(config_key=key).first()
        if config:
            config.set_value(value)
            config.updated_by = user_id
        else:
            config = SystemConfig(
                config_key=key,
                config_value=str(value) if value is not None else None,
                config_type=config_type,
                description=description
            )
            config.updated_by = user_id
            db.session.add(config)
        
        db.session.commit()
        return config