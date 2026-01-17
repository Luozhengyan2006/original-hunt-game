// ==================== 全局状态 ====================

let gameState = {
    currentLanguage: 'zh',
    currentPage: 'welcome',
    gameId: null,
    playerId: null,
    playerName: null,
    gameData: null,
    texts: {},
    isDrawer: false,
    gameStarted: false,
    gamePhase: null,  // keywords, modify, drawing, guessing, result
    currentPhaseStep: null,
    selectedDrawingIndex: null,  // 猜测阶段选中的绘画ID (player_id)
    progressInterval: null  // 轮询间隔ID
};

// 大厅自动同步控制
let lobbyUpdateInterval = null;
let LOBBY_UPDATE_INTERVAL = 800;  // 0.8秒更新一次（更频繁以显示新加入的玩家）

let canvasState = {
    isDrawing: false,
    context: null,
    history: [],
    currentColor: '#000000'
};

// ==================== 初始化 ====================

document.addEventListener('DOMContentLoaded', () => {
    initGame();
});

async function initGame() {
    // 从localStorage恢复连接状态
    const savedGameId = localStorage.getItem('gameId');
    const savedPlayerId = localStorage.getItem('playerId');
    
    if (savedGameId && savedPlayerId) {
        gameState.gameId = savedGameId;
        gameState.playerId = savedPlayerId;
        console.log('Restored from localStorage:', { gameId: savedGameId, playerId: savedPlayerId });
    }
    
    // 加载翻译文本
    await loadTexts('zh');
    updateUIText();
    
    // 初始化画布
    const canvas = document.getElementById('canvas');
    if (canvas) {
        canvasState.context = canvas.getContext('2d');
        setupCanvas();
    }
    
    // 如果已有游戏ID和玩家ID，尝试恢复到大厅
    if (gameState.gameId && gameState.playerId) {
        try {
            const response = await fetch(`/api/get-game/${gameState.gameId}?player_id=${gameState.playerId}`);
            const data = await response.json();
            if (data.success) {
                gameState.gameData = data.game;
                showLobby();
                return;  // 恢复成功，不继续
            }
        } catch (error) {
            console.log('Could not restore game connection');
            // 恢复失败，继续正常初始化
            localStorage.removeItem('gameId');
            localStorage.removeItem('playerId');
            gameState.gameId = null;
            gameState.playerId = null;
        }
    }
}

// ==================== 文本和语言 ====================

// 翻译辅助函数：获取当前语言的翻译文本
function t(key) {
    return gameState.texts[key] || key;
}

async function loadTexts(language) {
    try {
        const response = await fetch(`/api/text/${language}`);
        const data = await response.json();
        if (data.success) {
            gameState.texts = data.text;
        }
    } catch (error) {
        console.error('Error loading texts:', error);
    }
}

function updateUIText() {
    const texts = gameState.texts;
    
    // 主页标题 - 特殊处理
    if (document.getElementById('gameTitle')) {
        document.getElementById('gameTitle').textContent = t('game_title');
    }
    
    // 语言按钮
    const langBtn = document.getElementById('langBtn');
    if (langBtn) {
        langBtn.textContent = t('language_switch');
    }
    
    // 更新游戏代码显示
    const gameCodeDisplay = document.getElementById('gameCodeDisplay');
    if (gameCodeDisplay) {
        const codeText = document.getElementById('codeText');
        const code = codeText ? codeText.textContent : '-';
        gameCodeDisplay.innerHTML = t('gameCodeDisplay') + ' <strong id="codeText">' + code + '</strong>';
    }
    
    // 更新所有带 id 的文本元素
    Object.keys(texts).forEach(key => {
        const element = document.getElementById(key);
        if (element && !element.classList.contains('no-translate')) {
            // 跳过已经特殊处理的元素
            if (key === 'gameCodeDisplay' || key === 'game_title' || key === 'language_switch') {
                return;
            }
            
            // 检查是否是特殊的需要保留子元素的元素
            if (key === 'roundInfo' || key === 'roundInfo2' || key === 'roundInfo3') {
                // 这些元素包含 <span id="currentRound/2/3">数字</span>，需要保留
                const currentRoundId = key === 'roundInfo' ? 'currentRound' : 
                                        key === 'roundInfo2' ? 'currentRound2' : 'currentRound3';
                const currentRoundSpan = element.querySelector(`#${currentRoundId}`);
                const roundNumber = currentRoundSpan ? currentRoundSpan.textContent : '1';
                element.innerHTML = t('roundInfo') + ' <span id="' + currentRoundId + '">' + roundNumber + '</span> ' + t('roundInfo');
            } else if (element.textContent.trim() !== '') {
                // 其他元素直接替换
                element.textContent = texts[key];
            }
        }
    });
    
    // 更新输入框的 placeholder
    const creatorNameInput = document.getElementById('creatorName');
    if (creatorNameInput) {
        creatorNameInput.placeholder = t('placeholder_name');
    }
    
    const gameCodeInput = document.getElementById('gameCode');
    if (gameCodeInput) {
        gameCodeInput.placeholder = t('placeholder_code');
    }
    
    const joinPlayerNameInput = document.getElementById('joinPlayerName');
    if (joinPlayerNameInput) {
        joinPlayerNameInput.placeholder = t('placeholder_name');
    }
    
    const fakeKeyword1 = document.getElementById('fakeKeyword1');
    if (fakeKeyword1) {
        fakeKeyword1.placeholder = t('placeholder_keyword1');
    }
    
    const fakeKeyword2 = document.getElementById('fakeKeyword2');
    if (fakeKeyword2) {
        fakeKeyword2.placeholder = t('placeholder_keyword2');
    }
    
    const fakeKeyword3 = document.getElementById('fakeKeyword3');
    if (fakeKeyword3) {
        fakeKeyword3.placeholder = t('placeholder_keyword3');
    }
}

async function switchLanguage() {
    gameState.currentLanguage = gameState.currentLanguage === 'zh' ? 'en' : 'zh';
    
    // 加载新语言的翻译文本
    await loadTexts(gameState.currentLanguage);
    
    // 更新主页面的所有 UI 文本
    updateUIText();
    
    // 如果游戏已经开始，更改游戏的语言（随时可用）
    if (gameState.gameId && gameState.playerId) {
        try {
            console.log('Changing game language to:', gameState.currentLanguage);
            
            const response = await fetch('/api/change-language', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    game_id: gameState.gameId,
                    player_id: gameState.playerId,
                    language: gameState.currentLanguage
                })
            });
            
            const data = await response.json();
            if (data.success) {
                gameState.gameData = data.game;
                console.log('Game language changed successfully, keywords updated');
                
                // 根据当前状态更新显示
                if (gameState.gameData.status === 'setup') {
                    // 在大厅中，刷新大厅显示
                    updateLobby();
                } else if (gameState.gameData.status === 'playing') {
                    // 游戏进行中，刷新当前页面内容
                    const currentPhase = gameState.gameData.game_phase;
                    if (currentPhase === 'drawer_drawing' && gameState.isDrawer) {
                        updateDrawerDrawingPhase();
                    } else if (currentPhase === 'keywords_modified' && gameState.isDrawer) {
                        updateModifyKeywordsPhase();
                    } else if (currentPhase === 'other_drawing') {
                        updateAllDrawingPhase();
                    }
                    // 其他阶段（guessing, result）不需要重新加载关键词
                }
            }
        } catch (error) {
            console.error('Error during language switch:', error);
        }
    }
}

