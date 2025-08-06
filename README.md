# 🎭 剧本杀探案团 (Murder Mystery Game)

一个基于AI的多人在线剧本杀游戏平台，支持智能DM主持、角色扮演和案件推理。

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.3.3-green.svg)
![OpenAI](https://img.shields.io/badge/OpenAI-Compatible-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 🌟 核心特性

### 🎮 游戏功能
- **AI智能主持**：自动生成剧本、角色和线索
- **多人在线**：支持3-6人同时游戏
- **实时互动**：WebSocket实时聊天和游戏状态同步
- **角色扮演**：每个玩家获得独特角色和背景故事
- **推理系统**：分阶段推理，包括发言、质疑、投票环节
- **图片生成**：AI自动生成角色头像和线索图片

### 🔐 用户系统
- **个人账户**：每个用户独立的API配置和游戏记录
- **安全认证**：Flask-Login身份验证
- **API配置**：用户级阿里云百炼API密钥管理

### 🎨 用户界面
- **悬疑主题**：暗色调的神秘风格界面
- **响应式设计**：支持桌面和移动端
- **实时状态**：游戏阶段、计时器、玩家状态实时显示
- **富文本支持**：Markdown格式的聊天消息

## 🏗️ 技术架构

### 后端技术栈
```
Flask (Web框架)
├── Flask-SQLAlchemy (数据库ORM)
├── Flask-Login (用户认证)
├── Flask-WTF (表单处理)
└── SQLite (数据库)

AI集成
├── OpenAI API (兼容阿里云百炼)
├── GPT模型 (对话生成)
└── DALL-E模型 (图片生成)
```

### 前端技术栈
```
原生HTML/CSS/JavaScript
├── Bootstrap 5 (UI框架)
├── Font Awesome (图标)
├── WebSocket (实时通信)
└── Marked.js (Markdown渲染)
```

### 核心模块
- **`app.py`** - Flask应用主文件，路由和API
- **`models.py`** - 数据库模型定义
- **`ai_service.py`** - AI服务封装
- **`dm_agent.py`** - DM（主持人）智能代理
- **`player_agent.py`** - 玩家智能代理
- **`game.py`** - 游戏逻辑核心
- **`game_api.py`** - 游戏API接口

## 🚀 快速开始

### 环境要求
- Python 3.8+
- pip包管理器
- 阿里云百炼API密钥

### 1. 克隆项目
```bash
git clone <repository-url>
cd murdergame
```

### 2. 创建虚拟环境
```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
```

### 4. 启动应用
```bash
python app.py
```

### 5. 访问应用
打开浏览器访问：http://localhost:5000

## 🎯 使用指南

### 首次使用
1. **注册账户**：访问 `/register` 创建账户
2. **配置API**：登录后点击设置图标配置阿里云百炼API密钥
3. **开始游戏**：API配置完成后即可开始游戏

### 获取API密钥
1. 访问 [阿里云百炼控制台](https://dashscope.console.aliyun.com/)
2. 注册/登录阿里云账号
3. 开通百炼服务
4. 在"API Key管理"中创建新的API Key
5. 复制API Key到应用配置页面

```

## 🎲 游戏规则

### 游戏流程
1. **角色分配**：每位玩家获得独特角色和背景
2. **案件介绍**：DM介绍案件背景和基本信息
3. **证据收集**：玩家查看线索和证据
4. **自由讨论**：玩家可以自由交流和质疑
5. **推理发言**：每人轮流发表推理观点
6. **投票环节**：投票选出最可疑的人
7. **真相揭晓**：DM公布真相和解析

### 角色系统
- **侦探**：拥有额外线索，推理能力强
- **嫌疑人**：每人都有动机和不在场证明
- **证人**：掌握关键信息片段
- **凶手**：需要隐瞒真相，误导其他玩家

### 胜利条件
- **好人阵营**：找出真正的凶手
- **凶手阵营**：成功隐瞒身份或误导其他人

## 🔧 配置说明

### 环境变量
创建 `.env` 文件配置环境变量：
```env
# Flask配置
SECRET_KEY=your-secret-key-here
FLASK_DEBUG=True

# 数据库配置
DATABASE_URL=sqlite:///chat_app.db

# API配置（可选，优先使用用户配置）
API_KEY=your-api-key-here
API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
MODEL=qwen-plus-0806
MODEL_T2I=wan2.2-t2i-flash
```

### 数据库初始化
应用首次启动时会自动创建数据库和默认用户。如需重置：
```bash
# 删除数据库文件
rm instance/chat_app.db

# 重新启动应用
python app.py
```

## 🔍 故障排除

### 常见问题

**Q: API连接失败怎么办？**
A: 检查API密钥是否正确，网络连接是否正常，确保API服务可用。

**Q: 无法注册新用户？**
A: 检查用户名是否已被使用，邮箱格式是否正确（邮箱可选填）。

**Q: 游戏页面空白？**
A: 确保已配置有效的API密钥，检查浏览器控制台是否有错误信息。

**Q: 图片无法生成？**
A: 确认API密钥有图片生成权限，检查网络连接和API服务状态。

### 日志调试
应用运行时会在控制台输出详细日志：
```bash
python app.py
# 查看API调用、用户操作、错误信息等
```

## 🤝 开发指南

### 项目结构
```
murdergame/
├── app.py              # Flask应用入口
├── config.py           # 配置文件
├── models.py           # 数据库模型
├── ai_service.py       # AI服务封装
├── dm_agent.py         # DM智能代理
├── player_agent.py     # 玩家智能代理
├── game.py             # 游戏逻辑
├── game_api.py         # 游戏API
├── openai_utils.py     # OpenAI工具函数
├── requirements.txt    # Python依赖
├── template/           # HTML模板
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── chat_v3.html
│   ├── api_config.html
│   └── *.css/*.js
├── instance/           # 数据库文件
├── images/             # 生成的图片
├── log/                # 游戏日志
└── test/               # 测试文件
```

### 扩展开发
- **添加新角色类型**：修改 `dm_agent.py` 中的角色生成逻辑
- **自定义剧本**：在 `game.py` 中添加剧本模板
- **UI主题**：修改 `template/` 下的CSS文件
- **API集成**：在 `ai_service.py` 中添加新的API支持

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [Flask](https://flask.palletsprojects.com/) - 优秀的Python Web框架
- [OpenAI](https://openai.com/) - 强大的AI API服务
- [阿里云百炼](https://dashscope.console.aliyun.com/) - 国内AI服务平台
- [Bootstrap](https://getbootstrap.com/) - 现代化的CSS框架

---

**🎭 开始你的推理之旅吧！每个人都可能是凶手，真相只有一个！**