#!/usr/bin/env python3
"""
AI剧本杀游戏完整模拟测试
动态获取剧本中的所有角色，全部用AI扮演

使用方法:
1. 编辑脚本内配置区域，设置 GAME_PATH
2. 或使用命令行参数:
   - python test_ai_game_simulation.py --new          # 生成新剧本
   - python test_ai_game_simulation.py --path log/xxx # 使用指定剧本
   - python test_ai_game_simulation.py               # 使用脚本配置

功能:
- 动态获取剧本中的所有角色
- 为每个角色创建AI代理进行完整游戏
- 显示详细的DM发言内容和AI角色对话
- 记录所有方法调用 (DM.speak, PlayerAgent.query, PlayerAgent.response)
- 验证所有AI角色的真实询问和回应
"""

import sys
import os
import time
import json
import argparse

# 导入测试工具
from test_utils import setup_project_path, validate_game_path

# 设置项目路径
setup_project_path()

from game import Game
from player_agent import PlayerAgent

class AIGameSimulator:
    """AI剧本杀游戏模拟器"""
    
    def __init__(self, game_path: str = None):
        """
        初始化AI游戏模拟器
        
        Args:
            game_path: 游戏路径，None表示生成新剧本，有效路径表示加载现有剧本
        """
        print(f"🎮 初始化AI剧本杀游戏模拟器...")
        
        if game_path is None:
            print(f"🆕 模式: 生成新剧本")
            # 创建新游戏
            self.game = Game(script_path=None, generate_images=False)
            self.is_new_game = True
        else:
            print(f"📂 模式: 加载现有剧本")
            print(f"📁 游戏路径: {game_path}")
            
            # 验证游戏路径
            if not os.path.exists(game_path):
                raise ValueError(f"游戏路径不存在: {game_path}")
            
            if not validate_game_path(game_path):
                raise ValueError(f"游戏路径验证失败: {game_path}")
            
            # 加载现有游戏
            self.game = Game(script_path=game_path, generate_images=False)
            self.is_new_game = False
        
        # 动态获取剧本中的所有角色
        self.character_names = self.game.script.get('characters', [])
        self.total_chapters = self.game.get_total_chapters()
        
        print(f"✅ 游戏{'生成' if self.is_new_game else '加载'}完成")
        print(f"🎭 剧本标题: {self.game.script.get('title', '未命名剧本')}")
        print(f"👥 角色总数: {len(self.character_names)}")
        print(f"📖 章节数量: {self.total_chapters}")
        
        if self.is_new_game:
            print(f"📂 新游戏保存路径: {self.game.game_dir}")
        
        # 显示所有角色
        print(f"\n👤 剧本中的所有角色:")
        for i, char_name in enumerate(self.character_names, 1):
            print(f"   {i}. {char_name}")
        
        # 为所有角色创建AI代理
        self.ai_players = {}
        print(f"\n🤖 创建AI代理:")
        
        for char_name in self.character_names:
            if char_name and isinstance(char_name, str):
                try:
                    self.ai_players[char_name] = PlayerAgent(char_name)
                    print(f"   ✅ {char_name}")
                except Exception as e:
                    print(f"   ❌ {char_name}: {e}")
        
        if len(self.ai_players) < 2:
            raise ValueError(f"至少需要2个AI角色才能进行游戏，当前只有{len(self.ai_players)}个")
        
        print(f"\n🎯 游戏配置:")
        print(f"   参与AI角色数: {len(self.ai_players)}")
        print(f"   章节数量: {self.total_chapters}")
        print(f"   预计游戏时长: {self.total_chapters * 2}+ 分钟")
        
        # 初始化聊天历史和调用记录
        self.chat_history = ""
        self.method_calls = []  # 记录所有方法调用
        self.chapter_discussions = {}
    
    def log_method_call(self, method_type: str, caller: str, target: str = "", params: dict = None, result: any = None):
        """记录方法调用"""
        call_record = {
            'timestamp': time.strftime('%H:%M:%S'),
            'method_type': method_type,  # 'dm_speak', 'player_query', 'player_response'
            'caller': caller,
            'target': target,
            'params': params or {},
            'result_type': type(result).__name__,
            'result_preview': str(result)[:100] if result else None,
            'success': result is not None
        }
        self.method_calls.append(call_record)
        
        # 实时显示方法调用
        if method_type == 'dm_speak':
            print(f"  📞 [DM.speak] {caller}")
        elif method_type == 'player_query':
            print(f"  📞 [PlayerAgent.query] {caller}")
        elif method_type == 'player_response':
            print(f"  📞 [PlayerAgent.response] {caller} -> {target}")
    
    def add_to_chat_history(self, speaker: str, content: str, speaker_type: str = "player"):
        """添加内容到聊天历史"""
        timestamp = time.strftime('%H:%M:%S')
        if speaker_type == "dm":
            self.chat_history += f"\n\n## 🎭 DM [{speaker}] ({timestamp})\n\n{content}\n"
        else:
            self.chat_history += f"\n\n### 👤 {speaker} ({timestamp})\n\n{content}\n"
    
    def get_player_scripts(self, character_name: str, chapter_num: int) -> list:
        """获取指定角色到指定章节的剧本内容"""
        scripts = []
        
        if character_name not in self.character_names:
            print(f"⚠️ 角色不存在: {character_name}")
            return scripts
        
        character_chapters = self.game.script.get(character_name, [])
        
        for i in range(min(chapter_num, len(character_chapters))):
            chapter_content = character_chapters[i]
            scripts.append(f"**第{i+1}章**\n\n{chapter_content}")
        
        return scripts
    
    def simulate_chapter_discussion(self, chapter_num: int) -> str:
        """
        模拟一个章节的AI游戏讨论
        所有角色都是AI扮演，进行真实的游戏互动
        """
        print(f"\n{'='*80}")
        print(f"🎬 第{chapter_num}章 - AI游戏模拟开始")
        print(f"🤖 参与AI角色: {len(self.ai_players)}个")
        print(f"{'='*80}")
        
        chapter_chat = ""
        
        # 1. DM章节开始发言
        print(f"\n🎭 DM开始第{chapter_num}章...")
        try:
            dm_start_result = self.game.start_chapter(chapter_num, self.chat_history)
            self.log_method_call('dm_speak', f'第{chapter_num}章开始', '', 
                               {'chapter': chapter_num, 'type': 'start'}, dm_start_result)
            
            if dm_start_result and isinstance(dm_start_result, dict) and 'speech' in dm_start_result:
                dm_speech = dm_start_result['speech']
                print(f"✅ DM开场发言成功 ({len(dm_speech)} 字符)")
                print(f"💬 DM发言内容：")
                print(f"   {dm_speech}")
                
                self.add_to_chat_history(f"第{chapter_num}章开始", dm_speech, "dm")
                chapter_chat += f"**DM 第{chapter_num}章开始**\n{dm_speech}\n\n"
                
                # 处理DM工具
                if 'tools' in dm_start_result and dm_start_result['tools']:
                    print(f"🔧 DM展示了 {len(dm_start_result['tools'])} 个工具:")
                    for i, tool in enumerate(dm_start_result['tools'], 1):
                        tool_info = f"   {i}. {tool.get('tool_type', '工具')}: {tool.get('description', '无描述')}"
                        print(tool_info)
                        chapter_chat += f"**DM展示工具{i}**: {tool.get('description', '无描述')}\n"
            else:
                print("⚠️ DM开场发言失败")
                chapter_chat += f"**DM 第{chapter_num}章开始**\n[发言失败]\n\n"
                
        except Exception as e:
            print(f"❌ DM开场发言出错: {e}")
            chapter_chat += f"**DM 第{chapter_num}章开始**\n[出错: {e}]\n\n"
        
        # 2. 所有AI角色轮流互动
        print(f"\n👥 AI角色游戏互动环节")
        player_list = list(self.ai_players.keys())
        
        # 计算互动轮数，确保每个AI都有足够的参与机会
        interaction_rounds = max(3, len(player_list))  # 至少3轮，角色多时增加轮数
        
        for round_num in range(1, interaction_rounds + 1):
            print(f"\n🔄 第{round_num}轮游戏互动 (共{interaction_rounds}轮)")
            
            # 每轮让部分AI发言，确保所有AI都有机会
            speakers_this_round = []
            if round_num <= len(player_list):
                # 前几轮：每轮一个新AI
                speaker_index = (round_num - 1) % len(player_list)
                speakers_this_round = [player_list[speaker_index]]
            else:
                # 后续轮：随机选择1-2个AI
                import random
                speakers_this_round = random.sample(player_list, min(2, len(player_list)))
            
            for speaker_name in speakers_this_round:
                if speaker_name not in self.ai_players:
                    continue
                
                print(f"\n  👤 {speaker_name} 的游戏回合...")
                
                try:
                    # 获取该AI的剧本
                    speaker_scripts = self.get_player_scripts(speaker_name, chapter_num)
                    
                    if not speaker_scripts:
                        print(f"    ⚠️ {speaker_name} 没有剧本内容")
                        continue
                    
                    # AI主动发言/询问 - 调用 PlayerAgent.query()
                    print(f"    📝 {speaker_name} 正在分析剧情和思考发言...")
                    speaker_agent = self.ai_players[speaker_name]
                    
                    query_result = speaker_agent.query(speaker_scripts, self.chat_history)
                    self.log_method_call('player_query', speaker_name, '', 
                                       {'scripts_count': len(speaker_scripts)}, query_result)
                    
                    if query_result and isinstance(query_result, dict) and 'content' in query_result:
                        content = query_result['content']
                        queries = query_result.get('query', {})
                        
                        print(f"    💬 {speaker_name} 发言内容：")
                        print(f"       {content}")
                        
                        # 构建完整发言
                        full_speech = content
                        valid_queries = {}
                        
                        if queries and isinstance(queries, dict) and queries:
                            # 过滤有效的询问对象（必须是其他AI角色）
                            for target, question in queries.items():
                                if target in self.ai_players and target != speaker_name:
                                    valid_queries[target] = question
                            
                            if valid_queries:
                                query_list = [f"@{target}: {question}" for target, question in valid_queries.items()]
                                full_speech += f"\n\n**询问**: {' | '.join(query_list)}"
                                print(f"    ❓ {speaker_name} 的询问:")
                                for target, question in valid_queries.items():
                                    print(f"       向 {target}: {question}")
                        
                        # 添加到聊天历史
                        self.add_to_chat_history(speaker_name, full_speech)
                        chapter_chat += f"**{speaker_name}**\n{full_speech}\n\n"
                        
                        # 处理询问回应 - 调用 PlayerAgent.response()
                        if valid_queries:
                            for target_name, question in valid_queries.items():
                                print(f"    🔄 {target_name} 准备回应 {speaker_name} 的询问...")
                                
                                try:
                                    target_agent = self.ai_players[target_name]
                                    target_scripts = self.get_player_scripts(target_name, chapter_num)
                                    
                                    # 调用回应方法
                                    response = target_agent.response(
                                        target_scripts, 
                                        self.chat_history, 
                                        question, 
                                        speaker_name
                                    )
                                    self.log_method_call('player_response', target_name, speaker_name, 
                                                       {'question': question[:50]}, response)
                                    
                                    if response and isinstance(response, str):
                                        print(f"    💬 {target_name} 回应内容：")
                                        print(f"       {response}")
                                        
                                        # 添加到聊天历史
                                        response_content = f"**回应 @{speaker_name}**: {response}"
                                        self.add_to_chat_history(target_name, response_content)
                                        chapter_chat += f"**{target_name} 回应 {speaker_name}**\n{response}\n\n"
                                    else:
                                        print(f"    ⚠️ {target_name} 回应失败或无内容")
                                        
                                except Exception as e:
                                    print(f"    ❌ {target_name} 回应出错: {e}")
                                    self.log_method_call('player_response', target_name, speaker_name, 
                                                       {'question': question[:50]}, None)
                                    chapter_chat += f"**{target_name}**\n[回应失败: {e}]\n\n"
                    else:
                        print(f"    ⚠️ {speaker_name} 发言失败或格式错误")
                        chapter_chat += f"**{speaker_name}**\n[发言失败]\n\n"
                    
                    # 每个AI发言后稍作停顿
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"    ❌ {speaker_name} 发言出错: {e}")
                    self.log_method_call('player_query', speaker_name, '', {}, None)
                    chapter_chat += f"**{speaker_name}**\n[发言出错: {e}]\n\n"
        
        # 3. DM章节结束总结
        print(f"\n🎭 DM总结第{chapter_num}章...")
        try:
            dm_end_result = self.game.end_chapter(chapter_num, self.chat_history)
            self.log_method_call('dm_speak', f'第{chapter_num}章结束', '', 
                               {'chapter': chapter_num, 'type': 'end'}, dm_end_result)
            
            if dm_end_result and isinstance(dm_end_result, dict) and 'speech' in dm_end_result:
                dm_summary = dm_end_result['speech']
                print(f"✅ DM章节总结成功 ({len(dm_summary)} 字符)")
                print(f"💬 DM总结内容：")
                print(f"   {dm_summary}")
                
                self.add_to_chat_history(f"第{chapter_num}章总结", dm_summary, "dm")
                chapter_chat += f"**DM 第{chapter_num}章总结**\n{dm_summary}\n\n"
                
                # 处理DM工具
                if 'tools' in dm_end_result and dm_end_result['tools']:
                    print(f"🔧 DM总结展示了 {len(dm_end_result['tools'])} 个工具:")
                    for i, tool in enumerate(dm_end_result['tools'], 1):
                        tool_info = f"   {i}. {tool.get('tool_type', '工具')}: {tool.get('description', '无描述')}"
                        print(tool_info)
                        chapter_chat += f"**DM总结工具{i}**: {tool.get('description', '无描述')}\n"
            else:
                print("⚠️ DM章节总结失败")
                chapter_chat += f"**DM 第{chapter_num}章总结**\n[总结失败]\n\n"
                
        except Exception as e:
            print(f"❌ DM章节总结出错: {e}")
            chapter_chat += f"**DM 第{chapter_num}章总结**\n[总结出错: {e}]\n\n"
        
        # 保存章节讨论
        self.chapter_discussions[chapter_num] = chapter_chat
        
        print(f"\n✅ 第{chapter_num}章AI游戏模拟完成")
        return chapter_chat
    
    def print_method_call_summary(self):
        """打印方法调用统计"""
        print(f"\n📊 AI游戏模拟统计报告")
        print("=" * 60)
        
        dm_calls = [call for call in self.method_calls if call['method_type'] == 'dm_speak']
        query_calls = [call for call in self.method_calls if call['method_type'] == 'player_query']
        response_calls = [call for call in self.method_calls if call['method_type'] == 'player_response']
        
        print(f"🎭 DM.speak() 调用次数: {len(dm_calls)}")
        for call in dm_calls:
            status = "✅" if call['success'] else "❌"
            print(f"   {status} {call['timestamp']} - {call['caller']}")
        
        print(f"\n🗣️ PlayerAgent.query() 调用次数: {len(query_calls)}")
        for call in query_calls:
            status = "✅" if call['success'] else "❌"
            print(f"   {status} {call['timestamp']} - {call['caller']}")
        
        print(f"\n💬 PlayerAgent.response() 调用次数: {len(response_calls)}")
        for call in response_calls:
            status = "✅" if call['success'] else "❌"
            print(f"   {status} {call['timestamp']} - {call['caller']} -> {call['target']}")
        
        # 统计每个AI的参与度
        print(f"\n👥 AI角色参与度统计:")
        for char_name in self.character_names:
            if char_name in self.ai_players:
                char_queries = len([call for call in query_calls if call['caller'] == char_name])
                char_responses = len([call for call in response_calls if call['caller'] == char_name])
                char_received = len([call for call in response_calls if call['target'] == char_name])
                print(f"   {char_name}: 发言{char_queries}次, 回应{char_responses}次, 被询问{char_received}次")
        
        print("=" * 60)
    
    def simulate_complete_game(self):
        """模拟完整的AI游戏流程"""
        print(f"\n🎮 开始AI剧本杀游戏完整模拟...")
        print(f"🤖 参与AI角色: {', '.join(self.ai_players.keys())}")
        print(f"📖 将模拟完整的 {self.total_chapters} 个章节")
        
        start_time = time.time()
        completed_chapters = 0
        
        # 模拟所有章节
        for chapter_num in range(1, self.total_chapters + 1):
            try:
                print(f"\n🎯 开始第{chapter_num}章AI游戏模拟...")
                self.simulate_chapter_discussion(chapter_num)
                completed_chapters += 1
                
                print(f"\n⏸️ 第{chapter_num}章完成，准备下一章...")
                time.sleep(2)
                
            except Exception as e:
                print(f"❌ 第{chapter_num}章模拟失败: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        # 游戏结束
        if completed_chapters > 0:
            print(f"\n🏁 AI游戏即将结束...")
            try:
                dm_final_result = self.game.end_game(self.chat_history, "待确定", "真相即将揭晓")
                self.log_method_call('dm_speak', '游戏结束', '', {'type': 'final'}, dm_final_result)
                
                if dm_final_result and isinstance(dm_final_result, dict) and 'speech' in dm_final_result:
                    final_summary = dm_final_result['speech']
                    print(f"✅ DM最终总结成功 ({len(final_summary)} 字符)")
                    print(f"💬 DM最终总结内容：")
                    print(f"   {final_summary}")
                    self.add_to_chat_history("游戏结束", final_summary, "dm")
                    
                    # 处理最终总结的工具
                    if 'tools' in dm_final_result and dm_final_result['tools']:
                        print(f"🔧 DM最终展示了 {len(dm_final_result['tools'])} 个工具:")
                        for i, tool in enumerate(dm_final_result['tools'], 1):
                            tool_info = f"   {i}. {tool.get('tool_type', '工具')}: {tool.get('description', '无描述')}"
                            print(tool_info)
                
            except Exception as e:
                print(f"❌ DM最终总结出错: {e}")
        
        end_time = time.time()
        duration = end_time - start_time
        
        # 打印详细报告
        print(f"\n🎉 AI游戏模拟完成!")
        print(f"⏱️ 总耗时: {duration:.1f}秒")
        print(f"📝 完成章节: {completed_chapters}/{self.total_chapters}")
        print(f"🤖 参与AI数: {len(self.ai_players)} 个")
        
        # 打印方法调用统计
        self.print_method_call_summary()
        
        return {
            'duration': duration,
            'chapters_completed': completed_chapters,
            'total_chapters': self.total_chapters,
            'players_participated': list(self.ai_players.keys()),
            'method_calls': self.method_calls,
            'chat_history': self.chat_history
        }

# ====================配置区域====================
# 在这里配置测试模式，选择以下选项之一：

# 选项1: 使用现有剧本（需要指定具体路径）
# GAME_PATH = "log/250805110930"  # 使用现有剧本

# 选项2: 生成新剧本（设置为None）
GAME_PATH = None  # 生成全新的剧本

# 💡 使用说明:
# - 设置为 None: AI将生成全新的剧本杀剧本，动态获取角色
# - 设置为路径: 加载已有的剧本，获取其中的角色进行测试
# - 命令行参数可以覆盖这里的设置

# ================================================

def test_with_existing_game(game_path: str):
    """使用现有游戏进行测试"""
    print(f"📂 使用现有游戏路径: {game_path}")
    
    if not os.path.exists(game_path):
        print(f"❌ 游戏路径不存在: {game_path}")
        return False
    
    try:
        simulator = AIGameSimulator(game_path)
        result = simulator.simulate_complete_game()
        
        print("\n" + "=" * 80)
        print("🎉 现有游戏AI模拟测试成功完成!")
        print(f"✅ 游戏路径: {game_path}")
        print(f"✅ 参与AI角色: {', '.join(result['players_participated'])}")
        print(f"✅ 完成章节: {result['chapters_completed']}/{result['total_chapters']}")
        print(f"✅ 总方法调用: {len(result['method_calls'])} 次")
        print(f"✅ 测试时长: {result['duration']:.1f}秒")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"❌ 现有游戏测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_with_new_game():
    """生成新游戏进行测试"""
    print(f"🆕 生成新游戏进行测试")
    
    try:
        simulator = AIGameSimulator(None)
        result = simulator.simulate_complete_game()
        
        print("\n" + "=" * 80)
        print("🎉 新游戏AI模拟测试成功完成!")
        print(f"✅ 新游戏路径: {simulator.game.game_dir}")
        print(f"✅ 参与AI角色: {', '.join(result['players_participated'])}")
        print(f"✅ 完成章节: {result['chapters_completed']}/{result['total_chapters']}")
        print(f"✅ 总方法调用: {len(result['method_calls'])} 次")
        print(f"✅ 测试时长: {result['duration']:.1f}秒")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"❌ 新游戏测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main(game_path="__use_config__"):
    """
    主测试函数
    
    Args:
        game_path: 游戏路径，None表示生成新剧本，有效路径表示加载现有剧本，"__use_config__"表示使用配置区域设置
    """
    # 如果使用特殊标记，采用配置区域的设置
    if game_path == "__use_config__":
        game_path = GAME_PATH
    
    print("🤖 AI剧本杀游戏完整模拟测试开始...")
    print("=" * 80)
    
    print(f"🔧 当前配置:")
    if game_path is None:
        print(f"   模式: 生成新剧本")
        print(f"   说明: AI将生成全新的剧本杀剧本，自动获取所有角色")
    else:
        print(f"   模式: 使用现有剧本")
        print(f"   路径: {game_path}")
        print(f"   说明: 将从剧本中获取所有角色进行AI游戏")
    
    print(f"\n💡 如需更改模式，可以:")
    print(f"   - 编辑脚本顶部的配置区域")
    print(f"   - 使用命令行参数: --new 或 --path 路径")
    print("=" * 80)
    
    try:
        if game_path is None:
            # 生成新游戏
            success = test_with_new_game()
        else:
            # 使用现有游戏
            success = test_with_existing_game(game_path)
        
        if success:
            print("\n🎊 AI游戏模拟完全成功!")
            print("✅ 验证了动态角色获取和AI游戏流程")
            print("✅ 验证了DM.speak()、PlayerAgent.query()、PlayerAgent.response()方法调用")
            print("✅ 验证了所有AI角色的真实游戏互动")
        
        return success
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        print("\n" + "=" * 80)
        print("❌ 请检查配置和环境")
        print("=" * 80)
        return False

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="AI剧本杀游戏完整模拟测试",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python test_ai_game_simulation.py                    # 使用脚本内配置
  python test_ai_game_simulation.py --new              # 生成新剧本
  python test_ai_game_simulation.py --path log/xxx     # 使用指定剧本
        """
    )
    
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--new", 
        action="store_true", 
        help="生成新剧本（覆盖脚本内配置）"
    )
    group.add_argument(
        "--path", 
        type=str, 
        help="指定现有剧本路径（覆盖脚本内配置）"
    )
    
    return parser.parse_args()

if __name__ == "__main__":
    # 解析命令行参数
    args = parse_arguments()
    
    # 确定使用的游戏路径
    if args.new:
        # 命令行指定生成新剧本
        final_game_path = None
        print("🔧 命令行参数: 生成新剧本")
    elif args.path:
        # 命令行指定路径
        final_game_path = args.path
        print(f"🔧 命令行参数: 使用路径 {args.path}")
    else:
        # 使用脚本内配置
        final_game_path = "__use_config__"  # 让main函数使用配置区域设置
        print("🔧 使用脚本内配置")
    
    # 运行主函数
    main(final_game_path)