// ==================== 页面导航 ====================

function showPage(pageName) {
    const prevPage = gameState.currentPage;

    // 隐藏所有页面
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });
    
    // 显示指定页面
    const page = document.getElementById(`page-${pageName}`);
    if (page) {
        page.classList.add('active');
        gameState.currentPage = pageName;
    }

    // 离开绘画页面：停止计时器，避免跨轮次/跨页面误触发超时提交
    if (prevPage === 'all-drawing' && pageName !== 'all-drawing' && timerInterval) {
        clearInterval(timerInterval);
        timerInterval = null;
        timeLeft = 120;
    }
    
    // 页面特定逻辑
    if (pageName === 'lobby') {
        // 进入大厅：启动自动更新
        if (lobbyUpdateInterval) {
            clearInterval(lobbyUpdateInterval);
        }
        updateLobby();  // 立即更新一次
        lobbyUpdateInterval = setInterval(() => {
            if (gameState.currentPage === 'lobby') {
                updateLobby();
            }
        }, LOBBY_UPDATE_INTERVAL);
    } else if (pageName !== 'lobby' && lobbyUpdateInterval) {
        // 离开大厅：停止自动更新
        clearInterval(lobbyUpdateInterval);
        lobbyUpdateInterval = null;
    }
}

function showWelcome() {
    showPage('welcome');
}

function showCreateGame() {
    showPage('create');
}

function showJoinGame() {
    showPage('join');
}

function showLobby() {
    showPage('lobby');
    // 确保按钮初始状态正确
    setTimeout(() => {
        if (gameState.gameData) {
            updateLobbyUI();
        }
    }, 100);
}

function showModifyKeywords() {
    showPage('modify-keywords');
}

function showWaitingDrawer() {
    showPage('waiting-drawer');
}

function showDrawerDrawing() {
    // 出题者第一阶段绘画，使用同样的页面但显示原始关键词
    updateDrawerDrawingPhase();
    showPage('all-drawing');
    // 延迟setupCanvas调用，确保页面已渲染
    setTimeout(() => {
        setupCanvas();
    }, 100);
}

function updateDrawerDrawingPhase() {
    const data = gameState.gameData;
    
    // 更新轮次
    const roundEl = document.getElementById('currentRound2');
    if (roundEl) roundEl.textContent = data.current_round;
    
    // 显示关键词（出题者看原始，其他人看修改后的）
    const keywordsList = document.getElementById('keywordsList');
    if (keywordsList) {
        keywordsList.innerHTML = '';
        
        const displayKeywords = data.display_keywords || data.original_keywords || [];
        displayKeywords.forEach(keyword => {
            const tag = document.createElement('div');
            tag.className = 'keyword-tag';
            tag.textContent = keyword;
            keywordsList.appendChild(tag);
        });
    }
    
    // 清空画布
    clearCanvas();
    
    // 启动计时器
    startTimer();
}

function showAllDrawing() {
    showPage('all-drawing');
    // 延迟setupCanvas调用，确保页面已渲染
    setTimeout(() => {
        setupCanvas();
    }, 100);
}

function showWaitingOthers() {
    showPage('waiting-drawer');  // 复用等待页面
}

function updateWaitingOthersDrawPhase() {
    // 更新轮次
    const roundEl = document.getElementById('currentRound');
    if (roundEl && gameState.gameData) roundEl.textContent = gameState.gameData.current_round;

    const waitingTitle = document.getElementById('waitingTitle');
    if (waitingTitle) {
        waitingTitle.textContent = (gameState.currentLanguage === 'zh')
            ? '等待其他玩家绘画和猜测...'
            : 'Waiting for other players to draw and guess...';
    }
    
    const waitingMessage = document.getElementById('waitingMessage');
    if (waitingMessage) {
        waitingMessage.textContent = (gameState.currentLanguage === 'zh')
            ? '其他玩家正在绘画，请耐心等待'
            : 'Other players are drawing, please wait';
    }
}

function updateWaitingOthersGuessPhase() {
    // 更新轮次
    const roundEl = document.getElementById('currentRound');
    if (roundEl && gameState.gameData) roundEl.textContent = gameState.gameData.current_round;

    const waitingTitle = document.getElementById('waitingTitle');
    if (waitingTitle) {
        waitingTitle.textContent = (gameState.currentLanguage === 'zh')
            ? '等待其他玩家猜测...'
            : 'Waiting for other players to guess...';
    }

    const waitingMessage = document.getElementById('waitingMessage');
    if (waitingMessage) {
        waitingMessage.textContent = (gameState.currentLanguage === 'zh')
            ? '其他玩家正在猜测，请耐心等待'
            : 'Other players are guessing, please wait';
    }
}

function showGuessing() {
    showPage('guessing');
}

function showResult() {
    showPage('result');
}

function showGameOver() {
    showPage('gameover');
}

function backToWelcome() {
    showWelcome();
    gameState.gameId = null;
    gameState.playerId = null;
    gameState.playerName = null;
}

// ==================== 游戏创建和加入 ====================

async function createGame() {
    const playerName = document.getElementById('creatorName').value.trim();
    const language = gameState.currentLanguage;  // 使用当前选中的语言
    
    if (!playerName) {
        alert(t('please_enter_name'));
        return;
    }
    
    // 防止重复点击
    const createBtn = document.querySelector('button[onclick="createGame()"]');
    if (createBtn) {
        createBtn.disabled = true;
    }
    
    try {
        console.log('Creating game with:', { player_name: playerName, language });
        
        // 创建游戏（新API：直接返回player_id）
        const createRes = await fetch('/api/create-game', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                player_name: playerName,
                language 
            })
        });
        
        const createData = await createRes.json();
        if (!createData.success) {
            throw new Error('Failed to create game');
        }
        
        console.log('Game created successfully:', { 
            game_id: createData.game_id,
            player_id: createData.player_id
        });
        
        // 保存游戏和玩家信息
        gameState.gameId = createData.game_id;
        gameState.playerId = createData.player_id;
        gameState.playerName = playerName;
        
        // 保存到localStorage
        localStorage.setItem('gameId', gameState.gameId);
        localStorage.setItem('playerId', gameState.playerId);
        localStorage.setItem('playerName', gameState.playerName);
        
        // 加载文本并显示大厅（showLobby会调用showPage，而showPage会再次调用updateLobby）
        await loadTexts(language);
        updateUIText();
        showLobby();  // 这会自动调用updateLobby
    } catch (error) {
        console.error('Error creating game:', error);
        alert(t('create_game_failed'));
        if (createBtn) {
            createBtn.disabled = false;
        }
    }
}

