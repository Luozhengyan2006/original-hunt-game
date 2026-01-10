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
};

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
    // 加载翻译文本
    await loadTexts('zh');
    updateUIText();
    
    // 初始化画布
    const canvas = document.getElementById('canvas');
    if (canvas) {
        canvasState.context = canvas.getContext('2d');
        setupCanvas();
    }
}

// ==================== 文本和语言 ====================

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
    
    // 主页
    if (document.getElementById('gameTitle')) {
        document.getElementById('gameTitle').textContent = gameState.currentLanguage === 'zh' ? '🎨 扭曲画猜' : '🎨 Twist Draw Guess';
    }
    
    // 更新所有文本元素
    Object.keys(texts).forEach(key => {
        const element = document.getElementById(key);
        if (element) {
            element.textContent = texts[key];
        }
    });
    
    // 更新语言按钮
    const langBtn = document.getElementById('langBtn');
    if (langBtn) {
        langBtn.textContent = gameState.currentLanguage === 'zh' ? '🌐 English' : '🌐 中文';
    }
}

async function switchLanguage() {
    gameState.currentLanguage = gameState.currentLanguage === 'zh' ? 'en' : 'zh';
    await loadTexts(gameState.currentLanguage);
    updateUIText();
}

// ==================== 页面导航 ====================

function showPage(pageName) {
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
}

function showModifyKeywords() {
    showPage('modify-keywords');
}

function showAllDrawing() {
    showPage('all-drawing');
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
    const language = document.getElementById('gameLanguage').value;
    
    if (!playerName) {
        alert(gameState.currentLanguage === 'zh' ? '请输入您的名字' : 'Please enter your name');
        return;
    }
    
    try {
        // 创建游戏
        const createRes = await fetch('/api/create-game', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ language })
        });
        
        const createData = await createRes.json();
        if (!createData.success) {
            throw new Error('Failed to create game');
        }
        
        gameState.gameId = createData.game_id;
        
        // 加入游戏
        const joinRes = await fetch('/api/join-game', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                game_id: gameState.gameId,
                player_name: playerName
            })
        });
        
        const joinData = await joinRes.json();
        if (joinData.success) {
            gameState.playerId = joinData.player_id;
            await loadTexts(language);
            updateUIText();
            updateLobby();
            showLobby();
        }
    } catch (error) {
        console.error('Error creating game:', error);
        alert('创建游戏失败 / Failed to create game');
    }
}

async function joinGame() {
    const gameId = document.getElementById('gameCode').value.trim();
    const playerName = document.getElementById('joinPlayerName').value.trim();
    
    if (!gameId || !playerName) {
        alert(gameState.currentLanguage === 'zh' ? '请输入游戏代码和名字' : 'Please enter game code and name');
        return;
    }
    
    try {
        const response = await fetch('/api/join-game', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                game_id: gameId,
                player_name: playerName
            })
        });
        
        const data = await response.json();
        if (data.success) {
            gameState.gameId = gameId;
            gameState.playerId = data.player_id;
            updateLobby();
            showLobby();
        } else {
            alert('加入失败 / Join failed');
        }
    } catch (error) {
        console.error('Error joining game:', error);
        alert('加入游戏失败 / Failed to join game');
    }
}

async function updateLobby() {
    try {
        const response = await fetch(`/api/get-game/${gameState.gameId}?player_id=${gameState.playerId}`);
        const data = await response.json();
        
        if (data.success) {
            gameState.gameData = data.game;
            
            // 更新游戏代码
            document.getElementById('codeText').textContent = gameState.gameId;
            
            // 更新玩家列表
            const playersList = document.getElementById('playersList');
            playersList.innerHTML = '';
            
            Object.values(gameState.gameData.players).forEach(player => {
                const div = document.createElement('div');
                div.className = 'player-item';
                div.textContent = `👤 ${player.name}`;
                playersList.appendChild(div);
            });
        }
    } catch (error) {
        console.error('Error updating lobby:', error);
    }
}

