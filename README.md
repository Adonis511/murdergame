# 🤖 AI聊天应用

一个基于Flask和OpenAI的智能聊天应用，支持完整的Markdown语法、用户认证和真实AI对话。

## ✨ 功能特色

- 🤖 **真实AI对话** - 集成OpenAI GPT-3.5-turbo模型
- 🧠 **上下文理解** - 支持多轮对话和历史记忆
- 🎨 **现代化UI设计** - 简洁美观的聊天界面
- 📝 **Markdown支持** - 完整支持Markdown语法渲染
- 🌈 **代码高亮** - 自动识别并高亮显示代码块
- 🔐 **用户认证系统** - 完整的注册、登录、会话管理
- 💾 **数据持久化** - SQLite数据库存储聊天记录
- 🔧 **可配置工具栏** - 灵活的工具按钮配置
- 💾 **数据导出** - 支持JSON和Markdown格式导出
- 📱 **响应式设计** - 适配各种屏幕尺寸
- ⚡ **实时交互** - 流畅的用户体验
- 🛠️ **REST API** - 完整的后端API接口

## 📁 项目结构

```
murdergame/
├── app.py                 # Flask主应用（用户认证、API路由）
├── models.py              # 数据库模型（用户、消息、日志）
├── config.py              # 应用配置（Flask、OpenAI等）
├── ai_service.py          # AI服务模块（OpenAI API集成）
├── install.py             # 自动安装脚本
├── run.py                 # 启动脚本
├── requirements.txt       # Python依赖
├── README.md             # 项目说明
└── template/             # 模板文件
    ├── base.html         # 基础模板（导航栏、样式）
    ├── index.html        # 首页模板
    ├── login.html        # 登录页面
    ├── register.html     # 注册页面
    ├── profile.html      # 个人资料页面
    ├── chat.html         # 聊天界面HTML
    ├── chat.css          # 样式文件
    ├── chat.js           # 前端交互逻辑
    └── config.js         # 配置文件
```

## 🚀 快速开始

### 方法一：自动安装（推荐）

```bash
# 运行自动安装脚本
python install.py

# 启动应用
python run.py
```

### 方法二：使用启动脚本

```bash
# 运行启动脚本（会检查依赖）
python run.py
```

### 方法三：手动安装

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 启动应用
python app.py
```

### 3. 访问应用

启动成功后，在浏览器中访问：

- **聊天界面**: http://localhost:5000/chat
- **登录页面**: http://localhost:5000/login
- **注册页面**: http://localhost:5000/register
- **个人资料**: http://localhost:5000/profile
- **应用首页**: http://localhost:5000/
- **API状态**: http://localhost:5000/api/status
- **AI测试**: http://localhost:5000/api/ai/test

## 🎮 使用指南

### 用户认证

1. **注册账户**: 访问注册页面，填写用户名、邮箱、密码等信息
2. **登录系统**: 使用注册的账户信息登录
3. **默认账户**: 系统提供了测试账户（admin/admin123, test/test123）

### AI聊天功能

1. **智能对话**: 登录后进入聊天室，AI会根据你的消息智能回复
2. **上下文理解**: AI能理解对话历史，提供连贯的回复
3. **Markdown渲染**: AI回复支持完整的Markdown格式
4. **多轮对话**: 支持复杂的多轮对话和话题切换

### 基础操作

1. **发送消息**: 在输入框中输入文本，按Enter或点击发送按钮
2. **换行**: 按Shift+Enter可以在消息中换行
3. **Markdown**: 直接输入Markdown语法，会自动渲染
4. **聊天历史**: 点击用户菜单可以加载历史聊天记录

### Markdown语法支持

| 语法 | 效果 |
|------|------|
| `**粗体**` | **粗体文本** |
| `*斜体*` | *斜体文本* |
| `\`代码\`` | `行内代码` |
| `# 标题` | 各级标题 |
| `- 列表项` | 无序列表 |
| `1. 列表项` | 有序列表 |
| `> 引用` | 引用文本 |

### 代码块示例