async function joinGame() {
    const gameId = document.getElementById('gameCode').value.trim().toUpperCase();  // 转大写
    const playerName = document.getElementById('joinPlayerName').value.trim();
    
    console.log('joinGame called with:', { gameId, playerName });
    
    if (!gameId || !playerName) {
        alert(t('please_enter_code_and_name'));
        return;
    }
    
    // 防止重复点击
    const joinBtn = document.querySelector('button[onclick="joinGame()"]');
    if (joinBtn) {
        joinBtn.disabled = true;
        joinBtn.textContent = t('loading') || '加载中...';
    }
    
    try {
        console.log('Sending join request:', { game_id: gameId, player_name: playerName });
        
        const response = await fetch('/api/join-game', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify({
                game_id: gameId,
                player_name: playerName
            })
        });
        
        console.log('Response status:', response.status);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Join response:', data);
        
        if (data.success) {
            gameState.gameId = gameId;
            gameState.playerId = data.player_id;
            gameState.playerName = playerName;
            // 保存到localStorage
            localStorage.setItem('gameId', gameState.gameId);
            localStorage.setItem('playerId', gameState.playerId);
            localStorage.setItem('playerName', gameState.playerName);
            
            console.log('Successfully joined game:', { game_id: gameId, player_id: data.player_id });
            
            // 立即更新大厅，并显示
            await updateLobby();
            showLobby();
        } else {
            console.error('Join game failed:', data.error);
            alert(t('join_failed') + ': ' + (data.error || 'Unknown error'));
            if (joinBtn) {
                joinBtn.disabled = false;
                joinBtn.innerHTML = '<span id="joinGameBtnText">' + t('joinGameBtnText') + '</span>';
            }
        }
    } catch (error) {
        console.error('Error joining game:', error);
        alert(t('join_game_failed') + ': ' + error.message);
        if (joinBtn) {
            joinBtn.disabled = false;
            joinBtn.innerHTML = '<span id="joinGameBtnText">' + t('joinGameBtnText') + '</span>';
        }
    }
}

async function updateLobby() {
    if (!gameState.gameId || !gameState.playerId) {
        console.warn('Cannot update lobby: missing gameId or playerId');
        return false;  // 没有游戏信息，无法更新
    }
    
    try {
        const response = await fetch(`/api/get-game/${gameState.gameId}?player_id=${gameState.playerId}`);
        const data = await response.json();
        
        if (data.success) {
            gameState.gameData = data.game;
            
            // ✅ 设置游戏的语言（从game_data中获取）
            if (data.game.language) {
                gameState.currentLanguage = data.game.language;
            }
            
            // ✅ 检查游戏是否已开始 - 所有玩家都应该自动进入游戏
            if (data.game.status === 'playing' && gameState.currentPage === 'lobby') {
                console.log('Game has started! Transitioning to game...');
                gameState.gameStarted = true;
                clearInterval(lobbyUpdateInterval);  // 停止大厅轮询
                lobbyUpdateInterval = null;
                startGameRound();  // 立即进入游戏
                return true;
            }
            
            updateLobbyUI();
            return true;
        } else {
            console.error('Failed to get game data:', data.error);
            return false;
        }
    } catch (error) {
        console.error('Error updating lobby:', error);
        return false;
    }
}

function updateLobbyUI() {
    if (!gameState.gameData) {
        console.warn('No game data to update UI');
        return;
    }
    
    // 更新游戏代码
    const codeText = document.getElementById('codeText');
    if (codeText) {
        codeText.textContent = gameState.gameId;
    }
    
    // 更新玩家列表
    const playersList = document.getElementById('playersList');
    if (playersList) {
        playersList.innerHTML = '';
        
        Object.entries(gameState.gameData.players).forEach(([playerId, player]) => {
            const div = document.createElement('div');
            div.className = 'player-item';
            const readyIcon = player.ready ? '✅' : '⏳';
            const isYou = playerId === gameState.playerId ? ' (你)' : '';
            const isHost = playerId === gameState.gameData.owner_id ? ' 👑' : '';
            div.innerHTML = `👤 ${player.name}${isHost}${isYou} ${readyIcon}`;
            playersList.appendChild(div);
        });
    }
    
    // 更新玩家数量显示
    const playerCountEl = document.getElementById('playerCount');
    if (playerCountEl) {
        playerCountEl.textContent = Object.keys(gameState.gameData.players).length;
    }
    
    // 检查是否是房主
    const isHost = gameState.playerId === gameState.gameData.owner_id;
    const readyCount = Object.values(gameState.gameData.players).filter(p => p.ready).length;
    const totalCount = Object.keys(gameState.gameData.players).length;
    
    console.log('=== LOBBY UPDATE ===');
    console.log('Current player ID:', gameState.playerId);
    console.log('Owner ID:', gameState.gameData.owner_id);
    console.log('Is host:', isHost);
    console.log('Total players:', totalCount);
    console.log('Ready count:', readyCount);
    
    // 更新准备状态提示
    const readyStatus = document.getElementById('readyStatus');
    if (readyStatus) {
        if (readyCount === totalCount && totalCount >= 2) {
            readyStatus.textContent = isHost ? '所有玩家已准备！点击"开始游戏"开始' : '所有玩家已准备！等待房主开始...';
            readyStatus.style.color = '#28a745';
        } else {
            readyStatus.textContent = `${readyCount}/${totalCount} 玩家已准备`;
            readyStatus.style.color = '#666';
        }
    }
    
    // 更新准备按钮状态
    const readyBtn = document.getElementById('readyBtn');
    const readyBtnText = document.getElementById('readyBtnText');
    if (readyBtn && readyBtnText && gameState.gameData.players[gameState.playerId]) {
        const isReady = gameState.gameData.players[gameState.playerId].ready;
        if (isReady) {
            readyBtn.className = 'btn btn-warning';
            readyBtnText.textContent = '取消准备';
        } else {
            readyBtn.className = 'btn btn-primary';
            readyBtnText.textContent = '准备';
        }
    }
    
    // 显示/隐藏开始游戏按钮（只有房主可见）
    const startGameBtn = document.getElementById('startGameBtn');
    console.log('Start game button element:', startGameBtn);
    if (startGameBtn) {
        console.log('Checking start button visibility - isHost:', isHost, 'totalCount:', totalCount);
        if (isHost && totalCount >= 2) {
            console.log('Showing start game button');
            startGameBtn.style.display = 'block';
            // 检查是否所有人都准备好
            const allReady = readyCount === totalCount;
            console.log('All ready:', allReady, '(', readyCount, '/', totalCount, ')');
            startGameBtn.disabled = !allReady;
            startGameBtn.style.opacity = allReady ? '1' : '0.5';
        } else {
            console.log('Hiding start game button - isHost:', isHost, 'totalCount:', totalCount);
            startGameBtn.style.display = 'none';
        }
    } else {
        console.error('Start game button not found in DOM!');
    }
    
    console.log('Lobby UI updated');
}

function leaveLobby() {
    // 停止所有后台任务，避免退出后仍被轮询/计时器拉回等待页面
    if (gameState.pollInterval) {
        clearInterval(gameState.pollInterval);
        gameState.pollInterval = null;
    }
    if (gameState.progressInterval) {
        clearInterval(gameState.progressInterval);
        gameState.progressInterval = null;
    }
    if (timerInterval) {
        clearInterval(timerInterval);
        timerInterval = null;
        timeLeft = 120;
    }

    // 停止大厅自动更新
    if (lobbyUpdateInterval) {
        clearInterval(lobbyUpdateInterval);
        lobbyUpdateInterval = null;
    }
    // 清空localStorage
    localStorage.removeItem('gameId');
    localStorage.removeItem('playerId');
    gameState.gameId = null;
    gameState.playerId = null;
    backToWelcome();
}