function leaveLobby() {
    backToWelcome();
}

async function startGame() {
    try {
        const response = await fetch('/api/start-game', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                game_id: gameState.gameId,
                player_id: gameState.playerId
            })
        });
        
        const data = await response.json();
        if (data.success) {
            gameState.gameData = data.game;
            gameState.gameStarted = true;
            startGameRound();
        }
    } catch (error) {
        console.error('Error starting game:', error);
    }
}

async function startGameRound() {
    try {
        const response = await fetch(`/api/get-game/${gameState.gameId}?player_id=${gameState.playerId}`);
        const data = await response.json();
        
        if (data.success) {
            gameState.gameData = data.game;
            gameState.gamePhase = data.game.game_phase;
            
            // 检查是否是绘图者
            gameState.isDrawer = gameState.gameData.current_drawer === gameState.playerId;
            
            // 根据当前阶段显示正确的页面
            if (gameState.gamePhase === 'keywords' || gameState.gamePhase === 'modify') {
                if (gameState.isDrawer) {
                    updateModifyKeywordsPhase();
                    showModifyKeywords();
                } else {
                    // 其他玩家等待绘图者准备
                    showWaitingForDrawer();
                }
            } else if (gameState.gamePhase === 'drawing') {
                updateAllDrawingPhase();
                showAllDrawing();
            } else if (gameState.gamePhase === 'guessing') {
                updateGuessingPhase();
                showGuessing();
            } else if (gameState.gamePhase === 'result') {
                showResultPhase();
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
        
        data.original_keywords.forEach(keyword => {
            const tag = document.createElement('div');
            tag.className = 'keyword-tag';
            tag.textContent = keyword;
            originalKeywords.appendChild(tag);
        });
    }
    
    // 清空假关键词输入框
    document.getElementById('fakeKeyword1').value = '';
    document.getElementById('fakeKeyword2').value = '';
    document.getElementById('fakeKeyword3').value = '';
}

async function submitFakeKeywords() {
    const fakeKeywords = [
        document.getElementById('fakeKeyword1').value.trim() || gameState.gameData.original_keywords[0],
        document.getElementById('fakeKeyword2').value.trim() || gameState.gameData.original_keywords[1],
        document.getElementById('fakeKeyword3').value.trim() || gameState.gameData.original_keywords[2]
    ];
    
    try {
        const response = await fetch('/api/set-fake-keywords', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                game_id: gameState.gameId,
                player_id: gameState.playerId,
                fake_keywords: fakeKeywords
            })
        });
        
        const data = await response.json();
        if (data.success) {
            gameState.gameData = data.game;
            // 绘图者提交假关键词后，所有玩家进入绘画阶段
            updateAllDrawingPhase();
            showAllDrawing();
        }
    } catch (error) {
        console.error('Error submitting fake keywords:', error);
    }
}

// 等待绘图者的页面占位函数
function showWaitingForDrawer() {
    // 简单起见，定期检查游戏状态
    setTimeout(() => {
        startGameRound();
    }, 2000);
}

// ==================== 所有玩家绘画阶段 ====================

function updateAllDrawingPhase() {
    const data = gameState.gameData;
    
    // 更新轮次
    const roundEl = document.getElementById('currentRound2');
    if (roundEl) roundEl.textContent = data.current_round;
    
    // 显示关键词 (假关键词给其他玩家，原始给绘图者参考)
    const keywordsList = document.getElementById('keywordsList');
    if (keywordsList) {
        keywordsList.innerHTML = '';
        
        const displayKeywords = gameState.isDrawer ? 
            data.original_keywords : 
            data.fake_keywords;
        
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
    const rect = canvas.getBoundingClientRect();
    
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
    const drawingData = canvas.toDataURL('image/png');
    
    try {
        const response = await fetch('/api/submit-drawing', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                game_id: gameState.gameId,
                player_id: gameState.playerId,
                drawing_data: drawingData
            })
        });
        
        const data = await response.json();
        if (data.success) {
            gameState.gameData = data.game;
            // 进入猜测阶段（当所有玩家都提交了画）
            if (data.game.game_phase === 'guessing') {
                updateGuessingPhase();
                showGuessing();
            } else {
                // 等待其他玩家完成绘画
                showWaitingMessage('等待其他玩家完成绘画...');
                // 定期检查游戏状态
                checkGamePhaseProgress();
            }
        }
    } catch (error) {
        console.error('Error submitting drawing:', error);
    }
}

