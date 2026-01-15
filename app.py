"""
扭曲画猜 - Flask Web 应用
网页版本 - 支持多人在线游戏
"""

from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import json
import random
import uuid
from datetime import datetime, timedelta
import os

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = 'twist-draw-guess-secret-key-2026'
CORS(app)

# ==================== 全局配置 ====================

# 游戏配置
GAME_CONFIG = {
    'max_players': 10,
    'min_players': 2,
    'rounds': 5,
    'time_per_round': 120,  # 秒
}

# 语言配置
LANGUAGES = {
    'zh': '中文',
    'en': 'English'
}

# 翻译文本
TRANSLATIONS = {
    'zh': {
        # 页面标题和基础UI
        'game_title': '🎨 扭曲画猜',
        'language_switch': '🌐 English',
        
        # 欢迎页
        'welcome': '欢迎来到扭曲画猜！',
        'create_new_game': '创建新游戏',
        'join_existing_game': '加入游戏',
        'creator_name': '您的名字',
        'game_language': '游戏语言',
        'chinese': '中文',
        'english': 'English',
        'create_game': '创建游戏',
        
        # 加入游戏
        'game_code': '游戏代码',
        'join_player_name': '您的名字',
        'join_game': '加入游戏',
        'please_enter_name': '请输入您的名字',
        'please_enter_code_and_name': '请输入游戏代码和名字',
        'join_failed': '加入失败',
        'join_game_failed': '加入游戏失败',
        'create_game_failed': '创建游戏失败',
        'start_game_failed': '启动游戏失败',
        
        # 大厅页
        'lobby': '游戏大厅',
        'game_code_label': '游戏代码：',
        'players': '玩家列表：',
        'player_count': '玩家数：',
        'playerCountLabel': '玩家数量',
        'maxPlayersLabel': '最多10人',
        'start_game': '开始游戏',
        'ready': '准备',
        'cancel_ready': '取消准备',
        'waiting_for_players': '等待更多玩家加入...',
        'waiting_all_ready': '等待所有玩家准备...',
        'all_ready': '所有玩家已准备！游戏即将开始...',
        'player_icon': '👤',
        
        # 游戏阶段
        'drawer_drawing': '出题者绘画阶段',
        'keywords_modified': '修改关键词阶段',
        'other_drawing': '其他玩家绘画阶段',
        'guessing': '猜测阶段',
        'result': '结果阶段',
        'gameover': '游戏结束',
        
        # 绘画相关
        'current_round': '当前轮数：',
        'keywords': '关键词',
        'original_keywords': '原始关键词',
        'submit_drawing': '提交绘画',
        'submitting': '提交中...',
        'drawing_canvas': '请在下面绘制内容',
        'clear_canvas': '清除画布',
        'undo': '撤销',
        'submit_failed': '提交失败',
        'canvas_not_found': 'Canvas 元素未找到',
        'canvas_error': '无法转换画布为图片',
        'http_error': 'HTTP 错误',
        'invalid_response': '服务器响应无效',
        'server_error': '服务器错误',
        'network_error': '网络错误',
        'unknown_error': '未知错误',
        'submitting_drawing': '正在提交绘画...',
        'waiting_for_others': '等待其他玩家完成...',
        'waiting_for_drawer': '等待出题者绘画...',
        'waiting_for_drawing': '等待其他玩家加入绘画...',
        'waiting_for_guess': '等待其他玩家完成猜测...',
        'waiting_to_modify_keywords': '等待出题者修改关键词...',
        'timeout_submitted': '时间已到，等待其他玩家...',
        'missing_game_or_player_id': '游戏ID或玩家ID缺失',
        'failed_to_start_game': '启动游戏失败',
        'failed_submit_keywords': '提交修改关键词失败',
        'drawing_timeout_text': '画',
        
        # 修改关键词
        'modify_keywords': '修改关键词',
        'original_keywords_label': '原始关键词：',
        'modified_keywords_label': '修改后的关键词：',
        'submit_keywords': '提交修改',
        'submit_keywords_failed': '提交修改关键词失败',
        'modify_failed': '修改失败',
        
        # 猜测
        'guess_question': '请选择一幅画',
        'select_drawing': '请选择一幅画',
        'submit_guess': '提交猜测',
        'drawings_gallery': '绘画库',
        
        # 结果
        'round_result': '本轮结果',
        'drawer': '出题者：',
        'round_scores': '本轮分数',
        'total_scores': '总分排行',
        'scenario': '场景说明',
        'next_round': '下一轮',
        'game_finished': '游戏结束',
        'final_winner': '最终胜者：',
        'final_scores': '最终排名',
        'play_again': '再玩一次',
        'loading': '加载中...',
        'loading_next_step': '已提交，正在加载下一步...',
        'points': '分',
        'score_for_round': '+',
        'back_to_home': '返回首页',
        
        # HTML 页面文本
        'welcomeTitle': '欢迎来到扭曲画猜',
        'welcomeDesc': '一个创意绘画和猜测游戏',
        'createTitle': '创建新游戏',
        'joinTitle': '加入游戏',
        'lobbyTitle': '游戏大厅',
        'gameCodeDisplay': '游戏代码:',
        'playersLabel': '玩家列表',
        'modifyKeywordsTitle': '修改关键词',
        'roundInfo': '轮',
        'roundInfo2': '轮',
        'roundInfo3': '轮',
        'modifyInstructions': '您是绘图者！可以修改以下关键词来迷惑其他玩家：',
        'originalKeywordsLabel': '原始关键词:',
        'fakeKeywordsLabel': '修改为这些假关键词 (可选):',
        'allDrawingTitle': '绘画阶段',
        'drawKeywordsLabel': '请绘制以下关键词之一:',
        'timeLabel': '剩余时间:',
        'guessingTitle': '识别阶段',
        'guessingInstructions': '看这些画，猜猜哪个是绘图者画的？',
        'resultTitle': '本轮结果',
        'drawerLabel': '绘图者:',
        'scenarioLabel': '计分情景:',
        'scoresLabel': '本轮分数',
        'totalScoresLabel': '总分排名',
        'gameOverTitle': '游戏结束',
        'winnerLabel': '🏆 获胜者',
        'finalScoresLabel': '最终排名',
        'createGameBtn': '创建新游戏',
        'joinGameBtn': '加入游戏',
        'playerNameLabel': '您的名字',
        'languageLabel': '游戏语言',
        'startGameBtn': '开始游戏',
        'backBtn': '返回',
        'gameCodeLabel': '游戏代码',
        'playerNameLabel2': '您的名字',
        'joinGameBtnText': '加入游戏',
        'codeText': '-',
        'startBtn': '开始游戏',
        'leaveBtn': '离开',
        'submitKeywordsBtn': '确认并继续',
        'submitDrawingBtn': '提交绘画',
        'clearBtn': '清除画布',
        'undoBtn': '撤销',
        'submitGuessBtn': '提交猜测',
        'nextRoundBtn': '下一轮',
        'playAgainBtn': '再玩一次',
        'backToHomeBtn': '返回首页',
        'creatorName': '您的名字',
        'placeholder_name': '输入您的名字',
        'placeholder_code': '输入游戏代码',
        'placeholder_keyword1': '关键词1 (可选修改)',
        'placeholder_keyword2': '关键词2 (可选修改)',
        'placeholder_keyword3': '关键词3 (可选修改)',
    },
    'en': {
        # 页面标题和基础UI
        'game_title': '🎨 Twist Draw Guess',
        'language_switch': '🌐 中文',
        
        # 欢迎页
        'welcome': 'Welcome to Twist Draw Guess!',
        'create_new_game': 'Create New Game',
        'join_existing_game': 'Join Game',
        'creator_name': 'Your Name',
        'game_language': 'Game Language',
        'chinese': '中文',
        'english': 'English',
        'create_game': 'Create Game',
        
        # 加入游戏
        'game_code': 'Game Code',
        'join_player_name': 'Your Name',
        'join_game': 'Join Game',
        'please_enter_name': 'Please enter your name',
        'please_enter_code_and_name': 'Please enter game code and name',
        'join_failed': 'Join failed',
        'join_game_failed': 'Failed to join game',
        'create_game_failed': 'Failed to create game',
        'start_game_failed': 'Failed to start game',
        
        # 大厅页
        'lobby': 'Game Lobby',
        'game_code_label': 'Game Code: ',
        'players': 'Players: ',
        'player_count': 'Number of Players: ',
        'playerCountLabel': 'Players',
        'maxPlayersLabel': 'Max 10',
        'start_game': 'Start Game',
        'ready': 'Ready',
        'cancel_ready': 'Cancel',
        'waiting_for_players': 'Waiting for more players to join...',
        'waiting_all_ready': 'Waiting for all players to be ready...',
        'all_ready': 'All players ready! Game starting...',
        'player_icon': '👤',
        
        # 游戏阶段
        'drawer_drawing': 'Drawer Drawing Phase',
        'keywords_modified': 'Keywords Modified Phase',
        'other_drawing': 'Other Players Drawing Phase',
        'guessing': 'Guessing Phase',
        'result': 'Result Phase',
        'gameover': 'Game Over',
        
        # 绘画相关
        'current_round': 'Current Round: ',
        'keywords': 'Keywords',
        'original_keywords': 'Original Keywords',
        'submit_drawing': 'Submit Drawing',
        'submitting': 'Submitting...',
        'drawing_canvas': 'Draw below',
        'clear_canvas': 'Clear Canvas',
        'undo': 'Undo',
        'submit_failed': 'Submit failed',
        'canvas_not_found': 'Canvas element not found',
        'canvas_error': 'Failed to convert canvas to image',
        'http_error': 'HTTP Error',
        'invalid_response': 'Invalid response from server',
        'server_error': 'Server error',
        'network_error': 'Network error',
        'unknown_error': 'Unknown error',
        'submitting_drawing': 'Submitting drawing...',
        'waiting_for_others': 'Waiting for other players...',
        'waiting_for_drawer': 'Waiting for drawer...',
        'waiting_for_drawing': 'Waiting for players to draw...',
        'waiting_for_guess': 'Waiting for players to guess...',
        'waiting_to_modify_keywords': 'Waiting for drawer to modify keywords...',
        'timeout_submitted': 'Time expired, waiting for others...',
        'missing_game_or_player_id': 'Missing gameId or playerId',
        'failed_to_start_game': 'Failed to start game',
        'failed_submit_keywords': 'Failed to submit modified keywords',
        'drawing_timeout_text': 'Drawing',
        
        # 修改关键词
        'modify_keywords': 'Modify Keywords',
        'original_keywords_label': 'Original Keywords: ',
        'modified_keywords_label': 'Modified Keywords: ',
        'submit_keywords': 'Submit Changes',
        'submit_keywords_failed': 'Failed to submit keywords',
        'modify_failed': 'Modification failed',
        
        # 猜测
        'guess_question': 'Please select a drawing',
        'select_drawing': 'Please select a drawing',
        'submit_guess': 'Submit Guess',
        'drawings_gallery': 'Drawings Gallery',
        
        # 结果
        'round_result': 'Round Result',
        'drawer': 'Drawer: ',
        'round_scores': 'Round Scores',
        'total_scores': 'Total Scores',
        'scenario': 'Scenario Description',
        'next_round': 'Next Round',
        'game_finished': 'Game Finished',
        'final_winner': 'Final Winner: ',
        'final_scores': 'Final Rankings',
        'play_again': 'Play Again',
        'loading': 'Loading...',
        'loading_next_step': 'Submitted, loading next step...',
        'points': 'points',
        'score_for_round': '+',
        'back_to_home': 'Back to Home',
        
        # HTML 页面文本
        'welcomeTitle': 'Welcome to Twist Draw Guess',
        'welcomeDesc': 'A creative drawing and guessing game',
        'createTitle': 'Create New Game',
        'joinTitle': 'Join Game',
        'lobbyTitle': 'Game Lobby',
        'gameCodeDisplay': 'Game Code:',
        'playersLabel': 'Players List',
        'modifyKeywordsTitle': 'Modify Keywords',
        'roundInfo': 'Round',
        'roundInfo2': 'Round',
        'roundInfo3': 'Round',
        'modifyInstructions': 'You are the drawer! You can modify the keywords below to confuse other players:',
        'originalKeywordsLabel': 'Original Keywords:',
        'fakeKeywordsLabel': 'Modify to these fake keywords (optional):',
        'allDrawingTitle': 'Drawing Phase',
        'drawKeywordsLabel': 'Please draw one of the keywords below:',
        'timeLabel': 'Time Remaining:',
        'guessingTitle': 'Guessing Phase',
        'guessingInstructions': 'Look at these drawings, can you guess which one is drawn by the drawer?',
        'resultTitle': 'Round Result',
        'drawerLabel': 'Drawer:',
        'scenarioLabel': 'Scoring Scenario:',
        'scoresLabel': 'Round Scores',
        'totalScoresLabel': 'Total Score Rankings',
        'gameOverTitle': 'Game Over',
        'winnerLabel': '🏆 Winner',
        'finalScoresLabel': 'Final Rankings',
        'createGameBtn': 'Create New Game',
        'joinGameBtn': 'Join Game',
        'playerNameLabel': 'Your Name',
        'languageLabel': 'Game Language',
        'startGameBtn': 'Start Game',
        'backBtn': 'Back',
        'gameCodeLabel': 'Game Code',
        'playerNameLabel2': 'Your Name',
        'joinGameBtnText': 'Join Game',
        'codeText': '-',
        'startBtn': 'Start Game',
        'leaveBtn': 'Leave',
        'submitKeywordsBtn': 'Confirm and Continue',
        'submitDrawingBtn': 'Submit Drawing',
        'clearBtn': 'Clear Canvas',
        'undoBtn': 'Undo',
        'submitGuessBtn': 'Submit Guess',
        'nextRoundBtn': 'Next Round',
        'playAgainBtn': 'Play Again',
        'backToHomeBtn': 'Back to Home',
        'creatorName': 'Your Name',
        'placeholder_name': 'Enter your name',
        'placeholder_code': 'Enter game code',
        'placeholder_keyword1': 'Keyword 1 (optional to modify)',
        'placeholder_keyword2': 'Keyword 2 (optional to modify)',
        'placeholder_keyword3': 'Keyword 3 (optional to modify)',
    }
}


