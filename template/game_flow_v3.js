/**
 * 剧本杀游戏严格流程控制器 V3
 * 实现: DM发言 → 玩家发言/询问 → 被询问玩家回答 的严格三阶段流程
 */

class GameFlowController {
    constructor() {
        this.gameState = window.gameState;
        this.phaseTimer = null;
        this.gameTimer = null;
        this.messageHistory = [];
        this.currentScript = null;
        this.progressChecker = null;
        
        // 游戏配置 (从config.py加载)
        this.config = {
            playerSpeakTime: 180,    // 玩家发言阶段时间(秒)
            playerAnswerTime: 60,    // 玩家回答阶段时间(秒)
            chapterCycles: 3,        // 每章节循环次数
            dmSpeakDelay: 2,         // DM发言延迟(秒)
            aiResponseDelay: 3       // AI玩家回应延迟(秒)
        };
        
        this.init();
    }
    
    init() {
        this.setupMarkdown();
        this.loadGameConfig();
        this.startGameTimer();
        this.checkExistingGame();
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
                // 更新配置
                this.config.playerSpeakTime = data.data.GAME_PLAYER_SPEAK_TIME || 180;
                this.config.playerAnswerTime = data.data.GAME_PLAYER_ANSWER_TIME || 60;
                this.config.chapterCycles = data.data.GAME_CHAPTER_CYCLES || 3;
                this.config.dmSpeakDelay = data.data.GAME_DM_SPEAK_DELAY || 2;
                this.config.aiResponseDelay = data.data.GAME_AI_RESPONSE_DELAY || 3;
                
                console.log('游戏配置加载成功:', this.config);
            }
        } catch (error) {
            console.error('加载游戏配置失败:', error);
        }
    }
    
    checkExistingGame() {
        // 检查是否有正在进行的游戏
        const savedSession = localStorage.getItem('currentGameSession');
        if (savedSession) {
            this.gameState.gameSession = savedSession;
            this.checkGameStatus();
        }
    }
    
    async checkGameStatus() {
        if (!this.gameState.gameSession) return;
        
        try {
            const response = await fetch(`/api/game/status/${this.gameState.gameSession}`);
            const data = await response.json();
            
            if (data.status === 'success') {
                const gameData = data.data;
                
                // 更新游戏状态
                this.gameState.currentChapter = gameData.current_chapter || 0;
                this.gameState.currentPhase = gameData.current_phase || 'waiting';
                this.gameState.currentCycle = gameData.current_cycle || 0;
                
                // 检查用户是否已选择角色
                const userCharacter = gameData.players[this.gameState.user.id];
                if (userCharacter) {
                    this.gameState.currentCharacter = userCharacter;
                    this.gameState.gameMode = 'playing';
                    this.showMainGameInterface();
                    await this.loadCharacters();
                    await this.loadCharacterScript();
                } else if (gameData.game_state === 'character_select') {
                    this.gameState.gameMode = 'character_select';
                    this.showCharacterSelection(gameData.characters || []);
                }
                
                this.updateGameStatusDisplay();
            }
        } catch (error) {
            console.error('检查游戏状态失败:', error);
        }
    }
    
    // ================== 游戏配置管理 ==================
    
    showGameConfig() {
        document.getElementById('configPanel').style.display = 'block';
    }

    hideGameConfig() {
        document.getElementById('configPanel').style.display = 'none';
    }

    applyGameConfig() {
        const scriptSource = document.querySelector('input[name="scriptSource"]:checked').value;
        const localScriptPath = document.getElementById('localScriptPath').value;
        const generateImages = document.getElementById('generateImages').checked;

        if (scriptSource === 'local' && !localScriptPath.trim()) {
            this.showToast('请选择本地剧本路径', 'warning');
            return;
        }

        this.gameState.config = {
            scriptSource,
            localScriptPath: localScriptPath.trim(),
            generateImages
        };

        this.hideGameConfig();
        this.showToast('配置已保存', 'success');
    }

    async browseLocalScripts() {
        try {
            const response = await fetch('/api/game/list');
            const data = await response.json();
            
            if (data.status === 'success' && data.data.games.length > 0) {
                this.showLocalScriptsModal(data.data.games);
            } else {
                this.showToast('未找到可用的本地剧本', 'warning');
            }
        } catch (error) {
            console.error('浏览本地剧本失败:', error);
            this.showToast('浏览失败，请重试', 'error');
        }
    }
    
    // ================== 游戏启动管理 ==================
    
    async startNewGame() {
        if (!this.gameState.config) {
            this.showToast('请先配置游戏参数', 'warning');
            this.showGameConfig();
            return;
        }

        const config = this.gameState.config;
        
        if (config.scriptSource === 'local') {
            await this.loadExistingGame(config.localScriptPath);
        } else {
            await this.createNewGame(config.generateImages);
        }
    }

    async createNewGame(generateImages = true) {
        try {
            this.addSystemMessage('🎭 正在生成新的剧本杀剧本...');
            this.showProgressModal();
            
            const response = await fetch('/api/game/new', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    generate_images: generateImages,
                    wait_for_completion: true,
                    user_id: this.gameState.user.id
                })
            });
            
            const data = await response.json();
            if (data.status === 'success') {
                this.gameState.gameSession = data.data.game_session;
                localStorage.setItem('currentGameSession', this.gameState.gameSession);
                
                this.updateStoryTitle(data.data.story_title);
                
                if (generateImages) {
                    this.startProgressMonitoring(data.data.game_session);
                } else {
                    this.hideProgressModal();
                    this.showCharacterSelection(data.data.characters);
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
            await this.showGameListModal();
            return;
        }

        try {
            this.addSystemMessage('📂 正在加载游戏...');
            
            const response = await fetch('/api/game/load', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    game_path: gamePath,
                    user_id: this.gameState.user.id
                })
            });
            
            const data = await response.json();
            if (data.status === 'success') {
                this.gameState.gameSession = data.data.game_session;
                localStorage.setItem('currentGameSession', this.gameState.gameSession);
                
                this.updateStoryTitle(data.data.story_title);
                this.showCharacterSelection(data.data.characters);
                
                this.addSystemMessage('✅ 游戏加载成功！请选择您的角色。');
            } else {
                this.addSystemMessage('❌ 加载游戏失败：' + data.message);
            }
        } catch (error) {
            console.error('加载游戏失败:', error);
            this.addSystemMessage('❌ 网络错误，请检查连接后重试。');
        }
    }
    
    // ================== 角色选择管理 ==================
    
    showCharacterSelection(characters) {
        const panel = document.getElementById('characterSelection');
        const grid = document.getElementById('characterGrid');
        
        grid.innerHTML = characters.map((char, index) => {
            const isString = typeof char === 'string';
            const charName = isString ? char : char.name;
            const charDesc = isString ? `神秘的角色：${charName}` : (char.description || '神秘的角色，等待你来揭开面纱...');
            const charImage = (!isString && char.image) ? 
                `<img src="/${char.image}" class="character-image" alt="${charName}">` : 
                `<div class="character-avatar">${this.getCharacterEmoji(charName)}</div>`;
            
            return `
                <div class="character-card" onclick="selectCharacter('${charName}', ${index})">
                    ${charImage}
                    <div class="character-name">${charName}</div>
                    <div class="character-description">${charDesc}</div>
                </div>
            `;
        }).join('');
        
        panel.style.display = 'block';
        this.gameState.availableCharacters = characters;
    }
    
    selectCharacter(characterName, index) {
        document.querySelectorAll('.character-card').forEach(card => {
            card.classList.remove('selected');
        });
        
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
                headers: { 'Content-Type': 'application/json' },
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
                
                // 隐藏角色选择，显示游戏界面
                document.getElementById('characterSelection').style.display = 'none';
                this.showMainGameInterface();
                
                // 加载角色列表和剧本
                await this.loadCharacters();
                await this.loadCharacterScript();
                
                // 开始游戏
                await this.startGameSession();
                
                this.addSystemMessage(`✅ 成功加入游戏！您现在是：${this.gameState.currentCharacter}`);
            } else {
                this.addSystemMessage('❌ 加入游戏失败：' + data.message);
            }
        } catch (error) {
            console.error('确认角色选择失败:', error);
            this.addSystemMessage('❌ 网络错误，请检查连接后重试。');
        }
    }
    
    // ================== 主游戏界面管理 ==================
    
    showMainGameInterface() {
        document.getElementById('gameMain').style.display = 'grid';
        this.setupPhaseControl();
    }
    
    async loadCharacters() {
        try {
            const response = await fetch(`/api/game/characters/${this.gameState.gameSession}`);
            const data = await response.json();
            
            if (data.status === 'success') {
                this.gameState.characters = data.data.characters;
                this.displayCharactersList();
            }
        } catch (error) {
            console.error('加载角色列表失败:', error);
        }
    }
    
    displayCharactersList() {
        const container = document.getElementById('charactersList');
        
        container.innerHTML = this.gameState.characters.map(char => {
            const isCurrentUser = char.is_current_user;
            const playerType = char.is_ai ? 'AI' : '玩家';
            const status = isCurrentUser ? '你' : (char.is_ai ? '待机中' : '在线');
            
            const avatarHtml = char.image ? 
                `<img src="/${char.image}" class="character-avatar-small" alt="${char.name}">` :
                `<div class="character-avatar-placeholder">${this.getCharacterEmoji(char.name)}</div>`;
            
            return `
                <div class="character-item ${isCurrentUser ? 'current-user' : ''} ${char.is_ai ? 'ai-player' : ''}">
                    ${avatarHtml}
                    <div class="character-info">
                        <div class="name">${char.name}</div>
                        <div class="status">${status}</div>
                        <div class="player-type">${playerType}</div>
                    </div>
                </div>
            `;
        }).join('');
    }
    
    async loadCharacterScript() {
        if (!this.gameState.gameSession || !this.gameState.currentCharacter) return;

        try {
            const response = await fetch(`/api/game/script/${this.gameState.gameSession}/${this.gameState.currentCharacter}`);
            const data = await response.json();
            
            if (data.status === 'success') {
                this.currentScript = data.data.script;
                this.displayScript('current');
                this.updateScriptTabs();
            }
        } catch (error) {
            console.error('加载剧本失败:', error);
        }
    }
    
    // ================== 游戏流程控制 ==================
    
    async startGameSession() {
        try {
            const response = await fetch(`/api/game/status/${this.gameState.gameSession}`);
            const data = await response.json();
            
            if (data.status === 'success') {
                this.gameState.currentChapter = data.data.current_chapter || 0;
                this.gameState.currentCycle = data.data.current_cycle || 0;
                this.gameState.currentPhase = data.data.current_phase || 'waiting';
                
                this.updateGameStatusDisplay();
                
                // 如果游戏还没开始，开始第一章
                if (this.gameState.currentChapter === 0) {
                    setTimeout(() => {
                        this.startChapter(1);
                    }, 3000); // 3秒后开始
                } else {
                    // 恢复当前阶段
                    this.resumeCurrentPhase();
                }
            }
        } catch (error) {
            console.error('启动游戏会话失败:', error);
        }
    }
    
    async startChapter(chapterNum) {
        try {
            this.addSystemMessage(`📖 第${chapterNum}章即将开始...`);
            
            const response = await fetch('/api/game/chapter/start', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    game_session: this.gameState.gameSession,
                    chapter_num: chapterNum,
                    character_name: this.gameState.currentCharacter
                })
            });
            
            const data = await response.json();
            if (data.status === 'success') {
                this.gameState.currentChapter = chapterNum;
                this.gameState.currentCycle = 1;
                this.updateGameStatusDisplay();
                
                // 重新加载剧本（新章节内容）
                await this.loadCharacterScript();
                
                // 开始DM发言阶段
                this.startDMSpeakPhase(data.data.dm_speech);
                
                this.addSystemMessage(`✅ 第${chapterNum}章已开始！`);
            } else {
                this.addSystemMessage('❌ 开始章节失败：' + data.message);
            }
        } catch (error) {
            console.error('开始章节失败:', error);
            this.addSystemMessage('❌ 网络错误，请检查连接后重试。');
        }
    }
    
    // ================== 三阶段流程管理 ==================
    
    startDMSpeakPhase(dmContent = null) {
        this.gameState.currentPhase = 'dm_speak';
        this.updatePhaseDisplay('🎭 DM发言阶段', '请等待游戏主持人讲述剧情...');
        this.disableInput('DM正在发言，请等待...');
        
        // 模拟DM发言延迟
        setTimeout(() => {
            if (dmContent) {
                this.addDMMessage('游戏主持', dmContent);
            } else {
                this.addDMMessage('游戏主持', `第${this.gameState.currentChapter}章 - 第${this.gameState.currentCycle}轮讨论开始。请仔细观察，寻找线索，大胆推理！`);
            }
            
            // 发言完成后开始玩家发言阶段
            setTimeout(() => {
                this.startPlayerSpeakPhase();
            }, this.config.dmSpeakDelay * 1000);
            
        }, 1000);
    }
    
    startPlayerSpeakPhase() {
        this.gameState.currentPhase = 'player_speak';
        this.updatePhaseDisplay('💬 玩家发言阶段', '你可以发言并询问其他玩家');
        this.enableInput();
        this.setupQueryList();
        
        // 启动计时器
        this.startPhaseTimer(this.config.playerSpeakTime, () => {
            // 时间到自动发送
            this.autoSendPlayerMessage();
        });
    }
    
    startPlayerAnswerPhase(queries) {
        this.gameState.currentPhase = 'player_answer';
        this.updatePhaseDisplay('🗣️ 玩家回答阶段', '等待被询问的玩家回答问题');
        this.disableInput('当前是回答阶段，请等待其他玩家回答');
        
        // 处理AI玩家的自动回答
        this.handleAIPlayerAnswers(queries);
        
        // 启动计时器
        this.startPhaseTimer(this.config.playerAnswerTime, () => {
            // 时间到进入下一轮或总结
            this.endAnswerPhase();
        });
    }
    
    async handleAIPlayerAnswers(queries) {
        // 延迟后让AI玩家回答
        setTimeout(async () => {
            for (const [targetPlayer, question] of Object.entries(queries)) {
                const targetChar = this.gameState.characters.find(c => c.name === targetPlayer);
                if (targetChar && targetChar.is_ai) {
                    try {
                        // 调用AI回答API
                        const response = await fetch('/api/game/ai_answer', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                game_session: this.gameState.gameSession,
                                character_name: targetPlayer,
                                question: question,
                                asker: this.gameState.currentCharacter,
                                chapter: this.gameState.currentChapter
                            })
                        });
                        
                        const data = await response.json();
                        if (data.status === 'success') {
                            this.addPlayerMessage(targetPlayer, data.data.answer, 'response');
                        }
                    } catch (error) {
                        console.error(`AI玩家 ${targetPlayer} 回答失败:`, error);
                    }
                }
            }
        }, this.config.aiResponseDelay * 1000);
    }
    
    endAnswerPhase() {
        this.stopPhaseTimer();
        
        // 检查是否完成当前章节的所有循环
        if (this.gameState.currentCycle >= this.config.chapterCycles) {
            this.startDMSummaryPhase();
        } else {
            // 进入下一循环
            this.gameState.currentCycle++;
            this.updateGameStatusDisplay();
            this.startDMSpeakPhase();
        }
    }
    
    startDMSummaryPhase() {
        this.gameState.currentPhase = 'dm_summary';
        this.updatePhaseDisplay('📋 DM总结阶段', 'DM正在总结本章节内容...');
        this.disableInput('DM正在总结，请等待...');
        
        // 模拟DM总结
        setTimeout(() => {
            this.addDMMessage('游戏主持', `第${this.gameState.currentChapter}章总结：根据大家的讨论，现在公布新的线索...`);
            
            // 总结完成后进入下一章节或结束游戏
            setTimeout(() => {
                if (this.gameState.currentChapter >= 3) { // 假设共3章
                    this.endGame();
                } else {
                    this.startChapter(this.gameState.currentChapter + 1);
                }
            }, 5000);
            
        }, 2000);
    }
    
    // ================== 输入控制管理 ==================
    
    setupPhaseControl() {
        // 设置初始状态
        this.disableInput('等待游戏开始...');
    }
    
    enableInput() {
        const inputArea = document.getElementById('inputArea');
        const phaseDisabled = document.getElementById('phaseDisabled');
        
        inputArea.style.display = 'block';
        phaseDisabled.style.display = 'none';
    }
    
    disableInput(message) {
        const inputArea = document.getElementById('inputArea');
        const phaseDisabled = document.getElementById('phaseDisabled');
        const disabledText = document.getElementById('disabledText');
        
        inputArea.style.display = 'none';
        phaseDisabled.style.display = 'flex';
        disabledText.textContent = message;
    }
    
    setupQueryList() {
        const queryList = document.getElementById('queryList');
        const otherCharacters = this.gameState.characters.filter(c => 
            c.name !== this.gameState.currentCharacter
        );
        
        queryList.innerHTML = otherCharacters.map(char => `
            <div class="query-item">
                <label>${char.name}:</label>
                <input type="text" data-character="${char.name}" placeholder="询问 ${char.name} 的问题...">
            </div>
        `).join('');
    }
    
    toggleQuerySection() {
        const queryList = document.getElementById('queryList');
        const toggleBtn = document.getElementById('queryToggleBtn');
        
        if (queryList.style.display === 'none') {
            queryList.style.display = 'block';
            toggleBtn.textContent = '收起询问';
        } else {
            queryList.style.display = 'none';
            toggleBtn.textContent = '展开询问';
        }
    }
    
    // ================== 计时器管理 ==================
    
    startPhaseTimer(seconds, onTimeout) {
        this.stopPhaseTimer();
        
        let timeLeft = seconds;
        this.gameState.phaseTimeLeft = timeLeft;
        
        this.updateTimerDisplay(timeLeft);
        
        this.phaseTimer = setInterval(() => {
            timeLeft--;
            this.gameState.phaseTimeLeft = timeLeft;
            this.updateTimerDisplay(timeLeft);
            
            if (timeLeft <= 0) {
                this.stopPhaseTimer();
                if (onTimeout) onTimeout();
            }
        }, 1000);
    }
    
    stopPhaseTimer() {
        if (this.phaseTimer) {
            clearInterval(this.phaseTimer);
            this.phaseTimer = null;
        }
    }
    
    updateTimerDisplay(timeLeft) {
        const minutes = Math.floor(timeLeft / 60);
        const seconds = timeLeft % 60;
        const timeString = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        
        // 更新显示
        document.getElementById('phaseTimer').textContent = timeString;
        document.getElementById('phaseTimerDisplay').textContent = timeString;
        
        // 更新进度条
        const totalTime = this.gameState.currentPhase === 'player_speak' ? 
            this.config.playerSpeakTime : this.config.playerAnswerTime;
        const percentage = (timeLeft / totalTime) * 100;
        document.getElementById('timerFill').style.width = `${percentage}%`;
        
        // 颜色变化
        const timerElement = document.getElementById('phaseTimer');
        if (timeLeft <= 30) {
            timerElement.style.color = '#FF6B6B';
        } else if (timeLeft <= 60) {
            timerElement.style.color = '#FFA500';
        } else {
            timerElement.style.color = '#FFD700';
        }
    }
    
    // ================== 消息发送管理 ==================
    
    prepareSendMessage() {
        // 收集发言内容
        const content = document.getElementById('contentInput').value.trim();
        
        // 收集询问内容
        const queries = {};
        document.querySelectorAll('#queryList input').forEach(input => {
            const character = input.dataset.character;
            const question = input.value.trim();
            if (question) {
                queries[character] = question;
            }
        });
        
        // 验证内容
        if (!content && Object.keys(queries).length === 0) {
            this.showToast('请输入发言内容或询问问题', 'warning');
            return;
        }
        
        // 存储待发送内容
        this.gameState.pendingContent = content || '[保持沉默]';
        this.gameState.pendingQueries = queries;
        
        // 显示确认模态框
        this.showSendConfirmModal();
    }
    
    showSendConfirmModal() {
        const modal = document.getElementById('sendConfirmModal');
        const contentPreview = document.getElementById('contentPreview');
        const queriesPreview = document.getElementById('queriesPreview');
        const queriesListPreview = document.getElementById('queriesListPreview');
        
        // 显示发言预览
        contentPreview.innerHTML = this.renderMarkdown(this.gameState.pendingContent);
        
        // 显示询问预览
        const queries = this.gameState.pendingQueries;
        if (Object.keys(queries).length > 0) {
            queriesPreview.style.display = 'block';
            queriesListPreview.innerHTML = Object.entries(queries).map(([character, question]) => `
                <div class="query-preview">
                    <div class="target">→ ${character}</div>
                    <div class="content">${question}</div>
                </div>
            `).join('');
        } else {
            queriesPreview.style.display = 'none';
        }
        
        modal.style.display = 'flex';
    }
    
    cancelSendMessage() {
        document.getElementById('sendConfirmModal').style.display = 'none';
        this.gameState.pendingContent = '';
        this.gameState.pendingQueries = {};
    }
    
    async confirmSendMessage() {
        document.getElementById('sendConfirmModal').style.display = 'none';
        
        try {
            // 立即显示用户消息
            this.addPlayerMessage(
                this.gameState.currentCharacter, 
                this.gameState.pendingContent,
                'speak'
            );
            
            // 显示询问
            Object.entries(this.gameState.pendingQueries).forEach(([character, question]) => {
                this.addPlayerMessage(
                    this.gameState.currentCharacter,
                    `询问 ${character}: ${question}`,
                    'query'
                );
            });
            
            // 清空输入
            this.clearInputs();
            
            // 发送到后端
            const response = await fetch('/api/game/player_action', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    game_session: this.gameState.gameSession,
                    character_name: this.gameState.currentCharacter,
                    content: this.gameState.pendingContent,
                    queries: this.gameState.pendingQueries,
                    chapter: this.gameState.currentChapter,
                    cycle: this.gameState.currentCycle
                })
            });
            
            const data = await response.json();
            if (data.status === 'success') {
                // 停止计时器，进入回答阶段
                this.stopPhaseTimer();
                this.startPlayerAnswerPhase(this.gameState.pendingQueries);
            } else {
                this.addSystemMessage('❌ 发送失败：' + data.message);
            }
            
        } catch (error) {
            console.error('发送消息失败:', error);
            this.addSystemMessage('❌ 网络错误，请检查连接后重试。');
        }
        
        // 清空待发送内容
        this.gameState.pendingContent = '';
        this.gameState.pendingQueries = {};
    }
    
    autoSendPlayerMessage() {
        // 自动发送当前输入的内容
        const content = document.getElementById('contentInput').value.trim();
        
        if (content) {
            this.gameState.pendingContent = content;
            this.gameState.pendingQueries = {}; // 超时时丢弃询问
            this.confirmSendMessage();
        } else {
            // 如果没有输入，发送默认内容
            this.gameState.pendingContent = '[保持沉默]';
            this.gameState.pendingQueries = {};
            this.confirmSendMessage();
        }
        
        this.showToast('时间到！已自动发送', 'warning');
    }
    
    clearInputs() {
        document.getElementById('contentInput').value = '';
        document.querySelectorAll('#queryList input').forEach(input => {
            input.value = '';
        });
        this.updateCharCount();
    }
    
    updateCharCount() {
        const input = document.getElementById('contentInput');
        const charCount = document.getElementById('charCount');
        
        if (input && charCount) {
            const length = input.value.length;
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
    
    // ================== 显示管理 ==================
    
    updateStoryTitle(title) {
        document.getElementById('storyTitle').textContent = `📚 ${title}`;
    }
    
    updatePhaseDisplay(phaseName, description) {
        document.getElementById('currentPhase').textContent = phaseName;
        document.getElementById('phaseText').textContent = description;
    }
    
    updateGameStatusDisplay() {
        document.getElementById('chapterInfo').textContent = `第${this.gameState.currentChapter}章`;
        document.getElementById('cycleInfo').textContent = `循环 ${this.gameState.currentCycle}/${this.config.chapterCycles}`;
        
        // 更新统计
        document.getElementById('currentChapterStat').textContent = this.gameState.currentChapter;
        document.getElementById('currentCycleStat').textContent = `${this.gameState.currentCycle}/${this.config.chapterCycles}`;
    }
    
    // ================== 消息显示 ==================
    
    addMessage(content, type = 'system', speaker = '系统', icon = '🔔', timestamp = null) {
        const container = document.getElementById('messagesContainer');
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
        
        container.appendChild(messageElement);
        this.scrollToBottom();
        
        // 保存到历史记录
        this.messageHistory.push({
            content, type, speaker, timestamp: new Date()
        });
    }
    
    addSystemMessage(content) {
        this.addMessage(content, 'system', '系统', '🔔');
    }
    
    addDMMessage(speaker, content) {
        this.addMessage(content, 'dm', `🎭 ${speaker}`, '🎭');
    }
    
    addPlayerMessage(speaker, content, messageType = 'speak') {
        let icon = '👤';
        let type = 'player';
        
        switch (messageType) {
            case 'query':
                icon = '❓';
                break;
            case 'response':
                icon = '💬';
                break;
            case 'speak':
            default:
                icon = '👤';
                break;
        }
        
        this.addMessage(content, type, speaker, icon);
    }
    
    // ================== 工具方法 ==================
    
    renderMarkdown(content) {
        if (typeof marked !== 'undefined') {
            try {
                const html = marked.parse(content);
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
        const container = document.getElementById('messagesContainer');
        if (container) {
            setTimeout(() => {
                container.scrollTop = container.scrollHeight;
            }, 100);
        }
    }
    
    getCurrentTime() {
        const now = new Date();
        return now.toLocaleTimeString('zh-CN', { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
    }
    
    getCharacterEmoji(characterName) {
        if (!characterName) return '👤';
        
        const emojis = ['🕵️', '👨‍💼', '👩‍💼', '👨‍⚖️', '👩‍⚖️', '👨‍🎨', '👩‍🎨', '👨‍🔬', '👩‍🔬', '🤵', '👸'];
        const index = characterName.length % emojis.length;
        return emojis[index];
    }
    
    startGameTimer() {
        const startTime = new Date();
        this.gameTimer = setInterval(() => {
            const now = new Date();
            const diff = now - startTime;
            const minutes = Math.floor(diff / 60000);
            const seconds = Math.floor((diff % 60000) / 1000);
            
            document.getElementById('gameTimeStat').textContent = 
                `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        }, 1000);
    }
    
    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.style.cssText = `
            position: fixed;
            top: 90px;
            right: 20px;
            background: ${type === 'error' ? '#FF6B6B' : type === 'warning' ? '#FFA500' : '#4CAF50'};
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            z-index: 1001;
            animation: slideInToast 0.3s ease;
            max-width: 300px;
        `;
        toast.textContent = message;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.style.animation = 'slideOutToast 0.3s ease';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
    
    // ================== 进度管理 ==================
    
    showProgressModal() {
        document.getElementById('progressModal').style.display = 'flex';
        this.updateProgress(0, '开始生成剧本...');
        this.updateProgressStatus('scriptStatus', 'progress', '生成中...');
        this.updateProgressStatus('imageStatus', 'waiting', '等待中...');
        this.updateProgressStatus('gameStatus', 'waiting', '等待中...');
    }

    hideProgressModal() {
        document.getElementById('progressModal').style.display = 'none';
        if (this.progressChecker) {
            clearInterval(this.progressChecker);
            this.progressChecker = null;
        }
    }

    updateProgress(percentage, text) {
        const progressBar = document.getElementById('progressFill');
        const progressText = document.getElementById('progressText');
        
        if (progressBar) progressBar.style.width = `${percentage}%`;
        if (progressText) progressText.textContent = text;
    }

    updateProgressStatus(elementId, status, text) {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = text;
            element.className = `progress-status ${status}`;
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
                    
                    if (gameData.script_ready) {
                        this.updateProgressStatus('scriptStatus', 'completed', '已完成');
                        progress = Math.max(progress, 40);
                        this.updateProgress(progress, '正在生成角色图片...');
                    }
                    
                    if (gameData.images_ready) {
                        this.updateProgressStatus('imageStatus', 'completed', '已完成');
                        progress = Math.max(progress, 80);
                        this.updateProgress(progress, '正在准备游戏...');
                    }
                    
                    if (gameData.game_ready) {
                        this.updateProgressStatus('gameStatus', 'completed', '已完成');
                        progress = 100;
                        this.updateProgress(progress, '游戏准备完成！');
                        
                        setTimeout(() => {
                            this.hideProgressModal();
                            this.showCharacterSelection(gameData.characters);
                            this.addSystemMessage('✅ 剧本和图片生成完成！请选择您要扮演的角色。');
                        }, 1000);
                        
                        clearInterval(this.progressChecker);
                        this.progressChecker = null;
                    }
                }
            } catch (error) {
                console.error('监控进度失败:', error);
            }
        }, 2000);
    }
    
    // ================== 剧本显示管理 ==================
    
    showScriptChapter(chapter) {
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

        if (chapter === 'current') {
            // 显示当前章节
            const currentChapterIndex = Math.max(0, this.gameState.currentChapter - 1);
            if (this.currentScript[currentChapterIndex]) {
                container.innerHTML = `
                    <div class="script-chapter">
                        <h5>第${this.gameState.currentChapter}章</h5>
                        <div class="script-chapter-content">${this.currentScript[currentChapterIndex]}</div>
                    </div>
                `;
            } else {
                container.innerHTML = '<div class="script-placeholder">当前章节剧本尚未开放</div>';
            }
        } else if (chapter === 'all') {
            // 显示所有已开放章节
            let content = '';
            this.currentScript.forEach((chapterContent, index) => {
                content += `
                    <div class="script-chapter">
                        <h5>第${index + 1}章</h5>
                        <div class="script-chapter-content">${chapterContent}</div>
                    </div>
                `;
            });
            container.innerHTML = content || '<div class="script-placeholder">暂无可用剧本</div>';
        }
    }

    updateScriptTabs() {
        // 根据当前章节更新标签显示
        const currentTab = document.querySelector('[data-chapter="current"]');
        if (currentTab) {
            currentTab.textContent = `第${this.gameState.currentChapter}章`;
            currentTab.style.display = this.gameState.currentChapter > 0 ? 'block' : 'none';
        }
    }
    
    // ================== 其他工具功能 ==================
    
    showClues() {
        this.showToast('线索功能开发中...', 'info');
    }

    showNotes() {
        this.showToast('笔记功能开发中...', 'info');
    }

    showHistory() {
        this.showToast('历史功能开发中...', 'info');
    }

    showSettings() {
        this.showToast('设置功能开发中...', 'info');
    }
    
    endGame() {
        this.addSystemMessage('🎉 游戏结束！感谢您的参与。');
        this.disableInput('游戏已结束');
        this.stopPhaseTimer();
        
        // 清理游戏状态
        localStorage.removeItem('currentGameSession');
    }
}

// ================== 全局函数 ==================

function showGameConfig() {
    if (window.gameController) {
        window.gameController.showGameConfig();
    }
}

function hideGameConfig() {
    if (window.gameController) {
        window.gameController.hideGameConfig();
    }
}

function applyGameConfig() {
    if (window.gameController) {
        window.gameController.applyGameConfig();
    }
}

function browseLocalScripts() {
    if (window.gameController) {
        window.gameController.browseLocalScripts();
    }
}

function startNewGame() {
    if (window.gameController) {
        window.gameController.startNewGame();
    }
}

function loadExistingGame() {
    if (window.gameController) {
        window.gameController.loadExistingGame();
    }
}

function selectCharacter(characterName, index) {
    if (window.gameController) {
        window.gameController.selectCharacter(characterName, index);
    }
}

function confirmCharacterSelection() {
    if (window.gameController) {
        window.gameController.confirmCharacterSelection();
    }
}

function toggleQuerySection() {
    if (window.gameController) {
        window.gameController.toggleQuerySection();
    }
}

function prepareSendMessage() {
    if (window.gameController) {
        window.gameController.prepareSendMessage();
    }
}

function cancelSendMessage() {
    if (window.gameController) {
        window.gameController.cancelSendMessage();
    }
}

function confirmSendMessage() {
    if (window.gameController) {
        window.gameController.confirmSendMessage();
    }
}

function showScriptChapter(chapter) {
    if (window.gameController) {
        window.gameController.showScriptChapter(chapter);
    }
}

function showClues() {
    if (window.gameController) {
        window.gameController.showClues();
    }
}

function showNotes() {
    if (window.gameController) {
        window.gameController.showNotes();
    }
}

function showHistory() {
    if (window.gameController) {
        window.gameController.showHistory();
    }
}

function showSettings() {
    if (window.gameController) {
        window.gameController.showSettings();
    }
}

// 添加CSS动画
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
`;
document.head.appendChild(additionalStyles);