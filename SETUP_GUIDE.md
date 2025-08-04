# 🚀 AI聊天应用安装指南

## 📋 前提条件

1. **Python 3.7+** - 确保已安装Python 3.7或更高版本
2. **OpenAI API密钥** - 你提供的密钥：`sk-fb535aeda39f42d0b8f7039b98699374`
3. **网络连接** - 用于下载依赖包和调用OpenAI API

## 🔧 快速安装

### 步骤1：安装依赖

```bash
# 方法一：使用自动安装脚本（推荐）
python install.py

# 方法二：手动安装
pip install -r requirements.txt
```

### 步骤2：启动应用

```bash
# 使用启动脚本（包含检查功能）
python run.py

# 或直接运行应用
python app.py
```

### 步骤3：访问应用

浏览器访问：http://localhost:5000

## 🔑 默认账户

| 角色 | 用户名 | 密码 | 说明 |
|------|--------|------|------|
| 管理员 | admin | admin123 | 具有管理权限 |
| 普通用户 | test | test123 | 普通聊天用户 |

## 🤖 AI功能说明

### OpenAI配置

应用已预配置你的API密钥，无需额外设置：
- **模型**: GPT-3.5-turbo
- **API密钥**: sk-fb535aeda39f42d0b8f7039b98699374
- **最大回复长度**: 1000 tokens
- **创造性**: 0.7 (适中)

### AI功能特色

1. **智能对话**: 基于GPT-3.5-turbo的真实AI对话
2. **上下文记忆**: 记住对话历史，提供连贯回复
3. **Markdown输出**: AI回复支持完整Markdown格式
4. **多轮对话**: 支持复杂的对话流程
5. **意图分析**: 分析用户消息意图和关键词

## 📱 功能使用指南

### 1. 用户注册/登录

1. 访问 http://localhost:5000/register 注册新账户
2. 或使用默认账户直接登录
3. 登录后自动跳转到首页

### 2. 开始聊天

1. 点击"进入聊天室"或访问 http://localhost:5000/chat
2. 在输入框中输入消息
3. AI会智能回复，支持Markdown格式
4. 可以进行多轮对话

### 3. 高级功能

- **聊天历史**: 点击用户头像 → 聊天历史
- **个人资料**: 查看统计信息和账户详情
- **数据导出**: 导出聊天记录为JSON或Markdown
- **AI测试**: 访问 http://localhost:5000/api/ai/test

## 🌐 API接口测试

### 测试AI服务

```bash
curl http://localhost:5000/api/ai/test
```

### 发送消息（需要登录）

```bash
curl -X POST http://localhost:5000/api/chat/send \
  -H "Content-Type: application/json" \
  -d '{"message": "你好，我是测试消息"}'
```

### 分析消息意图

```bash
curl -X POST http://localhost:5000/api/ai/analyze \
  -H "Content-Type: application/json" \
  -d '{"message": "帮我写一个Python函数"}'
```

## 🛠️ 故障排除

### 常见问题

1. **依赖安装失败**
   ```bash
   # 升级pip后重试
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

2. **AI服务连接失败**
   - 检查网络连接
   - 确认API密钥有效
   - 查看控制台错误信息

3. **端口占用**
   ```bash
   # 查看端口使用情况
   netstat -ano | findstr :5000
   # 或使用其他端口
   python app.py  # 然后修改app.run中的port参数
   ```

4. **数据库错误**
   ```bash
   # 删除数据库文件重新初始化
   del chat_app.db  # Windows
   rm chat_app.db   # Linux/Mac
   ```

### 日志查看

启动应用时，控制台会显示详细的状态信息：
- ✅ 成功信息（绿色）
- ⚠️ 警告信息（黄色）
- ❌ 错误信息（红色）

## 🔧 自定义配置

### 修改AI行为

编辑 `ai_service.py` 中的系统提示词：

```python
self.system_prompt = """你是一个友好、有帮助的AI助手。
你的回答应该：
1. 准确、有用、富有洞察力
2. 支持Markdown格式输出
3. 保持对话的连贯性和上下文理解
4. 用中文回答（除非用户特别要求其他语言）
"""
```

### 修改模型参数

在 `config.py` 中调整：

```python
OPENAI_MODEL = 'gpt-3.5-turbo'  # 或 gpt-4
OPENAI_MAX_TOKENS = 1000        # 回复最大长度
OPENAI_TEMPERATURE = 0.7        # 创造性 (0-1)
```

## 📞 技术支持

如果遇到问题：

1. **检查日志**: 查看控制台输出的详细错误信息
2. **验证环境**: 确保Python版本和依赖包正确安装
3. **测试网络**: 确认可以访问OpenAI API
4. **重启应用**: 有时简单重启可以解决问题

## 🎯 下一步

- 探索AI聊天功能的各种用法
- 自定义界面主题和工具按钮
- 尝试不同的对话场景和话题
- 查看个人资料中的使用统计
- 导出有趣的聊天记录

祝你使用愉快！🎉