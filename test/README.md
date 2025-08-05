# 测试和演示脚本目录

这个目录包含了项目开发过程中创建的各种测试和演示脚本。

## 📁 文件说明

### 🧪 测试脚本

#### `test_player.py`
- **用途**: 测试PlayerAgent的功能
- **功能**: 
  - 测试query方法（主动发言，返回JSON格式）
  - 测试response方法（被动回应）
  - 多场景测试
- **运行**: `python test/test_player.py`
- **返回格式**: 
  ```json
  {
    "content": "发言内容（markdown格式）",
    "query": {"人名": "问题内容"}
  }
  ```

#### `test_dm_image.py`
- **用途**: 测试DMAgent的图片生成功能
- **功能**:
  - 测试单张图片生成
  - 测试角色图片生成
  - 测试线索图片生成
  - 错误处理和环境检查
- **运行**: `python test/test_dm_image.py`
- **依赖**: 阿里云百炼API密钥

#### `test_game.py`
- **用途**: 测试Game类的完整功能
- **功能**:
  - 测试动态剧本生成 + 图片生成
  - 测试现有剧本加载
  - 测试选择性图片生成
  - 错误处理和边界情况
- **运行**: `python test/test_game.py`
- **依赖**: DMAgent和PlayerAgent

### 🎯 演示脚本

#### `demo_json_query.py`
- **用途**: 演示PlayerAgent的JSON格式输出功能
- **功能**:
  - 展示JSON格式的基本用法
  - 多场景演示
  - JSON结构说明
- **运行**: `python test/demo_json_query.py`

#### `demo_response_api.py`
- **用途**: 演示PlayerAgent.response()方法的新API
- **功能**:
  - 展示必选参数query和query_player的用法
  - 不同问题类型的针对性回应演示
  - API变更说明和错误处理
- **运行**: `python test/demo_response_api.py`

## 🚀 快速开始

### 运行所有测试
```bash
# 测试PlayerAgent功能
python test/test_player.py

# 演示JSON格式输出
python test/demo_json_query.py

# 演示response方法新API
python test/demo_response_api.py

# 测试图片生成功能
python test/test_dm_image.py

# 测试游戏类功能
python test/test_game.py
```

### 测试特定功能
```bash
# 进入测试目录
cd test

# 运行单个测试
python test_player.py
python demo_json_query.py
python demo_response_api.py
python test_dm_image.py
python test_game.py
```

## 📊 测试覆盖

- ✅ **PlayerAgent.query()** - 主动发言功能（返回JSON格式）
- ✅ **PlayerAgent.response()** - 被动回应功能（字符串格式）
  - 必须指定具体问题和提问者
  - 根据具体问题和提问者生成精准回应
- ✅ **DMAgent.gen_image()** - 图片生成功能（阿里云百炼）
  - 异步任务提交和轮询
  - 角色图片生成
  - 线索图片生成
  - 本地图片下载和保存
- ✅ **Game类功能** - 完整游戏流程
  - 动态剧本生成和现有剧本加载
  - 自动角色和线索图片生成
  - 图片信息管理和保存
  - PlayerAgent集成
- ✅ **JSON格式输出** - 结构化数据返回
- ✅ **多场景测试** - 不同角色的行为验证
- ✅ **错误处理** - 异常情况的处理

## 💡 使用说明

### PlayerAgent基本用法
```python
from player_agent import PlayerAgent

# 创建玩家
player = PlayerAgent("李华")

# 主动发言（返回JSON）
result = player.query(scripts, chat_history)
content = result['content']
queries = result['query']

# 被动回应（返回字符串，必须指定问题和提问者）
response = player.response(scripts, chat_history, 
                          query="你昨晚在做什么？", 
                          query_player="李华")
```

### DMAgent基本用法
```python
from dm_agent import DMAgent

# 创建DM
dm = DMAgent()

# 生成剧本
script = dm.gen_script()

# 生成图片
image_result = dm.gen_image("一间豪华的书房，深色木质书桌，昏暗的灯光")

if image_result and image_result.get('success'):
    print(f"图片URL: {image_result['url']}")
    print(f"本地文件: {image_result['local_path']}")
else:
    print(f"生成失败: {image_result.get('error_message')}")
```