async function toggleReady() {
    if (!gameState.gameId || !gameState.playerId) {
        console.error('Missing gameId or playerId');
        return;
    }
    
    const currentReady = gameState.gameData?.players?.[gameState.playerId]?.ready || false;
    const newReady = !currentReady;
    
    try {
        const response = await fetch('/api/player-ready', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                game_id: gameState.gameId,
                player_id: gameState.playerId,
                ready: newReady
            })
        });
        
        const data = await response.json();
        if (data.success) {
            gameState.gameData = data.game;
            
            // 检查游戏是否已开始
            if (data.game.status === 'playing') {
                console.log('Game started! Transitioning...');
                gameState.gameStarted = true;
                clearInterval(lobbyUpdateInterval);
                lobbyUpdateInterval = null;
                startGameRound();
                return;
            }
            
            // 手动触发大厅更新（不重新获取数据）
            updateLobbyUI();
        }
    } catch (error) {
        console.error('Error toggling ready:', error);
    }
}

async function startGame() {
    console.log('startGame() called with gameState:', gameState);
    
    // 验证必要参数
    if (!gameState.gameId || !gameState.playerId) {
        console.error('Missing gameId or playerId');
        alert(t('missing_game_or_player_id'));
        return;
    }
    
    // 禁用按钮防止多次点击
    const startBtn = document.querySelector('button[onclick="startGame()"]');
    if (startBtn) {
        startBtn.disabled = true;
    }
    
    try {
        console.log('Sending start-game request with:', { 
            game_id: gameState.gameId,
            player_id: gameState.playerId
        });
        
        const response = await fetch('/api/start-game', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                game_id: gameState.gameId,
                player_id: gameState.playerId
            })
        });
        
        console.log('Response status:', response.status);
        const data = await response.json();
        console.log('Response data:', data);
        
        if (data.success) {
            console.log('Game started successfully');
            gameState.gameData = data.game;
            gameState.gameStarted = true;
            startGameRound();
        } else {
            console.error('Server returned error:', data.error);
            alert(t('start_game_failed'));
            if (startBtn) {
                startBtn.disabled = false;
            }
        }
    } catch (error) {
        console.error('Error starting game:', error);
        alert(t('failed_to_start_game') + ': ' + error.message);
        if (startBtn) {
            startBtn.disabled = false;
        }
    }
}

async function startGameRound() {
    try {
        const response = await fetch(`/api/get-game/${gameState.gameId}?player_id=${gameState.playerId}`);
        const data = await response.json();
        
        console.log('startGameRound response:', data);
        
        if (data.success) {
            gameState.gameData = data.game;
            gameState.gamePhase = data.game.game_phase;
            
            // ✅ 确保游戏的语言被设置
            if (data.game.language) {
                gameState.currentLanguage = data.game.language;
            }
            
            console.log('Current game phase:', gameState.gamePhase);
            console.log('Current drawer:', data.game.current_drawer);
            console.log('Current player:', gameState.playerId);
            
            // 检查是否是绘图者
            gameState.isDrawer = gameState.gameData.current_drawer === gameState.playerId;
            
            console.log('Is drawer:', gameState.isDrawer);
            
            // 根据当前阶段显示正确的页面
            if (gameState.gamePhase === 'keywords_modified') {
                // 关键词修改阶段
                if (gameState.isDrawer) {
                    console.log('Showing modify keywords phase');
                    updateModifyKeywordsPhase();
                    showModifyKeywords();
                } else {
                    // 其他玩家等待
                    console.log('Showing waiting for drawer (modify)');
                    updateWaitingDrawerPage();
                    showWaitingDrawer();
                    pollGameStatus();
                }
            } else if (gameState.gamePhase === 'other_drawing') {
                // 其他玩家绘画阶段
                if (gameState.isDrawer) {
                    // 出题者等待其他人绘画和猜测
                    console.log('Drawer waiting for others to draw');
                    updateWaitingOthersDrawPhase();
                    showWaitingOthers();
                    pollGameStatusForOtherDrawing();  // 轮询等待guessing阶段
                } else {
                    // 其他玩家进行绘画
                    console.log('Showing all drawing phase for non-drawer');
                    updateAllDrawingPhase();
                    showAllDrawing();
                }
            } else if (gameState.gamePhase === 'guessing') {
                // 猜测阶段
                if (gameState.isDrawer) {
                    // ✅ 出题者不参与猜测：等待其他玩家猜测
                    console.log('Drawer waiting for others to guess');
                    updateWaitingOthersGuessPhase();
                    showWaitingOthers();
                    pollGameStatusForGuessing();
                } else {
                    console.log('Showing guessing phase');
                    updateGuessingPhase();
                    showGuessing();
                    pollGameStatusForGuessing();  // 轮询等待result或下一轮
                }
            } else if (gameState.gamePhase === 'result') {
                // 结果阶段
                console.log('Showing result phase');
                showResultPhase();
            } else if (gameState.gamePhase === 'drawer_drawing') {
                // 兼容旧版本：如果出现drawer_drawing，转向修改关键词阶段
                if (gameState.isDrawer) {
                    updateModifyKeywordsPhase();
                    showModifyKeywords();
                } else {
                    updateWaitingDrawerPage();
                    showWaitingDrawer();
                    pollGameStatus();
                }
            } else {
                console.warn('Unknown game phase:', gameState.gamePhase);
            }
        }
    } catch (error) {
        console.error('Error starting round:', error);
    }
}

// ==================== 修改关键词阶段 (仅绘图者) ====================

function updateModifyKeywordsPhase() {
    const data = gameState.gameData;
    
    // 更新轮次
    const roundEl = document.getElementById('currentRound');
    if (roundEl) roundEl.textContent = data.current_round;
    
    // 显示原始关键词
    const originalKeywords = document.getElementById('originalKeywords');
    if (originalKeywords) {
        originalKeywords.innerHTML = '';
        
        if (data.original_keywords) {
            data.original_keywords.forEach(keyword => {
                const tag = document.createElement('div');
                tag.className = 'keyword-tag';
                tag.textContent = keyword;
                originalKeywords.appendChild(tag);
            });
        }
    }
    
    // 清空假关键词输入框，或使用原始关键词作为默认值
    const kw1 = document.getElementById('fakeKeyword1');
    const kw2 = document.getElementById('fakeKeyword2');
    const kw3 = document.getElementById('fakeKeyword3');
    if (kw1 && kw2 && kw3 && data.original_keywords) {
        kw1.value = data.original_keywords[0] || '';
        kw2.value = data.original_keywords[1] || '';
        kw3.value = data.original_keywords[2] || '';
    }
}

