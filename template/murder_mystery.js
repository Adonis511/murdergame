/**
 * 剧本杀游戏前端逻辑
 * 主要功能：游戏状态管理、UI交互、后端通信
 */

class MurderMysteryGame {
    constructor() {
        this.gameState = window.gameState || {};
        this.socket = null;
        this.messageHistory = [];
        this.gameTimer = null;
        this.startTime = null;
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.initializeUI();
        this.setupMarkdown();
        this.loadGameConfig();
    }
    
    setupEventListeners() {
        // 发送消息
        const sendBtn = document.getElementById('sendBtn');
        const messageInput = document.getElementById('messageInput');
        
        if (sendBtn) {
            sendBtn.addEventListener('click', () => this.sendMessage());
        }
        
        if (messageInput) {
            messageInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && e.ctrlKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });
            
            messageInput.addEventListener('input', () => {
                this.updateCharCount();
                this.updateSendButton();
            });
        }
        
        // 输入模式切换
        document.querySelectorAll('.input-option').forEach(btn => {
            btn.addEventListener('click', () => {
                const mode = btn.id.replace('Btn', '');
                this.setInputMode(mode);
            });
        });
    }
    
    initializeUI() {
        this.updateCharCount();
        this.updateSendButton();
        this.startGameTimer();
    }
    
    setupMarkdown() {
        if (typeof marked !== 'undefined') {
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
        }
    }
    
    async loadGameConfig() {
        try {
            const response = await fetch('/api/config');
            const data = await response.json();
            if (data.status === 'success') {
                this.gameConfig = data.data;
                console.log('游戏配置加载成功:', this.gameConfig);
            }
        } catch (error) {
            console.error('加载游戏配置失败:', error);
        }
    }
    
    // 游戏流程管理
    async startNewGame() {
        try {
            this.addSystemMessage('🎭 正在生成新的剧本杀剧本...');
            this.addSystemMessage('⏳ 请稍候，AI正在为您创建一个神秘的故事...');
            
            const response = await fetch('/api/game/new', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    generate_images: false,
                    user_id: this.gameState.user.id
                })
            });
            
            const data = await response.json();
            if (data.status === 'success') {
                this.gameState.gameSession = data.data.game_session;
                this.gameState.gameMode = 'character_select';
                
                // 更新UI
                this.updateStoryInfo(data.data.story_title, data.data.story_subtitle);
                this.showCharacterSelection(data.data.characters);
                
                this.addSystemMessage('✅ 剧本生成成功！请选择您要扮演的角色。');
            } else {
                this.addSystemMessage('❌ 生成剧本失败：' + data.message);
            }
        } catch (error) {
            console.error('启动新游戏失败:', error);
            this.addSystemMessage('❌ 网络错误，请检查连接后重试。');
        }
    }
    
    async loadExistingGame() {
        const modal = this.createModal('加载游戏', `
            <div class="game-list">
                <div class="loading-message">🔍 正在搜索可用的游戏...</div>
                <div id="gameListContainer"></div>
            </div>
        `);
        
        try {
            const response = await fetch('/api/game/list');
            const data = await response.json();
            
            const container = document.getElementById('gameListContainer');
            const loadingMsg = container.previousElementSibling;
            loadingMsg.style.display = 'none';
            
            if (data.status === 'success' && data.data.games.length > 0) {
                container.innerHTML = data.data.games.map(game => `
                    <div class="game-item" onclick="selectGame('${game.path}')">
                        <div class="game-title">${game.title}</div>
                        <div class="game-info">
                            <span>👥 ${game.characters.length} 角色</span>
                            <span>📖 ${game.chapters} 章节</span>
                            <span>🕒 ${this.formatDate(game.created_at)}</span>
                        </div>
                    </div>
                `).join('');
            } else {
                container.innerHTML = '<div class="no-games">未找到可用的游戏存档</div>';
            }
        } catch (error) {
            console.error('加载游戏列表失败:', error);
            document.getElementById('gameListContainer').innerHTML = 
                '<div class="error-message">加载失败，请重试</div>';
        }
    }
    
    async selectGame(gamePath) {
        try {
            this.closeAllModals();
            this.addSystemMessage('📂 正在加载游戏...');
            
            const response = await fetch('/api/game/load', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    game_path: gamePath,
                    user_id: this.gameState.user.id
                })
            });
            
            const data = await response.json();
            if (data.status === 'success') {
                this.gameState.gameSession = data.data.game_session;
                this.gameState.gameMode = 'character_select';
                
                this.updateStoryInfo(data.data.story_title, data.data.story_subtitle);
                this.showCharacterSelection(data.data.characters);
                
                this.addSystemMessage('✅ 游戏加载成功！请选择您的角色。');
            } else {
                this.addSystemMessage('❌ 加载游戏失败：' + data.message);
            }
        } catch (error) {
            console.error('选择游戏失败:', error);
            this.addSystemMessage('❌ 网络错误，请检查连接后重试。');
        }
    }
    
    showCharacterSelection(characters) {
        const panel = document.getElementById('characterPanel');
        const grid = document.getElementById('characterGrid');
        
        grid.innerHTML = characters.map((char, index) => `
            <div class="character-card" onclick="selectCharacter('${char.name}', ${index})">
                <div class="character-avatar">${this.getCharacterEmoji(char.name)}</div>
                <div class="character-name">${char.name}</div>
                <div class="character-description">${char.description || '神秘的角色，等待你来揭开面纱...'}</div>
            </div>
        `).join('');
        
        panel.style.display = 'block';
        this.gameState.availableCharacters = characters;
    }
    
    selectCharacter(characterName, index) {
        // 取消之前的选择
        document.querySelectorAll('.character-card').forEach(card => {
            card.classList.remove('selected');
        });
        
        // 选择当前角色
        document.querySelectorAll('.character-card')[index].classList.add('selected');
        
        this.gameState.selectedCharacter = characterName;
        document.getElementById('confirmCharacterBtn').disabled = false;
        
        this.addSystemMessage(`您选择了角色：${characterName}`);
    }
    
    async confirmCharacterSelection() {
        if (!this.gameState.selectedCharacter) return;
        
        try {
            this.addSystemMessage('🎭 正在确认角色选择...');
            
            const response = await fetch('/api/game/join', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    game_session: this.gameState.gameSession,
                    character_name: this.gameState.selectedCharacter,
                    user_id: this.gameState.user.id
                })
            });
            
            const data = await response.json();
            if (data.status === 'success') {
                this.gameState.currentCharacter = this.gameState.selectedCharacter;
                this.gameState.gameMode = 'playing';
                
                // 隐藏角色选择面板，显示游戏界面
                document.getElementById('characterPanel').style.display = 'none';
                document.getElementById('playerInfoBar').style.display = 'flex';
                
                // 更新玩家信息
                this.updatePlayerInfo();
                
                // 开始游戏
                this.startGameSession();
                
                this.addSystemMessage(`✅ 成功加入游戏！您现在是：${this.gameState.currentCharacter}`);
            } else {
                this.addSystemMessage('❌ 加入游戏失败：' + data.message);
            }
        } catch (error) {
            console.error('确认角色选择失败:', error);
            this.addSystemMessage('❌ 网络错误，请检查连接后重试。');
        }
    }
    
    async startGameSession() {
        try {
            // 获取游戏状态
            const response = await fetch(`/api/game/status/${this.gameState.gameSession}`);
            const data = await response.json();
            
            if (data.status === 'success') {
                this.gameState.totalChapters = data.data.total_chapters;
                this.gameState.currentChapter = data.data.current_chapter;
                
                this.updateGameProgress();
                
                // 开始第一章
                if (this.gameState.currentChapter === 0) {
                    await this.startChapter(1);
                }
            }
        } catch (error) {
            console.error('启动游戏会话失败:', error);
        }
    }
    
    async startChapter(chapterNum) {
        try {
            this.addSystemMessage(`📖 第${chapterNum}章开始...`);
            
            const response = await fetch('/api/game/chapter/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    game_session: this.gameState.gameSession,
                    chapter_num: chapterNum,
                    character_name: this.gameState.currentCharacter
                })
            });
            
            const data = await response.json();
            if (data.status === 'success') {
                this.gameState.currentChapter = chapterNum;
                this.updateGameProgress();
                
                // 显示DM开场
                if (data.data.dm_speech) {
                    this.addDMMessage('章节开始', data.data.dm_speech);
                }
                
                // 显示角色剧本
                if (data.data.character_script) {
                    this.addSystemMessage('📜 您收到了新的剧本信息，请查看右侧剧本按钮。');
                    this.gameState.currentScript = data.data.character_script;
                }
                
                this.addSystemMessage(`✅ 第${chapterNum}章已开始，请开始角色扮演！`);
            } else {
                this.addSystemMessage('❌ 开始章节失败：' + data.message);
            }
        } catch (error) {
            console.error('开始章节失败:', error);
            this.addSystemMessage('❌ 网络错误，请检查连接后重试。');
        }
    }
    
    // 消息发送和接收
    async sendMessage() {
        const messageInput = document.getElementById('messageInput');
        const message = messageInput.value.trim();
        
        if (!message) return;
        
        const inputMode = this.gameState.inputMode || 'speak';
        let targetPlayer = null;
        
        if (inputMode === 'ask') {
            targetPlayer = document.getElementById('askTargetSelect')?.value;
            if (!targetPlayer) {
                this.showToast('请选择询问对象', 'warning');
                return;
            }
        } else if (inputMode === 'whisper') {
            targetPlayer = document.getElementById('whisperTargetSelect')?.value;
            if (!targetPlayer) {
                this.showToast('请选择私聊对象', 'warning');
                return;
            }
        }
        
        try {
            // 立即显示用户消息
            this.addPlayerMessage(this.gameState.currentCharacter || this.gameState.user.nickname, message, inputMode, targetPlayer);
            
            // 清空输入框
            messageInput.value = '';
            this.updateCharCount();
            this.updateSendButton();
            
            // 发送到后端
            const requestData = {
                game_session: this.gameState.gameSession,
                character_name: this.gameState.currentCharacter,
                message: message,
                message_type: inputMode,
                target_player: targetPlayer,
                chapter: this.gameState.currentChapter
            };
            
            const response = await fetch('/api/game/message', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestData)
            });
            
            const data = await response.json();
            if (data.status === 'success') {
                // 处理其他玩家的回应
                if (data.data.responses) {
                    data.data.responses.forEach(response => {
                        this.addPlayerMessage(response.character, response.content, 'response', this.gameState.currentCharacter);
                    });
                }
                
                // 处理DM回应
                if (data.data.dm_response) {
                    this.addDMMessage('游戏主持', data.data.dm_response);
                }
            } else {
                this.addSystemMessage('❌ 消息发送失败：' + data.message);
            }
        } catch (error) {
            console.error('发送消息失败:', error);
            this.addSystemMessage('❌ 网络错误，请检查连接后重试。');
        }
    }
    
    // UI更新方法
    updateStoryInfo(title, subtitle) {
        document.getElementById('storyTitle').textContent = `📚 ${title}`;
        document.getElementById('storySubtitle').textContent = subtitle;
    }
    
    updatePlayerInfo() {
        document.getElementById('playerName').textContent = this.gameState.user.nickname;
        document.getElementById('characterName').textContent = this.gameState.currentCharacter;
        document.getElementById('playerStatus').textContent = '游戏中';
        document.getElementById('playerAvatar').textContent = this.getCharacterEmoji(this.gameState.currentCharacter);
    }
    
    updateGameProgress() {
        const current = this.gameState.currentChapter;
        const total = this.gameState.totalChapters;
        
        document.getElementById('currentChapter').textContent = `${current}/${total}`;
        document.getElementById('chapterIndicator').textContent = `第${current}章`;
        
        const progress = total > 0 ? (current / total) * 100 : 0;
        document.getElementById('progressFill').style.width = `${progress}%`;
    }
    
    updateCharCount() {
        const messageInput = document.getElementById('messageInput');
        const charCount = document.getElementById('charCount');
        
        if (messageInput && charCount) {
            const length = messageInput.value.length;
            charCount.textContent = `${length}/500`;
            
            if (length > 450) {
                charCount.style.color = '#FF6B6B';
            } else if (length > 350) {
                charCount.style.color = '#FFA500';
            } else {
                charCount.style.color = '#888';
            }
        }
    }
    
    updateSendButton() {
        const messageInput = document.getElementById('messageInput');
        const sendBtn = document.getElementById('sendBtn');
        
        if (messageInput && sendBtn) {
            const hasText = messageInput.value.trim().length > 0;
            sendBtn.disabled = !hasText || this.gameState.gameMode !== 'playing';
        }
    }
    
    setInputMode(mode) {
        this.gameState.inputMode = mode;
        
        // 更新UI
        document.querySelectorAll('.input-option').forEach(btn => {
            btn.classList.remove('active');
        });
        document.getElementById(`${mode}Btn`).classList.add('active');
        
        // 更新输入模式显示
        const modeTexts = {
            speak: '💬 自由发言',
            ask: '❓ 询问他人',
            whisper: '🤫 私聊',
            action: '🎬 行动描述'
        };
        document.getElementById('inputMode').textContent = modeTexts[mode];
        
        // 显示/隐藏目标选择
        document.getElementById('askTarget').style.display = mode === 'ask' ? 'flex' : 'none';
        document.getElementById('whisperTarget').style.display = mode === 'whisper' ? 'flex' : 'none';
        
        // 更新占位符
        const placeholders = {
            speak: '请输入你的发言内容...',
            ask: '请输入你要询问的问题...',
            whisper: '请输入私聊内容...',
            action: '请描述你的行动...'
        };
        document.getElementById('messageInput').placeholder = placeholders[mode];
    }
    
    // 消息显示方法
    addMessage(content, type = 'system', speaker = '系统', icon = '🔔', timestamp = null) {
        const messagesContainer = document.getElementById('gameMessages');
        const messageElement = document.createElement('div');
        messageElement.className = `message ${type}-message`;
        
        const time = timestamp || this.getCurrentTime();
        
        messageElement.innerHTML = `
            <div class="message-header">
                <span class="speaker-icon">${icon}</span>
                <span class="speaker-name">${speaker}</span>
                <span class="message-time">${time}</span>
            </div>
            <div class="message-content">
                ${this.renderMarkdown(content)}
            </div>
        `;
        
        messagesContainer.appendChild(messageElement);
        this.scrollToBottom();
        
        // 保存到历史记录
        this.messageHistory.push({
            content,
            type,
            speaker,
            timestamp: new Date()
        });
    }
    
    addSystemMessage(content) {
        this.addMessage(content, 'system', '系统', '🔔');
    }
    
    addDMMessage(speaker, content) {
        this.addMessage(content, 'dm', `🎭 ${speaker}`, '🎭');
    }
    
    addPlayerMessage(speaker, content, messageType = 'speak', target = null) {
        let icon = '👤';
        let type = 'player';
        let displayContent = content;
        
        switch (messageType) {
            case 'ask':
                icon = '❓';
                if (target) {
                    displayContent = `**询问 @${target}**: ${content}`;
                }
                break;
            case 'whisper':
                icon = '🤫';
                type = 'whisper';
                if (target) {
                    displayContent = `**私聊 @${target}**: ${content}`;
                }
                break;
            case 'action':
                icon = '🎬';
                type = 'action';
                displayContent = `*${content}*`;
                break;
            case 'response':
                icon = '💬';
                if (target) {
                    displayContent = `**回应 @${target}**: ${content}`;
                }
                break;
        }
        
        this.addMessage(displayContent, type, speaker, icon);
    }
    
    renderMarkdown(content) {
        if (typeof marked !== 'undefined') {
            try {
                const html = marked.parse(content);
                // 高亮代码块
                setTimeout(() => {
                    document.querySelectorAll('pre code').forEach((block) => {
                        if (typeof hljs !== 'undefined') {
                            hljs.highlightElement(block);
                        }
                    });
                }, 100);
                return html;
            } catch (error) {
                console.error('Markdown渲染错误:', error);
                return content;
            }
        }
        return content;
    }
    
    scrollToBottom() {
        const messagesContainer = document.getElementById('gameMessages');
        if (messagesContainer) {
            setTimeout(() => {
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            }, 100);
        }
    }
    
    // 工具方法
    getCurrentTime() {
        const now = new Date();
        return now.toLocaleTimeString('zh-CN', { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
    }
    
    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('zh-CN');
    }
    
    getCharacterEmoji(characterName) {
        if (!characterName) return '👤';
        
        const emojis = ['🕵️', '👨‍💼', '👩‍💼', '👨‍⚖️', '👩‍⚖️', '👨‍🎨', '👩‍🎨', '👨‍🔬', '👩‍🔬', '🤵', '👸'];
        const index = characterName.length % emojis.length;
        return emojis[index];
    }
    
    startGameTimer() {
        this.startTime = new Date();
        this.gameTimer = setInterval(() => {
            this.updateGameTime();
        }, 1000);
    }
    
    updateGameTime() {
        if (!this.startTime) return;
        
        const now = new Date();
        const diff = now - this.startTime;
        const minutes = Math.floor(diff / 60000);
        const seconds = Math.floor((diff % 60000) / 1000);
        
        document.getElementById('gameTime').textContent = 
            `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }
    
    pauseGameTimer() {
        if (this.gameTimer) {
            clearInterval(this.gameTimer);
        }
    }
    
    resumeGameTimer() {
        this.startGameTimer();
    }
    
    // 模态框管理
    createModal(title, content) {
        const modalContainer = document.getElementById('modalContainer');
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="modal-content">
                <button class="modal-close" onclick="this.closest('.modal-overlay').remove()">×</button>
                <div class="modal-header">${title}</div>
                <div class="modal-body">${content}</div>
            </div>
        `;
        
        modalContainer.appendChild(modal);
        
        // 点击外部关闭
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
        
        return modal;
    }
    
    closeAllModals() {
        document.querySelectorAll('.modal-overlay').forEach(modal => {
            modal.remove();
        });
    }
    
    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${type === 'error' ? '#FF6B6B' : type === 'warning' ? '#FFA500' : '#4CAF50'};
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            z-index: 1001;
            animation: slideInToast 0.3s ease;
        `;
        toast.textContent = message;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.style.animation = 'slideOutToast 0.3s ease';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
}

// 全局函数（供HTML调用）
function initializeGameInterface() {
    window.murderMysteryGame = new MurderMysteryGame();
}

function setupGameEvents() {
    // 已在类中处理
}

function checkGameStatus() {
    // 检查是否有进行中的游戏
    if (window.murderMysteryGame) {
        window.murderMysteryGame.loadGameConfig();
    }
}

function startNewGame() {
    if (window.murderMysteryGame) {
        window.murderMysteryGame.startNewGame();
    }
}

function loadExistingGame() {
    if (window.murderMysteryGame) {
        window.murderMysteryGame.loadExistingGame();
    }
}

function selectCharacter(characterName, index) {
    if (window.murderMysteryGame) {
        window.murderMysteryGame.selectCharacter(characterName, index);
    }
}

function confirmCharacterSelection() {
    if (window.murderMysteryGame) {
        window.murderMysteryGame.confirmCharacterSelection();
    }
}

function selectGame(gamePath) {
    if (window.murderMysteryGame) {
        window.murderMysteryGame.selectGame(gamePath);
    }
}

function setInputMode(mode) {
    if (window.murderMysteryGame) {
        window.murderMysteryGame.setInputMode(mode);
    }
}

function sendMessage() {
    if (window.murderMysteryGame) {
        window.murderMysteryGame.sendMessage();
    }
}

function showGameMenu() {
    if (window.murderMysteryGame) {
        window.murderMysteryGame.createModal('游戏菜单', `
            <div class="game-menu">
                <button class="mystery-btn" onclick="showSettings()">⚙️ 游戏设置</button>
                <button class="mystery-btn" onclick="showHelp()">❓ 游戏帮助</button>
                <button class="mystery-btn" onclick="exportGame()">📁 导出游戏</button>
                <button class="mystery-btn emergency" onclick="exitGame()">🚪 退出游戏</button>
            </div>
        `);
    }
}

function showClues() {
    console.log('显示线索');
}

function showScript() {
    console.log('显示剧本');
}

function showNotes() {
    console.log('显示笔记');
}

function showPlayers() {
    console.log('显示玩家列表');
}

function showHistory() {
    console.log('显示历史记录');
}

function showSettings() {
    console.log('显示设置');
}

function emergencyCall() {
    console.log('紧急呼叫');
}

function closeAllModals() {
    if (window.murderMysteryGame) {
        window.murderMysteryGame.closeAllModals();
    }
}

// 添加CSS动画
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInToast {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOutToast {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
    
    .game-menu {
        display: flex;
        flex-direction: column;
        gap: 15px;
        min-width: 300px;
    }
    
    .game-menu .mystery-btn {
        width: 100%;
        padding: 15px;
        font-size: 1.1em;
        justify-content: center;
    }
    
    .game-list {
        max-width: 600px;
        max-height: 400px;
        overflow-y: auto;
    }
    
    .game-item {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 10px;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .game-item:hover {
        background: rgba(255, 255, 255, 0.2);
        transform: translateY(-2px);
    }
    
    .game-title {
        color: #FFD700;
        font-weight: bold;
        margin-bottom: 8px;
    }
    
    .game-info {
        color: #B0B0B0;
        font-size: 0.9em;
        display: flex;
        gap: 15px;
    }
    
    .loading-message, .no-games, .error-message {
        text-align: center;
        color: #B0B0B0;
        padding: 40px 20px;
        font-style: italic;
    }
`;
document.head.appendChild(style);