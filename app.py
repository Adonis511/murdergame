from flask import Flask, render_template, send_from_directory, jsonify, request, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Optional
import os
import secrets
from datetime import datetime
from config import Config
from models import db, User, ChatMessage, LoginLog, init_db
from ai_service import ai_service

# 导入游戏API蓝图
try:
    from game_api import game_bp
    GAME_API_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ 游戏API模块导入失败: {e}")
    print("⚠️ 剧本杀游戏功能可能不可用")
    GAME_API_AVAILABLE = False

# 创建Flask应用实例
app = Flask(__name__, 
            template_folder='template',  # 模板文件夹
            static_folder='template',    # 静态文件夹
            static_url_path='/static')

# 配置应用
app.config.from_object(Config)

# 初始化扩展
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = '请先登录后访问此页面。'
login_manager.login_message_category = 'info'

# 注册游戏API蓝图
if GAME_API_AVAILABLE:
    app.register_blueprint(game_bp)
    print("✅ 剧本杀游戏API已注册")

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.before_request
def require_login():
    """在请求处理前检查登录状态"""
    # 定义不需要登录的端点
    exempt_endpoints = ['login', 'register', 'static', 'css_files', 'js_files', 'game_files']
    # API端点中的一些公开接口
    exempt_api_endpoints = ['api_status', 'get_config']
    
    # 如果当前端点在免登录列表中，直接通过
    if request.endpoint in exempt_endpoints or request.endpoint in exempt_api_endpoints:
        return
    
    # 如果用户未登录且不是注册相关请求，跳转到登录页面
    if not current_user.is_authenticated:
        return redirect(url_for('login', next=request.url))

# 表单类
class LoginForm(FlaskForm):
    """登录表单"""
    username = StringField('用户名', validators=[DataRequired(), Length(1, 80)])
    password = PasswordField('密码', validators=[DataRequired()])
    remember_me = BooleanField('记住我')
    submit = SubmitField('登录')

class RegisterForm(FlaskForm):
    """注册表单"""
    username = StringField('用户名', validators=[
        DataRequired(), 
        Length(3, 80, message='用户名长度应在3-80个字符之间')
    ])
    email = EmailField('邮箱', validators=[Optional(), Email()])
    nickname = StringField('昵称', validators=[Length(0, 80)])
    password = PasswordField('密码', validators=[
        DataRequired(), 
        Length(6, 128, message='密码长度应在6-128个字符之间')
    ])
    password2 = PasswordField('确认密码', validators=[
        DataRequired(), 
        EqualTo('password', message='两次输入的密码不一致')
    ])
    submit = SubmitField('注册')
    
    # 移除自动验证方法，在视图中手动检查
    # 这样可以避免表单验证与路由验证的冲突

class MessageForm(FlaskForm):
    """消息表单"""
    content = TextAreaField('消息内容', validators=[DataRequired(), Length(1, 2000)])
    submit = SubmitField('发送')