function updateWaitingDrawerPage() {
    const data = gameState.gameData;

    // 更新轮次
    const roundEl = document.getElementById('currentRound');
    if (roundEl) roundEl.textContent = data.current_round;
    
    // 更新等待标题和消息（关键词修改阶段）
    const waitingTitle = document.getElementById('waitingTitle');
    if (waitingTitle) {
        if (gameState.currentLanguage === 'zh') {
            waitingTitle.textContent = '等待出题者修改关键词...';
        } else {
            waitingTitle.textContent = 'Waiting for drawer to modify keywords...';
        }
    }
    
    const waitingMessage = document.getElementById('waitingMessage');
    if (waitingMessage) {
        if (gameState.currentLanguage === 'zh') {
            waitingMessage.textContent = '出题者正在修改关键词，请稍候';
        } else {
            waitingMessage.textContent = 'Drawer is modifying keywords, please wait';
        }
    }
    
    // 显示绘图者名字
    const drawer = data.players[data.current_drawer];
    const drawerEl = document.getElementById('drawerNameWaiting');
    if (drawerEl && drawer) {
        drawerEl.textContent = `${gameState.currentLanguage === 'zh' ? '出题者：' : 'Drawer: '} ${drawer.name}`;
    }

    // 等待页退出按钮文案
    const leaveBtnText = document.getElementById('leaveWaitingBtnText');
    if (leaveBtnText) {
        leaveBtnText.textContent = (gameState.currentLanguage === 'zh') ? '离开' : 'Leave';
    }
}

async function submitFakeKeywords() {
    const modifiedKeywords = [
        document.getElementById('fakeKeyword1').value.trim() || gameState.gameData.original_keywords[0],
        document.getElementById('fakeKeyword2').value.trim() || gameState.gameData.original_keywords[1],
        document.getElementById('fakeKeyword3').value.trim() || gameState.gameData.original_keywords[2]
    ];
    
    console.log('Submitting modified keywords:', modifiedKeywords);
    
    try {
        const response = await fetch('/api/submit-modified-keywords', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                game_id: gameState.gameId,
                player_id: gameState.playerId,
                modified_keywords: modifiedKeywords
            })
        });
        
        const data = await response.json();
        console.log('Submit modified keywords response:', data);
        
        if (data.success) {
            gameState.gameData = data.game;
            const newPhase = data.game.game_phase;
            console.log('Game phase after modifying keywords:', newPhase);
            
            if (newPhase === 'other_drawing') {
                // 进入其他玩家绘画阶段
                console.log('Entering other_drawing phase');
                updateAllDrawingPhase();
                showAllDrawing();
            } else {
                // 等待其他玩家
                console.log('Waiting for other players...');
                showWaitingMessage(t('waiting_for_drawing'));
                checkGamePhaseProgress();
            }
        } else {
            console.error('Server error:', data.error);
            alert(t('submit_failed'));
        }
    } catch (error) {
        console.error('Error submitting modified keywords:', error);
        alert(t('failed_submit_keywords'));
    }
}

// 等待绘图者的页面占位函数
// 等待绘图者的轮询函数
function pollGameStatus() {
    // 如果已经有轮询在进行，先清除它
    if (gameState.pollInterval) {
        clearInterval(gameState.pollInterval);
    }
    
    // 每2秒检查一次游戏状态
    gameState.pollInterval = setInterval(async () => {
        if (gameState.currentPage !== 'waiting-drawer' || !gameState.gameId) {
            clearInterval(gameState.pollInterval);
            gameState.pollInterval = null;
            return;
        }
        
        try {
            const response = await fetch(`/api/get-game/${gameState.gameId}?player_id=${gameState.playerId}`);
            const data = await response.json();
            
            if (data.success) {
                gameState.gameData = data.game;
                const currentPhase = data.game.game_phase;
                
                // 如果阶段发生改变（绘图者已提交），跳转到绘画阶段
                if (currentPhase !== gameState.gamePhase) {
                    console.log('Game phase changed to:', currentPhase);
                    gameState.gamePhase = currentPhase;
                    
                    // 停止轮询
                    clearInterval(gameState.pollInterval);
                    gameState.pollInterval = null;
                    
                    // 进入绘画阶段
                    if (currentPhase === 'other_drawing') {
                        updateAllDrawingPhase();
                        showAllDrawing();
                    }
                }
            }
        } catch (error) {
            console.error('Error polling game status:', error);
        }
    }, 2000);  // 每2秒检查一次
}

// 轮询等待other_drawing阶段完成（出题者在这个阶段等待）
function pollGameStatusForOtherDrawing() {
    if (gameState.pollInterval) {
        clearInterval(gameState.pollInterval);
    }
    
    gameState.pollInterval = setInterval(async () => {
        if (!gameState.gameId || !gameState.playerId) {
            clearInterval(gameState.pollInterval);
            gameState.pollInterval = null;
            return;
        }
        
        try {
            const response = await fetch(`/api/get-game/${gameState.gameId}?player_id=${gameState.playerId}`);
            const data = await response.json();
            
            if (data.success) {
                const currentPhase = data.game.game_phase;
                
                // 如果阶段从other_drawing转移到guessing，进入猜测阶段
                if (currentPhase === 'guessing' && gameState.gamePhase === 'other_drawing') {
                    console.log('Phase changed from other_drawing to guessing');
                    gameState.gamePhase = currentPhase;
                    gameState.gameData = data.game;
                    
                    clearInterval(gameState.pollInterval);
                    gameState.pollInterval = null;
                    
                    updateGuessingPhase();
                    showGuessing();
                    pollGameStatusForGuessing();  // 继续轮询等待result
                }
            }
        } catch (error) {
            console.error('Error polling for other_drawing:', error);
        }
    }, 2000);
}

// 轮询等待guessing阶段完成（所有玩家在猜测后需要转移到result）
function pollGameStatusForGuessing() {
    if (gameState.pollInterval) {
        clearInterval(gameState.pollInterval);
    }
    
    gameState.pollInterval = setInterval(async () => {
        if (!gameState.gameId || !gameState.playerId) {
            clearInterval(gameState.pollInterval);
            gameState.pollInterval = null;
            return;
        }
        
        try {
            const response = await fetch(`/api/get-game/${gameState.gameId}?player_id=${gameState.playerId}`);
            const data = await response.json();
            
            if (data.success) {
                const currentPhase = data.game.game_phase;
                
                // 如果阶段从guessing转移到result，进入结果阶段
                if ((currentPhase === 'result' || currentPhase === 'next_round') && gameState.gamePhase === 'guessing') {
                    console.log('Phase changed from guessing to:', currentPhase);
                    gameState.gamePhase = currentPhase;
                    gameState.gameData = data.game;
                    
                    clearInterval(gameState.pollInterval);
                    gameState.pollInterval = null;
                    
                    if (currentPhase === 'result') {
                        showResultPhase();
                    } else {
                        // next_round或其他，重新开始一轮
                        startGameRound();
                    }
                }
            }
        } catch (error) {
            console.error('Error polling for guessing:', error);
        }
    }, 2000);
}

// ==================== 所有玩家绘画阶段 ====================

function updateAllDrawingPhase() {
    const data = gameState.gameData;

    // 重置提交按钮（避免上一轮已提交导致状态残留）
    const submitBtn = document.getElementById('submitDrawingBtn');
    if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.textContent = t('submit_drawing');
    }
    
    // 更新轮次
    const roundEl = document.getElementById('currentRound2');
    if (roundEl) roundEl.textContent = data.current_round;
    
    // 显示关键词（使用API返回的display_keywords，已根据权限处理）
    const keywordsList = document.getElementById('keywordsList');
    if (keywordsList) {
        keywordsList.innerHTML = '';
        
        const displayKeywords = data.display_keywords || [];
        displayKeywords.forEach(keyword => {
            const tag = document.createElement('div');
            tag.className = 'keyword-tag';
            tag.textContent = keyword;
            keywordsList.appendChild(tag);
        });
    }
    
    // 清空画布
    clearCanvas();
    
    // 启动计时器
    startTimer();
}

