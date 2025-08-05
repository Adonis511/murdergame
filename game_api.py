"""
剧本杀游戏后端API接口
与test_ai_game_simulation.py中的游戏流程对接
"""

from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
import os
import json
import time
from datetime import datetime
import traceback

# 导入游戏相关模块
try:
    from game import Game
    from player_agent import PlayerAgent
    from dm_agent import DMAgent
except ImportError as e:
    print(f"导入游戏模块失败: {e}")
    print("请确保game.py、player_agent.py、dm_agent.py等文件存在")

# 创建蓝图
game_bp = Blueprint('game', __name__, url_prefix='/api/game')

# 全局游戏会话存储
ACTIVE_GAMES = {}
PLAYER_SESSIONS = {}

class GameSession:
    """游戏会话管理"""
    
    def __init__(self, session_id, game_path=None):
        self.session_id = session_id
        self.game_path = game_path
        self.created_at = datetime.now()
        self.players = {}  # user_id -> character_name
        self.current_chapter = 0
        self.game_state = 'waiting'  # waiting, generating, character_select, playing, finished
        self.chat_history = ""
        self.game_instance = None
        self.ai_players = {}  # character_name -> PlayerAgent
        
        # 进度跟踪
        self.script_ready = False
        self.images_ready = False
        self.game_ready = False
        
    def add_player(self, user_id, character_name):
        """添加玩家到游戏"""
        self.players[user_id] = character_name
        
    def get_player_character(self, user_id):
        """获取玩家角色"""
        return self.players.get(user_id)
        
    def to_dict(self):
        """转换为字典"""
        return {
            'session_id': self.session_id,
            'game_path': self.game_path,
            'created_at': self.created_at.isoformat(),
            'players': self.players,
            'current_chapter': self.current_chapter,
            'game_state': self.game_state,
            'total_chapters': self.get_total_chapters() if self.game_instance else 0
        }
        
    def get_total_chapters(self):
        """获取总章节数"""
        if self.game_instance:
            return self.game_instance.get_total_chapters()
        return 0

@game_bp.route('/new', methods=['POST'])
@login_required
def create_new_game():
    """创建新游戏"""
    try:
        data = request.get_json() or {}
        generate_images = data.get('generate_images', True)  # 默认生成图片
        wait_for_completion = data.get('wait_for_completion', True)
        
        print(f"🎮 用户 {current_user.nickname} 请求创建新游戏")
        print(f"🖼️ 生成图片: {generate_images}")
        print(f"⏳ 等待完成: {wait_for_completion}")
        
        # 创建新游戏实例
        game = Game(script_path=None, generate_images=generate_images)
        
        # 生成会话ID
        session_id = f"game_{int(time.time())}_{current_user.id}"
        
        # 创建游戏会话
        session = GameSession(session_id, game.game_dir)
        session.game_instance = game
        session.game_state = 'character_select'
        
        # 保存到全局会话
        ACTIVE_GAMES[session_id] = session
        
        # 获取角色列表
        characters = game.script.get('characters', [])
        character_list = []
        
        for char_name in characters:
            # 检查是否有角色图片
            char_image = None
            if generate_images:
                import glob
                image_pattern = os.path.join(game.imgs_dir, f"character_{char_name}.*")
                image_files = glob.glob(image_pattern)
                if image_files:
                    # 返回相对路径
                    char_image = os.path.relpath(image_files[0], '.').replace('\\', '/')
            
            character_list.append({
                'name': char_name,
                'description': f"一个神秘的角色：{char_name}，等待你来揭开面纱...",
                'image': char_image
            })
        
        print(f"✅ 新游戏创建成功: {session_id}")
        print(f"📂 游戏目录: {game.game_dir}")
        print(f"👥 角色数量: {len(character_list)}")
        
        # 设置游戏状态
        if generate_images and wait_for_completion:
            session.game_state = 'generating'
            session.script_ready = True
            session.images_ready = generate_images and os.path.exists(game.imgs_dir) and len(os.listdir(game.imgs_dir)) > 0
            session.game_ready = session.images_ready or not generate_images
        else:
            session.game_state = 'ready'
            session.script_ready = True
            session.images_ready = True
            session.game_ready = True
        
        return jsonify({
            'status': 'success',
            'message': '新游戏创建成功',
            'data': {
                'game_session': session_id,
                'story_title': game.script.get('title', '未命名剧本'),
                'story_subtitle': '一个充满谜团的故事即将开始...',
                'characters': character_list,
                'total_chapters': game.get_total_chapters(),
                'game_path': game.game_dir,
                'wait_for_completion': wait_for_completion,
                'generate_images': generate_images
            }
        })
        
    except Exception as e:
        print(f"❌ 创建新游戏失败: {e}")
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': f'创建新游戏失败: {str(e)}'
        }), 500

