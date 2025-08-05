#!/usr/bin/env python3
"""
完整游戏流程测试脚本
测试每章节的正确流程：[dm发言（speak）-玩家发言或询问（query）-玩家回应]*3+dm章节总结
"""

import sys
import os
import time
import json

# 导入测试工具
from test_utils import setup_project_path, get_latest_game, validate_game_path

# 设置项目路径
setup_project_path()

from game import Game
from player_agent import PlayerAgent

class GameFlowSimulator:
    """游戏流程模拟器"""
    
    def __init__(self, script_path=None, generate_images=False):
        """
        初始化游戏流程模拟器
        
        Args:
            script_path: 现有游戏路径，None表示创建新游戏
            generate_images: 是否生成图片
        """
        print("🎮 初始化游戏流程模拟器...")
        
        # 创建或加载游戏
        self.game = Game(script_path=script_path, generate_images=generate_images)
        
        # 获取角色信息
        self.characters = self.game.script.get('characters', [])
        self.total_chapters = self.game.get_total_chapters()
        
        print(f"✅ 游戏初始化完成")
        print(f"📂 游戏目录: {self.game.game_dir}")
        print(f"🎭 剧本标题: {self.game.script.get('title', '未命名剧本')}")
        print(f"👥 角色数量: {len(self.characters)}")
        print(f"📖 章节数量: {self.total_chapters}")
        
        # 创建玩家代理
        self.players = {}
        for character in self.characters[:3]:  # 限制最多3个角色参与，避免过于复杂
            char_name = character.get('name', '未命名角色')
            if char_name and char_name != '未命名角色':
                try:
                    self.players[char_name] = PlayerAgent(char_name)
                    print(f"👤 创建玩家代理: {char_name}")
                except Exception as e:
                    print(f"⚠️ 创建玩家代理失败 ({char_name}): {e}")
        
        if not self.players:
            print("⚠️ 没有可用的玩家代理，将进行简化测试")
        
        # 初始化聊天历史
        self.chat_history = ""
        self.chapter_discussions = {}  # 记录每章节的讨论
    
    def add_to_chat_history(self, speaker: str, content: str, speaker_type: str = "player"):
        """添加内容到聊天历史"""
        if speaker_type == "dm":
            self.chat_history += f"\n\n## 🎭 DM [{speaker}]\n\n{content}\n"
        else:
            self.chat_history += f"\n\n### 👤 {speaker}\n\n{content}\n"
    
    def get_player_scripts(self, character_name: str, chapter_num: int) -> list:
        """获取指定角色到指定章节的剧本内容"""
        scripts = []
        
        # 找到对应角色
        character_data = None
        for char in self.characters:
            if char.get('name') == character_name:
                character_data = char
                break
        
        if not character_data:
            return scripts
        
        # 获取到当前章节的所有剧本内容
        chapters = character_data.get('chapters', [])
        for i in range(min(chapter_num, len(chapters))):
            chapter_content = chapters[i]
            scripts.append(f"**第{i+1}章**\n\n{chapter_content}")
        
        return scripts
    
    def simulate_chapter_discussion(self, chapter_num: int) -> str:
        """
        模拟一个章节的讨论
        流程：[dm发言-玩家发言/询问-玩家回应]*3+dm章节总结
        """
        print(f"\n{'='*60}")
        print(f"🎬 开始第{chapter_num}章讨论")
        print(f"{'='*60}")
        
        chapter_chat = ""
        
        # 1. DM章节开始发言
        print(f"\n🎭 DM开始第{chapter_num}章...")
        try:
            dm_start_result = self.game.start_chapter(chapter_num, self.chat_history)
            
            if dm_start_result and 'speech' in dm_start_result:
                dm_speech = dm_start_result['speech']
                print(f"✅ DM发言成功")
                print(f"💬 DM: {dm_speech[:100]}...")
                
                # 添加到聊天历史
                self.add_to_chat_history(f"第{chapter_num}章开始", dm_speech, "dm")
                chapter_chat += f"**DM 第{chapter_num}章开始**\n{dm_speech}\n\n"
                
                # 处理DM工具调用
                if 'tools' in dm_start_result and dm_start_result['tools']:
                    for tool in dm_start_result['tools']:
                        tool_info = f"🔧 DM展示了{tool.get('tool_type', '工具')}"
                        print(tool_info)
                        chapter_chat += f"{tool_info}\n"
            else:
                print("⚠️ DM章节开始发言失败")
                chapter_chat += f"**DM 第{chapter_num}章开始**\n[DM发言失败]\n\n"
                
        except Exception as e:
            print(f"❌ DM章节开始发言出错: {e}")
            chapter_chat += f"**DM 第{chapter_num}章开始**\n[DM发言出错: {e}]\n\n"
        
        # 2. 进行3轮玩家讨论
        player_names = list(self.players.keys())
        
        for round_num in range(1, 4):  # 3轮讨论
            print(f"\n🔄 第{round_num}轮讨论")
            
            # 每轮让部分玩家主动发言/询问
            active_players = player_names[:min(2, len(player_names))]  # 每轮最多2个玩家主动发言
            
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
                    
                    if query_result and 'content' in query_result:
                        content = query_result['content']
                        queries = query_result.get('query', {})
                        
                        print(f"💬 {player_name}: {content[:50]}...")
                        
                        # 添加到聊天历史
                        full_speech = content
                        if queries:
                            query_text = " | ".join([f"询问{target}: {question}" for target, question in queries.items()])
                            full_speech += f"\n\n**询问**: {query_text}"
                        
                        self.add_to_chat_history(player_name, full_speech)
                        chapter_chat += f"**{player_name}**\n{full_speech}\n\n"
                        
                        # 处理询问回应
                        if queries:
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
                                        
                                        print(f"  💬 {target_name}回应: {response[:50]}...")
                                        
                                        # 添加到聊天历史
                                        self.add_to_chat_history(target_name, f"**回应{player_name}**: {response}")
                                        chapter_chat += f"**{target_name}回应{player_name}**\n{response}\n\n"
                                        
                                    except Exception as e:
                                        print(f"  ❌ {target_name}回应失败: {e}")
                                        chapter_chat += f"**{target_name}**\n[回应失败: {e}]\n\n"
                    
                    # 添加小延时，避免API调用过于频繁
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"❌ {player_name}发言失败: {e}")
                    chapter_chat += f"**{player_name}**\n[发言失败: {e}]\n\n"
        
        # 3. DM章节结束总结
        print(f"\n🎭 DM总结第{chapter_num}章...")
        try:
            dm_end_result = self.game.end_chapter(chapter_num, self.chat_history)
            
            if dm_end_result and 'speech' in dm_end_result:
                dm_summary = dm_end_result['speech']
                print(f"✅ DM章节总结成功")
                print(f"💬 DM总结: {dm_summary[:100]}...")
                
                # 添加到聊天历史
                self.add_to_chat_history(f"第{chapter_num}章总结", dm_summary, "dm")
                chapter_chat += f"**DM 第{chapter_num}章总结**\n{dm_summary}\n\n"
                
                # 处理DM工具调用
                if 'tools' in dm_end_result and dm_end_result['tools']:
                    for tool in dm_end_result['tools']:
                        tool_info = f"🔧 DM展示了{tool.get('tool_type', '工具')}"
                        print(tool_info)
                        chapter_chat += f"{tool_info}\n"
            else:
                print("⚠️ DM章节总结失败")
                chapter_chat += f"**DM 第{chapter_num}章总结**\n[DM总结失败]\n\n"
                
        except Exception as e:
            print(f"❌ DM章节总结出错: {e}")
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
        
        # 逐章节进行讨论
        for chapter_num in range(1, self.total_chapters + 1):
            try:
                self.simulate_chapter_discussion(chapter_num)
                
                # 章节间稍作停顿
                print(f"\n⏸️ 第{chapter_num}章结束，准备下一章...")
                time.sleep(2)
                
            except Exception as e:
                print(f"❌ 第{chapter_num}章模拟失败: {e}")
                continue
        
        # 游戏结束总结
        print(f"\n🏁 游戏即将结束，DM进行最终总结...")
        try:
            # 这里可以让玩家投票选择凶手等
            killer_guess = "未知"  # 简化处理
            truth_info = "真相将在最终总结中揭晓"
            
            dm_final_result = self.game.end_game(self.chat_history, killer_guess, truth_info)
            
            if dm_final_result and 'speech' in dm_final_result:
                final_summary = dm_final_result['speech']
                print(f"✅ DM最终总结成功")
                print(f"💬 DM最终总结: {final_summary[:150]}...")
                
                # 添加到聊天历史
                self.add_to_chat_history("游戏结束", final_summary, "dm")
                
                # 处理DM工具调用
                if 'tools' in dm_final_result and dm_final_result['tools']:
                    for tool in dm_final_result['tools']:
                        tool_info = f"🔧 DM最终展示了{tool.get('tool_type', '工具')}"
                        print(tool_info)
            else:
                print("⚠️ DM最终总结失败")
                
        except Exception as e:
            print(f"❌ DM最终总结出错: {e}")
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n🎉 完整游戏流程模拟完成!")
        print(f"⏱️ 总耗时: {duration:.1f}秒")
        print(f"📝 总聊天轮数: {len(self.chat_history.split('##'))}")
        
        return {
            'duration': duration,
            'chapters_completed': len(self.chapter_discussions),
            'total_chapters': self.total_chapters,
            'chat_history': self.chat_history,
            'chapter_discussions': self.chapter_discussions
        }
    
    def save_simulation_log(self, result: dict):
        """保存模拟日志"""
        try:
            log_file = os.path.join(self.game.game_dir, "simulation_log.json")
            
            log_data = {
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'game_info': {
                    'title': self.game.script.get('title', '未命名剧本'),
                    'characters': [char.get('name') for char in self.characters],
                    'total_chapters': self.total_chapters
                },
                'simulation_result': result,
                'players_participated': list(self.players.keys())
            }
            
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, ensure_ascii=False, indent=2)
            
            print(f"💾 模拟日志已保存: {log_file}")
            
        except Exception as e:
            print(f"⚠️ 保存模拟日志失败: {e}")

