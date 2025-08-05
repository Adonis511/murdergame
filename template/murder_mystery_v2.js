/**
 * 剧本杀游戏前端逻辑 V2
 * 三列布局，增强的功能和界面
 */

class MurderMysteryGameV2 {
    constructor() {
        this.gameState = window.gameState || {};
        this.messageHistory = [];
        this.gameTimer = null;
        this.startTime = null;
        this.progressChecker = null;
        this.currentScript = null;
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.initializeUI();
        this.setupMarkdown();
        this.loadGameConfig();
        this.startGameTimer();
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

        // 配置面板切换
        document.querySelectorAll('input[name="scriptSource"]').forEach(radio => {
            radio.addEventListener('change', () => {
                this.handleScriptSourceChange();
            });
        });
    }
    
    initializeUI() {
        this.updateCharCount();
        this.updateSendButton();
        this.hideMainGameArea();
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

    // ============= 配置管理 =============
    
    showGameConfig() {
        document.getElementById('configPanel').style.display = 'block';
    }

    hideGameConfig() {
        document.getElementById('configPanel').style.display = 'none';
    }

    handleScriptSourceChange() {
        const localPathGroup = document.getElementById('localPathGroup');
        const isLocal = document.querySelector('input[name="scriptSource"]:checked').value === 'local';
        localPathGroup.style.display = isLocal ? 'block' : 'none';
    }

    async browseLocalScripts() {
        try {
            const response = await fetch('/api/game/list');
            const data = await response.json();
            
            if (data.status === 'success' && data.data.games.length > 0) {
                const modal = this.createModal('选择本地剧本', `
                    <div class="local-scripts-list">
                        ${data.data.games.map(game => `
                            <div class="local-script-item" onclick="selectLocalScript('${game.path}', '${game.title}')">
                                <div class="script-title">${game.title}</div>
                                <div class="script-info">
                                    <span>👥 ${game.characters.length} 角色</span>
                                    <span>📖 ${game.chapters} 章节</span>
                                    <span>🕒 ${this.formatDate(game.created_at)}</span>
                                </div>
                                <div class="script-path">${game.path}</div>
                            </div>
                        `).join('')}
                    </div>
                `);
            } else {
                this.showToast('未找到可用的本地剧本', 'warning');
            }
        } catch (error) {
            console.error('浏览本地剧本失败:', error);
            this.showToast('浏览失败，请重试', 'error');
        }
    }

    selectLocalScript(path, title) {
        document.getElementById('localScriptPath').value = path;
        this.closeAllModals();
        this.showToast(`已选择剧本：${title}`, 'success');
    }

    applyGameConfig() {
        // 获取配置
        const scriptSource = document.querySelector('input[name="scriptSource"]:checked').value;
        const localScriptPath = document.getElementById('localScriptPath').value;
        const generateImages = document.getElementById('generateImages').checked;
        const waitForCompletion = document.getElementById('waitForCompletion').checked;

        // 验证配置
        if (scriptSource === 'local' && !localScriptPath.trim()) {
            this.showToast('请选择本地剧本路径', 'warning');
            return;
        }

        // 保存配置
        this.gameState.config = {
            scriptSource,
            localScriptPath: localScriptPath.trim(),
            generateImages,
            waitForCompletion
        };

        this.hideGameConfig();
        this.showToast('配置已保存', 'success');
    }

    // ============= 游戏流程管理 =============
    
    async startNewGame() {
        // 确保有配置
        if (!this.gameState.config) {
            this.showToast('请先配置游戏参数', 'warning');
            this.showGameConfig();
            return;
        }

        const config = this.gameState.config;
        
        if (config.scriptSource === 'local') {
            // 加载本地剧本
            await this.loadExistingGame(config.localScriptPath);
        } else {
            // 生成新剧本
            await this.createNewGame(config.generateImages, config.waitForCompletion);
        }
    }

    async createNewGame(generateImages = true, waitForCompletion = true) {
        try {
            this.addSystemMessage('🎭 正在生成新的剧本杀剧本...');
            
            // 显示进度模态框
            if (waitForCompletion) {
                this.showProgressModal();
            }
            
            const response = await fetch('/api/game/new', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    generate_images: generateImages,
                    wait_for_completion: waitForCompletion,
                    user_id: this.gameState.user.id
                })
            });
            