@game_bp.route('/list', methods=['GET'])
@login_required
def list_games():
    """获取可用游戏列表"""
    try:
        games = []
        log_dir = 'log'
        
        if os.path.exists(log_dir):
            for item in os.listdir(log_dir):
                item_path = os.path.join(log_dir, item)
                if os.path.isdir(item_path):
                    # 检查是否是有效的游戏目录
                    script_file = os.path.join(item_path, 'script.json')
                    if os.path.exists(script_file):
                        try:
                            with open(script_file, 'r', encoding='utf-8') as f:
                                script = json.load(f)
                            
                            games.append({
                                'path': item_path,
                                'title': script.get('title', '未命名剧本'),
                                'characters': script.get('characters', []),
                                'chapters': len(script.get('chapters', [])),
                                'created_at': datetime.fromtimestamp(
                                    os.path.getctime(item_path)
                                ).isoformat()
                            })
                        except Exception as e:
                            print(f"解析游戏 {item_path} 失败: {e}")
                            continue
        
        # 按创建时间倒序排列
        games.sort(key=lambda x: x['created_at'], reverse=True)
        
        return jsonify({
            'status': 'success',
            'data': {
                'games': games
            }
        })
        
    except Exception as e:
        print(f"❌ 获取游戏列表失败: {e}")
        return jsonify({
            'status': 'error',
            'message': f'获取游戏列表失败: {str(e)}'
        }), 500

@game_bp.route('/load', methods=['POST'])
@login_required
def load_existing_game():
    """加载现有游戏"""
    try:
        data = request.get_json()
        game_path = data.get('game_path')
        
        if not game_path or not os.path.exists(game_path):
            return jsonify({
                'status': 'error',
                'message': '游戏路径不存在'
            }), 400
        
        print(f"📂 用户 {current_user.nickname} 请求加载游戏: {game_path}")
        
        # 加载游戏实例
        game = Game(script_path=game_path, generate_images=False)
        
        # 生成会话ID
        session_id = f"game_{int(time.time())}_{current_user.id}"
        
        # 创建游戏会话
        session = GameSession(session_id, game_path)
        session.game_instance = game
        session.game_state = 'character_select'
        
        # 保存到全局会话
        ACTIVE_GAMES[session_id] = session
        
        # 获取角色列表（包含图片）
        characters = game.script.get('characters', [])
        character_list = []
        
        for char_name in characters:
            # 检查是否有角色图片
            char_image = None
            if hasattr(game, 'imgs_dir') and os.path.exists(game.imgs_dir):
                import glob
                image_pattern = os.path.join(game.imgs_dir, f"character_{char_name}.*")
                image_files = glob.glob(image_pattern)
                if image_files:
                    # 返回相对路径
                    char_image = os.path.relpath(image_files[0], '.').replace('\\', '/')
            
            character_list.append({
                'name': char_name,
                'description': f"角色：{char_name}",
                'image': char_image
            })
        
        print(f"✅ 游戏加载成功: {session_id}")
        
        return jsonify({
            'status': 'success',
            'message': '游戏加载成功',
            'data': {
                'game_session': session_id,
                'story_title': game.script.get('title', '未命名剧本'),
                'story_subtitle': '继续你的推理之旅...',
                'characters': character_list,
                'total_chapters': game.get_total_chapters()
            }
        })
        
    except Exception as e:
        print(f"❌ 加载游戏失败: {e}")
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': f'加载游戏失败: {str(e)}'
        }), 500

