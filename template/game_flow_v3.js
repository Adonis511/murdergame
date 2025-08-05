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
    
    // 通用的fetch请求包装器，添加日志
    async apiRequest(url, options = {}) {
        const method = options.method || 'GET';
        const hasBody = options.body ? JSON.parse(options.body) : null;
        
        console.log(`🌐 [${method}] 发起请求: ${url}`);
        if (hasBody) {
            console.log(`📤 请求参数:`, hasBody);
        }
        
        try {
            const response = await fetch(url, options);
            console.log(`📡 [${response.status}] 响应: ${url}`);
            
            const data = await response.json();
            console.log(`📦 响应数据:`, data);
            
            return { response, data };
        } catch (error) {
            console.error(`❌ 请求失败: ${url}`, error);
            throw error;
        }
    }
    
    init() {
        console.log('🎮 【游戏初始化】剧本杀游戏控制器启动');
        console.log('📚 【流程说明】游戏流程: 新游戏 → 角色选择 → 章节循环(DM发言 → 玩家发言 → 玩家回答) × 3轮 → DM总结 → 下一章');
        console.log('🌐 【API接口】前端将调用以下接口:');
        console.log('   - /api/config (获取游戏配置)');
        console.log('   - /api/game/new (创建新游戏)');
        console.log('   - /api/game/join (加入游戏选择角色)');
        console.log('   - /api/game/chapter/start (开始章节)');
        console.log('   - /api/game/trigger_all_ai_speak (触发AI发言)');
        console.log('   - /api/game/speaking_status (监控发言状态)');
        console.log('   - /api/game/player_action (玩家行动)');
        console.log('   - /api/game/ai_answer (AI回答)');
        console.log('   - /api/game/dm_speak (DM发言)');
        console.log('   - /api/game/characters (获取角色列表)');
        console.log('   - /api/game/script (获取角色剧本)');
        console.log('   - /api/game/status (获取游戏状态)');
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
                 
                 // 保存默认剧本路径
                 this.config.defaultScriptPath = data.data.DEFAULT_SCRIPT_PATH || null;
                 
                 console.log('游戏配置加载成功:', this.config);
                 
                 // 如果有默认剧本路径，自动设置配置
                 if (this.config.defaultScriptPath) {
                     this.gameState.config = {
                         scriptSource: 'local',
                         localScriptPath: this.config.defaultScriptPath,
                         generateImages: true
                     };
                     
                     // 更新配置界面
                     this.updateConfigUI();
                 }
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
            console.log('🎭 【新游戏】开始创建新游戏');
            console.log(`🖼️ 生成图片: ${generateImages}`);
            this.addSystemMessage('🎭 正在生成剧本...');
            this.showProgressModal();
            
            const { response, data } = await this.apiRequest('/api/game/new', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    generate_images: generateImages,
                    wait_for_completion: true,
                    user_id: this.gameState.user.id
                })
            });
            
            if (data.status === 'success') {
                this.gameState.gameSession = data.data.game_session;
                localStorage.setItem('currentGameSession', this.gameState.gameSession);
                
                this.updateStoryTitle(data.data.story_title);
                
                if (generateImages) {
                    this.startProgressMonitoring(data.data.game_session);
                } else {
                    this.hideProgressModal();
                    this.showCharacterSelection(data.data.characters);
                    this.addSystemMessage('✅ 生成完成，请选择角色');
                }
            } else {
                this.hideProgressModal();
                this.addSystemMessage('❌ 生成剧本失败：' + data.message);
            }
        } catch (error) {
            console.error('启动新游戏失败:', error);
            this.hideProgressModal();
            this.addSystemMessage('❌ 网络错误');
        }
    }

    async loadExistingGame(gamePath = null) {
        if (!gamePath) {
            await this.showGameListModal();
            return;
        }

        try {
            this.addSystemMessage('📂 正在加载...');
            
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
                
                this.addSystemMessage('✅ 加载完成，请选择角色');
            } else {
                this.addSystemMessage('❌ 加载游戏失败：' + data.message);
            }
                 } catch (error) {
             console.error('加载游戏失败:', error);
             this.addSystemMessage('❌ 网络错误');
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
         console.log(`👤 【角色选择】选择角色: ${characterName} (索引: ${index})`);
         document.querySelectorAll('.character-card').forEach(card => {
             card.classList.remove('selected');
         });
         
         document.querySelectorAll('.character-card')[index].classList.add('selected');
         
         this.gameState.selectedCharacter = characterName;
         document.getElementById('confirmCharacterBtn').disabled = false;
         
         // 移除角色选择确认提示，界面已有足够的视觉反馈
     }
    
         async confirmCharacterSelection() {
         if (!this.gameState.selectedCharacter) return;
         
         try {
             // 移除角色选择过程提示
             
                         const { response, data } = await this.apiRequest('/api/game/join', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    game_session: this.gameState.gameSession,
                    character_name: this.gameState.selectedCharacter,
                    user_id: this.gameState.user.id
                })
            });
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
                 
                 // 只在游戏真正开始时提示一次
                 this.addSystemMessage(`🎭 游戏开始 - ${this.gameState.currentCharacter}`);
             } else {
                 this.addSystemMessage('❌ 加入游戏失败：' + data.message);
             }
         } catch (error) {
             console.error('确认角色选择失败:', error);
             this.addSystemMessage('❌ 网络错误');
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
             
             // 改进图片路径处理
             let avatarHtml;
             if (char.image) {
                 // 确保图片路径正确
                 const imagePath = char.image.startsWith('/') ? char.image : `/${char.image}`;
                 avatarHtml = `<img src="${imagePath}" class="character-avatar-small" alt="${char.name}" 
                              onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';">
                              <div class="character-avatar-placeholder" style="display:none;">${this.getCharacterEmoji(char.name)}</div>`;
             } else {
                 avatarHtml = `<div class="character-avatar-placeholder">${this.getCharacterEmoji(char.name)}</div>`;
             }
             
             return `
                 <div class="character-item ${isCurrentUser ? 'current-user' : ''} ${char.is_ai ? 'ai-player' : ''}" 
                      title="${char.name} - ${playerType} - ${status}">
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
            console.log('#'.repeat(80));
            console.log(`📖 【章节变换】开始第${chapterNum}章`);
            console.log(`🎯 游戏会话: ${this.gameState.gameSession}`);
            console.log(`👤 当前角色: ${this.gameState.currentCharacter}`);
            console.log('#'.repeat(80));
            
            // 只在章节转换时提示
            this.addSystemMessage(`📖 第${chapterNum}章开始`);
            
            const { response, data } = await this.apiRequest('/api/game/chapter/start', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    game_session: this.gameState.gameSession,
                    chapter_num: chapterNum,
                    character_name: this.gameState.currentCharacter
                })
            });
            
            if (data.status === 'success') {
                this.gameState.currentChapter = chapterNum;
                this.gameState.currentCycle = 1;
                this.updateGameStatusDisplay();
                
                // 重新加载剧本（新章节内容）
                await this.loadCharacterScript();
                
                // 开始DM发言阶段
                this.startDMSpeakPhase(data.data.dm_speech);
                
                // 移除重复的章节开始提示
            } else {
                this.addSystemMessage('❌ 开始章节失败：' + data.message);
            }
        } catch (error) {
            console.error('开始章节失败:', error);
            this.addSystemMessage('❌ 网络错误');
        }
    }
    
    // ================== 三阶段流程管理 ==================
    
    startDMSpeakPhase(dmContent = null) {
        console.log('='.repeat(60));
        console.log('🎭 【阶段变换】进入 DM发言阶段');
        console.log(`📊 当前状态: 第${this.gameState.currentChapter}章 第${this.gameState.currentCycle}轮`);
        console.log('='.repeat(60));
        
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
                console.log('🎭 DM发言完成，准备开始玩家发言阶段');
                this.startPlayerSpeakPhase();
            }, this.config.dmSpeakDelay * 1000);
            
        }, 1000);
    }
    
    async startPlayerSpeakPhase() {
        console.log('='.repeat(60));
        console.log('💬 【阶段变换】进入 玩家发言阶段');
        console.log(`📊 当前状态: 第${this.gameState.currentChapter}章 第${this.gameState.currentCycle}轮`);
        console.log(`⏰ 阶段时长: ${this.config.playerSpeakTime}秒`);
        console.log('='.repeat(60));
        
        this.gameState.currentPhase = 'player_speak';
        this.updatePhaseDisplay('💬 玩家发言阶段', '你可以发言并询问其他玩家');
        this.enableInput();
        this.setupQueryList();
        
        // 初始化发言状态跟踪
        this.initializeSpeakingStatus();
        
        // 触发所有AI玩家发言
        console.log('⏰ 设置2秒后触发AI发言');
        setTimeout(async () => {
            console.log('⏰ 2秒计时结束，现在触发AI发言');
            await this.triggerAISpeaking();
        }, 2000); // 2秒后AI玩家开始发言
        
        // 开始监控发言状态
        this.startSpeakingStatusMonitor();
        
        // 启动计时器
        this.startPhaseTimer(this.config.playerSpeakTime, () => {
            // 时间到自动发送
            this.autoSendPlayerMessage();
        });
    }
    
    startPlayerAnswerPhase(queries) {
        console.log('='.repeat(60));
        console.log('🗣️ 【阶段变换】进入 玩家回答阶段');
        console.log(`📊 当前状态: 第${this.gameState.currentChapter}章 第${this.gameState.currentCycle}轮`);
        console.log(`⏰ 阶段时长: ${this.config.playerAnswerTime}秒`);
        console.log('❓ 待回答问题:', queries);
        console.log('='.repeat(60));
        
        this.gameState.currentPhase = 'player_answer';
        this.updatePhaseDisplay('🗣️ 玩家回答阶段', '被询问的玩家可以回答问题');
        
        // 初始化回复状态跟踪
        this.initializeAnswerStatus(queries);
        
        // 检查是否有人需要回复
        if (this.gameState.answerStatus.needToAnswer.size === 0) {
            // 没有人需要回复，直接进入下一阶段
            this.addSystemMessage('📋 无人需要回复，直接进入下一轮');
            setTimeout(() => {
                this.endAnswerPhase();
            }, 1000);
            return;
        }
        
        // 检查人类玩家是否被询问
        const userNeedsToAnswer = this.checkIfUserNeedsToAnswer(queries);
        
        if (userNeedsToAnswer) {
            this.enableAnswerInput();
        } else {
            this.disableInput('当前是回答阶段，等待其他玩家回答');
        }
        
        // 处理AI玩家的自动回答
        this.handleAIPlayerAnswers(queries);
        
        // 启动回复状态监控
        this.startAnswerStatusMonitor();
        
        // 启动计时器
        this.startPhaseTimer(this.config.playerAnswerTime, () => {
            // 时间到进入下一轮或总结
            this.endAnswerPhase();
        });
    }
    
         async handleAIPlayerAnswers(queries) {
         console.log('🤖 【AI回复】开始处理AI回复，传入的询问:', queries);
         
         // 收集所有需要AI回答的问题 - 只使用传入的queries，避免重复收集
         const aiQuestions = [];
         
         // 从传入的queries参数中收集AI需要回答的问题
         for (const [targetPlayer, question] of Object.entries(queries)) {
             const targetChar = this.gameState.characters.find(c => c.name === targetPlayer);
             if (targetChar && targetChar.is_ai) {
                 // 需要找到提问者，从action_history中查找这个问题是谁问的
                 let asker = this.gameState.currentCharacter; // 默认是当前用户
                 
                 if (this.gameState && this.gameState.action_history) {
                     const currentCycle = this.gameState.currentCycle;
                     const currentChapter = this.gameState.currentChapter;
                     
                     for (const action of this.gameState.action_history) {
                         if (action.type === 'player_action' && 
                             action.cycle === currentCycle && 
                             action.chapter === currentChapter &&
                             action.action_type === 'speak' &&
                             action.queries) {
                             
                             // 检查这个action中是否包含对targetPlayer的同样问题
                             if (action.queries[targetPlayer] === question) {
                                 asker = action.character;
                                 break;
                             }
                         }
                     }
                 }
                 
                 aiQuestions.push({
                     targetPlayer,
                     question,
                     asker: asker
                 });
                 console.log(`🎯 【AI回复】添加AI问题: ${asker} 问 ${targetPlayer}: ${question}`);
             }
         }
         
         console.log(`🤖 【AI回复】需要AI回复的问题数: ${aiQuestions.length}`);
         
         // 延迟后让AI玩家依次回答
         if (aiQuestions.length > 0) {
             // 初始化AI回复跟踪
             this.gameState.aiRepliesStatus = {
                 totalQuestions: aiQuestions.length,
                 completedReplies: 0,
                 allCompleted: false
             };
             
             for (let i = 0; i < aiQuestions.length; i++) {
                 const questionData = aiQuestions[i];
                 
                 setTimeout(async () => {
                     try {
                         console.log(`🤖 【AI回复】${questionData.targetPlayer} 开始回答问题`);
                         // 调用AI回答API
                         const response = await fetch('/api/game/ai_answer', {
                             method: 'POST',
                             headers: { 'Content-Type': 'application/json' },
                             body: JSON.stringify({
                                 game_session: this.gameState.gameSession,
                                 character_name: questionData.targetPlayer,
                                 question: questionData.question,
                                 asker: questionData.asker,
                                 chapter: this.gameState.currentChapter
                             })
                         });
                         
                         const data = await response.json();
                         if (data.status === 'success') {
                             this.addPlayerMessage(
                                 questionData.targetPlayer, 
                                 `回答 ${questionData.asker} 的问题：${data.data.answer}`, 
                                 'response'
                             );
                             console.log(`✅ 【AI回复】${questionData.targetPlayer} 回复完成`);
                         } else {
                             this.addPlayerMessage(
                                 questionData.targetPlayer, 
                                 `[${questionData.targetPlayer}选择不回答这个问题]`, 
                                 'response'
                             );
                             console.log(`⚠️ 【AI回复】${questionData.targetPlayer} 选择不回答`);
                         }
                         
                         // 立即更新该AI的回复状态
                         if (this.gameState.answerStatus) {
                             this.gameState.answerStatus.hasAnswered.add(questionData.targetPlayer);
                             console.log(`✅ 【回复状态】标记${questionData.targetPlayer}已回复`);
                         }
                         
                         // 将AI回复记录到前端action_history
                         const aiAnswerLog = {
                             type: 'answer',
                             character: questionData.targetPlayer,
                             content: data.data.answer,
                             question: questionData.question,
                             asker: questionData.asker,
                             chapter: this.gameState.currentChapter,
                             cycle: this.gameState.currentCycle,
                             action_type: 'answer',
                             timestamp: new Date().toISOString(),
                             is_ai: true
                         };
                         
                         if (!this.gameState.action_history) {
                             this.gameState.action_history = [];
                         }
                         this.gameState.action_history.push(aiAnswerLog);
                         console.log(`💾 【AI回复记录】将AI回复保存到前端action_history:`, aiAnswerLog);
                         
                         // 更新AI回复完成状态
                         if (this.gameState.aiRepliesStatus) {
                             this.gameState.aiRepliesStatus.completedReplies++;
                             console.log(`📊 【AI回复】进度: ${this.gameState.aiRepliesStatus.completedReplies}/${this.gameState.aiRepliesStatus.totalQuestions}`);
                             
                             // 检查是否所有AI都回复完成
                             if (this.gameState.aiRepliesStatus.completedReplies >= this.gameState.aiRepliesStatus.totalQuestions) {
                                 this.gameState.aiRepliesStatus.allCompleted = true;
                                 console.log('🎉 【AI回复】所有AI回复完成');
                                 // 检查回复完成状态
                                 setTimeout(() => {
                                     this.checkAnswerCompletion();
                                 }, 500);
                             }
                         }
                         
                     } catch (error) {
                         console.error(`❌ 【AI回复】${questionData.targetPlayer} 回答失败:`, error);
                         this.addPlayerMessage(
                             questionData.targetPlayer, 
                             `[${questionData.targetPlayer}无法回答这个问题]`, 
                             'response'
                         );
                         
                         // 即使失败也要标记为已回复
                         if (this.gameState.answerStatus) {
                             this.gameState.answerStatus.hasAnswered.add(questionData.targetPlayer);
                             console.log(`⚠️ 【回复状态】标记${questionData.targetPlayer}已回复（失败）`);
                         }
                         
                         // 将失败的AI回复也记录到前端action_history
                         const aiAnswerLog = {
                             type: 'answer',
                             character: questionData.targetPlayer,
                             content: `[${questionData.targetPlayer}无法回答这个问题]`,
                             question: questionData.question,
                             asker: questionData.asker,
                             chapter: this.gameState.currentChapter,
                             cycle: this.gameState.currentCycle,
                             action_type: 'answer',
                             timestamp: new Date().toISOString(),
                             is_ai: true
                         };
                         
                         if (!this.gameState.action_history) {
                             this.gameState.action_history = [];
                         }
                         this.gameState.action_history.push(aiAnswerLog);
                         console.log(`💾 【AI回复记录】将失败AI回复保存到前端action_history:`, aiAnswerLog);
                         
                         // 即使失败也要更新完成状态
                         if (this.gameState.aiRepliesStatus) {
                             this.gameState.aiRepliesStatus.completedReplies++;
                             if (this.gameState.aiRepliesStatus.completedReplies >= this.gameState.aiRepliesStatus.totalQuestions) {
                                 this.gameState.aiRepliesStatus.allCompleted = true;
                                 console.log('🎉 【AI回复】所有AI回复完成（含失败）');
                                 // 检查回复完成状态
                                 setTimeout(() => {
                                     this.checkAnswerCompletion();
                                 }, 500);
                             }
                         }
                     }
                 }, (i + 1) * this.config.aiResponseDelay * 1000); // 间隔回答
             }
         } else {
             console.log('📝 【AI回复】无需AI回复');
             // 如果没有AI需要回复，直接标记回复状态完成
             setTimeout(() => {
                 this.checkAnswerCompletion();
             }, 1000);
         }
     }
     
     // ================== 回复状态监控 ==================
     
     initializeAnswerStatus(queries) {
         // 初始化回复状态跟踪
         this.gameState.answerStatus = {
             needToAnswer: new Set(),
             hasAnswered: new Set(),
             allCompleted: false
         };
         
         // 收集所有需要回复的玩家
         if (queries) {
             Object.keys(queries).forEach(playerName => {
                 this.gameState.answerStatus.needToAnswer.add(playerName);
             });
         }
         
         // 从历史记录中查找所有被询问的玩家
         if (this.gameState && this.gameState.action_history) {
             const currentCycle = this.gameState.currentCycle;
             const currentChapter = this.gameState.currentChapter;
             
             for (const action of this.gameState.action_history) {
                 if (action.type === 'player_action' && 
                     action.cycle === currentCycle && 
                     action.chapter === currentChapter &&
                     action.queries) {
                     
                     Object.keys(action.queries).forEach(playerName => {
                         this.gameState.answerStatus.needToAnswer.add(playerName);
                     });
                 }
             }
         }
         
         console.log('需要回复的玩家:', Array.from(this.gameState.answerStatus.needToAnswer));
     }
     
     startAnswerStatusMonitor() {
         // 监控回复状态
         this.answerStatusChecker = setInterval(async () => {
             if (this.gameState.currentPhase !== 'player_answer') {
                 this.stopAnswerStatusMonitor();
                 return;
             }
             
             await this.checkAnswerCompletion();
         }, 2000); // 每2秒检查一次
     }
     
     stopAnswerStatusMonitor() {
         if (this.answerStatusChecker) {
             clearInterval(this.answerStatusChecker);
             this.answerStatusChecker = null;
         }
     }
     
     async checkAnswerCompletion() {
         if (!this.gameState.answerStatus || this.gameState.answerStatus.allCompleted) {
             return;
         }
         
         console.log('🔍 【回复检测】检查回复完成状态');
         
         // 检查是否所有需要回复的人都已经回复
         const needToAnswer = this.gameState.answerStatus.needToAnswer;
         const hasAnswered = this.gameState.answerStatus.hasAnswered;
         
         console.log(`📝 【回复检测】需要回复: [${Array.from(needToAnswer).join(', ')}]`);
         console.log(`✅ 【回复检测】已回复: [${Array.from(hasAnswered).join(', ')}]`);
         
         // 检查历史记录中的回复
         if (this.gameState.action_history) {
             const currentCycle = this.gameState.currentCycle;
             const currentChapter = this.gameState.currentChapter;
             
             for (const action of this.gameState.action_history) {
                 if (action.type === 'answer' && 
                     action.cycle === currentCycle && 
                     action.chapter === currentChapter &&
                     action.character) {
                     
                     hasAnswered.add(action.character);
                     console.log(`📋 【回复检测】从历史记录发现回复: ${action.character}`);
                 }
             }
         }
         
         // 检查AI回复是否完成
         let aiRepliesCompleted = true;
         if (this.gameState.aiRepliesStatus && !this.gameState.aiRepliesStatus.allCompleted) {
             aiRepliesCompleted = false;
             console.log(`⏳ 【回复检测】AI回复尚未完成: ${this.gameState.aiRepliesStatus.completedReplies}/${this.gameState.aiRepliesStatus.totalQuestions}`);
         }
         
         // 检查是否所有人都完成回复
         let allAnswered = true;
         const missingAnswers = [];
         for (const playerName of needToAnswer) {
             if (!hasAnswered.has(playerName)) {
                 allAnswered = false;
                 missingAnswers.push(playerName);
             }
         }
         
         if (missingAnswers.length > 0) {
             console.log(`⏳ 【回复检测】等待回复: [${missingAnswers.join(', ')}]`);
         }
         
         // 只有当所有人类和AI都回复完成时才进入下一阶段
         if (allAnswered && aiRepliesCompleted) {
             console.log('🎉 【回复检测】所有回复完成，准备进入下一阶段');
             this.gameState.answerStatus.allCompleted = true;
             this.handleAllAnswersComplete();
         } else {
             console.log('⏳ 【回复检测】回复尚未完成，继续等待');
         }
     }
     
     handleAllAnswersComplete() {
         // 所有回复完成，提前进入下一阶段
         this.addSystemMessage('📋 所有回复完成，进入下一轮');
         this.stopPhaseTimer();
         this.stopAnswerStatusMonitor();
         
         setTimeout(() => {
             this.endAnswerPhase();
         }, 1500);
     }
    
    endAnswerPhase() {
        this.stopPhaseTimer();
        this.stopAnswerStatusMonitor(); // 确保停止回复状态监控
        
        // 检查是否完成当前章节的所有循环
        if (this.gameState.currentCycle >= this.config.chapterCycles) {
            console.log('📋 【循环控制】当前章节所有循环完成，开始DM总结');
            this.startDMSummaryPhase();
        } else {
            // 进入下一循环 - 这是轮次更换，需要提示
            this.gameState.currentCycle++;
            console.log(`🔄 【循环控制】进入第${this.gameState.currentChapter}章 第${this.gameState.currentCycle}轮 (${this.gameState.currentCycle}/${this.config.chapterCycles})`);
            this.updateGameStatusDisplay();
            this.addSystemMessage(`🔄 第${this.gameState.currentChapter}章 第${this.gameState.currentCycle}轮`);
            this.startDMSpeakPhase();
        }
    }
    
    async startDMSummaryPhase() {
        console.log('='.repeat(60));
        console.log('📋 【阶段变换】进入 DM总结阶段');
        console.log(`📊 当前状态: 第${this.gameState.currentChapter}章`);
        console.log('='.repeat(60));
        
        this.gameState.currentPhase = 'dm_summary';
        
        // 判断是否是最后一章
        const isLastChapter = this.gameState.currentChapter >= 3; // 假设共3章
        
        if (isLastChapter) {
            console.log('🎉 【游戏结束】这是最后一章，开始最终总结');
            this.updatePhaseDisplay('🎉 游戏最终总结', 'DM正在揭示完整真相...');
            this.addSystemMessage('🎉 最终总结');
        } else {
            console.log('📋 【章节总结】准备进入下一章');
            this.updatePhaseDisplay('📋 DM章节总结', 'DM正在总结本章节内容...');
            this.addSystemMessage(`📋 第${this.gameState.currentChapter}章总结`);
        }
        
        this.disableInput('DM正在总结，请等待...');
        
        // 模拟DM总结
        setTimeout(async () => {
            if (isLastChapter) {
                // 最后一章 - 游戏结束总结
                await this.generateGameEndSummary();
            } else {
                // 章节总结
                await this.generateChapterSummary();
            }
            
            // 总结完成后进入下一章节或结束游戏
            setTimeout(() => {
                if (isLastChapter) {
                    this.endGame();
                } else {
                    this.startChapter(this.gameState.currentChapter + 1);
                }
            }, 5000);
            
        }, 2000);
    }
    
    async generateChapterSummary() {
        // 生成章节总结
        try {
            const response = await fetch('/api/game/dm_speak', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    game_session: this.gameState.gameSession,
                    chapter: this.gameState.currentChapter,
                    speak_type: 'chapter_end',
                    chat_history: this.getRecentChatHistory()
                })
            });
            
            const data = await response.json();
            if (data.status === 'success') {
                this.addDMMessage('游戏主持', data.data.speech);
            } else {
                // 回退方案
                const cluesContent = await this.getChapterClues(this.gameState.currentChapter);
                let summaryContent = `第${this.gameState.currentChapter}章总结：根据大家的讨论，现在公布新的线索：\n\n`;
                summaryContent += cluesContent;
                this.addDMMessage('游戏主持', summaryContent);
            }
        } catch (error) {
            console.error('生成章节总结失败:', error);
            // 回退方案
            const cluesContent = await this.getChapterClues(this.gameState.currentChapter);
            let summaryContent = `第${this.gameState.currentChapter}章总结：根据大家的讨论，现在公布新的线索：\n\n`;
            summaryContent += cluesContent;
            this.addDMMessage('游戏主持', summaryContent);
        }
    }
    
    async generateGameEndSummary() {
        // 生成游戏结束总结
        try {
            const response = await fetch('/api/game/dm_speak', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    game_session: this.gameState.gameSession,
                    chapter: this.gameState.currentChapter,
                    speak_type: 'game_end',
                    chat_history: this.getAllChatHistory(),
                    killer: '凶手身份待确认',
                    truth_info: '最终真相待揭示'
                })
            });
            
            const data = await response.json();
            if (data.status === 'success') {
                this.addDMMessage('游戏主持', data.data.speech);
            } else {
                // 回退方案
                const finalSummary = `🎉 游戏结束！\n\n感谢各位玩家的精彩表现！让我们回顾这场惊心动魄的推理之旅...\n\n经过三章的激烈讨论和缜密推理，真相已经浮出水面。每位玩家都展现了出色的观察力和逻辑思维能力。\n\n这个剧本杀游戏到此圆满结束，希望大家都享受了这次推理的乐趣！`;
                this.addDMMessage('游戏主持', finalSummary);
            }
        } catch (error) {
            console.error('生成游戏结束总结失败:', error);
            // 回退方案
            const finalSummary = `🎉 游戏结束！\n\n感谢各位玩家的精彩表现！让我们回顾这场惊心动魄的推理之旅...\n\n经过三章的激烈讨论和缜密推理，真相已经浮出水面。每位玩家都展现了出色的观察力和逻辑思维能力。\n\n这个剧本杀游戏到此圆满结束，希望大家都享受了这次推理的乐趣！`;
            this.addDMMessage('游戏主持', finalSummary);
        }
    }
    
    getRecentChatHistory() {
        // 获取最近的聊天记录
        const recentMessages = this.messageHistory.slice(-20);
        return recentMessages.map(msg => `**${msg.speaker}**: ${msg.content}`).join('\n');
    }
    
    getAllChatHistory() {
        // 获取所有聊天记录
        return this.messageHistory.map(msg => `**${msg.speaker}**: ${msg.content}`).join('\n');
    }
    
    // ================== 输入控制管理 ==================
    
    setupPhaseControl() {
        // 设置初始状态
        this.disableInput('等待游戏开始...');
    }
    
    enableInput() {
        const inputArea = document.getElementById('inputArea');
        const phaseDisabled = document.getElementById('phaseDisabled');
        const contentInput = document.getElementById('contentInput');
        const sendBtn = document.getElementById('sendBtn');
        
        inputArea.style.display = 'block';
        phaseDisabled.style.display = 'none';
        
        // 启用输入框和发送按钮
        if (contentInput) {
            contentInput.disabled = false;
        }
        if (sendBtn) {
            sendBtn.disabled = false;
        }
    }
    
    disableInput(message) {
        const inputArea = document.getElementById('inputArea');
        const phaseDisabled = document.getElementById('phaseDisabled');
        const disabledText = document.getElementById('disabledText');
        const contentInput = document.getElementById('contentInput');
        const sendBtn = document.getElementById('sendBtn');
        
        // 保持输入区域可见，但显示禁用消息
        inputArea.style.display = 'block';
        phaseDisabled.style.display = 'flex';
        disabledText.textContent = message;
        
        // 禁用输入框和发送按钮
        if (contentInput) {
            contentInput.disabled = true;
            contentInput.placeholder = message;
        }
        if (sendBtn) {
            sendBtn.disabled = true;
        }
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
         // 如果是回答阶段，直接发送回答
         if (this.gameState.currentPhase === 'player_answer') {
             this.sendPlayerAnswer();
             return;
         }
         
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
                    cycle: this.gameState.currentCycle,
                    action_type: 'speak'  // 明确标记为发言
                })
            });
            
            const data = await response.json();
            if (data.status === 'success') {
                // 重要：将用户发言记录添加到前端action_history
                const userActionLog = {
                    type: 'player_action',
                    character: this.gameState.currentCharacter,
                    content: this.gameState.pendingContent,
                    queries: this.gameState.pendingQueries,
                    chapter: this.gameState.currentChapter,
                    cycle: this.gameState.currentCycle,
                    action_type: 'speak',
                    timestamp: new Date().toISOString(),
                    is_ai: false
                };
                
                if (!this.gameState.action_history) {
                    this.gameState.action_history = [];
                }
                this.gameState.action_history.push(userActionLog);
                console.log(`💾 【用户记录】将用户发言保存到前端action_history:`, userActionLog);
                
                // 用户发言完成，但不直接进入回答阶段
                // 等待所有玩家（包括AI）发言完成后再统一进入回答阶段
                console.log('✅ 【用户发言】用户发言完成，等待其他玩家完成发言');
                
                // 如果所有玩家都已经发言完成，才进入回答阶段
                // 否则继续等待AI玩家完成发言
            } else {
                this.addSystemMessage('❌ 发送失败');
            }
             
         } catch (error) {
             console.error('发送消息失败:', error);
             this.addSystemMessage('❌ 网络错误');
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
                             this.addSystemMessage('✅ 生成完成，请选择角色');
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
         this.stopSpeakingStatusMonitor();
         
         // 清理游戏状态
         localStorage.removeItem('currentGameSession');
     }
     
     // ================== AI发言和状态管理 ==================
     
     initializeSpeakingStatus() {
         // 初始化发言状态跟踪 - 每轮重新初始化
         console.log(`🔄 【发言状态】初始化第${this.gameState.currentChapter}章第${this.gameState.currentCycle}轮发言状态`);
         this.gameState.speakingStatus = {
             totalPlayers: this.gameState.characters.length,
             spokenPlayers: new Set(),
             allCompleted: false,
             currentCycle: this.gameState.currentCycle,
             currentChapter: this.gameState.currentChapter
         };
         console.log(`👥 总玩家数: ${this.gameState.speakingStatus.totalPlayers}`);
     }
     
     async triggerAISpeaking() {
         try {
             console.log('🤖 开始触发AI发言...');
             console.log('📊 游戏状态:', {
                 gameSession: this.gameState.gameSession,
                 chapter: this.gameState.currentChapter,
                 phase: this.gameState.currentPhase
             });
             
                         const { response, data } = await this.apiRequest('/api/game/trigger_all_ai_speak', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    game_session: this.gameState.gameSession,
                    chapter: this.gameState.currentChapter
                })
            });
             
             if (data.status === 'success') {
                 const aiActions = data.data.ai_actions;
                 console.log(`🎯 获取到 ${aiActions.length} 个AI玩家的发言`);
                 
                 // 延迟显示AI发言，模拟思考时间
                 for (let i = 0; i < aiActions.length; i++) {
                     const action = aiActions[i];
                     console.log(`⏰ 安排AI玩家 ${action.character_name} 在 ${(i + 1) * 3} 秒后发言`);
                     
                     setTimeout(() => {
                         console.log(`💬 AI玩家 ${action.character_name} 开始发言:`, action);
                                                 if (action.success) {
                            // 显示AI发言
                            this.addPlayerMessage(action.character_name, action.content, 'speak');
                            console.log(`✅ 显示AI发言: ${action.character_name} - ${action.content}`);
                            
                            // 显示AI询问
                            Object.entries(action.queries).forEach(([target, question]) => {
                                this.addPlayerMessage(
                                    action.character_name,
                                    `询问 ${target}: ${question}`,
                                    'query'
                                );
                                console.log(`❓ 显示AI询问: ${action.character_name} -> ${target}: ${question}`);
                            });
                            
                            // 重要：将AI发言记录添加到前端action_history
                            const aiActionLog = {
                                type: 'player_action',
                                character: action.character_name,
                                content: action.content,
                                queries: action.queries,
                                chapter: this.gameState.currentChapter,
                                cycle: this.gameState.currentCycle,
                                action_type: 'speak',
                                timestamp: new Date().toISOString(),
                                is_ai: true
                            };
                            
                            if (!this.gameState.action_history) {
                                this.gameState.action_history = [];
                            }
                            this.gameState.action_history.push(aiActionLog);
                            console.log(`💾 【AI记录】将AI发言保存到前端action_history:`, aiActionLog);
                            
                            // 更新发言状态
                            this.gameState.speakingStatus.spokenPlayers.add(action.character_name);
                            console.log(`📝 更新发言状态，已发言玩家:`, this.gameState.speakingStatus.spokenPlayers);
                        } else {
                            this.addPlayerMessage(action.character_name, action.content, 'speak');
                            console.log(`⚠️ AI发言失败: ${action.character_name} - ${action.content}`);
                        }
                     }, (i + 1) * 3000); // 每个AI间隔3秒发言
                 }
             } else {
                 console.error('❌ AI发言接口返回错误:', data);
                 this.addSystemMessage('❌ AI发言失败：' + data.message);
             }
         } catch (error) {
             console.error('触发AI发言失败:', error);
             this.addSystemMessage('❌ AI发言错误');
         }
     }
     
     startSpeakingStatusMonitor() {
         // 监控发言状态
         this.speakingStatusChecker = setInterval(async () => {
             try {
                 const response = await fetch(`/api/game/speaking_status/${this.gameState.gameSession}`);
                 const data = await response.json();
                 
                 if (data.status === 'success') {
                     const status = data.data;
                     
                     // 更新进度显示
                     this.updateSpeakingProgress(status);
                     
                     // 检查是否所有玩家都发言完毕
                     if (status.all_completed && !this.gameState.speakingStatus.allCompleted) {
                         this.gameState.speakingStatus.allCompleted = true;
                         this.handleAllPlayersSpokeComplete();
                     }
                 }
             } catch (error) {
                 console.error('监控发言状态失败:', error);
             }
         }, 3000); // 每3秒检查一次
     }
     
     stopSpeakingStatusMonitor() {
         if (this.speakingStatusChecker) {
             clearInterval(this.speakingStatusChecker);
             this.speakingStatusChecker = null;
         }
     }
     
     updateSpeakingProgress(status) {
         // 更新发言进度显示
         const progressText = `发言进度: ${status.spoken_count}/${status.total_players} (${Math.round(status.completion_rate)}%)`;
         
         // 更新UI显示（可以添加到状态栏或其他地方）
         const phaseText = document.getElementById('phaseText');
         if (phaseText) {
             phaseText.textContent = `${progressText} - 你可以发言并询问其他玩家`;
         }
     }
     
         handleAllPlayersSpokeComplete() {
        console.log('📋 【发言完成】所有玩家发言完毕，收集询问');
        // 所有玩家发言完毕，提前进入下一阶段（只在轮次转换时提示）
        this.addSystemMessage('📋 进入回答阶段');
        this.stopPhaseTimer();
        this.stopSpeakingStatusMonitor();
        
        // 收集所有询问 - 从action_history中收集当前轮次的所有询问
        const allQueries = {};
        
        // 首先从pendingQueries收集（用户的询问）
        if (this.gameState && this.gameState.pendingQueries) {
            Object.assign(allQueries, this.gameState.pendingQueries);
            console.log('📝 【询问收集】从pendingQueries收集:', this.gameState.pendingQueries);
        }
        
        // 然后从action_history收集所有玩家的询问
        if (this.gameState && this.gameState.action_history) {
            const currentCycle = this.gameState.currentCycle;
            const currentChapter = this.gameState.currentChapter;
            
            for (const action of this.gameState.action_history) {
                if (action.type === 'player_action' && 
                    action.cycle === currentCycle && 
                    action.chapter === currentChapter &&
                    action.action_type === 'speak' &&  // 只收集发言阶段的询问
                    action.queries) {
                    
                    // 合并这个玩家的所有询问
                    Object.assign(allQueries, action.queries);
                    console.log(`📝 【询问收集】从${action.character}收集询问:`, action.queries);
                }
            }
        }
        
        console.log('🎯 【询问收集】最终收集到的所有询问:', allQueries);
        console.log(`❓ 【询问收集】总询问数: ${Object.keys(allQueries).length}`);
        
        setTimeout(() => {
            this.startPlayerAnswerPhase(allQueries);
        }, 2000);
    }
     
     async getChapterClues(chapter) {
         try {
             const response = await fetch(`/api/game/clues/${this.gameState.gameSession}/${chapter}`);
             const data = await response.json();
             
             if (data.status === 'success') {
                 const clues = data.data.clues;
                 
                 // 格式化线索为markdown
                 let cluesMarkdown = '### 🔍 新发现的线索：\n\n';
                 clues.forEach((clue, index) => {
                     cluesMarkdown += `${index + 1}. **${clue}**\n\n`;
                 });
                 
                 return cluesMarkdown;
             } else {
                 return '### 🔍 线索分析：\n\n当前没有新的线索公布，请继续观察和推理...';
             }
         } catch (error) {
             console.error('获取章节线索失败:', error);
             return '### 🔍 线索分析：\n\n线索获取失败，请继续根据已知信息推理...';
         }
     }
     
     updateConfigUI() {
         // 更新配置界面显示
         try {
             if (this.gameState.config) {
                 const scriptSourceRadios = document.querySelectorAll('input[name="scriptSource"]');
                 scriptSourceRadios.forEach(radio => {
                     if (radio.value === this.gameState.config.scriptSource) {
                         radio.checked = true;
                     }
                 });
                 
                 const localScriptPathInput = document.getElementById('localScriptPath');
                 if (localScriptPathInput) {
                     localScriptPathInput.value = this.gameState.config.localScriptPath || '';
                 }
                 
                 const generateImagesCheckbox = document.getElementById('generateImages');
                 if (generateImagesCheckbox) {
                     generateImagesCheckbox.checked = this.gameState.config.generateImages;
                 }
                 
                 // 显示/隐藏本地路径输入框
                 const localPathGroup = document.getElementById('localPathGroup');
                 if (localPathGroup) {
                     localPathGroup.style.display = this.gameState.config.scriptSource === 'local' ? 'block' : 'none';
                 }
                 
                 console.log('配置界面已更新:', this.gameState.config);
             }
         } catch (error) {
             console.error('更新配置界面失败:', error);
         }
     }
     
     checkIfUserNeedsToAnswer(queries) {
         // 检查人类玩家是否被询问
         if (!this.gameState.currentCharacter) return false;
         
         // 检查直接传入的queries
         if (queries && queries[this.gameState.currentCharacter]) {
             return true;
         }
         
         // 检查最近的聊天历史中是否有针对当前用户的询问
         if (this.gameState.action_history) {
             const currentCycle = this.gameState.currentCycle;
             const currentChapter = this.gameState.currentChapter;
             
             for (const action of this.gameState.action_history.slice(-10)) {
                 if (action.type === 'player_action' && 
                     action.cycle === currentCycle && 
                     action.chapter === currentChapter &&
                     action.queries) {
                     
                     if (action.queries[this.gameState.currentCharacter]) {
                         return true;
                     }
                 }
             }
         }
         
         return false;
     }
     
     enableAnswerInput() {
         // 启用回答输入
         const inputArea = document.getElementById('inputArea');
         const phaseDisabled = document.getElementById('phaseDisabled');
         const contentInput = document.getElementById('contentInput');
         const sendBtn = document.getElementById('sendBtn');
         
         inputArea.style.display = 'block';
         phaseDisabled.style.display = 'none';
         
         // 启用输入框和发送按钮
         if (contentInput) {
             contentInput.disabled = false;
             contentInput.placeholder = '输入你的回答...';
         }
         if (sendBtn) {
             sendBtn.disabled = false;
         }
         
         // 隐藏询问区域（回答阶段不需要询问）
         const queryList = document.getElementById('queryList');
         if (queryList) {
             queryList.style.display = 'none';
         }
         
         const queryToggleBtn = document.getElementById('queryToggleBtn');
         if (queryToggleBtn) {
             queryToggleBtn.style.display = 'none';
         }
         
         // 移除回答提示，界面状态已经足够清晰
     }
     
     async sendPlayerAnswer() {
         // 发送玩家回答
         const content = document.getElementById('contentInput').value.trim();
         
         if (!content) {
             this.showToast('请输入回答内容', 'warning');
             return;
         }
         
         try {
             // 立即显示用户回答
             this.addPlayerMessage(
                 this.gameState.currentCharacter, 
                 content,
                 'response'
             );
             
             // 清空输入
             document.getElementById('contentInput').value = '';
             this.updateCharCount();
             
             // 发送到后端记录
             const response = await fetch('/api/game/player_action', {
                 method: 'POST',
                 headers: { 'Content-Type': 'application/json' },
                 body: JSON.stringify({
                     game_session: this.gameState.gameSession,
                     character_name: this.gameState.currentCharacter,
                     content: content,
                     queries: {},
                     chapter: this.gameState.currentChapter,
                     cycle: this.gameState.currentCycle,
                     action_type: 'answer'
                 })
             });
             
                         if (response.ok) {
                // 移除回答成功提示，减少系统消息干扰
                // 更新回复状态
                if (this.gameState.answerStatus) {
                    this.gameState.answerStatus.hasAnswered.add(this.gameState.currentCharacter);
                    console.log(`✅ 【回复状态】标记${this.gameState.currentCharacter}已回复`);
                }
                
                // 将用户回复记录到前端action_history
                const userAnswerLog = {
                    type: 'answer',
                    character: this.gameState.currentCharacter,
                    content: content,
                    chapter: this.gameState.currentChapter,
                    cycle: this.gameState.currentCycle,
                    action_type: 'answer',
                    timestamp: new Date().toISOString(),
                    is_ai: false
                };
                
                if (!this.gameState.action_history) {
                    this.gameState.action_history = [];
                }
                this.gameState.action_history.push(userAnswerLog);
                console.log(`💾 【用户回复记录】将用户回复保存到前端action_history:`, userAnswerLog);
                
                // 禁用输入，等待阶段结束
                this.disableInput('已回答，等待其他玩家...');
            } else {
                this.addSystemMessage('❌ 回答失败');
            }
             
         } catch (error) {
             console.error('发送回答失败:', error);
             this.addSystemMessage('❌ 网络错误');
         }
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