### Game类基本用法
```python
from game import Game

# 方式1: 动态生成剧本并生成所有图片（完整流程）
game1 = Game()

# 方式2: 使用现有剧本，不生成图片
game2 = Game(script_path='log/250108123456/script.json', generate_images=False)

# 方式3: 仅生成角色图片
game3 = Game(generate_images=False)
game3._generate_character_images()

# 获取游戏信息
game_dir = game1.get_game_directory()  # 获取游戏目录
character_image = game1.get_character_image('角色名')
clue_images = game1.get_clue_images(1)  # 第1章线索
all_images = game1.get_all_character_images()

# 游戏信息自动保存为 game_info.json
# 包含完整的统计和文件结构信息

# 访问剧本和玩家信息
print(f"剧本标题: {game1.script['title']}")
print(f"角色列表: {game1.script['characters']}")
print(f"游戏目录: {game1.get_game_directory()}")
print(f"玩家代理: {[agent.name for agent in game1.player_agents]}")

# 新的目录结构
# log/YYMMDDhhmmss/
# ├── script.json
# ├── game_info.json  
# └── imgs/
#     ├── 角色名.png
#     └── clue-ch1-1.png
```

### JSON格式说明
```json
{
  "content": "我觉得我们需要分析一下时间线...",
  "query": {
    "王强": "你昨晚具体在哪里？",
    "张雪": "你有注意到异常吗？"
  }
}
```

## 🔧 开发说明

### 添加新测试
1. 在test目录下创建新的测试文件
2. 遵循命名规范：`test_*.py` 或 `demo_*.py`
3. 包含必要的错误处理和结果验证
4. 更新本README文件

### 测试环境要求
- Python 3.7+
- 已安装项目依赖 (`pip install -r requirements.txt`)
- 配置了OpenAI API密钥
- 网络连接正常

## 📝 历史记录

- **2025-01-08**: 创建test目录，移动测试脚本
- **2025-01-08**: 修改PlayerAgent.query()返回JSON格式
- **2025-01-08**: 添加demo_json_query.py演示脚本
- **2025-01-08**: 优化测试脚本的输出格式和错误处理
- **2025-01-08**: 为PlayerAgent.response()方法添加query和query_player参数（必选）
- **2025-01-08**: 完成DMAgent.gen_image()图片生成功能（阿里云百炼）
- **2025-01-08**: 增强Game类，支持剧本加载和完整图片生成流程
- **2025-01-08**: 重构文件存储结构，使用带时间戳的游戏目录

## 🐛 故障排除

### 常见问题

1. **ImportError: No module named 'openai'**
   - 解决: 运行 `python install.py` 安装依赖

2. **API调用失败**
   - 检查config.py中的API_KEY配置
   - 确认网络连接正常

3. **JSON解析错误**
   - 这是正常现象，脚本有容错机制
   - 会自动返回默认格式

4. **图片生成失败**
   - 检查阿里云百炼API密钥是否正确配置
   - 确认网络连接稳定，可以访问dashscope.aliyuncs.com
   - 检查提示词是否符合内容安全要求

5. **图片生成超时**
   - 默认超时时间为300秒，可以调整max_wait_time参数
   - 网络较慢时建议增加轮询间隔poll_interval

6. **图片下载失败**
   - 检查本地images目录是否有写入权限
   - 确认磁盘空间充足

### 调试提示
- 使用 `python -v test/test_player.py` 查看详细输出
- 使用 `python test/test_dm_image.py` 测试图片生成功能
- 使用 `python test/test_game.py` 测试完整游戏流程
- 使用 `python demo_new_structure.py` 查看新目录结构演示
- 检查log目录中的游戏会话
  - `log/YYMMDDhhmmss/` - 游戏会话目录
  - `script.json` - 剧本文件
  - `game_info.json` - 游戏信息和统计
- 检查imgs目录中的生成图片
  - 角色图片命名: `角色名.png`
  - 线索图片命名: `clue-ch章节-序号.png`
- 确认剧本文件格式正确
- 图片生成任务ID可用于追踪问题

---

📞 **需要帮助?** 请参考项目根目录的README.md或SETUP_GUIDE.md文件。