            const data = await response.json();
            if (data.status === 'success') {
                this.gameState.gameSession = data.data.game_session;
                this.gameState.gameMode = 'character_select';
                
                // 更新UI
                this.updateStoryInfo(data.data.story_title, data.data.story_subtitle);
                
                if (waitForCompletion && generateImages) {
                    // 开始监控进度
                    this.startProgressMonitoring(data.data.game_session);
                } else {
                    // 直接显示角色选择
                    this.showCharacterSelection(data.data.characters);
                    this.hideProgressModal();
                    this.addSystemMessage('✅ 剧本生成成功！请选择您要扮演的角色。');
                }
            } else {
                this.hideProgressModal();
                this.addSystemMessage('❌ 生成剧本失败：' + data.message);
            }
        } catch (error) {
            console.error('启动新游戏失败:', error);
            this.hideProgressModal();
            this.addSystemMessage('❌ 网络错误，请检查连接后重试。');
        }
    }

    async loadExistingGame(gamePath = null) {
        if (!gamePath) {
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
            return;
        }

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

    // ============= 进度监控 =============

    showProgressModal() {
        document.getElementById('progressModal').style.display = 'flex';
        this.updateProgress(0, '开始生成剧本...');
        this.updateProgressDetail('scriptStatus', 'progress', '生成中...');
        this.updateProgressDetail('imageStatus', 'waiting', '等待中...');
        this.updateProgressDetail('gameStatus', 'waiting', '等待中...');
    }

    hideProgressModal() {
        document.getElementById('progressModal').style.display = 'none';
        if (this.progressChecker) {
            clearInterval(this.progressChecker);
            this.progressChecker = null;
        }
    }

    updateProgress(percentage, text) {
        const progressBar = document.getElementById('gameProgressBar');
        const progressText = document.getElementById('progressText');
        
        if (progressBar) progressBar.style.width = `${percentage}%`;
        if (progressText) progressText.textContent = text;
    }

    updateProgressDetail(elementId, status, text) {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = text;
            element.className = `detail-status ${status}`;
        }
    }

    startProgressMonitoring(gameSession) {
        let progress = 10;
        this.updateProgress(progress, '正在生成剧本内容...');

        this.progressChecker = setInterval(async () => {
            try {
                const response = await fetch(`/api/game/progress/${gameSession}`);
                const data = await response.json();
                
                if (data.status === 'success') {
                    const gameData = data.data;
                    
                    // 更新进度
                    if (gameData.script_ready) {
                        this.updateProgressDetail('scriptStatus', 'completed', '已完成');
                        progress = Math.max(progress, 40);
                        this.updateProgress(progress, '正在生成角色图片...');
                    }
                    
                    if (gameData.images_ready) {
                        this.updateProgressDetail('imageStatus', 'completed', '已完成');
                        progress = Math.max(progress, 80);
                        this.updateProgress(progress, '正在准备游戏...');
                    }
                    
                    if (gameData.game_ready) {
                        this.updateProgressDetail('gameStatus', 'completed', '已完成');
                        progress = 100;
                        this.updateProgress(progress, '游戏准备完成！');
                        
                        // 显示角色选择
                        setTimeout(() => {
                            this.hideProgressModal();
                            this.showCharacterSelection(gameData.characters);
                            this.addSystemMessage('✅ 剧本和图片生成完成！请选择您要扮演的角色。');
                        }, 1000);
                        
                        clearInterval(this.progressChecker);
                        this.progressChecker = null;
                    }
                } else {
                    console.error('获取进度失败:', data.message);
                }
            } catch (error) {
                console.error('监控进度失败:', error);
            }
        }, 2000); // 每2秒检查一次

        // 显示跳过按钮
        setTimeout(() => {
            const skipBtn = document.getElementById('skipWaitBtn');
            if (skipBtn) skipBtn.style.display = 'block';
        }, 10000); // 10秒后显示跳过按钮
    }

    skipWait() {
        if (confirm('确定要跳过等待吗？图片可能还未生成完成。')) {
            this.hideProgressModal();
            // 获取当前可用的角色
            this.getCurrentGameCharacters();
        }
    }

    async getCurrentGameCharacters() {
        try {
            const response = await fetch(`/api/game/status/${this.gameState.gameSession}`);
            const data = await response.json();
            
            if (data.status === 'success') {
                this.showCharacterSelection(data.data.characters || []);
                this.addSystemMessage('✅ 已跳过等待，开始选择角色！');
            }
        } catch (error) {
            console.error('获取角色失败:', error);
            this.addSystemMessage('❌ 获取角色信息失败');
        }
    }

    // ============= 角色选择 =============
    
    showCharacterSelection(characters) {
        const panel = document.getElementById('characterPanel');
        const grid = document.getElementById('characterGrid');
        
        grid.innerHTML = characters.map((char, index) => {
            const isString = typeof char === 'string';
            const charName = isString ? char : char.name;
            const charDesc = isString ? `神秘的角色：${charName}` : (char.description || '神秘的角色，等待你来揭开面纱...');
            const charImage = (!isString && char.image) ? `<img src="${char.image}" class="character-image" alt="${charName}">` : '';
            
            return `
                <div class="character-card" onclick="selectCharacter('${charName}', ${index})">
                    ${charImage}
                    <div class="character-avatar">${this.getCharacterEmoji(charName)}</div>
                    <div class="character-name">${charName}</div>
                    <div class="character-description">${charDesc}</div>
                </div>
            `;
        }).join('');
        
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
                this.showMainGameArea();
                
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

    // ============= 界面管理 =============

    hideMainGameArea() {
        document.getElementById('mainGameArea').style.display = 'none';
    }

    showMainGameArea() {
        document.getElementById('mainGameArea').style.display = 'grid';
    }

    updateStoryInfo(title, subtitle) {
        document.getElementById('storyTitle').textContent = `📚 ${title}`;
        document.getElementById('storySubtitle').textContent = subtitle;
    }
    
    updatePlayerInfo() {
        document.getElementById('myCharacterName').textContent = this.gameState.currentCharacter;
        document.getElementById('myAvatar').textContent = this.getCharacterEmoji(this.gameState.currentCharacter);
        document.getElementById('myStatus').textContent = '游戏中';
    }

    // ============= 剧本查看功能 =============

    async loadCharacterScript() {
        if (!this.gameState.gameSession || !this.gameState.currentCharacter) return;

        try {
            const response = await fetch(`/api/game/script/${this.gameState.gameSession}/${this.gameState.currentCharacter}`);
            const data = await response.json();
            
            if (data.status === 'success') {
                this.currentScript = data.data.script;
                this.displayScript('all');
                this.updateScriptTabs();
            }
        } catch (error) {
            console.error('加载剧本失败:', error);
        }
    }

    showScriptChapter(chapter) {
        // 更新标签状态
        document.querySelectorAll('.script-tab').forEach(tab => {
            tab.classList.remove('active');
        });
        document.querySelector(`[data-chapter="${chapter}"]`).classList.add('active');
        
        this.displayScript(chapter);
    }

    displayScript(chapter) {
        const container = document.getElementById('scriptContent');
        
        if (!this.currentScript) {
            container.innerHTML = '<div class="script-placeholder">剧本加载中...</div>';
            return;
        }

        if (chapter === 'all') {
            // 显示所有章节
            let content = '';
            this.currentScript.forEach((chapterContent, index) => {
                content += `
                    <div class="script-chapter">
                        <h5>第${index + 1}章</h5>
                        <div class="script-chapter-content">${chapterContent}</div>
                    </div>
                `;
            });
            container.innerHTML = content;
        } else {
            // 显示特定章节
            const chapterIndex = parseInt(chapter) - 1;
            if (this.currentScript[chapterIndex]) {
                container.innerHTML = `
                    <div class="script-chapter">
                        <h5>第${chapter}章</h5>
                        <div class="script-chapter-content">${this.currentScript[chapterIndex]}</div>
                    </div>
                `;
            } else {
                container.innerHTML = '<div class="script-placeholder">该章节暂未开放</div>';
            }
        }
    }

    updateScriptTabs() {
        if (!this.currentScript) return;
        
        // 只显示可用的章节标签
        document.querySelectorAll('.script-tab').forEach((tab, index) => {
            const chapter = tab.dataset.chapter;
            if (chapter === 'all') return;
            
            const chapterIndex = parseInt(chapter) - 1;
            if (chapterIndex >= this.currentScript.length) {
                tab.style.display = 'none';
            } else {
                tab.style.display = 'block';
            }
        });
    }

    // ============= 游戏会话管理 =============
    
    async startGameSession() {
        try {
            // 获取游戏状态
            const response = await fetch(`/api/game/status/${this.gameState.gameSession}`);
            const data = await response.json();
            
            if (data.status === 'success') {
                this.gameState.totalChapters = data.data.total_chapters;
                this.gameState.currentChapter = data.data.current_chapter;
                
                this.updateGameProgress();
                
                // 加载角色剧本
                await this.loadCharacterScript();
                
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
                
                // 更新剧本显示
                if (data.data.character_script) {
                    await this.loadCharacterScript();
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

    updateGameProgress() {
        const current = this.gameState.currentChapter;
        const total = this.gameState.totalChapters;
        
        document.getElementById('currentChapter').textContent = `${current}/${total}`;
        document.getElementById('chapterIndicator').textContent = `第${current}章`;
        
        const progress = total > 0 ? (current / total) * 100 : 0;
        document.getElementById('progressFill').style.width = `${progress}%`;
    }
    
    // ============= 消息处理 =============
    
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
            this.updateMessageCount();
            
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

    updateMessageCount() {
        const current = parseInt(document.getElementById('messageCount').textContent) || 0;
        document.getElementById('messageCount').textContent = current + 1;
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
    
    // ============= 消息显示 =============
    
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

    // ============= UI工具方法 =============
    
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
    
    // ============= 模态框管理 =============
    
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

    // ============= 工具功能 =============

    showClues() {
        this.createModal('🔍 线索管理', `
            <div class="clues-panel">
                <div class="clues-list" id="cluesList">
                    <div class="no-clues">暂无线索，继续游戏来收集线索吧！</div>
                </div>
            </div>
        `);
    }

    showNotes() {
        const currentNotes = this.gameState.notes || '';
        this.createModal('📝 个人笔记', `
            <div class="notes-panel">
                <textarea id="personalNotes" placeholder="在此记录您的推理和发现..." rows="10" style="width: 100%; background: rgba(0,0,0,0.7); color: #E0E0E0; border: 1px solid #444; border-radius: 6px; padding: 10px;">${currentNotes}</textarea>
                <div style="text-align: right; margin-top: 15px;">
                    <button class="mystery-btn" onclick="saveNotes()">保存笔记</button>
                </div>
            </div>
        `);
    }

    saveNotes() {
        const notes = document.getElementById('personalNotes').value;
        this.gameState.notes = notes;
        this.showToast('笔记已保存', 'success');
        this.closeAllModals();
    }

    showHistory() {
        const historyContent = this.messageHistory.map(msg => {
            const time = msg.timestamp.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
            return `<div class="history-item"><strong>${msg.speaker}</strong> (${time}): ${msg.content}</div>`;
        }).join('');

        this.createModal('📚 游戏历史', `
            <div class="history-panel" style="max-height: 400px; overflow-y: auto;">
                ${historyContent || '<div class="no-history">暂无历史记录</div>'}
            </div>
        `);
    }

    showSettings() {
        this.createModal('⚙️ 游戏设置', `
            <div class="settings-panel">
                <div class="setting-item">
                    <label><input type="checkbox" id="soundEnabled" ${this.gameState.soundEnabled !== false ? 'checked' : ''}> 🔊 启用音效</label>
                </div>
                <div class="setting-item">
                    <label><input type="checkbox" id="autoScroll" ${this.gameState.autoScroll !== false ? 'checked' : ''}> 📜 自动滚动消息</label>
                </div>
                <div class="setting-item">
                    <label>🎨 主题设置：</label>
                    <select id="themeSelect" style="background: rgba(0,0,0,0.7); color: #E0E0E0; border: 1px solid #444; border-radius: 4px; padding: 5px;">
                        <option value="dark">深色悬疑</option>
                        <option value="classic">经典剧本杀</option>
                    </select>
                </div>
                <div style="text-align: center; margin-top: 20px;">
                    <button class="mystery-btn" onclick="applySettings()">应用设置</button>
                </div>
            </div>
        `);
    }

    applySettings() {
        this.gameState.soundEnabled = document.getElementById('soundEnabled').checked;
        this.gameState.autoScroll = document.getElementById('autoScroll').checked;
        this.showToast('设置已保存', 'success');
        this.closeAllModals();
    }

    emergencyCall() {
        if (confirm('🚨 确定要发起紧急呼叫吗？这将通知所有玩家。')) {
            this.addSystemMessage('🚨 紧急呼叫已发出，等待响应...');
            this.showToast('紧急呼叫已发出', 'warning');
        }
    }

    exitGame() {
        if (confirm('🚪 确定要退出游戏吗？进度将会丢失。')) {
            window.location.href = '/';
        }
    }
}

// ============= 全局函数 =============

function initializeGameInterface() {
    window.murderMysteryGame = new MurderMysteryGameV2();
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

function showGameConfig() {
    if (window.murderMysteryGame) {
        window.murderMysteryGame.showGameConfig();
    }
}

function hideGameConfig() {
    if (window.murderMysteryGame) {
        window.murderMysteryGame.hideGameConfig();
    }
}

function applyGameConfig() {
    if (window.murderMysteryGame) {
        window.murderMysteryGame.applyGameConfig();
    }
}

function browseLocalScripts() {
    if (window.murderMysteryGame) {
        window.murderMysteryGame.browseLocalScripts();
    }
}

function selectLocalScript(path, title) {
    if (window.murderMysteryGame) {
        window.murderMysteryGame.selectLocalScript(path, title);
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
        window.murderMysteryGame.loadExistingGame(gamePath);
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

function showScriptChapter(chapter) {
    if (window.murderMysteryGame) {
        window.murderMysteryGame.showScriptChapter(chapter);
    }
}

function skipWait() {
    if (window.murderMysteryGame) {
        window.murderMysteryGame.skipWait();
    }
}

function showClues() {
    if (window.murderMysteryGame) {
        window.murderMysteryGame.showClues();
    }
}

function showNotes() {
    if (window.murderMysteryGame) {
        window.murderMysteryGame.showNotes();
    }
}

function saveNotes() {
    if (window.murderMysteryGame) {
        window.murderMysteryGame.saveNotes();
    }
}

function showHistory() {
    if (window.murderMysteryGame) {
        window.murderMysteryGame.showHistory();
    }
}

function showSettings() {
    if (window.murderMysteryGame) {
        window.murderMysteryGame.showSettings();
    }
}

function applySettings() {
    if (window.murderMysteryGame) {
        window.murderMysteryGame.applySettings();
    }
}

function emergencyCall() {
    if (window.murderMysteryGame) {
        window.murderMysteryGame.emergencyCall();
    }
}

function exitGame() {
    if (window.murderMysteryGame) {
        window.murderMysteryGame.exitGame();
    }
}

function closeAllModals() {
    if (window.murderMysteryGame) {
        window.murderMysteryGame.closeAllModals();
    }
}

// ============= CSS样式注入 =============

const additionalStyles = document.createElement('style');
additionalStyles.textContent = `
    @keyframes slideInToast {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOutToast {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
    
    .local-scripts-list, .game-list {
        max-width: 600px;
        max-height: 400px;
        overflow-y: auto;
    }
    
    .local-script-item, .game-item {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 10px;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .local-script-item:hover, .game-item:hover {
        background: rgba(255, 255, 255, 0.2);
        transform: translateY(-2px);
    }
    
    .script-title, .game-title {
        color: #FFD700;
        font-weight: bold;
        margin-bottom: 8px;
    }
    
    .script-info, .game-info {
        color: #B0B0B0;
        font-size: 0.9em;
        display: flex;
        gap: 15px;
        margin-bottom: 5px;
    }
    
    .script-path {
        color: #888;
        font-size: 0.8em;
        font-family: monospace;
    }
    
    .loading-message, .no-games, .error-message, .no-clues, .no-history {
        text-align: center;
        color: #B0B0B0;
        padding: 40px 20px;
        font-style: italic;
    }
    
    .clues-panel, .notes-panel, .history-panel, .settings-panel {
        min-width: 400px;
        max-width: 600px;
    }
    
    .setting-item {
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .setting-item label {
        color: #E0E0E0;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .history-item {
        padding: 10px;
        border-bottom: 1px solid #333;
        color: #E0E0E0;
        line-height: 1.4;
    }
    
    .history-item strong {
        color: #FFD700;
    }
`;
document.head.appendChild(additionalStyles);