class ChatInterface {
    constructor() {
        this.chatMessages = document.getElementById('chatMessages');
        this.messageInput = document.getElementById('messageInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.messages = [];
        
        this.init();
        this.bindEvents();
        this.initToolbarButtons();
    }
    
    init() {
        // 配置marked.js
        marked.setOptions({
            highlight: function(code, lang) {
                if (lang && hljs.getLanguage(lang)) {
                    try {
                        return hljs.highlight(code, { language: lang }).value;
                    } catch (err) {
                        console.error('代码高亮错误:', err);
                    }
                }
                return hljs.highlightAuto(code).value;
            },
            breaks: true,
            gfm: true
        });
        
        // 自动调整输入框高度
        this.autoResizeTextarea();
        
        // 滚动到底部
        this.scrollToBottom();
    }
    
    bindEvents() {
        // 发送按钮点击事件
        this.sendBtn.addEventListener('click', () => {
            this.sendMessage();
        });
        
        // 输入框回车发送
        this.messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // 输入框输入事件
        this.messageInput.addEventListener('input', () => {
            this.autoResizeTextarea();
            this.updateSendButton();
        });
        
        // 输入框获得焦点时自动调整高度
        this.messageInput.addEventListener('focus', () => {
            this.autoResizeTextarea();
        });
    }
    
    initToolbarButtons() {
        // 清空聊天按钮
        document.getElementById('clearBtn').addEventListener('click', () => {
            this.clearChat();
        });
        
        // 保存聊天记录按钮
        document.getElementById('saveBtn').addEventListener('click', () => {
            this.saveChat();
        });
        
        // 设置按钮
        document.getElementById('settingsBtn').addEventListener('click', () => {
            this.openSettings();
        });
        
        // 帮助按钮
        document.getElementById('helpBtn').addEventListener('click', () => {
            this.showHelp();
        });
        
        // 导出Markdown按钮
        document.getElementById('exportBtn').addEventListener('click', () => {
            this.exportAsMarkdown();
        });
    }
    
    sendMessage() {
        const text = this.messageInput.value.trim();
        if (!text) return;
        
        // 添加用户消息
        this.addMessage(text, 'user');
        
        // 清空输入框
        this.messageInput.value = '';
        this.autoResizeTextarea();
        this.updateSendButton();
        
        // 模拟机器人回复
        setTimeout(() => {
            this.simulateBotResponse(text);
        }, 500);
    }
    
    addMessage(content, type = 'user', timestamp = null) {
        const messageId = Date.now() + Math.random();
        const time = timestamp || this.getCurrentTime();
        
        const messageData = {
            id: messageId,
            content: content,
            type: type,
            time: time,
            timestamp: new Date()
        };
        
        this.messages.push(messageData);
        
        const messageElement = this.createMessageElement(messageData);
        this.chatMessages.appendChild(messageElement);
        
        this.scrollToBottom();
        
        return messageId;
    }
    
    createMessageElement(messageData) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${messageData.type}-message`;
        messageDiv.setAttribute('data-message-id', messageData.id);
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        // 渲染Markdown
        if (messageData.type === 'bot' || this.isMarkdown(messageData.content)) {
            try {
                contentDiv.innerHTML = marked.parse(messageData.content);
                // 代码高亮
                contentDiv.querySelectorAll('pre code').forEach((block) => {
                    hljs.highlightElement(block);
                });
            } catch (error) {
                console.error('Markdown渲染错误:', error);
                contentDiv.textContent = messageData.content;
            }
        } else {
            contentDiv.textContent = messageData.content;
        }
        
        const timeDiv = document.createElement('div');
        timeDiv.className = 'message-time';
        timeDiv.textContent = messageData.time;
        
        messageDiv.appendChild(contentDiv);
        messageDiv.appendChild(timeDiv);
        
        return messageDiv;
    }
    
    isMarkdown(text) {
        // 简单检测是否包含Markdown语法
        const markdownPatterns = [
            /\*\*.*\*\*/,  // 粗体
            /\*.*\*/,      // 斜体
            /#+ /,         // 标题
            /```[\s\S]*```/, // 代码块
            /`.*`/,        // 行内代码
            /\[.*\]\(.*\)/, // 链接
            /^[-*+] /m     // 列表
        ];
        
        return markdownPatterns.some(pattern => pattern.test(text));
    }
    
    simulateBotResponse(userMessage) {
        this.showTypingIndicator();
        
        setTimeout(() => {
            this.hideTypingIndicator();
            
            // 根据用户消息生成回复
            let response = this.generateBotResponse(userMessage);
            this.addMessage(response, 'bot');
        }, 1000 + Math.random() * 1000);
    }
    
    generateBotResponse(userMessage) {
        const responses = [
            `收到您的消息：**${userMessage}**\n\n这是一个支持Markdown的回复示例。`,
            `### 感谢您的消息！\n\n您发送了：\`${userMessage}\`\n\n这里是一些功能演示：\n- ✅ 支持**粗体**\n- ✅ 支持*斜体*\n- ✅ 支持\`代码\`\n- ✅ 支持列表`,
            `## 代码示例\n\n根据您的输入 "${userMessage}"，这里是一个代码示例：\n\n\`\`\`javascript\nfunction processMessage(message) {\n    console.log("处理消息:", message);\n    return "处理完成";\n}\n\nprocessMessage("${userMessage}");\n\`\`\``,
            `> 这是一个引用样式的回复\n\n您的消息：**${userMessage}**\n\n这个聊天界面支持完整的Markdown语法，包括：\n\n1. 标题\n2. **粗体**和*斜体*\n3. \`代码片段\`\n4. 代码块\n5. 列表\n6. 引用\n7. 链接等`
        ];
        
