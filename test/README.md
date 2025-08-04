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
```

### 测试特定功能
```bash
# 进入测试目录
cd test

# 运行单个测试
python test_player.py
python demo_json_query.py
python demo_response_api.py
```

## 📊 测试覆盖

- ✅ **PlayerAgent.query()** - 主动发言功能（返回JSON格式）
- ✅ **PlayerAgent.response()** - 被动回应功能（字符串格式）
  - 必须指定具体问题和提问者
  - 根据具体问题和提问者生成精准回应
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

### 调试提示
- 使用 `python -v test/test_player.py` 查看详细输出
- 检查log目录中的日志文件
- 确认剧本文件格式正确

---

📞 **需要帮助?** 请参考项目根目录的README.md或SETUP_GUIDE.md文件。