@app.route('/')
def index():
    """首页路由 - 重定向到相应页面"""
    # 如果用户未登录，跳转到登录页面
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    # 如果用户已登录，直接跳转到游戏页面
    return redirect(url_for('chat'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """登录路由"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        # 记录登录尝试
        log_entry = LoginLog(
            username=form.username.data,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            success=False
        )
        
        if user and user.check_password(form.password.data):
            if user.is_active:
                login_user(user, remember=form.remember_me.data)
                user.update_login_info()
                
                # 更新登录日志
                log_entry.success = True
                log_entry.user_id = user.id
                db.session.add(log_entry)
                db.session.commit()
                
                flash(f'欢迎回来，{user.nickname}！', 'success')
                
                # 重定向到用户想要访问的页面
                next_page = request.args.get('next')
                if not next_page or not next_page.startswith('/'):
                    next_page = url_for('chat')  # 登录后默认跳转到游戏页面
                return redirect(next_page)
            else:
                log_entry.failure_reason = '账户已被禁用'
                flash('您的账户已被禁用，请联系管理员。', 'error')
        else:
            log_entry.failure_reason = '用户名或密码错误'
            flash('用户名或密码错误。', 'error')
        
        db.session.add(log_entry)
        db.session.commit()
    
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """注册路由"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        try:
            # 只检查用户名是否已存在 - 邮箱允许重复或为空
            existing_user = User.query.filter_by(username=form.username.data).first()
            if existing_user:
                flash('注册失败：该探案者代号已被使用，请换一个代号。', 'error')
                return render_template('register.html', form=form)
            
            # 创建新用户
            user = User(
                username=form.username.data,
                email=form.email.data or None,  # 如果邮箱为空则存储为None
                password=form.password.data,
                nickname=form.nickname.data or form.username.data
            )
            
            db.session.add(user)
            db.session.commit()
            
            # 自动登录新注册的用户
            login_user(user, remember=False)
            user.update_login_info()
            
            # 记录登录日志
            log_entry = LoginLog(
                username=user.username,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent'),
                success=True,
                user_id=user.id
            )
            db.session.add(log_entry)
            db.session.commit()
            
            flash(f'欢迎加入探案团队，{user.nickname}！案件现场等待你的到来...', 'success')
            return redirect(url_for('chat'))
            
        except Exception as e:
            db.session.rollback()
            print(f"注册失败: {e}")
            flash(f'注册失败：创建探案者档案时发生错误，请稍后重试。如果问题持续存在，请联系管理员。', 'error')
            return render_template('register.html', form=form)
    else:
        # 表单验证失败时显示具体错误信息
        if request.method == 'POST':
            error_messages = []
            for field, errors in form.errors.items():
                for error in errors:
                    error_messages.append(f'{form[field].label.text}: {error}')
            
            if error_messages:
                flash(f'注册失败：{"; ".join(error_messages)}', 'error')
    
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    """登出路由"""
    username = current_user.username
    logout_user()
    flash(f'{username}，您已成功登出。', 'info')
    return redirect(url_for('index'))

@app.route('/admin/clear-all-sessions')
def clear_all_sessions():
    """清除所有用户登录状态（管理员功能）"""
    try:
        # 清除Flask-Login的记住我token
        from models import User
        users = User.query.all()
        for user in users:
            user.last_login = None
            user.is_active = True  # 确保账户是活跃的
        db.session.commit()
        
        # 清除当前session
        session.clear()
        
        return jsonify({
            'status': 'success',
            'message': f'已清除所有用户登录状态，共{len(users)}个用户账户已重置',
            'cleared_users': len(users)
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'清除登录状态失败: {str(e)}'
        }), 500

@app.route('/admin/reset-database')
def reset_database():
    """重置数据库（删除所有数据并重新创建表）"""
    try:
        # 清除当前session
        session.clear()
        
        # 删除所有表
        db.drop_all()
        
        # 重新创建表
        db.create_all()
        
        return jsonify({
            'status': 'success',
            'message': '数据库已重置，所有数据已清空，表结构已重新创建'
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'重置数据库失败: {str(e)}'
        }), 500

@app.route('/admin/list-users')
def list_users():
    """列出所有用户（调试用）"""
    try:
        from models import User
        users = User.query.all()
        user_list = []
        for user in users:
            user_list.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'nickname': user.nickname,
                'is_active': user.is_active,
                'created_at': user.created_at.isoformat() if user.created_at else None
            })
        
        return jsonify({
            'status': 'success',
            'message': f'共找到 {len(users)} 个用户',
            'users': user_list
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'获取用户列表失败: {str(e)}'
        }), 500

@app.route('/admin/delete-all-users')
def delete_all_users():
    """管理员删除所有用户（危险操作）"""
    try:
        from models import User
        user_count = User.query.count()
        User.query.delete()
        db.session.commit()
        session.clear()
        return jsonify({
            'status': 'success',
            'message': f'已删除所有 {user_count} 个用户账户，数据库已清空'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'删除用户失败: {str(e)}'
        }), 500

@app.route('/chat')
@login_required
def chat():
    """剧本杀游戏界面路由（新版本）"""
    return render_template('chat_v3.html', user=current_user)

@app.route('/chat-old')
@login_required
def chat_old():
    """剧本杀游戏界面路由（旧版本）"""
    return render_template('chat.html', user=current_user)

@app.route('/murder-mystery')
@login_required
def murder_mystery():
    """剧本杀游戏专用界面路由"""
    return render_template('murder_mystery_chat.html', user=current_user)