        return responses[Math.floor(Math.random() * responses.length)];
    }
    
    showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message bot-message typing-indicator';
        typingDiv.id = 'typing-indicator';
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        for (let i = 0; i < 3; i++) {
            const dot = document.createElement('div');
            dot.className = 'typing-dot';
            contentDiv.appendChild(dot);
        }
        
        typingDiv.appendChild(contentDiv);
        this.chatMessages.appendChild(typingDiv);
        this.scrollToBottom();
    }
    
    hideTypingIndicator() {
        const indicator = document.getElementById('typing-indicator');
        if (indicator) {
            indicator.remove();
        }
    }
    
    getCurrentTime() {
        const now = new Date();
        return now.toLocaleTimeString('zh-CN', { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
    }
    
    autoResizeTextarea() {
        this.messageInput.style.height = 'auto';
        this.messageInput.style.height = Math.min(this.messageInput.scrollHeight, 120) + 'px';
    }
    
    updateSendButton() {
        const hasText = this.messageInput.value.trim().length > 0;
        this.sendBtn.disabled = !hasText;
    }
    
    scrollToBottom() {
        setTimeout(() => {
            this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        }, 100);
    }
    
    // 工具栏功能
    clearChat() {
        if (confirm('确定要清空聊天记录吗？')) {
            this.messages = [];
            this.chatMessages.innerHTML = '';
            this.showSystemMessage('聊天记录已清空');
        }
    }
    
    saveChat() {
        try {
            const chatData = {
                messages: this.messages,
                timestamp: new Date().toISOString(),
                title: `聊天记录_${new Date().toLocaleDateString('zh-CN')}`
            };
            
            const dataStr = JSON.stringify(chatData, null, 2);
            const dataBlob = new Blob([dataStr], { type: 'application/json' });
            
            const link = document.createElement('a');
            link.href = URL.createObjectURL(dataBlob);
            link.download = `chat_${Date.now()}.json`;
            link.click();
            
            this.showSystemMessage('聊天记录已保存');
        } catch (error) {
            console.error('保存失败:', error);
            this.showSystemMessage('保存失败，请重试');
        }
    }
    
    exportAsMarkdown() {
        try {
            let markdown = `# 聊天记录\n\n`;
            markdown += `导出时间：${new Date().toLocaleString('zh-CN')}\n\n---\n\n`;
            
            this.messages.forEach(msg => {
                const time = msg.timestamp ? new Date(msg.timestamp).toLocaleTimeString('zh-CN') : msg.time;
                const sender = msg.type === 'user' ? '用户' : '助手';
                
                markdown += `## ${sender} (${time})\n\n`;
                markdown += `${msg.content}\n\n`;
            });
            
            const blob = new Blob([markdown], { type: 'text/markdown;charset=utf-8' });
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.download = `chat_export_${Date.now()}.md`;
            link.click();
            
            this.showSystemMessage('Markdown文件已导出');
        } catch (error) {
            console.error('导出失败:', error);
            this.showSystemMessage('导出失败，请重试');
        }
    }
    
    openSettings() {
        const settings = {
            theme: localStorage.getItem('chat-theme') || 'light',
            fontSize: localStorage.getItem('chat-fontSize') || 'medium',
            autoScroll: localStorage.getItem('chat-autoScroll') !== 'false'
        };
        
        const settingsHtml = `
            <div style="padding: 20px; max-width: 400px;">
                <h3 style="margin-bottom: 15px;">聊天设置</h3>
                
                <div style="margin-bottom: 15px;">
                    <label style="display: block; margin-bottom: 5px;">主题:</label>
                    <select id="themeSelect" style="width: 100%; padding: 5px;">
                        <option value="light" ${settings.theme === 'light' ? 'selected' : ''}>浅色主题</option>
                        <option value="dark" ${settings.theme === 'dark' ? 'selected' : ''}>深色主题</option>
                    </select>
                </div>
                
                <div style="margin-bottom: 15px;">
                    <label style="display: block; margin-bottom: 5px;">字体大小:</label>
                    <select id="fontSizeSelect" style="width: 100%; padding: 5px;">
                        <option value="small" ${settings.fontSize === 'small' ? 'selected' : ''}>小</option>
                        <option value="medium" ${settings.fontSize === 'medium' ? 'selected' : ''}>中</option>
                        <option value="large" ${settings.fontSize === 'large' ? 'selected' : ''}>大</option>
                    </select>
                </div>
                
                <div style="margin-bottom: 15px;">
                    <label style="display: flex; align-items: center; gap: 8px;">
                        <input type="checkbox" id="autoScrollCheck" ${settings.autoScroll ? 'checked' : ''}>
                        自动滚动到底部
                    </label>
                </div>
                
                <div style="text-align: right; margin-top: 20px;">
                    <button onclick="this.closest('.settings-modal').remove()" style="margin-right: 10px; padding: 5px 15px;">取消</button>
                    <button onclick="chatInterface.applySettings()" style="padding: 5px 15px; background: #667eea; color: white; border: none; border-radius: 3px;">应用</button>
                </div>
            </div>
        `;
        
        this.showModal(settingsHtml, 'settings-modal');
    }
    
    applySettings() {
        const theme = document.getElementById('themeSelect').value;
        const fontSize = document.getElementById('fontSizeSelect').value;
        const autoScroll = document.getElementById('autoScrollCheck').checked;
        
        localStorage.setItem('chat-theme', theme);
        localStorage.setItem('chat-fontSize', fontSize);
        localStorage.setItem('chat-autoScroll', autoScroll);
        
        // 应用设置
        document.body.className = theme;
        document.body.style.fontSize = fontSize === 'small' ? '13px' : fontSize === 'large' ? '16px' : '14px';
        
        document.querySelector('.settings-modal').remove();
        this.showSystemMessage('设置已保存');
    }
    
    showHelp() {
        const helpContent = `
            <div style="padding: 20px; max-width: 500px;">
                <h3 style="margin-bottom: 15px;">帮助文档</h3>
                
                <h4>Markdown语法支持:</h4>
                <ul style="margin-bottom: 15px;">
                    <li><strong>**粗体**</strong> - 粗体文本</li>
                    <li><em>*斜体*</em> - 斜体文本</li>
                    <li><code>\`代码\`</code> - 行内代码</li>
                    <li># 标题 - 各级标题</li>
                    <li>- 列表项 - 无序列表</li>
                    <li>1. 列表项 - 有序列表</li>
                    <li>&gt; 引用 - 引用文本</li>
                </ul>
                
                <h4>快捷键:</h4>
                <ul style="margin-bottom: 15px;">
                    <li><strong>Enter</strong> - 发送消息</li>
                    <li><strong>Shift + Enter</strong> - 换行</li>
                </ul>
                
                <h4>工具按钮:</h4>
                <ul>
                    <li><strong>清空</strong> - 清空所有聊天记录</li>
                    <li><strong>保存</strong> - 保存聊天记录为JSON文件</li>
                    <li><strong>导出</strong> - 导出聊天记录为Markdown文件</li>
                    <li><strong>设置</strong> - 调整界面设置</li>
                </ul>
                
                <div style="text-align: right; margin-top: 20px;">
                    <button onclick="this.closest('.help-modal').remove()" style="padding: 5px 15px; background: #667eea; color: white; border: none; border-radius: 3px;">关闭</button>
                </div>
            </div>
        `;
        
        this.showModal(helpContent, 'help-modal');
    }
    
    showModal(content, className) {
        // 移除现有模态框
        document.querySelectorAll('.modal-overlay').forEach(modal => modal.remove());
        
        const overlay = document.createElement('div');
        overlay.className = `modal-overlay ${className}`;
        overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.5);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 1000;
        `;
        
        const modal = document.createElement('div');
        modal.style.cssText = `
            background: white;
            border-radius: 8px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
            max-height: 80vh;
            overflow-y: auto;
        `;
        modal.innerHTML = content;
        
        overlay.appendChild(modal);
        document.body.appendChild(overlay);
        
        // 点击外部关闭
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) {
                overlay.remove();
            }
        });
    }
    
    showSystemMessage(message) {
        const systemDiv = document.createElement('div');
        systemDiv.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #4CAF50;
            color: white;
            padding: 10px 15px;
            border-radius: 4px;
            z-index: 1000;
            animation: slideIn 0.3s ease;
        `;
        systemDiv.textContent = message;
        
        document.body.appendChild(systemDiv);
        
        setTimeout(() => {
            systemDiv.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => systemDiv.remove(), 300);
        }, 3000);
    }
}

// 添加CSS动画
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;
document.head.appendChild(style);

// 初始化聊天界面
let chatInterface;
document.addEventListener('DOMContentLoaded', () => {
    chatInterface = new ChatInterface();
});

// 导出到全局作用域，供HTML中的事件处理器使用
window.chatInterface = chatInterface;