@game_bp.route('/join', methods=['POST'])
@login_required
def join_game():
    """加入游戏（选择角色）"""
    try:
        data = request.get_json()
        session_id = data.get('game_session')
        character_name = data.get('character_name')
        
        if not session_id or session_id not in ACTIVE_GAMES:
            return jsonify({
                'status': 'error',
                'message': '游戏会话不存在'
            }), 400
        
        session = ACTIVE_GAMES[session_id]
        
        # 检查角色是否已被选择
        if character_name in session.players.values():
            return jsonify({
                'status': 'error',
                'message': '该角色已被其他玩家选择'
            }), 400
        
        # 添加玩家到游戏
        session.add_player(current_user.id, character_name)
        session.game_state = 'playing'
        
        # 为角色创建AI代理（用于与DM交互）
        try:
            session.ai_players[character_name] = PlayerAgent(character_name)
        except Exception as e:
            print(f"创建角色AI代理失败: {e}")
        
        # 记录玩家会话
        PLAYER_SESSIONS[current_user.id] = session_id
        
        print(f"✅ 用户 {current_user.nickname} 加入游戏 {session_id}，角色: {character_name}")
        
        return jsonify({
            'status': 'success',
            'message': '成功加入游戏',
            'data': {
                'character_name': character_name,
                'session_id': session_id,
                'game_state': session.game_state
            }
        })
        
    except Exception as e:
        print(f"❌ 加入游戏失败: {e}")
        return jsonify({
            'status': 'error',
            'message': f'加入游戏失败: {str(e)}'
        }), 500

@game_bp.route('/status/<session_id>', methods=['GET'])
@login_required
def get_game_status(session_id):
    """获取游戏状态"""
    try:
        if session_id not in ACTIVE_GAMES:
            return jsonify({
                'status': 'error',
                'message': '游戏会话不存在'
            }), 404
        
        session = ACTIVE_GAMES[session_id]
        
        return jsonify({
            'status': 'success',
            'data': session.to_dict()
        })
        
    except Exception as e:
        print(f"❌ 获取游戏状态失败: {e}")
        return jsonify({
            'status': 'error',
            'message': f'获取游戏状态失败: {str(e)}'
        }), 500