function setupCanvas() {
    const canvas = document.getElementById('canvas');
    
    canvas.addEventListener('mousedown', startDrawing);
    canvas.addEventListener('mousemove', draw);
    canvas.addEventListener('mouseup', stopDrawing);
    canvas.addEventListener('mouseout', stopDrawing);
    
    // 触摸支持
    canvas.addEventListener('touchstart', handleTouch);
    canvas.addEventListener('touchmove', handleTouch);
    canvas.addEventListener('touchend', stopDrawing);
}

function startDrawing(e) {
    canvasState.isDrawing = true;
    const rect = document.getElementById('canvas').getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    canvasState.context.beginPath();
    canvasState.context.moveTo(x, y);
    
    // 保存画布状态用于撤销
    canvasState.history.push(canvasState.context.getImageData(0, 0, 
        document.getElementById('canvas').width, 
        document.getElementById('canvas').height));
}

function draw(e) {
    if (!canvasState.isDrawing) return;
    
    const rect = document.getElementById('canvas').getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    canvasState.context.lineWidth = 2;
    canvasState.context.lineCap = 'round';
    canvasState.context.lineJoin = 'round';
    canvasState.context.strokeStyle = canvasState.currentColor;
    
    canvasState.context.lineTo(x, y);
    canvasState.context.stroke();
}

function stopDrawing() {
    canvasState.isDrawing = false;
    canvasState.context.closePath();
}

function handleTouch(e) {
    e.preventDefault();
    const touch = e.touches[0];
    const mouseEvent = new MouseEvent(e.type === 'touchstart' ? 'mousedown' : 'mousemove', {
        clientX: touch.clientX,
        clientY: touch.clientY
    });
    document.getElementById('canvas').dispatchEvent(mouseEvent);
}

function changeColor(color) {
    canvasState.currentColor = color;
}

function clearCanvas() {
    const canvas = document.getElementById('canvas');
    canvasState.context.clearRect(0, 0, canvas.width, canvas.height);
    canvasState.history = [];
}

function undoDrawing() {
    if (canvasState.history.length > 0) {
        const imageData = canvasState.history.pop();
        canvasState.context.putImageData(imageData, 0, 0);
    }
}

async function submitDrawing() {
    const canvas = document.getElementById('canvas');
    
    if (!canvas) {
        console.error('Canvas element not found!');
        alert(t('canvas_not_found'));
        return;
    }
    
    let drawingData;
    try {
        drawingData = canvas.toDataURL('image/png');
        console.log('Canvas toDataURL() successful, data length:', drawingData.length);
    } catch (err) {
        console.error('Failed to get drawing data:', err);
        alert(t('canvas_error'));
        return;
    }
    
    // 禁用提交按钮防止重复提交
    const submitBtn = document.getElementById('submitDrawingBtn');
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = t('submitting');
    }
    
    try {
        console.log('Submitting drawing to /api/submit-drawing');
        
        const response = await fetch('/api/submit-drawing', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                game_id: gameState.gameId,
                player_id: gameState.playerId,
                drawing_data: drawingData
            })
        });
        
        console.log('Response status:', response.status);
        
        if (!response.ok) {
            const errText = await response.text();
            console.error('HTTP Error:', response.status, errText);
            alert(t('http_error') + ` ${response.status}`);
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.textContent = t('submit_drawing');
            }
            return;
        }
        
        // 解析响应
        let data;
        try {
            data = await response.json();
        } catch (parseErr) {
            console.error('Failed to parse response JSON:', parseErr);
            alert(t('invalid_response'));
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.textContent = t('submit_drawing');
            }
            return;
        }
        
        // 检查API是否返回成功
        if (!data.success) {
            console.error('API error:', data.error);
            alert(t('server_error'));
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.textContent = t('submit_drawing');
            }
            return;
        }
        
        // 成功！更新游戏状态并显示等待页面
        console.log('Drawing submitted successfully!');
        console.log('New game phase:', data.game.game_phase);
        console.log('Is drawer:', gameState.isDrawer);
        
        gameState.gameData = data.game;
        gameState.gamePhase = data.game.game_phase;
        gameState.isDrawer = data.game.current_drawer === gameState.playerId;
        
        // 根据角色和阶段显示不同的等待消息
        let waitingMessage = t('waiting_for_others');
        if (gameState.isDrawer) {
            // 出题者提交绘画后，等待其他玩家猜测
            waitingMessage = t('waiting_for_guess') || '等待其他玩家猜测...';
        } else {
            // 其他玩家提交绘画后，等待其他玩家
            if (gameState.gamePhase === 'other_drawing') {
                waitingMessage = t('waiting_for_drawing');
            } else {
                waitingMessage = t('waiting_for_others');
            }
        }
        
        // 立即显示等待消息，让用户看到有进度
        showWaitingMessage(waitingMessage);
        console.log('Showing waiting message:', waitingMessage, ', starting polling...');
        
        // 立即启动轮询来检测阶段变化
        checkGamePhaseProgress();
        console.log('Polling started');
        
    } catch (error) {
        console.error('Network error in submitDrawing:', error);
        alert(t('network_error'));
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.textContent = t('submit_drawing');
        }
    }
}

// ==================== 猜测阶段 (识别绘图者的画) ====================

async function updateGuessingPhase() {
    try {
        console.log('updateGuessingPhase called');
        
        // ✅ 检查：如果当前玩家是出题者，显示等待页面而不是猜测页面
        if (gameState.isDrawer) {
            console.log('Current player is drawer, showing waiting page instead');
            showWaitingMessage(t('waiting_for_guess') || '等待其他玩家猜测...');
            checkGamePhaseProgress();  // 轮询等待结果阶段
            return;
        }
        
        console.log('Fetching drawings for guessing...');
        const response = await fetch(`/api/get-drawings/${gameState.gameId}?player_id=${gameState.playerId}`);
        const data = await response.json();
        
        console.log('Guessing phase data:', data);
        
        if (data.success) {
            const drawings = data.drawings;
            console.log('Received', drawings.length, 'drawings');
            
            const currentRound = document.getElementById('currentRound3');
            if (currentRound) {
                currentRound.textContent = gameState.gameData.current_round;
            }
            
            // 显示绘画库 (打乱后的顺序，但保留drawing_id)
            const gallery = document.getElementById('drawingsGallery');
            if (gallery) {
                gallery.innerHTML = '';
                
                drawings.forEach((drawing, displayIndex) => {
                    const drawingItem = document.createElement('div');
                    drawingItem.className = 'drawing-item';
                    drawingItem.id = `drawing-${drawing.drawing_id}`;
                    drawingItem.onclick = () => selectDrawing(drawing.drawing_id, displayIndex);
                    
                    const img = document.createElement('img');
                    img.src = drawing.drawing_data;  // 使用 drawing_data 字段
                    img.alt = `Drawing ${displayIndex + 1}`;
                    
                    const label = document.createElement('p');
                    label.textContent = `画 ${displayIndex + 1}`;
                    label.className = 'drawing-number';
                    
                    drawingItem.appendChild(img);
                    drawingItem.appendChild(label);
                    gallery.appendChild(drawingItem);
                });
                console.log('Gallery updated with', drawings.length, 'items');
            }
            
            // 显示页面
            console.log('Calling showGuessing()...');
            showGuessing();
            console.log('showGuessing() completed');
        } else {
            console.error('Failed to get drawings:', data.error);
            showPage('guessing');  // 至少显示页面
        }
    } catch (error) {
        console.error('Error loading drawings:', error);
        showPage('guessing');  // 错误时至少显示页面
    }
}