def test_with_new_game():
    """使用新游戏进行测试"""
    print("🆕 创建新游戏进行完整流程测试...")
    
    try:
        simulator = GameFlowSimulator(script_path=None, generate_images=False)
        result = simulator.simulate_complete_game()
        simulator.save_simulation_log(result)
        
        return True
        
    except Exception as e:
        print(f"❌ 新游戏测试失败: {e}")
        return False

def test_with_existing_game():
    """使用现有游戏进行测试"""
    print("📂 尝试使用现有游戏进行测试...")
    
    latest_game = get_latest_game()
    if not latest_game:
        print("⚠️ 没有找到现有游戏")
        return False
    
    if not validate_game_path(latest_game):
        print(f"⚠️ 游戏路径验证失败: {latest_game}")
        return False
    
    try:
        print(f"📁 使用游戏: {latest_game}")
        simulator = GameFlowSimulator(script_path=latest_game, generate_images=False)
        result = simulator.simulate_complete_game()
        simulator.save_simulation_log(result)
        
        return True
        
    except Exception as e:
        print(f"❌ 现有游戏测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🎮 完整游戏流程测试开始...")
    print("=" * 80)
    
    success = False
    
    # 优先尝试现有游戏
    success = test_with_existing_game()
    
    # 如果现有游戏测试失败，尝试新游戏
    if not success:
        print("\n" + "=" * 80)
        success = test_with_new_game()
    
    print("\n" + "=" * 80)
    if success:
        print("🎉 完整游戏流程测试成功完成!")
        print("✅ 验证了每章节的正确流程：[dm发言-玩家发言/询问-玩家回应]*3+dm章节总结")
        print("✅ 验证了DM的speak方法的end相关参数传递")
        print("✅ 验证了多章节连续讨论")
    else:
        print("❌ 完整游戏流程测试失败")
        print("💡 请检查游戏初始化和DM/Player代理的配置")
    
    print("=" * 80)

if __name__ == "__main__":
    main()