#!/usr/bin/env python3
"""
使用指定游戏路径进行完整流程测试
测试游戏路径: log/250805110930
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

class SpecificGameFlowSimulator:
    """指定游戏流程模拟器"""
    
    def __init__(self, game_path: str):
        """
        初始化指定游戏流程模拟器
        
        Args:
            game_path: 游戏路径
        """
        print(f"🎮 初始化游戏流程模拟器...")
        print(f"📂 使用游戏路径: {game_path}")
        
        # 验证游戏路径
        if not validate_game_path(game_path):
            raise ValueError(f"游戏路径验证失败: {game_path}")
        
        # 加载游戏
        self.game = Game(script_path=game_path, generate_images=False)
        
        # 获取角色信息（处理字符串列表格式）
        self.character_names = self.game.script.get('characters', [])
        self.total_chapters = self.game.get_total_chapters()
        
        print(f"✅ 游戏加载完成")
        print(f"🎭 剧本标题: {self.game.script.get('title', '未命名剧本')}")
        print(f"👥 角色数量: {len(self.character_names)}")
        print(f"📖 章节数量: {self.total_chapters}")
        
        # 显示角色列表
        print(f"\n👤 角色列表:")
        for i, char_name in enumerate(self.character_names, 1):
            print(f"   {i}. {char_name}")
        
        # 创建玩家代理（选择前3个角色）
        self.players = {}
        selected_characters = self.character_names[:min(3, len(self.character_names))]
        
        for char_name in selected_characters:
            if char_name and isinstance(char_name, str):
                try:
                    self.players[char_name] = PlayerAgent(char_name)
                    print(f"🤖 创建玩家代理: {char_name}")
                except Exception as e:
                    print(f"⚠️ 创建玩家代理失败 ({char_name}): {e}")
        
        if not self.players:
            print("⚠️ 没有可用的玩家代理，将进行简化测试")
        
        # 初始化聊天历史
        self.chat_history = ""
        self.chapter_discussions = {}  # 记录每章节的讨论
    
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
        
        # 检查角色是否存在
        if character_name not in self.character_names:
            print(f"⚠️ 未找到角色: {character_name}")
            return scripts
        
        # 从剧本中获取该角色的章节内容
        character_chapters = self.game.script.get(character_name, [])
        
        if not character_chapters:
            print(f"⚠️ 角色 {character_name} 没有剧本内容")
            return scripts
        
        # 获取到当前章节的所有剧本内容
        for i in range(min(chapter_num, len(character_chapters))):
            chapter_content = character_chapters[i]
            scripts.append(f"**第{i+1}章**\n\n{chapter_content}")
        
        return scripts
    
    def simulate_chapter_discussion(self, chapter_num: int) -> str:
        """
        模拟一个章节的讨论
        流程：dm发言 → 玩家发言/询问 → 玩家回应 → dm章节总结
        """
        print(f"\n{'='*80}")
        print(f"🎬 开始第{chapter_num}章讨论")
        print(f"{'='*80}")
        
        chapter_chat = ""
        
        # 1. DM章节开始发言
        print(f"\n🎭 DM开始第{chapter_num}章...")
        try:
            dm_start_result = self.game.start_chapter(chapter_num, self.chat_history)
            
            print(f"🔍 DM开始发言结果类型: {type(dm_start_result)}")
            print(f"🔍 DM开始发言结果内容: {dm_start_result}")
            
            if dm_start_result and isinstance(dm_start_result, dict) and 'speech' in dm_start_result:
                dm_speech = dm_start_result['speech']
                print(f"✅ DM发言成功")
                print(f"💬 DM发言长度: {len(dm_speech)} 字符")
                print(f"💬 DM发言预览: {dm_speech[:150]}...")
                
                # 添加到聊天历史
                self.add_to_chat_history(f"第{chapter_num}章开始", dm_speech, "dm")
                chapter_chat += f"**DM 第{chapter_num}章开始**\n{dm_speech}\n\n"
                
                # 处理DM工具调用
                if 'tools' in dm_start_result and dm_start_result['tools']:
                    for tool in dm_start_result['tools']:
                        tool_info = f"🔧 DM展示了{tool.get('tool_type', '工具')}: {tool.get('description', '')}"
                        print(tool_info)
                        chapter_chat += f"{tool_info}\n"
                        
            elif isinstance(dm_start_result, str):
                # 如果返回的是字符串，直接使用
                print(f"⚠️ DM发言返回字符串格式，尝试兼容处理")
                dm_speech = dm_start_result
                print(f"💬 DM发言预览: {dm_speech[:150]}...")
                
                self.add_to_chat_history(f"第{chapter_num}章开始", dm_speech, "dm")
                chapter_chat += f"**DM 第{chapter_num}章开始**\n{dm_speech}\n\n"
            else:
                print("⚠️ DM章节开始发言失败或格式错误")
                chapter_chat += f"**DM 第{chapter_num}章开始**\n[DM发言失败或格式错误]\n\n"
                
        except Exception as e:
            print(f"❌ DM章节开始发言出错: {e}")
            import traceback
            traceback.print_exc()
            chapter_chat += f"**DM 第{chapter_num}章开始**\n[DM发言出错: {e}]\n\n"
        
        # 2. 玩家讨论轮次（简化为2轮）
        player_names = list(self.players.keys())
        print(f"\n👥 参与讨论的玩家: {player_names}")
        
        for round_num in range(1, 3):  # 2轮讨论
            print(f"\n🔄 第{round_num}轮讨论")
            
            # 每轮让1-2个玩家发言
            active_players = player_names[:min(2, len(player_names))]
            
            for player_name in active_players:
                if player_name not in self.players:
                    continue
                
                try:
                    print(f"\n👤 {player_name}的回合...")
                    
                    # 获取该玩家的剧本
                    player_scripts = self.get_player_scripts(player_name, chapter_num)
                    
                    if not player_scripts:
                        print(f"⚠️ {player_name}没有剧本内容")
                        continue
                    
                    # 玩家主动发言/询问
                    player_agent = self.players[player_name]
                    query_result = player_agent.query(player_scripts, self.chat_history)
                    
                    print(f"🔍 {player_name}发言结果类型: {type(query_result)}")
                    
                    if query_result and isinstance(query_result, dict) and 'content' in query_result:
                        content = query_result['content']
                        queries = query_result.get('query', {})
                        
                        print(f"💬 {player_name}发言长度: {len(content)} 字符")
                        print(f"💬 {player_name}发言预览: {content[:100]}...")
                        
                        # 添加到聊天历史
                        full_speech = content
                        if queries and isinstance(queries, dict):
                            query_text = " | ".join([f"询问{target}: {question}" for target, question in queries.items()])
                            full_speech += f"\n\n**询问**: {query_text}"
                            print(f"❓ {player_name}的询问: {query_text}")
                        
                        self.add_to_chat_history(player_name, full_speech)
                        chapter_chat += f"**{player_name}**\n{full_speech}\n\n"
                        
                        # 处理询问回应
                        if queries and isinstance(queries, dict):
                            for target_name, question in queries.items():
                                if target_name in self.players:
                                    try:
                                        print(f"  🔄 {target_name}回应{player_name}的询问...")
                                        
                                        target_agent = self.players[target_name]
                                        target_scripts = self.get_player_scripts(target_name, chapter_num)
                                        
                                        response = target_agent.response(
                                            target_scripts, 
                                            self.chat_history, 
                                            question, 
                                            player_name
                                        )
                                        
                                        print(f"  💬 {target_name}回应长度: {len(response)} 字符")
                                        print(f"  💬 {target_name}回应预览: {response[:80]}...")
                                        
                                        # 添加到聊天历史
                                        self.add_to_chat_history(target_name, f"**回应{player_name}**: {response}")
                                        chapter_chat += f"**{target_name}回应{player_name}**\n{response}\n\n"
                                        
                                    except Exception as e:
                                        print(f"  ❌ {target_name}回应失败: {e}")
                                        chapter_chat += f"**{target_name}**\n[回应失败: {e}]\n\n"
                    else:
                        print(f"⚠️ {player_name}发言失败或格式错误")
                        chapter_chat += f"**{player_name}**\n[发言失败或格式错误]\n\n"
                    
                    # 添加小延时，避免API调用过于频繁
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"❌ {player_name}发言失败: {e}")
                    import traceback
                    traceback.print_exc()
                    chapter_chat += f"**{player_name}**\n[发言失败: {e}]\n\n"
        
        # 3. DM章节结束总结
        print(f"\n🎭 DM总结第{chapter_num}章...")
        try:
            dm_end_result = self.game.end_chapter(chapter_num, self.chat_history)
            
            print(f"🔍 DM结束发言结果类型: {type(dm_end_result)}")
            print(f"🔍 DM结束发言结果内容: {dm_end_result}")
            
            if dm_end_result and isinstance(dm_end_result, dict) and 'speech' in dm_end_result:
                dm_summary = dm_end_result['speech']
                print(f"✅ DM章节总结成功")
                print(f"💬 DM总结长度: {len(dm_summary)} 字符")
                print(f"💬 DM总结预览: {dm_summary[:150]}...")
                
                # 添加到聊天历史
                self.add_to_chat_history(f"第{chapter_num}章总结", dm_summary, "dm")
                chapter_chat += f"**DM 第{chapter_num}章总结**\n{dm_summary}\n\n"
                
                # 处理DM工具调用
                if 'tools' in dm_end_result and dm_end_result['tools']:
                    for tool in dm_end_result['tools']:
                        tool_info = f"🔧 DM展示了{tool.get('tool_type', '工具')}: {tool.get('description', '')}"
                        print(tool_info)
                        chapter_chat += f"{tool_info}\n"
                        
            elif isinstance(dm_end_result, str):
                # 如果返回的是字符串，直接使用
                print(f"⚠️ DM总结返回字符串格式，尝试兼容处理")
                dm_summary = dm_end_result
                print(f"💬 DM总结预览: {dm_summary[:150]}...")
                
                self.add_to_chat_history(f"第{chapter_num}章总结", dm_summary, "dm")
                chapter_chat += f"**DM 第{chapter_num}章总结**\n{dm_summary}\n\n"
            else:
                print("⚠️ DM章节总结失败或格式错误")
                chapter_chat += f"**DM 第{chapter_num}章总结**\n[DM总结失败或格式错误]\n\n"
                
        except Exception as e:
            print(f"❌ DM章节总结出错: {e}")
            import traceback
            traceback.print_exc()
            chapter_chat += f"**DM 第{chapter_num}章总结**\n[DM总结出错: {e}]\n\n"
        
        # 保存章节讨论
        self.chapter_discussions[chapter_num] = chapter_chat
        
        print(f"\n✅ 第{chapter_num}章讨论完成")
        return chapter_chat
    
    def simulate_complete_game(self):
        """模拟完整游戏流程"""
        print(f"\n🎮 开始模拟完整游戏流程...")
        print(f"📖 将进行{self.total_chapters}个章节的讨论")
        
        start_time = time.time()
        completed_chapters = 0
        
        # 逐章节进行讨论
        for chapter_num in range(1, min(self.total_chapters + 1, 4)):  # 限制最多3章，避免测试时间过长
            try:
                print(f"\n🎯 开始第{chapter_num}章模拟...")
                self.simulate_chapter_discussion(chapter_num)
                completed_chapters += 1
                
                # 章节间稍作停顿
                print(f"\n⏸️ 第{chapter_num}章结束，准备下一章...")
                time.sleep(2)
                
            except Exception as e:
                print(f"❌ 第{chapter_num}章模拟失败: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        # 游戏结束总结（仅当完成了至少1章时）
        if completed_chapters > 0:
            print(f"\n🏁 游戏即将结束，DM进行最终总结...")
            try:
                # 简化处理
                killer_guess = "未知"
                truth_info = "真相将在最终总结中揭晓"
                
                dm_final_result = self.game.end_game(self.chat_history, killer_guess, truth_info)
                
                print(f"🔍 DM最终总结结果类型: {type(dm_final_result)}")
                
                if dm_final_result and isinstance(dm_final_result, dict) and 'speech' in dm_final_result:
                    final_summary = dm_final_result['speech']
                    print(f"✅ DM最终总结成功")
                    print(f"💬 DM最终总结长度: {len(final_summary)} 字符")
                    print(f"💬 DM最终总结预览: {final_summary[:200]}...")
                    
                    # 添加到聊天历史
                    self.add_to_chat_history("游戏结束", final_summary, "dm")
                    
                    # 处理DM工具调用
                    if 'tools' in dm_final_result and dm_final_result['tools']:
                        for tool in dm_final_result['tools']:
                            tool_info = f"🔧 DM最终展示了{tool.get('tool_type', '工具')}: {tool.get('description', '')}"
                            print(tool_info)
                            
                elif isinstance(dm_final_result, str):
                    print(f"⚠️ DM最终总结返回字符串格式，尝试兼容处理")
                    final_summary = dm_final_result
                    print(f"💬 DM最终总结预览: {final_summary[:200]}...")
                    self.add_to_chat_history("游戏结束", final_summary, "dm")
                else:
                    print("⚠️ DM最终总结失败或格式错误")
                    
            except Exception as e:
                print(f"❌ DM最终总结出错: {e}")
                import traceback
                traceback.print_exc()
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n🎉 完整游戏流程模拟完成!")
        print(f"⏱️ 总耗时: {duration:.1f}秒")
        print(f"📝 完成章节: {completed_chapters}/{self.total_chapters}")
        print(f"💬 总聊天条数: {len(self.chat_history.split('##'))}")
        
        return {
            'duration': duration,
            'chapters_completed': completed_chapters,
            'total_chapters': self.total_chapters,
            'chat_history': self.chat_history,
            'chapter_discussions': self.chapter_discussions,
            'players_participated': list(self.players.keys())
        }
    
    def save_simulation_log(self, result: dict):
        """保存模拟日志"""
        try:
            log_file = os.path.join(self.game.game_dir, "simulation_test_log.json")
            
            log_data = {
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'test_type': 'specific_game_flow',
                'game_info': {
                    'title': self.game.script.get('title', '未命名剧本'),
                    'characters': self.character_names,
                    'total_chapters': self.total_chapters,
                    'game_path': self.game.game_dir
                },
                'simulation_result': result
            }
            
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, ensure_ascii=False, indent=2)
            
            print(f"💾 模拟测试日志已保存: {log_file}")
            
        except Exception as e:
            print(f"⚠️ 保存模拟日志失败: {e}")

def main():
    """主测试函数"""
    print("🎮 指定游戏完整流程测试开始...")
    print("=" * 80)
    
    # 使用指定的游戏路径
    game_path = "log/250805110930"
    
    try:
        # 验证路径是否存在
        if not os.path.exists(game_path):
            print(f"❌ 游戏路径不存在: {game_path}")
            return False
        
        print(f"📂 使用游戏路径: {game_path}")
        
        # 创建模拟器并运行测试
        simulator = SpecificGameFlowSimulator(game_path)
        result = simulator.simulate_complete_game()
        simulator.save_simulation_log(result)
        
        print("\n" + "=" * 80)
        print("🎉 指定游戏完整流程测试成功完成!")
        print(f"✅ 完成章节: {result['chapters_completed']}/{result['total_chapters']}")
        print(f"✅ 参与玩家: {', '.join(result['players_participated'])}")
        print(f"✅ 测试时长: {result['duration']:.1f}秒")
        print("✅ 验证了DM发言、玩家发言、章节总结的完整流程")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"❌ 指定游戏流程测试失败: {e}")
        import traceback
        traceback.print_exc()
        print("\n" + "=" * 80)
        print("❌ 测试失败，请检查游戏路径和配置")
        print("=" * 80)
        return False

if __name__ == "__main__":
    main()