from ai_service import AIService
from openai import OpenAI
from config import Config
import json
import time
class DMAgent:
    def __init__(self):
        # self.name = name
        # self.description = description
        # self.goals = goals
        # self.constraints = constraints
        # self.tools = tools
        self.system_prompt = """
        你是一名剧本杀dm，你需要完成以下工作：
        1. 编写一个完整的剧本杀剧本，要求剧情涉及4-6个人（每个玩家扮演一个人），分别从每个人物的视角出发，完成剧本的编写，以及一个上帝视角的真实剧本，用于dm自己推进，不提供给玩家
        2. 每个人的剧本需要分阶段，阶段初发放每个人本阶段的剧本，包含需要交谈完成各自的任务。（如谋杀案相互陈述印证）
        3. dm在大家每阶段任务差不多完成时，开启下一个阶段
        4. 每个阶段需要设计一些线索，在特定条件展示给玩家，为了增加代入感，创作剧本时还需生成线索的图像提示词
        5. 在最后一个阶段大家交谈结束后，dm需要揭示所有谜题，点评每个玩家的表现
        6. dm需要在剧本创作后附上给每个玩家的人物图画ai生成提示词，用于ai生成人物图画
        7. 每个人每章节的字数在1000字左右
        """
        self.client = OpenAI(
            base_url=Config.API_BASE,
            api_key=Config.API_KEY,
        )
    def gen_script(self):
        print("start generating script")
        start = time.time()
        completion = self.client.chat.completions.create(
        model="qwen-plus",
        messages=[
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": r"""你需要生成符合要求的剧本，要求以json格式输出，包含剧本内容，线索提示词，人物图画提示词，以及每个阶段需要交谈的内容。
            创作时你应该先思考有哪些人物，为他们取名，然后以系统上帝视角完成dm的每个章节，并思考每个章节可以给出哪些线索，再根据dm章节完成每个人物有限视角下的剧情，最后根据人物性格设计会话提示词
            {"character1_name":["chapter1 of character1","chapter2 of character1"...],
            "character2_name":["chapter1 of character2","chapter2 of character2"...],
            "character3_name":["chapter1 of character3","chapter2 of character3"...],
            "dm":["chapter1 of dm","chapter2 of dm","chapter3 of dm"...],
            "clues:"[[clue1 in chapter1,clue2 in chapter1],[clue1 in chapter1,clue2 in chapter1]...],
            "character1_name_image_prompt":"",
            "character2_name_image_prompt":"",
            "character3_name_image_prompt":"",
            """},
            ],
        )
        end = time.time()
        print(f"script generated in {end - start} seconds")
        with open("log/script.txt", "w") as f:
            f.write(completion.choices[0].message.content)
        return json.loads(completion.choices[0].message.content)
if __name__ == "__main__":
    dm_agent = DMAgent()
    print(dm_agent.gen_script())