// ==================== 猜测阶段 (识别绘图者的画) ====================

async function updateGuessingPhase() {
    try {
        const response = await fetch(`/api/get-drawings/${gameState.gameId}`);
        const data = await response.json();
        
        if (data.success) {
            const drawings = data.drawings;
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
                    img.src = drawing.image;
                    img.alt = `Drawing ${displayIndex + 1}`;
                    
                    const label = document.createElement('p');
                    label.textContent = `画 ${displayIndex + 1}`;
                    label.className = 'drawing-number';
                    
                    drawingItem.appendChild(img);
                    drawingItem.appendChild(label);
                    gallery.appendChild(drawingItem);
                });
            }
        }
    } catch (error) {
        console.error('Error loading drawings:', error);
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
        alert(gameState.currentLanguage === 'zh' ? '请选择一幅画' : 'Please select a drawing');
        return;
    }
    
    try {
        const response = await fetch('/api/submit-guess', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                game_id: gameState.gameId,
                player_id: gameState.playerId,
                guess_drawing_id: gameState.selectedDrawingIndex  // 发送drawing_id而不是index
            })
        });
        
        const data = await response.json();
        if (data.success) {
            gameState.gameData = data.game;
            // 检查是否所有玩家都已猜测
            if (data.game.game_phase === 'result') {
                showResultPhase();
            } else {
                // 等待其他玩家完成猜测
                showWaitingMessage('等待其他玩家完成猜测...');
                checkGamePhaseProgress();
            }
        }
    } catch (error) {
        console.error('Error submitting guess:', error);
    }
}

function showWaitingMessage(message) {
    // 简单起见，使用console.log（实际应该有专门的等待页面）
    console.log(message);
}

function checkGamePhaseProgress() {
    setTimeout(async () => {
        try {
            const response = await fetch(`/api/get-game/${gameState.gameId}`);
            const data = await response.json();
            
            if (data.success) {
                gameState.gameData = data.game;
                
                if (data.game.game_phase === 'guessing' && gameState.gamePhase === 'drawing') {
                    gameState.gamePhase = 'guessing';
                    updateGuessingPhase();
                    showGuessing();
                } else if (data.game.game_phase === 'result') {
                    gameState.gamePhase = 'result';
                    showResultPhase();
                }
            }
        } catch (error) {
            console.error('Error checking game progress:', error);
        }
    }, 2000);
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
        
        const sorted = Object.entries(gameState.gameData.total_scores || {})
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
    try {
        const response = await fetch('/api/next-round', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                game_id: gameState.gameId,
                player_id: gameState.playerId
            })
        });
        
        const data = await response.json();
        if (data.success) {
            gameState.gameData = data.game;
            gameState.selectedDrawingIndex = null;
            
            if (data.game_over) {
                showGameOverPage();
            } else {
                startGameRound();
            }
        }
    } catch (error) {
        console.error('Error loading next round:', error);
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
    
    timerInterval = setInterval(() => {
        timeLeft--;
        if (timerElement) {
            timerElement.textContent = timeLeft;
        }
        
        if (timeLeft <= 0) {
            clearInterval(timerInterval);
            if (gameState.gamePhase === 'drawing') {
                submitDrawing();
            }
        }
    }, 1000);
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