@game_bp.route('/progress/<session_id>', methods=['GET'])
@login_required
def get_game_progress(session_id):
    """获取游戏生成进度"""
    try:
        if session_id not in ACTIVE_GAMES:
            return jsonify({
                'status': 'error',
                'message': '游戏会话不存在'
            }), 404
        
        session = ACTIVE_GAMES[session_id]
        game = session.game_instance
        
        # 检查实际文件状态
        if game and os.path.exists(game.imgs_dir):
            image_files = [f for f in os.listdir(game.imgs_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
            session.images_ready = len(image_files) > 0
            
            # 如果图片已准备好，标记游戏为就绪
            if session.images_ready and session.script_ready:
                session.game_ready = True
                session.game_state = 'ready'
        
        # 获取角色列表（包含图片）
        characters = []
        if game and session.script_ready:
            for char_name in game.script.get('characters', []):
                char_image = None
                if session.images_ready:
                    import glob
                    image_pattern = os.path.join(game.imgs_dir, f"character_{char_name}.*")
                    image_files = glob.glob(image_pattern)
                    if image_files:
                        char_image = os.path.relpath(image_files[0], '.').replace('\\', '/')
                
                characters.append({
                    'name': char_name,
                    'description': f"角色：{char_name}",
                    'image': char_image
                })
        
        return jsonify({
            'status': 'success',
            'data': {
                'script_ready': session.script_ready,
                'images_ready': session.images_ready,
                'game_ready': session.game_ready,
                'game_state': session.game_state,
                'characters': characters
            }
        })
        
    except Exception as e:
        print(f"❌ 获取游戏进度失败: {e}")
        return jsonify({
            'status': 'error',
            'message': f'获取游戏进度失败: {str(e)}'
        }), 500

@game_bp.route('/script/<session_id>/<character_name>', methods=['GET'])
@login_required
def get_character_script(session_id, character_name):
    """获取角色剧本（只返回当前章节及之前的章节）"""
    try:
        if session_id not in ACTIVE_GAMES:
            return jsonify({
                'status': 'error',
                'message': '游戏会话不存在'
            }), 404
        
        session = ACTIVE_GAMES[session_id]
        game = session.game_instance
        
        if not game:
            return jsonify({
                'status': 'error',
                'message': '游戏实例不存在'
            }), 400
        
        # 获取角色完整剧本
        full_character_script = game.script.get(character_name, [])
        
        # 根据当前章节过滤剧本内容
        current_chapter = session.current_chapter
        available_script = []
        
        # 只提供当前章节及之前的章节
        for i in range(min(current_chapter, len(full_character_script))):
            available_script.append(full_character_script[i])
        
        # 如果当前章节为0，说明游戏还没开始，不提供任何剧本内容
        if current_chapter == 0:
            available_script = []
        
        return jsonify({
            'status': 'success',
            'data': {
                'character_name': character_name,
                'script': available_script,
                'current_chapter': current_chapter,
                'available_chapters': len(available_script),
                'total_chapters': len(full_character_script)
            }
        })
        
    except Exception as e:
        print(f"❌ 获取角色剧本失败: {e}")
        return jsonify({
            'status': 'error',
            'message': f'获取角色剧本失败: {str(e)}'
        }), 500

@game_bp.route('/images/<session_id>', methods=['GET'])
@login_required  
def get_game_images(session_id):
    """获取游戏图片列表"""
    try:
        if session_id not in ACTIVE_GAMES:
            return jsonify({
                'status': 'error',
                'message': '游戏会话不存在'
            }), 404
        
        session = ACTIVE_GAMES[session_id]
        game = session.game_instance
        
        if not game or not os.path.exists(game.imgs_dir):
            return jsonify({
                'status': 'success',
                'data': {
                    'character_images': {},
                    'clue_images': {}
                }
            })
        
        # 获取角色图片
        character_images = {}
        for char_name in game.script.get('characters', []):
            import glob
            image_pattern = os.path.join(game.imgs_dir, f"character_{char_name}.*")
            image_files = glob.glob(image_pattern)
            if image_files:
                character_images[char_name] = os.path.relpath(image_files[0], '.').replace('\\', '/')
        
        # 获取线索图片
        clue_images = {}
        clue_pattern = os.path.join(game.imgs_dir, "clue_*")
        clue_files = glob.glob(clue_pattern)
        for i, clue_file in enumerate(clue_files):
            clue_images[f'clue_{i+1}'] = os.path.relpath(clue_file, '.').replace('\\', '/')
        
        return jsonify({
            'status': 'success',
            'data': {
                'character_images': character_images,
                'clue_images': clue_images,
                'total_images': len(character_images) + len(clue_images)
            }
        })
        
    except Exception as e:
        print(f"❌ 获取游戏图片失败: {e}")
        return jsonify({
            'status': 'error',
            'message': f'获取游戏图片失败: {str(e)}'
        }), 500

@game_bp.route('/characters/<session_id>', methods=['GET'])
@login_required
def get_all_characters(session_id):
    """获取所有角色信息（包括图片）"""
    try:
        if session_id not in ACTIVE_GAMES:
            return jsonify({
                'status': 'error',
                'message': '游戏会话不存在'
            }), 404
        
        session = ACTIVE_GAMES[session_id]
        game = session.game_instance
        
        if not game:
            return jsonify({
                'status': 'error',
                'message': '游戏实例不存在'
            }), 400
        
        characters = []
        character_names = game.script.get('characters', [])
        
        for char_name in character_names:
            # 检查是否有角色图片
            char_image = None
            if hasattr(game, 'imgs_dir') and os.path.exists(game.imgs_dir):
                import glob
                image_pattern = os.path.join(game.imgs_dir, f"character_{char_name}.*")
                image_files = glob.glob(image_pattern)
                if image_files:
                    char_image = os.path.relpath(image_files[0], '.').replace('\\', '/')
            
            # 检查角色是否被玩家选择
            player_id = None
            is_ai = True
            for uid, selected_char in session.players.items():
                if selected_char == char_name:
                    player_id = uid
                    is_ai = False
                    break
            
            # 检查是否是当前用户的角色
            is_current_user = (player_id == current_user.id) if player_id else False
            
            characters.append({
                'name': char_name,
                'image': char_image,
                'player_id': player_id,
                'is_ai': is_ai,
                'is_current_user': is_current_user,
                'status': 'active' if player_id or is_ai else 'available'
            })
        
        return jsonify({
            'status': 'success',
            'data': {
                'characters': characters,
                'total_characters': len(characters),
                'human_players': len([c for c in characters if not c['is_ai']]),
                'ai_players': len([c for c in characters if c['is_ai']])
            }
        })
        
    except Exception as e:
        print(f"❌ 获取角色信息失败: {e}")
        return jsonify({
            'status': 'error',
            'message': f'获取角色信息失败: {str(e)}'
        }), 500

@game_bp.route('/chapter/start', methods=['POST'])
@login_required
def start_chapter():
    """开始章节"""
    try:
        data = request.get_json()
        session_id = data.get('game_session')
        chapter_num = data.get('chapter_num')
        character_name = data.get('character_name')
        
        if session_id not in ACTIVE_GAMES:
            return jsonify({
                'status': 'error',
                'message': '游戏会话不存在'
            }), 400
        
        session = ACTIVE_GAMES[session_id]
        game = session.game_instance
        
        if not game:
            return jsonify({
                'status': 'error',
                'message': '游戏实例不存在'
            }), 400
        
        print(f"📖 开始第{chapter_num}章，玩家: {character_name}")
        
        # 调用DM开始章节
        dm_result = game.start_chapter(chapter_num, session.chat_history)
        
        # 获取角色剧本
        character_script = None
        if character_name in game.script.get('characters', []):
            character_chapters = game.script.get(character_name, [])
            if chapter_num <= len(character_chapters):
                character_script = character_chapters[chapter_num - 1]
        
        session.current_chapter = chapter_num
        
        return jsonify({
            'status': 'success',
            'data': {
                'chapter_num': chapter_num,
                'dm_speech': dm_result.get('speech') if dm_result else None,
                'dm_tools': dm_result.get('tools', []) if dm_result else [],
                'character_script': character_script
            }
        })
        
    except Exception as e:
        print(f"❌ 开始章节失败: {e}")
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': f'开始章节失败: {str(e)}'
        }), 500