function selectDrawing(drawingId, displayIndex) {
    // 更新选中的绘画
    document.querySelectorAll('.drawing-item').forEach(item => {
        item.classList.remove('selected');
    });
    
    const selected = document.getElementById(`drawing-${drawingId}`);
    if (selected) {
        selected.classList.add('selected');
        gameState.selectedDrawingIndex = drawingId;  // 保存drawing_id
        
        // 启用提交按钮
        const submitBtn = document.getElementById('submitGuessBtn');
        if (submitBtn) submitBtn.disabled = false;
    }
}

async function submitGuess() {
    if (gameState.selectedDrawingIndex === null) {
        alert(t('select_drawing'));
        return;
    }
    
    // 防止重复提交
    const submitBtn = document.getElementById('submitGuessBtn');
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = t('submitting') || '提交中...';
    }
    
    try {
        console.log('=== SUBMIT GUESS ===');
        console.log('Current round:', gameState.gameData?.current_round);
        console.log('Game phase:', gameState.gamePhase);
        console.log('Selected drawing ID:', gameState.selectedDrawingIndex);
        console.log('Player ID:', gameState.playerId);
        console.log('Game ID:', gameState.gameId);
        
        const response = await fetch('/api/submit-guess', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                game_id: gameState.gameId,
                player_id: gameState.playerId,
                guess_drawing_id: gameState.selectedDrawingIndex  // 发送drawing_id而不是index
            })
        });
        
        console.log('Response status:', response.status);
        const data = await response.json();
        console.log('Guess submit response:', data);
        
        if (data.success) {
            gameState.gameData = data.game;
            gameState.gamePhase = data.game.game_phase;
            
            // 检查是否所有玩家都已猜测
            if (data.game.game_phase === 'result') {
                console.log('Moving to result phase immediately');
                showResultPhase();
            } else {
                // 等待其他玩家完成猜测
                console.log('Waiting for other players to guess');
                showWaitingMessage(t('waiting_for_guess'));
                checkGamePhaseProgress();
            }
        } else {
            console.error('Server returned error:', data.error);
            alert('提交失败: ' + (data.error || '未知错误'));
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.textContent = t('submit_guess') || '提交猜测';
            }
        }
    } catch (error) {
        console.error('Error submitting guess:', error);
        alert('提交失败，请重试');
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.textContent = t('submit_guess') || '提交猜测';
        }
    }
}

function showWaitingMessage(message) {
    // 显示等待消息页面
    console.log('Waiting:', message);
    
    // 更新等待消息
    const waitingText = document.getElementById('waitingText');
    if (waitingText) {
        waitingText.textContent = message;
    }
    
    // 显示等待页面
    showPage('waiting-page');
}

function checkGamePhaseProgress() {
    // 如果已经有轮询在进行，先清除它
    if (gameState.progressInterval) {
        clearInterval(gameState.progressInterval);
    }
    
    // 定期检查游戏阶段是否发生变化
    gameState.progressInterval = setInterval(async () => {
        if (gameState.currentPage === 'lobby' || !gameState.gameId) {
            clearInterval(gameState.progressInterval);
            gameState.progressInterval = null;
            return;
        }
        
        try {
            const response = await fetch(`/api/get-game/${gameState.gameId}?player_id=${gameState.playerId}`);
            const data = await response.json();
            
            if (data.success) {
                const newPhase = data.game.game_phase;
                console.log('Progress check - Current phase:', gameState.gamePhase, 'New phase:', newPhase);
                
                // 如果游戏阶段发生变化，更新状态
                if (newPhase !== gameState.gamePhase) {
                    console.log('Phase changed! Updating to:', newPhase);
                    gameState.gameData = data.game;
                    gameState.gamePhase = newPhase;
                    gameState.isDrawer = data.game.current_drawer === gameState.playerId;
                    
                    // 清除轮询
                    if (gameState.progressInterval) {
                        clearInterval(gameState.progressInterval);
                        gameState.progressInterval = null;
                    }
                    
                    // 根据新阶段重新显示内容
                    if (newPhase === 'drawer_drawing') {
                        if (gameState.isDrawer) {
                            showDrawerDrawing();
                        } else {
                            showWaitingForDrawer();
                        }
                    } else if (newPhase === 'keywords_modified') {
                        if (gameState.isDrawer) {
                            updateModifyKeywordsPhase();
                            showModifyKeywords();
                        } else {
                            showWaitingForDrawer();
                        }
                    } else if (newPhase === 'other_drawing') {
                        updateAllDrawingPhase();
                        showAllDrawing();
                    } else if (newPhase === 'guessing') {
                        updateGuessingPhase();  // This function now handles showing the page
                    } else if (newPhase === 'result') {
                        showResultPhase();
                    }
                }
            }
        } catch (error) {
            console.error('Error checking game progress:', error);
        }
    }, 1500);  // 每1.5秒检查一次
}

// ==================== 结果阶段 ====================

async function showResultPhase() {
    try {
        const response = await fetch(`/api/get-scores/${gameState.gameId}`);
        const data = await response.json();
        
        if (data.success) {
            showResult();
            updateResultPage(data);
        }
    } catch (error) {
        console.error('Error getting scores:', error);
    }
}

function updateResultPage(scoreData) {
    // 显示绘图者名字
    const drawer = gameState.gameData.players[gameState.gameData.current_drawer];
    const drawerNameEl = document.getElementById('drawerName');
    if (drawerNameEl && drawer) {
        drawerNameEl.textContent = drawer.name;
    }
    
    // 显示计分情景说明
    const scenario = scoreData.scenario || 'N/A';
    const scenarioEl = document.getElementById('scenarioDescription');
    if (scenarioEl) {
        scenarioEl.textContent = scenario;
    }
    
    // 显示本轮分数
    const scoresList = document.getElementById('scoresList');
    if (scoresList) {
        scoresList.innerHTML = '';
        
        Object.entries(gameState.gameData.players).forEach(([playerId, player]) => {
            const roundScore = scoreData.round_scores ? (scoreData.round_scores[playerId] || 0) : 0;
            const item = document.createElement('div');
            item.className = 'score-item';
            item.innerHTML = `<span class="score-name">${player.name}</span><span class="score-points">+${roundScore}</span>`;
            scoresList.appendChild(item);
        });
    }
    
    // 显示总分排名
    const totalScoresList = document.getElementById('totalScoresList');
    if (totalScoresList) {
        totalScoresList.innerHTML = '';
        
        // 使用 API 返回的 total_scores (实际是 game.scores)
        const totalScores = scoreData.total_scores || gameState.gameData.scores || {};
        const sorted = Object.entries(totalScores)
            .sort((a, b) => b[1] - a[1]);
        
        sorted.forEach(([playerId, score], index) => {
            const player = gameState.gameData.players[playerId];
            const item = document.createElement('div');
            item.className = 'score-rank';
            item.innerHTML = `
                <span>${index + 1}. ${player.name}</span>
                <span class="score-points">${score}</span>
            `;
            totalScoresList.appendChild(item);
        });
    }
}