@app.route('/profile')
@login_required
def profile():
    """用户资料页面"""
    return render_template('profile.html', user=current_user)

@app.route('/api/status')
def api_status():
    """API状态检查"""
    return jsonify({
        'status': 'success',
        'message': '聊天API运行正常',
        'version': '1.0.0',
        'features': [
            'Markdown支持',
            '代码高亮',
            '实时消息',
            '文件导出'
        ]
    })

@app.route('/api/chat/send', methods=['POST'])
@login_required
def send_message():
    """发送消息API接口"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        session_id = data.get('session_id', None)
        
        if not message.strip():
            return jsonify({
                'status': 'error',
                'message': '消息不能为空'
            }), 400
        
        # 保存用户消息到数据库
        user_message = ChatMessage(
            user_id=current_user.id,
            content=message,
            message_type='user',
            session_id=session_id
        )
        db.session.add(user_message)
        
        # 获取用户的聊天历史作为上下文
        chat_history = ChatMessage.query.filter_by(
            user_id=current_user.id,
            session_id=session_id,
            is_deleted=False
        ).order_by(ChatMessage.timestamp.desc()).limit(10).all()
        
        # 转换为AI服务需要的格式
        history_data = [msg.to_dict() for msg in reversed(chat_history)]
        
        # 用户信息上下文
        user_info = {
            'nickname': current_user.nickname,
            'username': current_user.username
        }
        
        # 生成AI回复
        try:
            bot_reply = ai_service.generate_response(message, history_data)
        except Exception as e:
            print(f"AI服务错误: {e}")
            # 如果AI服务失败，使用备用回复
            bot_reply = f"**AI服务暂时不可用**\n\n抱歉，{current_user.nickname}，AI服务遇到了一些问题。您的消息是：\n\n> {message}\n\n请稍后再试，或联系管理员。"
        
        # 保存机器人回复到数据库
        bot_message = ChatMessage(
            user_id=current_user.id,
            content=bot_reply,
            message_type='bot',
            session_id=session_id
        )
        db.session.add(bot_message)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'data': {
                'user_message': user_message.to_dict(),
                'bot_reply': bot_message.to_dict(),
                'timestamp': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'处理消息时发生错误：{str(e)}'
        }), 500

@app.route('/api/chat/history')
@login_required
def get_chat_history():
    """获取聊天历史记录"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        session_id = request.args.get('session_id', None)
        
        query = ChatMessage.query.filter_by(user_id=current_user.id, is_deleted=False)
        
        if session_id:
            query = query.filter_by(session_id=session_id)
        
        messages = query.order_by(ChatMessage.timestamp.desc()).paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'status': 'success',
            'data': {
                'messages': [msg.to_dict() for msg in messages.items],
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': messages.total,
                    'pages': messages.pages,
                    'has_next': messages.has_next,
                    'has_prev': messages.has_prev
                }
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'获取历史记录失败：{str(e)}'
        }), 500

@app.route('/api/config')
def get_config():
    """获取聊天配置"""
    return jsonify({
        'status': 'success',
        'data': {
            'markdown_enabled': True,
            'code_highlight': True,
            'max_message_length': Config.MAX_MESSAGE_LENGTH,
            'ai_enabled': True,
            'ai_model': Config.MODEL,
            'game_api_enabled': GAME_API_AVAILABLE,
            'GAME_PLAYER_SPEAK_TIME': Config.GAME_PLAYER_SPEAK_TIME,
            'GAME_PLAYER_ANSWER_TIME': Config.GAME_PLAYER_ANSWER_TIME,
            'GAME_CHAPTER_CYCLES': Config.GAME_CHAPTER_CYCLES,
            'GAME_DM_SPEAK_DELAY': Config.GAME_DM_SPEAK_DELAY,
            'GAME_AI_RESPONSE_DELAY': Config.GAME_AI_RESPONSE_DELAY,
            'DEFAULT_SCRIPT_PATH': Config.DEFAULT_SCRIPT_PATH,
            'supported_languages': [
                'javascript', 'python', 'java', 'html', 'css', 
                'markdown', 'json', 'xml', 'sql', 'cpp', 'csharp'
            ],
            'tool_buttons': [
                {'id': 'clear', 'label': '清空', 'enabled': True},
                {'id': 'save', 'label': '保存', 'enabled': True},
                {'id': 'export', 'label': '导出', 'enabled': True},
                {'id': 'settings', 'label': '设置', 'enabled': True},
                {'id': 'help', 'label': '帮助', 'enabled': True},
                {'id': 'ai_test', 'label': 'AI测试', 'enabled': True},
                {'id': 'murder_mystery', 'label': '剧本杀', 'enabled': GAME_API_AVAILABLE}
            ]
        }
    })