@game_bp.route('/message', methods=['POST'])
@login_required
def send_game_message():
    """发送游戏消息"""
    try:
        data = request.get_json()
        session_id = data.get('game_session')
        character_name = data.get('character_name')
        message = data.get('message')
        message_type = data.get('message_type', 'speak')  # speak, ask, whisper, action
        target_player = data.get('target_player')
        chapter = data.get('chapter', 1)
        
        if session_id not in ACTIVE_GAMES:
            return jsonify({
                'status': 'error',
                'message': '游戏会话不存在'
            }), 400
        
        session = ACTIVE_GAMES[session_id]
        game = session.game_instance
        
        # 更新聊天历史
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        if message_type == 'ask' and target_player:
            session.chat_history += f"\n\n### {character_name} ({timestamp})\n询问 @{target_player}: {message}\n"
        elif message_type == 'whisper' and target_player:
            session.chat_history += f"\n\n### {character_name} ({timestamp})\n私聊 @{target_player}: {message}\n"
        elif message_type == 'action':
            session.chat_history += f"\n\n### {character_name} ({timestamp})\n*{message}*\n"
        else:
            session.chat_history += f"\n\n### {character_name} ({timestamp})\n{message}\n"
        
        responses = []
        dm_response = None
        
        # 处理询问类型的消息
        if message_type == 'ask' and target_player:
            # 模拟AI角色回应
            if target_player in session.ai_players:
                try:
                    agent = session.ai_players[target_player]
                    # 获取目标角色的剧本
                    target_scripts = []
                    if target_player in game.script.get('characters', []):
                        target_character_chapters = game.script.get(target_player, [])
                        if chapter <= len(target_character_chapters):
                            target_scripts = [target_character_chapters[chapter - 1]]
                    
                    ai_response = agent.response(target_scripts, session.chat_history, message, character_name)
                    
                    if ai_response:
                        responses.append({
                            'character': target_player,
                            'content': ai_response,
                            'type': 'response'
                        })
                        
                        # 更新聊天历史
                        session.chat_history += f"\n\n### {target_player} ({timestamp})\n回应 @{character_name}: {ai_response}\n"
                        
                except Exception as e:
                    print(f"AI角色回应失败: {e}")
        
        # 有概率触发DM回应
        import random
        if random.random() < 0.3:  # 30%概率DM参与
            try:
                # 这里可以调用DM的回应逻辑
                dm_response = f"*游戏主持观察着场上的情况，记录下了这次互动...*"
            except Exception as e:
                print(f"DM回应失败: {e}")
        
        return jsonify({
            'status': 'success',
            'data': {
                'message_sent': True,
                'responses': responses,
                'dm_response': dm_response
            }
        })
        
    except Exception as e:
        print(f"❌ 发送游戏消息失败: {e}")
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': f'发送消息失败: {str(e)}'
        }), 500

@game_bp.route('/end/<session_id>', methods=['POST'])
@login_required
def end_game(session_id):
    """结束游戏"""
    try:
        if session_id not in ACTIVE_GAMES:
            return jsonify({
                'status': 'error',
                'message': '游戏会话不存在'
            }), 404
        
        session = ACTIVE_GAMES[session_id]
        game = session.game_instance
        
        # 调用游戏结束逻辑
        if game:
            final_result = game.end_game(
                session.chat_history, 
                "游戏结束", 
                "感谢所有玩家的参与！"
            )
        
        # 清理会话
        del ACTIVE_GAMES[session_id]
        
        # 清理玩家会话记录
        for user_id in session.players.keys():
            if user_id in PLAYER_SESSIONS:
                del PLAYER_SESSIONS[user_id]
        
        return jsonify({
            'status': 'success',
            'message': '游戏已结束',
            'data': {
                'final_result': final_result if 'final_result' in locals() else None
            }
        })
        
    except Exception as e:
        print(f"❌ 结束游戏失败: {e}")
        return jsonify({
            'status': 'error',
            'message': f'结束游戏失败: {str(e)}'
        }), 500

