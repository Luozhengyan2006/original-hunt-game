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
    'min_players': 4,
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
        'game_name': '扭曲画猜',
        'setup': '设置游戏',
        'num_players': '玩家人数',
        'player_name': '玩家名称',
        'language': '选择语言',
        'start_game': '开始游戏',
        'drawing_phase': '绘画阶段',
        'draw_your_keywords': '请绘制您的关键词',
        'time_left': '剩余时间',
        'guessing_phase': '猜测阶段',
        'guess': '猜测',
        'submit_guess': '提交猜测',
        'result': '结果',
        'correct': '正确！',
        'wrong': '错误',
        'next_round': '下一轮',
        'game_over': '游戏结束',
        'total_score': '总分',
        'thanks_for_playing': '感谢游玩！',
        'play_again': '再玩一次',
        'clear_canvas': '清除画布',
        'download_image': '下载图片',
    },
    'en': {
        'game_name': 'Twist Draw Guess',
        'setup': 'Setup Game',
        'num_players': 'Number of Players',
        'player_name': 'Player Name',
        'language': 'Select Language',
        'start_game': 'Start Game',
        'drawing_phase': 'Drawing Phase',
        'draw_your_keywords': 'Draw your keywords',
        'time_left': 'Time Left',
        'guessing_phase': 'Guessing Phase',
        'guess': 'Guess',
        'submit_guess': 'Submit Guess',
        'result': 'Result',
        'correct': 'Correct!',
        'wrong': 'Wrong',
        'next_round': 'Next Round',
        'game_over': 'Game Over',
        'total_score': 'Total Score',
        'thanks_for_playing': 'Thanks for playing!',
        'play_again': 'Play Again',
        'clear_canvas': 'Clear Canvas',
        'download_image': 'Download Image',
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
        self.current_round = 0
        self.status = 'setup'  # setup, playing, finished
        self.keywords = load_keywords_library(language)
        
        # 游戏状态
        self.current_drawer = None
        self.original_keywords = []        # 真实关键词 (出题者看到)
        self.fake_keywords = []            # 虚假关键词 (其他玩家看到)
        self.drawings = {}                 # 玩家ID → 绘画数据
        self.guesses = {}                  # 玩家ID → 猜测的是哪个绘画 (索引)
        self.scores = {}                   # 玩家ID → 累计分数
        self.round_scores = {}             # 本轮各玩家的分数
        
        self.game_phase = 'keywords'       # 游戏阶段: keywords, modify, drawing, guessing, result
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
    
    def add_player(self, player_id, name):
        """添加玩家"""
        if len(self.players) < GAME_CONFIG['max_players']:
            self.players[player_id] = {
                'name': name,
                'score': 0,
                'ready': False
            }
            self.scores[player_id] = 0
            return True
        return False
    
    def start_game(self):
        """开始游戏"""
        if len(self.players) >= GAME_CONFIG['min_players']:
            self.status = 'playing'
            self.current_round = 1
            self.start_new_round()
            return True
        return False
    
    def start_new_round(self):
        """开始新一轮"""
        if self.current_round > GAME_CONFIG['rounds']:
            self.status = 'finished'
            return False
        
        # 选择出题者 (轮流)
        player_ids = list(self.players.keys())
        self.current_drawer = player_ids[self.current_round % len(player_ids)]
        
        # 生成真实关键词
        self.original_keywords = random.sample(self.keywords, 3)
        self.fake_keywords = []        # 还未修改
        self.drawings = {}             # 清空绘画
        self.guesses = {}              # 清空猜测
        self.round_scores = {}         # 清空本轮分数
        self.game_phase = 'keywords'   # 开始关键词阶段
        
        return True
    
    def set_fake_keywords(self, fake_keywords):
        """设置虚假关键词"""
        self.fake_keywords = fake_keywords
        self.game_phase = 'drawing'
    
    def submit_drawing(self, player_id, drawing_data):
        """收集绘画"""
        self.drawings[player_id] = drawing_data
    
    def submit_guess(self, player_id, guess_drawer_id):
        """提交猜测: 猜测哪个绘画是出题者的"""
        self.guesses[player_id] = guess_drawer_id
    
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
                      如果是绘图者，返回真实关键词
                      否则返回假关键词
        """
        # 判断是否是绘图者
        is_drawer = (player_id == self.current_drawer)
        
        return {
            'id': self.id,
            'language': self.language,
            'players': self.players,
            'current_round': self.current_round,
            'status': self.status,
            'current_drawer': self.current_drawer,
            'original_keywords': self.original_keywords if is_drawer else self.fake_keywords,
            'fake_keywords': self.fake_keywords,
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
    language = data.get('language', 'zh')
    
    game_id = str(uuid.uuid4())[:8]
    game = Game(game_id, language)
    games[game_id] = game
    
    return jsonify({
        'success': True,
        'game_id': game_id,
        'language': language
    })

@app.route('/api/join-game', methods=['POST'])
def join_game():
    """加入游戏"""
    data = request.json
    game_id = data.get('game_id')
    player_name = data.get('player_name')
    
    if game_id not in games:
        return jsonify({'success': False, 'error': 'Game not found'})
    
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

@app.route('/api/start-game', methods=['POST'])
def start_game():
    """开始游戏 (需要权限验证)"""
    data = request.json
    game_id = data.get('game_id')
    player_id = data.get('player_id') or session.get('player_id')
    
    # ✅ 身份验证：检查player_id是否匹配session
    if session.get('player_id') != player_id:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    if game_id not in games:
        return jsonify({'success': False, 'error': 'Game not found'})
    
    game = games[game_id]
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
    """设置虚假关键词 (需要权限验证)"""
    data = request.json
    game_id = data.get('game_id')
    player_id = data.get('player_id')
    fake_keywords = data.get('fake_keywords')
    
    # ✅ 身份验证：检查player_id是否匹配session
    if session.get('player_id') != player_id:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    if game_id not in games:
        return jsonify({'success': False, 'error': 'Game not found'})
    
    game = games[game_id]
    game.set_fake_keywords(fake_keywords)
    
    return jsonify({'success': True})

@app.route('/api/submit-drawing', methods=['POST'])
def submit_drawing():
    """提交绘画 (需要权限验证)"""
    data = request.json
    game_id = data.get('game_id')
    player_id = data.get('player_id')
    drawing_data = data.get('drawing_data')
    
    # ✅ 身份验证：检查player_id是否匹配session
    if session.get('player_id') != player_id:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    if game_id not in games:
        return jsonify({'success': False, 'error': 'Game not found'})
    
    game = games[game_id]
    game.submit_drawing(player_id, drawing_data)
    
    return jsonify({'success': True})

@app.route('/api/submit-guess', methods=['POST'])
def submit_guess():
    """提交猜测: 猜测哪个绘画是出题者的 (需要权限验证)"""
    data = request.json
    game_id = data.get('game_id')
    player_id = data.get('player_id')
    guess_drawing_id = data.get('guess_drawing_id')
    
    # ✅ 身份验证：检查player_id是否匹配session
    if session.get('player_id') != player_id:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    if game_id not in games:
        return jsonify({'success': False, 'error': 'Game not found'})
    
    game = games[game_id]
    game.submit_guess(player_id, guess_drawing_id)
    
    return jsonify({'success': True})

@app.route('/api/next-round', methods=['POST'])
def next_round():
    """下一轮 (需要权限验证)"""
    data = request.json
    game_id = data.get('game_id')
    player_id = data.get('player_id')
    
    # ✅ 身份验证：检查player_id是否匹配session
    if session.get('player_id') != player_id:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    if game_id not in games:
        return jsonify({'success': False, 'error': 'Game not found'})
    
    game = games[game_id]
    game.current_round += 1
    
    if game.start_new_round():
        return jsonify({
            'success': True,
            'game': game.to_dict(player_id)
        })
    else:
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