# ==================== 关键词库 ====================

def load_keywords_library(language='zh'):
    """加载关键词库"""
    try:
        with open('keywords_library.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        keywords = []
        for category in data['categories'].values():
            if language == 'zh':
                keywords.extend(category.get('zh', []))
            else:
                keywords.extend(category.get('en', []))
        
        return keywords if keywords else get_fallback_keywords(language)
    except Exception as e:
        print(f"Error loading keywords: {e}")
        return get_fallback_keywords(language)

def get_fallback_keywords(language='zh'):
    """备用关键词池"""
    if language == 'zh':
        return ['记忆', '怀疑', '痛苦', '欢乐', '秘密', '变化', '光影', '梦想', '时间', '距离',
                '孤独', '连接', '信任', '失落', '新生', '循环', '碎片', '融合', '流动', '静寂']
    else:
        return ['Memory', 'Doubt', 'Pain', 'Joy', 'Secret', 'Change', 'Light', 'Dream', 'Time', 'Distance',
                'Loneliness', 'Connection', 'Trust', 'Loss', 'Rebirth', 'Cycle', 'Fragment', 'Fusion', 'Flow', 'Silence']

# ==================== 游戏状态管理 ====================

games = {}  # 存储所有游戏实例

class Game:
    """游戏实例 - 完整的扭曲画猜规则"""
    def __init__(self, game_id, language='zh'):
        self.id = game_id
        self.language = language
        self.players = {}
        self.owner_id = None  # 房主ID（第一个玩家）
        self.current_round = 0
        self.status = 'setup'  # setup, playing, finished
        self.keywords = load_keywords_library(language)
        
        # 游戏状态
        self.current_drawer = None
        self.original_keywords = []        # 真实关键词 (出题者看到)
        self.modified_keywords = []        # 修改后的关键词 (其他玩家看到)
        self.drawings = {}                 # 玩家ID → 绘画数据
        self.guesses = {}                  # 玩家ID → 猜测的是哪个绘画ID
        self.scores = {}                   # 玩家ID → 累计分数
        self.round_scores = {}             # 本轮各玩家的分数
        
        # 游戏阶段: drawer_drawing, keywords_modified, other_drawing, guessing, result
        self.game_phase = 'drawer_drawing'
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
    
    def add_player(self, player_id, name):
        """添加玩家"""
        if len(self.players) < GAME_CONFIG['max_players']:
            # 第一个玩家是房主
            if not self.owner_id:
                self.owner_id = player_id
            
            self.players[player_id] = {
                'name': name,
                'score': 0,
                'ready': False
            }
            self.scores[player_id] = 0
            return True
        return False
    
    def start_game(self):
        """开始游戏（由房主决定）"""
        if len(self.players) < GAME_CONFIG['min_players']:
            return False
        
        self.status = 'playing'
        self.current_round = 1
        self.start_new_round()
        return True
    
    def set_player_ready(self, player_id, ready=True):
        """设置玩家准备状态"""
        if player_id in self.players:
            self.players[player_id]['ready'] = ready
            return True
        return False
    
    def start_new_round(self):
        """开始新一轮"""
        if self.current_round > GAME_CONFIG['rounds']:
            self.status = 'finished'
            return False
        
        # 选择出题者 (轮流)
        # current_round 从 1 开始，因此这里要用 (current_round - 1) 做偏移
        player_ids = list(self.players.keys())
        self.current_drawer = player_ids[(self.current_round - 1) % len(player_ids)]
        
        # 生成真实关键词
        self.original_keywords = random.sample(self.keywords, 3)
        self.modified_keywords = []        # 还未修改
        self.drawings = {}                 # 清空绘画
        self.guesses = {}                  # 清空猜测
        self.round_scores = {}             # 清空本轮分数
        self.game_phase = 'keywords_modified' # 开始关键词修改阶段（出题者修改关键词）
        
        return True
    
    def set_fake_keywords(self, fake_keywords):
        """设置虚假关键词"""
        self.fake_keywords = fake_keywords
        self.game_phase = 'drawing'
    
    def submit_modified_keywords(self, modified_keywords):
        """出题者提交修改后的关键词
        
        Args:
            modified_keywords: 出题者修改后的关键词列表
        """
        self.modified_keywords = modified_keywords
        self.game_phase = 'other_drawing'
    
    def submit_drawing(self, player_id, drawing_data):
        """收集绘画"""
        self.drawings[player_id] = drawing_data
        print(f'Player {player_id} submitted drawing. Current drawings: {len(self.drawings)}/{len(self.players)}')
        
        # 检查是否所有玩家都已提交绘画
        if len(self.drawings) == len(self.players):
            # 所有人都提交了画，进入猜测阶段
            self.game_phase = 'guessing'
            print(f'All players submitted! Game phase changed to: {self.game_phase}')
    
    def submit_guess(self, player_id, guess_drawer_id):
        """提交猜测: 猜测哪个绘画是出题者的"""
        print(f'=== SUBMIT_GUESS ===')
        print(f'Round: {self.current_round}, Phase: {self.game_phase}')
        print(f'Player {player_id} guessing drawer: {guess_drawer_id}')
        print(f'Current drawer: {self.current_drawer}')
        print(f'Existing guesses before: {self.guesses}')
        
        self.guesses[player_id] = guess_drawer_id
        print(f'Player {player_id} submitted guess. Current guesses: {len(self.guesses)}/{len(self.players) - 1}')
        print(f'All guesses: {self.guesses}')
        
        # 检查是否所有非绘图者都已提交猜测
        if len(self.guesses) == (len(self.players) - 1):
            # 所有人都提交了猜测，计算分数并进入结果阶段
            print(f'All non-drawer players submitted! Calculating scores...')
            self.calculate_scores()
            self.game_phase = 'result'
            print(f'Game phase changed to: {self.game_phase}')
        else:
            print(f'Still waiting for {len(self.players) - 1 - len(self.guesses)} more guesses')
        print(f'===================\n')
    
    def calculate_scores(self):
        """计算本轮分数 (完整规则)"""
        self.round_scores = {}
        drawer_id = self.current_drawer
        
        # 初始化所有玩家的本轮分数
        for pid in self.players.keys():
            self.round_scores[pid] = 0
        
        # 统计有多少人猜对
        correct_count = 0
        for player_id, guessed_drawing_id in self.guesses.items():
            if player_id == drawer_id:
                continue  # 出题者不参与猜测
            
            # 检查猜测是否正确 (通过player_id而不是index)
            if guessed_drawing_id == drawer_id:
                correct_count += 1
        
        total_guessers = len(self.players) - 1  # 除去出题者
        
        # 应用计分规则
        if correct_count == 0 or correct_count == total_guessers:
            # 情况 A: 所有人都猜错 或 所有人都猜对
            self.round_scores[drawer_id] = 0
            for player_id, guessed_index in self.guesses.items():
                if player_id != drawer_id:
                    self.round_scores[player_id] = self.round_scores.get(player_id, 0) + 1
        else:
            # 情况 B: 部分人猜对
            self.round_scores[drawer_id] = 3
            
            for player_id, guessed_drawing_id in self.guesses.items():
                if player_id == drawer_id:
                    continue
                
                if guessed_drawing_id == drawer_id:
                    # 猜对的玩家
                    self.round_scores[player_id] = self.round_scores.get(player_id, 0) + 1
                else:
                    # 猜错的玩家检查是否有人猜他的画
                    if self._is_player_drawing_guessed(player_id):
                        self.round_scores[player_id] = self.round_scores.get(player_id, 0) + 2
        
        # 累加到总分
        for pid, points in self.round_scores.items():
            self.scores[pid] = self.scores.get(pid, 0) + points
        
        return self.round_scores
    
    def _is_player_drawing_guessed(self, player_id):
        """检查某玩家的绘画是否被至少一个人猜中"""
        for guesser_id, guessed_drawing_id in self.guesses.items():
            if guessed_drawing_id == player_id:
                return True
        return False
    
    def to_dict(self, player_id=None):
        """转换为字典
        
        Args:
            player_id: 请求玩家的ID，用于权限控制
                      - 出题者看到 original_keywords
                      - 其他玩家看到 modified_keywords
        """
        # 判断是否是绘图者
        is_drawer = (player_id == self.current_drawer)
        
        # 根据玩家身份返回不同的关键词
        if is_drawer:
            display_keywords = self.original_keywords
        else:
            display_keywords = self.modified_keywords if self.modified_keywords else self.original_keywords
        
        return {
            'id': self.id,
            'language': self.language,
            'owner_id': self.owner_id,  # 房主ID
            'players': self.players,
            'current_round': self.current_round,
            'status': self.status,
            'current_drawer': self.current_drawer,
            'original_keywords': self.original_keywords if is_drawer else [],  # 只有绘图者看到真实关键词
            'modified_keywords': self.modified_keywords,
            'display_keywords': display_keywords,  # 根据权限显示的关键词
            'drawings': self.drawings,
            'guesses': self.guesses,
            'scores': self.scores,
            'round_scores': self.round_scores,
            'game_phase': self.game_phase,
            'is_drawer': is_drawer,  # 告知客户端是否是绘图者
        }

# ==================== API 路由 ====================

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/api/create-game', methods=['POST'])
def create_game():
    """创建游戏"""
    data = request.json
    player_name = data.get('player_name', '').strip()  # 移除首尾空格
    language = data.get('language', 'zh')
    
    # 验证玩家名字不为空
    if not player_name:
        return jsonify({'success': False, 'error': 'Player name is required'})
    
    game_id = str(uuid.uuid4())[:8].upper()  # 转换为大写
    game = Game(game_id, language)
    games[game_id] = game
    
    print(f'Game created: {game_id}')  # 添加日志
    print(f'Current games: {list(games.keys())}')
    
    # 添加游戏创建者为第一个玩家
    player_id = str(uuid.uuid4())[:8]
    game.add_player(player_id, player_name)
    
    # 保存到session
    session['player_id'] = player_id
    session['game_id'] = game_id
    
    return jsonify({
        'success': True,
        'game_id': game_id,
        'player_id': player_id,
        'language': language
    })

@app.route('/api/join-game', methods=['POST'])
def join_game():
    """加入游戏"""
    data = request.json
    game_id = data.get('game_id', '').strip().upper()  # 转换为大写并移除空格
    player_name = data.get('player_name', '').strip()  # 移除首尾空格
    
    print(f'Join game request: game_id={game_id}, player_name={player_name}')
    print(f'Available games: {list(games.keys())}')
    
    if not game_id:
        return jsonify({'success': False, 'error': 'Game ID is required'})
    
    if not player_name:
        return jsonify({'success': False, 'error': 'Player name is required'})
    
    if game_id not in games:
        return jsonify({'success': False, 'error': f'Game not found. Available: {list(games.keys())}'})
    
    game = games[game_id]
    player_id = str(uuid.uuid4())[:8]
    
    if game.add_player(player_id, player_name):
        session['player_id'] = player_id
        session['game_id'] = game_id
        
        return jsonify({
            'success': True,
            'player_id': player_id,
            'game_id': game_id,
            'players': game.players
        })
    
    return jsonify({'success': False, 'error': 'Game is full'})

@app.route('/api/change-language', methods=['POST'])
def change_language():
    """改变游戏语言 - 随时可用，会更新关键词库"""
    data = request.json
    game_id = data.get('game_id')
    player_id = data.get('player_id')
    language = data.get('language', 'zh')
    
    if game_id not in games:
        return jsonify({'success': False, 'error': 'Game not found'})
    
    game = games[game_id]
    
    # ✅ 验证：player_id必须存在于游戏的玩家列表中
    if player_id not in game.players:
        return jsonify({'success': False, 'error': 'Player not in this game'}), 403
    
    # 改变游戏语言并重新加载关键词库
    old_language = game.language
    game.language = language
    game.keywords = load_keywords_library(language)
    
    # 如果游戏正在进行中，需要重新生成当前轮的关键词
    if game.status == 'playing' and hasattr(game, 'original_keywords'):
        # 重新从新语言的关键词库中选择
        game.original_keywords = random.sample(game.keywords, 3)
        # 如果出题者已经修改了关键词，也需要重置
        if game.modified_keywords:
            game.modified_keywords = []
        print(f'Language changed from {old_language} to {language}, regenerated keywords: {game.original_keywords}')
    
    return jsonify({'success': True, 'game': game.to_dict(player_id)})

@app.route('/api/player-ready', methods=['POST'])
def player_ready():
    """设置玩家准备状态"""
    data = request.json
    game_id = data.get('game_id')
    player_id = data.get('player_id')
    ready = data.get('ready', True)
    
    if game_id not in games:
        return jsonify({'success': False, 'error': 'Game not found'})
    
    game = games[game_id]
    
    if player_id not in game.players:
        return jsonify({'success': False, 'error': 'Player not in this game'}), 403
    
    game.set_player_ready(player_id, ready)
    
    return jsonify({
        'success': True,
        'game': game.to_dict(player_id)
    })

@app.route('/api/start-game', methods=['POST'])
def start_game():
    """开始游戏 (只有房主可以开始)"""
    data = request.json
    game_id = data.get('game_id')
    player_id = data.get('player_id')
    
    if game_id not in games:
        return jsonify({'success': False, 'error': 'Game not found'})
    
    game = games[game_id]
    
    # ✅ 验证：player_id必须存在于游戏的玩家列表中
    if player_id not in game.players:
        return jsonify({'success': False, 'error': 'Player not in this game'}), 403
    
    # ✅ 验证：只有房主可以开始游戏
    if player_id != game.owner_id:
        return jsonify({'success': False, 'error': 'Only the host can start the game'}), 403
    
    # 可选：保存session以便后续验证
    session['player_id'] = player_id
    session['game_id'] = game_id
    
    if game.start_game():
        return jsonify({
            'success': True,
            'game': game.to_dict(player_id)
        })
    
    return jsonify({'success': False, 'error': 'Not enough players'})

@app.route('/api/get-game/<game_id>', methods=['GET'])
def get_game(game_id):
    """获取游戏状态 (权限控制)"""
    if game_id not in games:
        return jsonify({'success': False, 'error': 'Game not found'})
    
    game = games[game_id]
    # 获取当前玩家ID (来自session或query参数)
    player_id = request.args.get('player_id') or session.get('player_id')
    
    return jsonify({
        'success': True,
        'game': game.to_dict(player_id)
    })

@app.route('/api/get-drawings/<game_id>', methods=['GET'])
def get_drawings(game_id):
    """获取本轮所有绘画 (打乱顺序，不返回敏感信息)"""
    if game_id not in games:
        return jsonify({'success': False, 'error': 'Game not found'})
    
    game = games[game_id]
    player_id = request.args.get('player_id') or session.get('player_id')
    
    # 获取所有绘画
    drawing_list = []
    for pid in game.players.keys():
        if pid in game.drawings:
            drawing_list.append({
                'drawing_id': pid,
                'player_id': pid,
                'drawing_data': game.drawings[pid],
                'player_name': game.players[pid]['name']
            })
    
    # 打乱顺序
    random.shuffle(drawing_list)
    
    return jsonify({
        'success': True,
        'drawings': drawing_list
        # 不返回drawer_id和original_keywords，通过to_dict()获取
    })

@app.route('/api/set-fake-keywords', methods=['POST'])
def set_fake_keywords():
    """设置虚假关键词 (已弃用，保留向后兼容)"""
    data = request.json
    game_id = data.get('game_id')
    player_id = data.get('player_id')
    fake_keywords = data.get('fake_keywords')
    
    if game_id not in games:
        return jsonify({'success': False, 'error': 'Game not found'})
    
    game = games[game_id]
    
    # ✅ 验证：player_id必须存在于游戏的玩家列表中
    if player_id not in game.players:
        return jsonify({'success': False, 'error': 'Player not in this game'}), 403
    
    # 可选：保存session
    session['player_id'] = player_id
    session['game_id'] = game_id
    
    game.set_fake_keywords(fake_keywords)
    return jsonify({'success': True})

@app.route('/api/submit-modified-keywords', methods=['POST'])
def submit_modified_keywords():
    """出题者提交修改后的关键词 (需要权限验证)"""
    data = request.json
    game_id = data.get('game_id')
    player_id = data.get('player_id')
    modified_keywords = data.get('modified_keywords')
    
    if game_id not in games:
        return jsonify({'success': False, 'error': 'Game not found'})
    
    game = games[game_id]
    
    # ✅ 验证：player_id必须存在于游戏的玩家列表中
    if player_id not in game.players:
        return jsonify({'success': False, 'error': 'Player not in this game'}), 403
    
    # ✅ 权限检查：只有出题者才能修改关键词
    if game.current_drawer != player_id:
        return jsonify({'success': False, 'error': 'Only drawer can modify keywords'}), 403
    
    # 可选：保存session
    session['player_id'] = player_id
    session['game_id'] = game_id
    
    game.submit_modified_keywords(modified_keywords)
    
    return jsonify({'success': True, 'game': game.to_dict(player_id)})

@app.route('/api/submit-drawing', methods=['POST'])
def submit_drawing():
    """提交绘画 (需要权限验证)"""
    data = request.json
    game_id = data.get('game_id')
    player_id = data.get('player_id')
    drawing_data = data.get('drawing_data')
    
    print(f'submit_drawing called: game_id={game_id}, player_id={player_id}')
    
    if game_id not in games:
        return jsonify({'success': False, 'error': 'Game not found'})
    
    game = games[game_id]
    
    # ✅ 验证：player_id必须存在于游戏的玩家列表中
    if player_id not in game.players:
        return jsonify({'success': False, 'error': 'Player not in this game'}), 403
    
    # 可选：保存session
    session['player_id'] = player_id
    session['game_id'] = game_id
    
    game.submit_drawing(player_id, drawing_data)
    print(f'Game phase after submit: {game.game_phase}')
    
    return jsonify({'success': True, 'game': game.to_dict(player_id)})

@app.route('/api/submit-guess', methods=['POST'])
def submit_guess():
    """提交猜测: 猜测哪个绘画是出题者的 (需要权限验证)"""
    data = request.json
    game_id = data.get('game_id')
    player_id = data.get('player_id')
    guess_drawing_id = data.get('guess_drawing_id')
    
    if game_id not in games:
        return jsonify({'success': False, 'error': 'Game not found'})
    
    game = games[game_id]
    
    # ✅ 验证：player_id必须存在于游戏的玩家列表中
    if player_id not in game.players:
        return jsonify({'success': False, 'error': 'Player not in this game'}), 403

    # ✅ 规则限制：出题者不参与猜测
    if player_id == game.current_drawer:
        return jsonify({'success': False, 'error': 'Drawer cannot guess'}), 403
    
    # 可选：保存session
    session['player_id'] = player_id
    session['game_id'] = game_id
    
    game.submit_guess(player_id, guess_drawing_id)
    
    return jsonify({'success': True, 'game': game.to_dict(player_id)})

@app.route('/api/timeout-drawing', methods=['POST'])
def timeout_drawing():
    """处理超时未提交的玩家 (自动提交空白画，跳过到下一阶段)"""
    data = request.json
    game_id = data.get('game_id')
    player_id = data.get('player_id')
    
    if game_id not in games:
        return jsonify({'success': False, 'error': 'Game not found'})
    
    game = games[game_id]
    
    # ✅ 验证：player_id必须存在于游戏的玩家列表中
    if player_id not in game.players:
        return jsonify({'success': False, 'error': 'Player not in this game'}), 403
    
    # 如果玩家已经提交过了，直接返回
    if player_id in game.drawings:
        return jsonify({'success': True, 'message': 'Already submitted', 'game': game.to_dict(player_id)})
    
    # 提交一个空白画（表示超时未提交）
    game.submit_drawing(player_id, 'data:image/png;base64,')  # 空白PNG
    
    return jsonify({'success': True, 'game': game.to_dict(player_id)})

@app.route('/api/next-round', methods=['POST'])
def next_round():
    """下一轮 (需要权限验证)"""
    data = request.json
    game_id = data.get('game_id')
    player_id = data.get('player_id')
    
    if game_id not in games:
        return jsonify({'success': False, 'error': 'Game not found'})
    
    game = games[game_id]
    
    # ✅ 验证：player_id必须存在于游戏的玩家列表中
    if player_id not in game.players:
        return jsonify({'success': False, 'error': 'Player not in this game'}), 403
    
    # 可选：保存session
    session['player_id'] = player_id
    session['game_id'] = game_id

    # ✅ 防重复推进：只有在结果阶段才能进入下一轮
    if game.game_phase != 'result':
        return jsonify({
            'success': True,
            'ignored': True,
            'message': 'Not in result phase',
            'game': game.to_dict(player_id)
        })

    # 增加轮数并开始新一轮（任何玩家都可以触发）
    game.current_round += 1
    print(f'[Next Round] Moving to round {game.current_round}')
    
    if game.start_new_round():
        print(f'[Next Round] Started round {game.current_round}, phase: {game.game_phase}')
        return jsonify({
            'success': True,
            'game': game.to_dict(player_id)
        })
    else:
        print(f'[Next Round] Game over after {game.current_round - 1} rounds')
        return jsonify({
            'success': True,
            'game_over': True,
            'game': game.to_dict(player_id)
        })

@app.route('/api/get-scores/<game_id>', methods=['GET'])
def get_scores(game_id):
    """获取分数"""
    if game_id not in games:
        return jsonify({'success': False, 'error': 'Game not found'})
    
    game = games[game_id]
    round_scores = game.calculate_scores()
    
    return jsonify({
        'success': True,
        'round_scores': round_scores,
        'total_scores': game.scores
    })

@app.route('/api/keywords/<language>', methods=['GET'])
def get_keywords(language):
    """获取关键词"""
    keywords = load_keywords_library(language)
    sample = random.sample(keywords, min(3, len(keywords)))
    
    return jsonify({
        'success': True,
        'keywords': sample
    })

@app.route('/api/text/<language>', methods=['GET'])
def get_text(language):
    """获取翻译文本"""
    if language not in TRANSLATIONS:
        language = 'zh'
    
    return jsonify({
        'success': True,
        'text': TRANSLATIONS[language]
    })

# ==================== 清理过期游戏 ====================

def cleanup_old_games():
    """清理超过1小时未活动的游戏"""
    current_time = datetime.now()
    expired_ids = []
    
    for game_id, game in games.items():
        if current_time - game.last_activity > timedelta(hours=1):
            expired_ids.append(game_id)
    
    for game_id in expired_ids:
        del games[game_id]

@app.before_request
def cleanup():
    """每次请求前清理过期游戏"""
    cleanup_old_games()

# ==================== 错误处理 ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Server error'}), 500

# ==================== 启动 ====================

if __name__ == '__main__':
    # 检查keywords_library.json是否存在
    if not os.path.exists('keywords_library.json'):
        print("Warning: keywords_library.json not found!")
    
    print("=" * 50)
    print("🎮 扭曲画猜 - Flask Web 应用")
    print("=" * 50)
    print("访问: http://localhost:5000")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