@game_bp.route('/player_action', methods=['POST'])
@login_required
def handle_player_action():
    """处理玩家行动（发言+询问）"""
    try:
        data = request.get_json()
        session_id = data.get('game_session')
        character_name = data.get('character_name')
        content = data.get('content', '')
        queries = data.get('queries', {})
        chapter = data.get('chapter', 1)
        cycle = data.get('cycle', 1)
        
        if session_id not in ACTIVE_GAMES:
            return jsonify({
                'status': 'error',
                'message': '游戏会话不存在'
            }), 404
        
        session = ACTIVE_GAMES[session_id]
        
        # 记录玩家行动
        action_log = {
            'type': 'player_action',
            'character': character_name,
            'content': content,
            'queries': queries,
            'chapter': chapter,
            'cycle': cycle,
            'timestamp': datetime.now().isoformat()
        }
        
        # 更新聊天历史
        if hasattr(session, 'action_history'):
            session.action_history.append(action_log)
        else:
            session.action_history = [action_log]
        
        print(f"🎮 玩家 {character_name} 在第{chapter}章第{cycle}轮发言")
        print(f"💬 发言内容: {content}")
        if queries:
            print(f"❓ 询问: {queries}")
        
        return jsonify({
            'status': 'success',
            'message': '玩家行动记录成功',
            'data': {
                'action_id': len(session.action_history) if hasattr(session, 'action_history') else 1,
                'queries_count': len(queries)
            }
        })
        
    except Exception as e:
        print(f"❌ 处理玩家行动失败: {e}")
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': f'处理玩家行动失败: {str(e)}'
        }), 500

@game_bp.route('/ai_answer', methods=['POST'])
@login_required
def handle_ai_answer():
    """处理AI玩家回答"""
    try:
        data = request.get_json()
        session_id = data.get('game_session')
        character_name = data.get('character_name')
        question = data.get('question')
        asker = data.get('asker')
        chapter = data.get('chapter', 1)
        
        if session_id not in ACTIVE_GAMES:
            return jsonify({
                'status': 'error',
                'message': '游戏会话不存在'
            }), 404
        
        session = ACTIVE_GAMES[session_id]
        game = session.game_instance
        
        if not game:
            return jsonify({
                'status': 'error',
                'message': '游戏实例不存在'
            }), 400
        
        # 获取AI玩家实例
        if character_name not in session.ai_players:
            from player_agent import PlayerAgent
            session.ai_players[character_name] = PlayerAgent(character_name)
        
        ai_player = session.ai_players[character_name]
        
        # 构建聊天历史
        chat_history = ""
        if hasattr(session, 'action_history'):
            for action in session.action_history[-10:]:  # 最近10条记录
                if action['type'] == 'player_action':
                    chat_history += f"**{action['character']}**: {action['content']}\n"
                    for target, query in action.get('queries', {}).items():
                        chat_history += f"**{action['character']}** 询问 **{target}**: {query}\n"
        
        # 获取角色剧本（只到当前章节）
        character_script = game.script.get(character_name, [])
        available_scripts = character_script[:chapter]
        
        # 调用AI回答
        answer = ai_player.response(
            scripts=available_scripts,
            chat_history=chat_history,
            query=question,
            query_player=asker
        )
        
        print(f"🤖 AI玩家 {character_name} 回答了 {asker} 的问题")
        print(f"❓ 问题: {question}")
        print(f"💬 回答: {answer}")
        
        return jsonify({
            'status': 'success',
            'message': 'AI回答生成成功',
            'data': {
                'character_name': character_name,
                'answer': answer,
                'question': question,
                'asker': asker
            }
        })
        
    except Exception as e:
        print(f"❌ AI回答生成失败: {e}")
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': f'AI回答生成失败: {str(e)}'
        }), 500

# 错误处理
@game_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'status': 'error',
        'message': '接口不存在',
        'code': 404
    }), 404

@game_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        'status': 'error',
        'message': '服务器内部错误',
        'code': 500
    }), 500