@app.route('/api/ai/test')
@login_required
def test_ai_service():
    """测试AI服务连接"""
    result = ai_service.test_connection()
    return jsonify({
        'status': result['status'],
        'message': result['message'],
        'data': {
            'model': result['model'],
            'test_response': result.get('response', '')
        }
    })

@app.route('/api/ai/analyze', methods=['POST'])
@login_required  
def analyze_message():
    """分析消息意图"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        
        if not message.strip():
            return jsonify({
                'status': 'error',
                'message': '消息不能为空'
            }), 400
        
        analysis = ai_service.analyze_message_intent(message)
        
        return jsonify({
            'status': 'success',
            'data': analysis
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'分析失败：{str(e)}'
        }), 500

# 静态文件路由
@app.route('/css/<path:filename>')
def css_files(filename):
    """CSS文件路由"""
    return send_from_directory('template', filename)

@app.route('/js/<path:filename>')
def js_files(filename):
    """JavaScript文件路由"""
    return send_from_directory('template', filename)

@app.route('/log/<path:filename>')
def game_files(filename):
    """游戏文件路由（包括图片）"""
    return send_from_directory('log', filename)

# 错误处理
@app.errorhandler(404)
def not_found(error):
    """404错误处理"""
    return jsonify({
        'status': 'error',
        'message': '页面未找到',
        'code': 404
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """500错误处理"""
    return jsonify({
        'status': 'error',
        'message': '服务器内部错误',
        'code': 500
    }), 500

# 在模板中添加一些辅助函数
@app.context_processor
def utility_processor():
    """模板上下文处理器"""
    def format_datetime(dt):
        """格式化日期时间"""
        if dt:
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        return ''
    
    def format_date(dt):
        """格式化日期"""
        if dt:
            return dt.strftime('%Y-%m-%d')
        return ''
    
    def time_ago(dt):
        """相对时间"""
        if not dt:
            return ''
        
        now = datetime.utcnow()
        diff = now - dt
        
        if diff.days > 0:
            return f'{diff.days}天前'
        elif diff.seconds > 3600:
            return f'{diff.seconds // 3600}小时前'
        elif diff.seconds > 60:
            return f'{diff.seconds // 60}分钟前'
        else:
            return '刚刚'
    
    return dict(
        format_datetime=format_datetime,
        format_date=format_date,
        time_ago=time_ago,
        datetime=datetime
    )

# CORS支持（如果需要跨域访问）
@app.after_request
def after_request(response):
    """添加CORS头"""
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response

if __name__ == '__main__':
    # 确保template目录存在
    if not os.path.exists('template'):
        os.makedirs('template')
    
    # 初始化数据库
    init_db(app)
    
    print("🚀 聊天应用启动中...")
    print("=" * 50)
    print("📱 聊天界面: http://localhost:5000/chat")
    if GAME_API_AVAILABLE:
        print("🎭 剧本杀游戏: http://localhost:5000/murder-mystery")
    print("🔑 登录页面: http://localhost:5000/login")
    print("📝 注册页面: http://localhost:5000/register")
    print("🔧 API状态: http://localhost:5000/api/status")
    print("📋 应用首页: http://localhost:5000/")
    print("=" * 50)
    print("🔐 默认账户:")
    print("   管理员 - 用户名: admin, 密码: admin123")
    print("   测试用户 - 用户名: test, 密码: test123")
    print("=" * 50)
    print("按 Ctrl+C 停止服务器\n")
    
    # 启动Flask应用
    app.run(
        host='0.0.0.0',  # 允许外部访问
        port=5000,       # 端口号
        debug=True,      # 调试模式
        threaded=True    # 多线程支持
    )