````markdown
```javascript
function hello() {
    console.log("Hello World!");
}
```
````

### 工具按钮说明

- 🗑️ **清空**: 清空所有聊天记录
- 💾 **保存**: 保存聊天记录为JSON文件
- ⚙️ **设置**: 调整主题、字体等设置
- ❓ **帮助**: 查看帮助文档
- 📄 **导出**: 导出聊天记录为Markdown文件

## 🔧 配置说明

### AI配置

应用使用OpenAI API，相关配置在 `config.py` 中：

```python
class Config:
    # OpenAI API配置
    OPENAI_API_KEY = 'your-api-key-here'  # 你的OpenAI API密钥
    OPENAI_MODEL = 'gpt-3.5-turbo'        # 使用的模型
    OPENAI_MAX_TOKENS = 1000              # 最大回复长度
    OPENAI_TEMPERATURE = 0.7              # 创造性程度(0-1)
```

### 环境变量

创建 `.env` 文件来配置环境变量：

```env
# OpenAI API配置
OPENAI_API_KEY=sk-your-api-key-here

# Flask配置
SECRET_KEY=your-secret-key-here
FLASK_DEBUG=True

# AI聊天配置
AI_MODEL=gpt-3.5-turbo
AI_MAX_TOKENS=1000
AI_TEMPERATURE=0.7
```

### 工具栏配置

在 `template/config.js` 中可以自定义工具按钮：

```javascript
toolButtons: [
    {
        id: 'customBtn',
        icon: '<svg>...</svg>',
        label: '自定义',
        title: '自定义功能',
        action: 'customAction',
        visible: true
    }
]
```

### 主题配置

支持浅色和深色主题，可在设置中切换或通过配置文件自定义：

```javascript
themes: {
    custom: {
        name: '自定义主题',
        primary: '#your-color',
        background: '#your-bg',
        // ...更多配置
    }
}
```

## 🌐 API接口

### 发送消息

```bash
POST /api/chat/send
Content-Type: application/json

{
    "message": "你的消息内容"
}
```

### 获取聊天历史

```bash
GET /api/chat/history
```

### 获取配置信息

```bash
GET /api/config
```

### API状态检查

```bash
GET /api/status
```

### AI服务测试

```bash
GET /api/ai/test
```

### 消息意图分析

```bash
POST /api/ai/analyze
Content-Type: application/json

{
    "message": "你的消息内容"
}
```

## 🛠️ 开发说明

### 技术栈

- **后端**: Flask (Python)
- **AI服务**: OpenAI GPT-3.5-turbo
- **数据库**: SQLite + SQLAlchemy
- **用户认证**: Flask-Login
- **表单处理**: Flask-WTF + WTForms
- **前端**: 原生JavaScript + HTML5 + CSS3
- **UI框架**: Bootstrap 5
- **Markdown**: Marked.js
- **代码高亮**: Highlight.js
- **图标**: Font Awesome + SVG图标

### 自定义开发

1. **添加新的工具按钮**:
   - 在 `config.js` 中添加按钮配置
   - 在 `chat.js` 中实现对应的方法

2. **修改AI行为**:
   - 编辑 `ai_service.py` 中的系统提示词
   - 调整模型参数（temperature、max_tokens等）
   - 添加新的AI功能接口

3. **扩展数据库**:
   - 在 `models.py` 中添加新的数据模型
   - 创建数据库迁移脚本

4. **修改样式**:
   - 编辑 `chat.css` 和模板文件
   - 使用CSS变量便于主题切换

5. **扩展API**:
   - 在 `app.py` 中添加新的路由
   - 支持更多AI模型、第三方服务集成等

### 环境要求

- Python 3.7+
- OpenAI API密钥
- 现代浏览器（支持ES6+）

## 📄 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目！

## 📞 支持

如果遇到问题或需要帮助，请：

1. 查看本README文档
2. 检查浏览器控制台是否有错误信息
3. 确认所有依赖已正确安装
4. 验证Python版本兼容性

---

💡 **提示**: 这个聊天界面可以很容易地集成到现有项目中，或者作为独立的聊天工具使用。