from ai_service import AIService
from openai import OpenAI
from config import Config
import json
import time
from datetime import datetime
class DMAgent:
    def __init__(self):
        # self.name = name
        # self.description = description
        # self.goals = goals
        # self.constraints = constraints
        # self.tools = tools
        self.system_prompt = """你是一名专业的剧本杀DM，负责创作完整的剧本杀剧本。

你需要完成以下工作：
1. 编写一个完整的剧本杀剧本，涉及4-6个角色，包含谋杀悬疑情节
2. 为每个角色创建分章节的剧本，剧本应该像写小说一样生动形象地展开，每章节每个人的剧本体量不少于500字
3. 创建DM专用的上帝视角剧本，用于推进游戏
4. 设计每阶段的线索和图像提示词
5. 创建角色图像生成提示词

重要要求：
- 必须返回纯JSON格式，不要用markdown代码块包装
- 确保JSON格式正确，可以直接解析
- 所有中文内容要完整清晰"""
        self.client = OpenAI(
            base_url=Config.API_BASE,
            api_key=Config.API_KEY,
        )
    def gen_script(self):
        print("start generating script")
        start = time.time()
        completion = self.client.chat.completions.create(
        model="qwen-plus",
        temperature=0.7,
        messages=[
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": """请创作一个剧本杀剧本，主题为豪门谋杀案。

创作步骤：
1. 设计4-6个角色，为他们取名
2. 创建DM章节（上帝视角）
3. 为每个角色创建分章节剧本
4. 设计线索和图像提示词

输出格式要求（纯JSON，不要markdown包装）：
{
  "title": "剧本标题",
  "theme": "剧本主题",
  "characters": ["角色1姓名", "角色2姓名", "角色3姓名", "角色4姓名"],
  "角色1姓名": ["第一章剧本内容", "第二章剧本内容", "第三章剧本内容"],
  "角色2姓名": ["第一章剧本内容", "第二章剧本内容", "第三章剧本内容"],
  "角色3姓名": ["第一章剧本内容", "第二章剧本内容", "第三章剧本内容"],
  "角色4姓名": ["第一章剧本内容", "第二章剧本内容", "第三章剧本内容"],
  "dm": ["DM第一章指引", "DM第二章指引", "DM第三章指引", "真相揭露"],
  "clues": [["第一章线索1", "第一章线索2"], ["第二章线索1", "第二章线索2"], ["第三章线索1", "第三章线索2"]],
  "clue_image_prompts": [["第一章线索1图像提示", "第一章线索2图像提示"], ["第二章线索1图像提示", "第二章线索2图像提示"]],
  "character_image_prompts": {
    "角色1姓名": "角色1的AI绘图提示词",
    "角色2姓名": "角色2的AI绘图提示词",
    "角色3姓名": "角色3的AI绘图提示词",
    "角色4姓名": "角色4的AI绘图提示词"
  }
}

请直接输出JSON，不要添加任何解释或markdown格式。"""},
            ],
        )
        end = time.time()
        print(f"script generated in {end - start} seconds")
        
        # 获取AI响应内容
        response_content = completion.choices[0].message.content
        print("Raw response preview:", response_content[:200])
        
        # 生成时间戳 (YYMMDDhhmmss格式)
        timestamp = datetime.now().strftime("%y%m%d%H%M%S")
        print(f"生成时间戳: {timestamp}")
        
        # 确保log目录存在
        import os
        os.makedirs("log", exist_ok=True)
        
        # 使用UTF-8编码写入文件（带时间戳）
        script_filename = f"log/script_{timestamp}.txt"
        with open(script_filename, "w", encoding="utf-8") as f:
            f.write(response_content)
        print(f"原始内容已保存到: {script_filename}")
        
        try:
            # 尝试解析JSON
            # 如果响应被包在```json代码块中，需要先提取
            if response_content.strip().startswith("```json"):
                # 提取JSON内容
                json_start = response_content.find("{")
                json_end = response_content.rfind("}") + 1
                if json_start != -1 and json_end != 0:
                    json_content = response_content[json_start:json_end]
                else:
                    json_content = response_content
            else:
                json_content = response_content
            
            # 解析JSON
            script_data = json.loads(json_content)
            
            # 保存格式化的JSON（带时间戳）
            formatted_filename = f"log/script_formatted_{timestamp}.json"
            with open(formatted_filename, "w", encoding="utf-8") as f:
                json.dump(script_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 剧本生成成功！已保存到 {formatted_filename}")
            return script_data
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON解析失败: {e}")
            print(f"原始响应已保存到 {script_filename}，请查看内容")
            
            # 尝试手动修复JSON格式
            try:
                # 移除可能的markdown代码块标记
                cleaned_content = response_content.replace("```json", "").replace("```", "").strip()
                script_data = json.loads(cleaned_content)
                
                formatted_filename = f"log/script_formatted_{timestamp}.json"
                with open(formatted_filename, "w", encoding="utf-8") as f:
                    json.dump(script_data, f, ensure_ascii=False, indent=2)
                
                print(f"✅ JSON修复成功！已保存到 {formatted_filename}")
                return script_data
                
            except Exception as repair_error:
                print(f"❌ JSON修复也失败: {repair_error}")
                return None
if __name__ == "__main__":
    dm_agent = DMAgent()
    print(dm_agent.gen_script())
