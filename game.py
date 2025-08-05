from dm_agent import DMAgent    
from player_agent import PlayerAgent
import json
import os
import time

class Game:
    def __init__(self, script_path=None, generate_images=True):
        """
        初始化游戏
        
        Args:
            script_path: 游戏目录路径，None则动态生成新游戏
            generate_images: 是否生成角色和线索图片（仅对新游戏有效）
        """
        print("🎮 初始化剧本杀游戏...")
        
        self.dm_agent = DMAgent()
        self.character_images = {}  # 存储角色图片信息
        self.clue_images = {}       # 存储线索图片信息
        
        if script_path:
            # 加载现有游戏
            self._load_existing_game(script_path)
        else:
            # 创建新游戏
            self._create_new_game(generate_images)
        
        # 创建玩家代理
        self.player_agents = []
        characters = self.script.get("characters", [])
        for character in characters:
            self.player_agents.append(PlayerAgent(character))
            print(f"🎭 创建角色: {character}")
        
        self.chapter = 0
        
        print("🎉 游戏初始化完成!")
        print(f"📂 游戏资源目录: {self.game_dir}")
    
    def _load_existing_game(self, script_path: str):
        """加载现有游戏目录"""
        if not os.path.isdir(script_path):
            raise ValueError(f"❌ 游戏目录不存在: {script_path}")
        
        print(f"📖 加载现有游戏: {script_path}")
        
        # 设置游戏目录
        self.game_dir = script_path
        self.imgs_dir = os.path.join(self.game_dir, "imgs")
        
        # 验证必要文件
        script_file = os.path.join(self.game_dir, "script.json")
        if not os.path.exists(script_file):
            raise ValueError(f"❌ 剧本文件不存在: {script_file}")
        
        # 加载剧本
        self.script = self._load_script(script_file)
        if not self.script:
            raise ValueError("❌ 剧本加载失败!")
        
        print(f"✅ 剧本加载成功: {self.script.get('title', '未命名剧本')}")
        print(f"👥 角色数量: {len(self.script.get('characters', []))}")
        
        # 检查并加载现有图片
        self._load_existing_images()
        
        # 加载游戏信息（如果存在）
        info_file = os.path.join(self.game_dir, "game_info.json")
        if os.path.exists(info_file):
            print(f"📄 游戏信息文件: {info_file}")
        else:
            print("⚠️ 游戏信息文件不存在，可能是旧版本游戏")
    
    def _create_new_game(self, generate_images: bool):
        """创建新游戏"""
        # 创建带时间戳的游戏目录
        timestamp = time.strftime("%y%m%d%H%M%S")
        self.game_dir = f"log/{timestamp}"
        self.imgs_dir = os.path.join(self.game_dir, "imgs")
        
        # 创建目录结构
        os.makedirs(self.game_dir, exist_ok=True)
        os.makedirs(self.imgs_dir, exist_ok=True)
        print(f"📁 创建游戏目录: {self.game_dir}")
        
        # 生成新剧本
        print("🎭 开始生成新剧本...")
        self.script = self.dm_agent.gen_script()
        
        if not self.script:
            raise ValueError("❌ 剧本生成失败!")
        
        # 保存剧本到游戏目录
        script_file = os.path.join(self.game_dir, "script.json")
        self._save_script(script_file)
        
        print(f"✅ 剧本生成成功: {self.script.get('title', '未命名剧本')}")
        print(f"👥 角色数量: {len(self.script.get('characters', []))}")
        print(f"📄 剧本文件: {script_file}")
        
        # 生成图片
        if generate_images:
            self._generate_character_images()
            self._generate_clue_images()
        
        # 保存游戏信息
        self.save_game_info()
    
    def _load_existing_images(self):
        """加载现有图片信息"""
        if not os.path.exists(self.imgs_dir):
            print("⚠️ 图片目录不存在")
            return
        
        print(f"🖼️ 检查现有图片...")
        
        # 加载角色图片
        characters = self.script.get('characters', [])
        for character in characters:
            img_file = os.path.join(self.imgs_dir, f"{character}.png")
            if os.path.exists(img_file):
                self.character_images[character] = {
                    'success': True,
                    'local_path': img_file,
                    'filename': f"{character}.png",
                    'loaded_from_disk': True
                }
                print(f"✅ 找到角色图片: {character}")
            else:
                print(f"⚠️ 缺少角色图片: {character}")
                self.character_images[character] = None
        
        # 加载线索图片
        clue_prompts = self.script.get('clue_image_prompts', [])
        for chapter_idx, chapter_clues in enumerate(clue_prompts):
            chapter_num = chapter_idx + 1
            if chapter_num not in self.clue_images:
                self.clue_images[chapter_num] = []
            
            for clue_idx, prompt in enumerate(chapter_clues):
                clue_name = f"第{chapter_num}章线索{clue_idx + 1}"
                filename = f"clue-ch{chapter_num}-{clue_idx + 1}.png"
                img_file = os.path.join(self.imgs_dir, filename)
                
                if os.path.exists(img_file):
                    clue_info = {
                        'name': clue_name,
                        'prompt': prompt,
                        'image_result': {
                            'success': True,
                            'local_path': img_file,
                            'filename': filename,
                            'loaded_from_disk': True
                        }
                    }
                    print(f"✅ 找到线索图片: {clue_name}")
                else:
                    clue_info = {
                        'name': clue_name,
                        'prompt': prompt,
                        'image_result': None
                    }
                    print(f"⚠️ 缺少线索图片: {clue_name}")
                
                self.clue_images[chapter_num].append(clue_info)
        
        # 统计现有图片
        char_count = sum(1 for img in self.character_images.values() if img and img.get('success'))
        clue_count = 0
        total_clues = 0
        for chapter_clues in self.clue_images.values():
            total_clues += len(chapter_clues)
            clue_count += sum(1 for clue in chapter_clues 
                            if clue['image_result'] and clue['image_result'].get('success'))
        
        print(f"📊 现有图片统计:")
        print(f"   角色图片: {char_count}/{len(characters)} 个")
        print(f"   线索图片: {clue_count}/{total_clues} 个")
    
    def _load_script(self, script_path: str) -> dict:
        """从JSON文件加载剧本"""
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                script = json.load(f)
            
            # 验证剧本格式
            required_keys = ['title', 'characters', 'dm']
            for key in required_keys:
                if key not in script:
                    print(f"⚠️ 剧本缺少必要字段: {key}")
            
            return script
            
        except json.JSONDecodeError as e:
            print(f"❌ 剧本文件格式错误: {e}")
            return None
        except Exception as e:
            print(f"❌ 加载剧本失败: {e}")
            return None
    
    def _save_script(self, script_file: str):
        """保存剧本到指定文件"""
        try:
            with open(script_file, 'w', encoding='utf-8') as f:
                json.dump(self.script, f, ensure_ascii=False, indent=2)
            print(f"💾 剧本已保存: {script_file}")
        except Exception as e:
            print(f"❌ 剧本保存失败: {e}")
    
    def _download_image(self, image_url: str, filename: str) -> str:
        """下载图片到指定位置"""
        try:
            import requests
            
            # 下载图片
            response = requests.get(image_url, timeout=60)
            response.raise_for_status()
            
            # 保存图片到imgs目录
            local_path = os.path.join(self.imgs_dir, filename)
            with open(local_path, 'wb') as f:
                f.write(response.content)
            
            return local_path
            
        except Exception as e:
            print(f"❌ 图片下载失败: {str(e)}")
            return None
    
    def _generate_character_images(self):
        """生成角色图片"""
        character_prompts = self.script.get('character_image_prompts', {})
        
        if not character_prompts:
            print("⚠️ 剧本中没有找到角色图片提示词")
            return
        
        print(f"\n🎨 开始生成角色图片...")
        print(f"📋 需要生成 {len(character_prompts)} 个角色图片")
        
        for i, (character, prompt) in enumerate(character_prompts.items(), 1):
            print(f"\n👤 [{i}/{len(character_prompts)}] 生成角色: {character}")
            print(f"📝 提示词: {prompt[:50]}...")
            
            try:
                # 生成角色图片
                result = self.dm_agent.gen_image(prompt)
                
                if result and result.get('success'):
                    # 下载图片到本地
                    filename = f"{character}.png"
                    local_path = self._download_image(result['url'], filename)
                    
                    if local_path:
                        # 更新结果信息
                        result['local_path'] = local_path
                        result['filename'] = filename
                        self.character_images[character] = result
                        print(f"✅ {character} 图片生成成功!")
                        print(f"📁 保存路径: {local_path}")
                    else:
                        print(f"❌ {character} 图片下载失败!")
                        self.character_images[character] = None
                else:
                    print(f"❌ {character} 图片生成失败!")
                    if result:
                        print(f"   错误: {result.get('error_message')}")
                    self.character_images[character] = None
                
                # 避免API频率限制
                if i < len(character_prompts):
                    print("⏳ 等待3秒避免频率限制...")
                    time.sleep(3)
                    
            except Exception as e:
                print(f"❌ {character} 图片生成异常: {str(e)}")
                self.character_images[character] = None
        
        success_count = sum(1 for result in self.character_images.values() if result and result.get('success'))
        print(f"\n📊 角色图片生成完成: {success_count}/{len(character_prompts)} 成功")
    
    def _generate_clue_images(self):
        """生成线索图片"""
        clue_prompts = self.script.get('clue_image_prompts', [])
        
        if not clue_prompts:
            print("⚠️ 剧本中没有找到线索图片提示词")
            return
        
        print(f"\n🔍 开始生成线索图片...")
        total_clues = sum(len(chapter_clues) for chapter_clues in clue_prompts)
        print(f"📋 需要生成 {total_clues} 个线索图片")
        
        clue_count = 0
        
        for chapter_idx, chapter_clues in enumerate(clue_prompts):
            chapter_num = chapter_idx + 1
            print(f"\n📖 第{chapter_num}章线索:")
            
            if chapter_num not in self.clue_images:
                self.clue_images[chapter_num] = []
            
            for clue_idx, prompt in enumerate(chapter_clues):
                clue_count += 1
                clue_name = f"第{chapter_num}章线索{clue_idx + 1}"
                
                print(f"\n🔍 [{clue_count}/{total_clues}] 生成: {clue_name}")
                print(f"📝 提示词: {prompt[:50]}...")
                
                try:
                    # 生成线索图片
                    result = self.dm_agent.gen_image(prompt)
                    
                    if result and result.get('success'):
                        # 下载图片到本地，使用新的命名格式
                        filename = f"clue-ch{chapter_num}-{clue_idx + 1}.png"
                        local_path = self._download_image(result['url'], filename)
                        
                        if local_path:
                            # 更新结果信息
                            result['local_path'] = local_path
                            result['filename'] = filename
                            clue_info = {
                                'name': clue_name,
                                'prompt': prompt,
                                'image_result': result
                            }
                            self.clue_images[chapter_num].append(clue_info)
                            print(f"✅ {clue_name} 图片生成成功!")
                            print(f"📁 保存路径: {local_path}")
                        else:
                            print(f"❌ {clue_name} 图片下载失败!")
                            clue_info = {
                                'name': clue_name,
                                'prompt': prompt,
                                'image_result': None
                            }
                            self.clue_images[chapter_num].append(clue_info)
                    else:
                        print(f"❌ {clue_name} 图片生成失败!")
                        if result:
                            print(f"   错误: {result.get('error_message')}")
                        clue_info = {
                            'name': clue_name,
                            'prompt': prompt,
                            'image_result': None
                        }
                        self.clue_images[chapter_num].append(clue_info)
                    
                    # 避免API频率限制
                    if clue_count < total_clues:
                        print("⏳ 等待3秒避免频率限制...")
                        time.sleep(3)
                        
                except Exception as e:
                    print(f"❌ {clue_name} 图片生成异常: {str(e)}")
                    clue_info = {
                        'name': clue_name,
                        'prompt': prompt,
                        'image_result': None
                    }
                    self.clue_images[chapter_num].append(clue_info)
        
        # 统计成功数量
        success_count = 0
        for chapter_clues in self.clue_images.values():
            success_count += sum(1 for clue in chapter_clues 
                               if clue['image_result'] and clue['image_result'].get('success'))
        
        print(f"\n📊 线索图片生成完成: {success_count}/{total_clues} 成功")
    
    def get_character_image(self, character: str) -> dict:
        """获取角色图片信息"""
        return self.character_images.get(character)
    
    def get_clue_images(self, chapter: int) -> list:
        """获取指定章节的线索图片"""
        return self.clue_images.get(chapter, [])
    
    def get_all_character_images(self) -> dict:
        """获取所有角色图片信息"""
        return self.character_images
    
    def get_all_clue_images(self) -> dict:
        """获取所有线索图片信息"""
        return self.clue_images
    
    def save_game_info(self):
        """保存游戏信息到游戏目录"""
        info_file = os.path.join(self.game_dir, "game_info.json")
        
        # 统计生成结果
        character_success = sum(1 for result in self.character_images.values() 
                              if result and result.get('success'))
        clue_success = 0
        clue_total = 0
        for chapter_clues in self.clue_images.values():
            clue_total += len(chapter_clues)
            clue_success += sum(1 for clue in chapter_clues 
                              if clue['image_result'] and clue['image_result'].get('success'))
        
        game_info = {
            'game_directory': self.game_dir,
            'script_title': self.script.get('title', '未命名剧本'),
            'characters': self.script.get('characters', []),
            'chapters': len(self.script.get('dm', [])),
            'generation_summary': {
                'characters': {
                    'total': len(self.character_images),
                    'success': character_success,
                    'success_rate': f"{character_success/len(self.character_images)*100:.1f}%" if self.character_images else "0%"
                },
                'clues': {
                    'total': clue_total,
                    'success': clue_success,
                    'success_rate': f"{clue_success/clue_total*100:.1f}%" if clue_total > 0 else "0%"
                }
            },
            'file_structure': {
                'script': 'script.json',
                'images_dir': 'imgs/',
                'character_images': [f"{char}.png" for char in self.script.get('characters', [])],
                'clue_images': [f"clue-ch{ch}-{i+1}.png" 
                              for ch in range(1, len(self.script.get('dm', [])) + 1)
                              for i in range(len(self.script.get('clue_image_prompts', [[]])[ch-1] if ch-1 < len(self.script.get('clue_image_prompts', [])) else []))]
            },
            'detailed_results': {
                'character_images': self.character_images,
                'clue_images': self.clue_images
            },
            'creation_time': time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        try:
            with open(info_file, 'w', encoding='utf-8') as f:
                json.dump(game_info, f, ensure_ascii=False, indent=2, default=str)
            print(f"💾 游戏信息已保存到: {info_file}")
            
            # 显示统计信息
            print(f"\n📊 生成统计:")
            print(f"   角色图片: {character_success}/{len(self.character_images)} 成功")
            print(f"   线索图片: {clue_success}/{clue_total} 成功")
            
        except Exception as e:
            print(f"❌ 保存游戏信息失败: {e}")
    
    def get_game_directory(self) -> str:
        """获取游戏目录路径"""
        return self.game_dir
    
    def get_current_chapter(self) -> int:
        """获取当前章节号"""
        return self.chapter
    
    def get_total_chapters(self) -> int:
        """获取总章节数"""
        return len(self.script.get('dm', []))
    
    def start_chapter(self, chapter_num: int, chat_history: str = "") -> dict:
        """开始新章节，返回DM开场发言"""
        dm_script = self.script.get('dm', [])
        
        print(f"📖 开始第{chapter_num}章 (共{len(dm_script)}章)")
        self.chapter = chapter_num
        
        dm_result = self.dm_agent.speak(
            chapter=chapter_num - 1,  # speak方法从0开始计数
            script=dm_script,
            chat_history=chat_history,
            title=self.script.get('title', '剧本杀游戏'),
            characters=self.script.get('characters', []),
            clues=self.script.get('clues', []),
            base_path=self.game_dir
        )
        
        return dm_result
    
    def end_chapter(self, chapter_num: int, chat_history: str) -> dict:
        """结束当前章节，返回DM总结发言"""
        dm_script = self.script.get('dm', [])
        
        print(f"📖 结束第{chapter_num}章")
        
        dm_result = self.dm_agent.speak(
            chapter=chapter_num - 1,
            script=dm_script,
            chat_history=chat_history,
            is_chapter_end=True,
            title=self.script.get('title', '剧本杀游戏'),
            characters=self.script.get('characters', []),
            clues=self.script.get('clues', []),
            base_path=self.game_dir
        )
        
        return dm_result
    
    def end_game(self, chat_history: str, killer: str = "", truth_info: str = "") -> dict:
        """结束游戏，返回DM最终总结发言"""
        dm_script = self.script.get('dm', [])
        
        print(f"🎉 游戏结束！")
        
        dm_result = self.dm_agent.speak(
            chapter=len(dm_script) - 1,
            script=dm_script,
            chat_history=chat_history,
            is_game_end=True,
            killer=killer,
            truth_info=truth_info,
            title=self.script.get('title', '剧本杀游戏'),
            characters=self.script.get('characters', []),
            clues=self.script.get('clues', []),
            base_path=self.game_dir
        )
        
        return dm_result
    
    def dm_interject(self, chat_history: str, trigger_reason: str = "", guidance: str = "") -> dict:
        """DM穿插发言"""
        dm_script = self.script.get('dm', [])
        
        print(f"🎭 DM穿插发言...")
        
        dm_result = self.dm_agent.speak(
            chapter=self.chapter - 1 if self.chapter > 0 else 0,
            script=dm_script,
            chat_history=chat_history,
            is_interject=True,
            trigger_reason=trigger_reason,
            guidance=guidance,
            title=self.script.get('title', '剧本杀游戏'),
            characters=self.script.get('characters', []),
            clues=self.script.get('clues', []),
            base_path=self.game_dir
        )
        
        return dm_result
    
    def should_dm_interject(self, chat_history: str, message_count_since_last_dm: int = 0) -> bool:
        """判断是否需要DM穿插发言
        
        Args:
            chat_history: 聊天历史
            message_count_since_last_dm: 自上次DM发言后的消息数量
            
        Returns:
            bool: 是否需要DM发言
        """
        # 简单的触发条件逻辑，可以根据需要扩展
        
        # 如果玩家聊天太久没有DM发言
        if message_count_since_last_dm > 10:
            return True
        
        # 如果聊天中出现关键词
        keywords = ["凶手", "线索", "真相", "怀疑", "证据", "推理"]
        recent_messages = chat_history[-500:] if len(chat_history) > 500 else chat_history
        
        keyword_count = sum(1 for keyword in keywords if keyword in recent_messages)
        if keyword_count >= 3:  # 如果最近消息中出现多个关键词
            return True
        
        # 如果聊天变得重复或偏离主题
        if "无话可说" in recent_messages or "不知道" in recent_messages:
            return True
            
        return False
    
if __name__ == "__main__":
    game=Game()
    # game = Game(script_path="log/250805110930")
    print(game.player_agents)
    print(game.chapter)
    