async function nextRound() {
    // 防止重复点击
    const nextBtn = document.getElementById('nextRoundBtn');
    if (nextBtn) {
        nextBtn.disabled = true;
        nextBtn.textContent = t('loading') || '加载中...';
    }
    
    try {
        console.log('Requesting next round...');
        
        const response = await fetch('/api/next-round', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                game_id: gameState.gameId,
                player_id: gameState.playerId
            })
        });
        
        const data = await response.json();
        console.log('Next round response:', data);
        
        if (data.success) {
            if (data.ignored) {
                // 已经有其他玩家推进了游戏
                console.log('Round already advanced by another player');
                // 重新获取游戏状态
                const gameResp = await fetch(`/api/get-game/${gameState.gameId}?player_id=${gameState.playerId}`);
                const gameData = await gameResp.json();
                if (gameData.success) {
                    gameState.gameData = gameData.game;
                    gameState.gamePhase = gameData.game.game_phase;
                    gameState.isDrawer = gameData.game.current_drawer === gameState.playerId;
                    // 根据当前阶段显示对应页面
                    if (gameData.game.game_phase === 'keywords_modified') {
                        if (gameState.isDrawer) {
                            showModifyKeywords();
                        } else {
                            showWaitingForDrawer();
                        }
                    }
                }
            } else {
                gameState.gameData = data.game;
                gameState.gamePhase = data.game.game_phase;
                gameState.isDrawer = data.game.current_drawer === gameState.playerId;
                gameState.selectedDrawingIndex = null;
                
                if (data.game_over) {
                    console.log('Game over, showing final results');
                    showGameOverPage();
                } else {
                    console.log('Starting new round:', data.game.current_round);
                    startGameRound();
                }
            }
        } else {
            alert('进入下一轮失败: ' + (data.error || '未知错误'));
            if (nextBtn) {
                nextBtn.disabled = false;
                nextBtn.textContent = t('next_round') || '下一轮';
            }
        }
    } catch (error) {
        console.error('Error loading next round:', error);
        alert('进入下一轮失败，请刷新页面重试');
        if (nextBtn) {
            nextBtn.disabled = false;
            nextBtn.textContent = t('next_round') || '下一轮';
        }
    }
}

// ==================== 游戏结束 ====================

function showGameOverPage() {
    showGameOver();
    updateGameOverPage();
}

function updateGameOverPage() {
    const data = gameState.gameData;
    
    // 找到获胜者
    const sorted = Object.entries(data.total_scores || {})
        .sort((a, b) => b[1] - a[1]);
    const winnerId = sorted[0][0];
    const winnerName = data.players[winnerId].name;
    
    const winnerNameEl = document.getElementById('winnerName');
    if (winnerNameEl) {
        winnerNameEl.textContent = winnerName;
    }
    
    // 显示最终排名
    const finalScoresList = document.getElementById('finalScoresList');
    if (finalScoresList) {
        finalScoresList.innerHTML = '';
        
        sorted.forEach(([playerId, score], index) => {
            const player = data.players[playerId];
            const item = document.createElement('div');
            item.className = 'score-rank';
            item.innerHTML = `
                <span>${index + 1}. ${player.name}</span>
                <span class="score-points">${score}</span>
            `;
            finalScoresList.appendChild(item);
        });
    }
}

function playAgain() {
    showWelcome();
    gameState.gameId = null;
    gameState.playerId = null;
    gameState.playerName = null;
    gameState.gameStarted = false;
    gameState.selectedDrawingIndex = null;
}

// ==================== 计时器 ====================

let timerInterval = null;
let timeLeft = 120;

function startTimer() {
    timeLeft = 120;
    
    if (timerInterval) {
        clearInterval(timerInterval);
    }
    
    const timerElement = document.getElementById('timer');
    if (!timerElement) return;  // 如果不在绘画页面则跳过

    // 立即同步显示，避免看起来“快到0”从而触发误解
    timerElement.textContent = timeLeft;
    
    timerInterval = setInterval(() => {
        // 如果已经离开绘画页面，立刻停止计时器
        if (gameState.currentPage !== 'all-drawing') {
            clearInterval(timerInterval);
            timerInterval = null;
            return;
        }

        timeLeft--;
        if (timerElement) {
            timerElement.textContent = timeLeft;
        }
        
        if (timeLeft <= 0) {
            clearInterval(timerInterval);
            timerInterval = null;
            // 检查是否在绘画阶段 (drawer_drawing 或 other_drawing)
            if (gameState.currentPage === 'all-drawing' && (gameState.gamePhase === 'drawer_drawing' || gameState.gamePhase === 'other_drawing')) {
                console.log('Time expired for drawing phase');
                // 如果还没有提交，自动提交超时处理
                handleDrawingTimeout();
            }
        }
    }, 1000);
}

async function handleDrawingTimeout() {
    // 只允许在绘画页面触发超时提交
    if (gameState.currentPage !== 'all-drawing') {
        console.log('Ignore drawing timeout: not on drawing page');
        return;
    }

    // 只允许在绘画阶段触发
    if (gameState.gamePhase !== 'drawer_drawing' && gameState.gamePhase !== 'other_drawing') {
        console.log('Ignore drawing timeout: not in drawing phase');
        return;
    }

    // 检查是否已经提交了
    const submitBtn = document.getElementById('submitDrawingBtn');
    if (!submitBtn) {
        console.log('Ignore drawing timeout: submit button not found');
        return;
    }
    if (submitBtn && submitBtn.disabled) {
        // 已经提交过了，不需要处理
        console.log('Drawing already submitted');
        return;
    }
    
    console.log('Handling drawing timeout for player:', gameState.playerId);
    
    try {
        const response = await fetch('/api/timeout-drawing', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                game_id: gameState.gameId,
                player_id: gameState.playerId
            })
        });
        
        if (!response.ok) {
            console.error('Timeout handling failed:', response.status);
            return;
        }
        
        const data = await response.json();
        if (data.success) {
            console.log('Timeout submitted, new phase:', data.game.game_phase);
            gameState.gameData = data.game;
            
            // 显示等待消息，让轮询机制负责更新页面
            showWaitingMessage(t('timeout_submitted'));
            
            // 立即启动轮询来检测阶段变化
            setTimeout(() => {
                checkGamePhaseProgress();
            }, 500);
        }
    } catch (error) {
        console.error('Error handling drawing timeout:', error);
    }
}

// ==================== 工具函数 ====================

function formatTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}

// 导出canvas为图片
function downloadDrawing() {
    const canvas = document.getElementById('canvas');
    const link = document.createElement('a');
    link.href = canvas.toDataURL('image/png');
    link.download = 'drawing.png';
    link.click();
}
