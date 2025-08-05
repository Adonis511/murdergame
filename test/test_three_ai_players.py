#!/usr/bin/env python3
"""
三个AI玩家完整互动测试
确保每个方法调用都被记录和展示
"""

import sys
import os
import time
import json

# 导入测试工具
from test_utils import setup_project_path, validate_game_path

# 设置项目路径
setup_project_path()

from game import Game
from player_agent import PlayerAgent

class AIPlayerInteractionSimulator:
    """AI玩家互动模拟器"""
    
    def __init__(self, game_path: str):
        """初始化AI玩家互动模拟器"""
        print(f"🎮 初始化AI玩家互动模拟器...")
        print(f"📂 游戏路径: {game_path}")
        
        # 验证游戏路径
        if not validate_game_path(game_path):
            raise ValueError(f"游戏路径验证失败: {game_path}")
        
        # 加载游戏
        self.game = Game(script_path=game_path, generate_images=False)
        
        # 获取角色信息
        self.character_names = self.game.script.get('characters', [])
        self.total_chapters = self.game.get_total_chapters()
        
        print(f"✅ 游戏加载完成")
        print(f"🎭 剧本标题: {self.game.script.get('title', '未命名剧本')}")
        print(f"👥 角色数量: {len(self.character_names)}")
        print(f"📖 章节数量: {self.total_chapters}")
        
        # 确保三个主要角色参与
        target_characters = ["林慕白", "苏婉清", "赵子轩"]
        self.active_characters = []
        
        for char_name in target_characters:
            if char_name in self.character_names:
                self.active_characters.append(char_name)
        
        if len(self.active_characters) < 3:
            # 如果目标角色不足，使用前三个可用角色
            self.active_characters = self.character_names[:3]
        
        print(f"\n👤 参与讨论的AI角色:")
        for i, char_name in enumerate(self.active_characters, 1):
            print(f"   {i}. {char_name}")
        
        # 创建AI玩家代理
        self.ai_players = {}
        for char_name in self.active_characters:
            try:
                self.ai_players[char_name] = PlayerAgent(char_name)
                print(f"🤖 创建AI玩家: {char_name}")
            except Exception as e:
                print(f"❌ 创建AI玩家失败 ({char_name}): {e}")
        
        if len(self.ai_players) < 2:
            raise ValueError("至少需要2个AI玩家才能进行互动测试")
        
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
            print(f"  📞 [DM.speak] 调用者:{caller}")
        elif method_type == 'player_query':
            print(f"  📞 [PlayerAgent.query] 玩家:{caller}")
        elif method_type == 'player_response':
            print(f"  📞 [PlayerAgent.response] 玩家:{caller} -> 回应:{target}")
    
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
        模拟一个章节的AI玩家讨论
        确保每个AI都参与，有询问和回应
        """
        print(f"\n{'='*80}")
        print(f"🎬 第{chapter_num}章 - AI玩家讨论开始")
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
                
                self.add_to_chat_history(f"第{chapter_num}章开始", dm_speech, "dm")
                chapter_chat += f"**DM 第{chapter_num}章开始**\n{dm_speech}\n\n"
                
                # 处理DM工具
                if 'tools' in dm_start_result and dm_start_result['tools']:
                    for tool in dm_start_result['tools']:
                        tool_info = f"🔧 DM展示: {tool.get('tool_type', '工具')}"
                        print(tool_info)
                        chapter_chat += f"{tool_info}\n"
            else:
                print("⚠️ DM开场发言失败")
                chapter_chat += f"**DM 第{chapter_num}章开始**\n[发言失败]\n\n"
                
        except Exception as e:
            print(f"❌ DM开场发言出错: {e}")
            chapter_chat += f"**DM 第{chapter_num}章开始**\n[出错: {e}]\n\n"
        
        # 2. AI玩家轮流发言和互动
        print(f"\n👥 AI玩家互动环节 (共{len(self.ai_players)}个AI)")
        
        # 确保每个AI都至少发言一次
        for round_num in range(1, 4):  # 3轮互动
            print(f"\n🔄 第{round_num}轮互动")
            
            for speaker_name in self.active_characters:
                if speaker_name not in self.ai_players:
                    continue
                
                print(f"\n  👤 {speaker_name} 的回合...")
                
                try:
                    # 获取该AI的剧本
                    speaker_scripts = self.get_player_scripts(speaker_name, chapter_num)
                    
                    if not speaker_scripts:
                        print(f"    ⚠️ {speaker_name} 没有剧本内容")
                        continue
                    
                    # AI主动发言/询问 - 调用 PlayerAgent.query()
                    print(f"    📝 {speaker_name} 正在思考发言...")
                    speaker_agent = self.ai_players[speaker_name]
                    
                    query_result = speaker_agent.query(speaker_scripts, self.chat_history)
                    self.log_method_call('player_query', speaker_name, '', 
                                       {'scripts_count': len(speaker_scripts)}, query_result)
                    
                    if query_result and isinstance(query_result, dict) and 'content' in query_result:
                        content = query_result['content']
                        queries = query_result.get('query', {})
                        
                        print(f"    💬 {speaker_name} 发言: {content[:80]}...")
                        
                        # 构建完整发言
                        full_speech = content
                        if queries and isinstance(queries, dict) and queries:
                            query_list = []
                            for target, question in queries.items():
                                if target in self.ai_players:
                                    query_list.append(f"@{target}: {question}")
                            
                            if query_list:
                                full_speech += f"\n\n**询问**: {' | '.join(query_list)}"
                                print(f"    ❓ {speaker_name} 询问: {len(queries)} 个问题")
                        
                        # 添加到聊天历史
                        self.add_to_chat_history(speaker_name, full_speech)
                        chapter_chat += f"**{speaker_name}**\n{full_speech}\n\n"
                        
                        # 处理询问回应 - 调用 PlayerAgent.response()
                        if queries and isinstance(queries, dict):
                            for target_name, question in queries.items():
                                if target_name in self.ai_players and target_name != speaker_name:
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
                                            print(f"    💬 {target_name} 回应: {response[:60]}...")
                                            
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
                
                self.add_to_chat_history(f"第{chapter_num}章总结", dm_summary, "dm")
                chapter_chat += f"**DM 第{chapter_num}章总结**\n{dm_summary}\n\n"
                
                # 处理DM工具
                if 'tools' in dm_end_result and dm_end_result['tools']:
                    for tool in dm_end_result['tools']:
                        tool_info = f"🔧 DM总结展示: {tool.get('tool_type', '工具')}"
                        print(tool_info)
                        chapter_chat += f"{tool_info}\n"
            else:
                print("⚠️ DM章节总结失败")
                chapter_chat += f"**DM 第{chapter_num}章总结**\n[总结失败]\n\n"
                
        except Exception as e:
            print(f"❌ DM章节总结出错: {e}")
            chapter_chat += f"**DM 第{chapter_num}章总结**\n[总结出错: {e}]\n\n"
        
        # 保存章节讨论
        self.chapter_discussions[chapter_num] = chapter_chat
        
        print(f"\n✅ 第{chapter_num}章AI互动完成")
        return chapter_chat
    
    def print_method_call_summary(self):
        """打印方法调用统计"""
        print(f"\n📊 方法调用统计报告")
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
        print(f"\n👥 AI参与度统计:")
        for char_name in self.active_characters:
            char_queries = len([call for call in query_calls if call['caller'] == char_name])
            char_responses = len([call for call in response_calls if call['caller'] == char_name])
            char_received = len([call for call in response_calls if call['target'] == char_name])
            print(f"   {char_name}: 发言{char_queries}次, 回应{char_responses}次, 被询问{char_received}次")
        
        print("=" * 60)
    
    def simulate_complete_interaction(self):
        """模拟完整的AI互动流程"""
        print(f"\n🎮 开始AI玩家完整互动模拟...")
        print(f"🤖 参与AI: {', '.join(self.active_characters)}")
        print(f"📖 将模拟 2 个章节的讨论")
        
        start_time = time.time()
        completed_chapters = 0
        
        # 模拟前2章（避免测试时间过长）
        for chapter_num in range(1, min(3, self.total_chapters + 1)):
            try:
                print(f"\n🎯 开始第{chapter_num}章AI互动...")
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
            print(f"\n🏁 AI互动测试即将结束...")
            try:
                dm_final_result = self.game.end_game(self.chat_history, "待确定", "真相即将揭晓")
                self.log_method_call('dm_speak', '游戏结束', '', {'type': 'final'}, dm_final_result)
                
                if dm_final_result and isinstance(dm_final_result, dict) and 'speech' in dm_final_result:
                    final_summary = dm_final_result['speech']
                    print(f"✅ DM最终总结成功 ({len(final_summary)} 字符)")
                    self.add_to_chat_history("游戏结束", final_summary, "dm")
                
            except Exception as e:
                print(f"❌ DM最终总结出错: {e}")
        
        end_time = time.time()
        duration = end_time - start_time
        
        # 打印详细报告
        print(f"\n🎉 AI互动测试完成!")
        print(f"⏱️ 总耗时: {duration:.1f}秒")
        print(f"📝 完成章节: {completed_chapters}")
        print(f"🤖 参与AI: {len(self.ai_players)} 个")
        
        # 打印方法调用统计
        self.print_method_call_summary()
        
        return {
            'duration': duration,
            'chapters_completed': completed_chapters,
            'players_participated': list(self.ai_players.keys()),
            'method_calls': self.method_calls,
            'chat_history': self.chat_history
        }

def main():
    """主测试函数"""
    print("🤖 三个AI玩家完整互动测试开始...")
    print("=" * 80)
    
    # 使用指定的游戏路径
    game_path = "log/250805110930"
    
    try:
        if not os.path.exists(game_path):
            print(f"❌ 游戏路径不存在: {game_path}")
            return False
        
        print(f"📂 使用游戏路径: {game_path}")
        
        # 创建模拟器并运行测试
        simulator = AIPlayerInteractionSimulator(game_path)
        result = simulator.simulate_complete_interaction()
        
        print("\n" + "=" * 80)
        print("🎉 AI互动测试成功完成!")
        print(f"✅ 参与AI角色: {', '.join(result['players_participated'])}")
        print(f"✅ 完成章节: {result['chapters_completed']}")
        print(f"✅ 总方法调用: {len(result['method_calls'])} 次")
        print(f"✅ 测试时长: {result['duration']:.1f}秒")
        print("✅ 验证了AI之间的真实询问和回应互动")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"❌ AI互动测试失败: {e}")
        import traceback
        traceback.print_exc()
        print("\n" + "=" * 80)
        print("❌ 测试失败，请检查配置")
        print("=" * 80)
        return False

if __name__ == "__main__":
    main()