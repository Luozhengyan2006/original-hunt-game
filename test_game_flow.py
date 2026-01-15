"""
游戏流程测试脚本 - 验证出题者修改关键词流程
"""

import requests
import json
import time
from typing import Dict, Tuple

BASE_URL = 'http://127.0.0.1:5000/api'

class GameFlowTester:
    def __init__(self):
        self.game_id = None
        self.players = {}  # player_name -> player_id
        self.game_data = {}
    
    def create_game(self, language='zh') -> str:
        """创建游戏"""
        response = requests.post(f'{BASE_URL}/create-game', 
            json={'player_name': 'Alice', 'language': language})
        data = response.json()
        self.game_id = data['game_id']
        alice_id = data['player_id']
        self.players['Alice'] = alice_id
        print(f"✅ 游戏创建成功: {self.game_id}")
        return self.game_id
    
    def add_player(self, name: str) -> str:
        """添加玩家"""
        response = requests.post(f'{BASE_URL}/join-game',
            json={'game_id': self.game_id, 'player_name': name})
        data = response.json()
        player_id = data['player_id']
        self.players[name] = player_id
        print(f"✅ 玩家添加成功: {name} ({player_id})")
        return player_id
    
    def start_game(self, player_id: str):
        """开始游戏"""
        response = requests.post(f'{BASE_URL}/start-game',
            json={'game_id': self.game_id, 'player_id': player_id})
        data = response.json()
        if data['success']:
            print("✅ 游戏启动成功")
            self.game_data = data['game']
            print(f"   初始阶段: {data['game']['game_phase']}")
        return data['success']
    
    def get_game_state(self, player_id: str = None) -> Dict:
        """获取游戏状态"""
        params = {}
        if player_id:
            params['player_id'] = player_id
        response = requests.get(f'{BASE_URL}/get-game/{self.game_id}', params=params)
        data = response.json()
        return data['game']
    
    def submit_modified_keywords(self, drawer_id: str, keywords: list):
        """出题者提交修改的关键词"""
        response = requests.post(f'{BASE_URL}/submit-modified-keywords',
            json={
                'game_id': self.game_id,
                'player_id': drawer_id,
                'modified_keywords': keywords
            })
        data = response.json()
        if data['success']:
            print(f"✅ 修改后的关键词提交成功")
            print(f"   新阶段: {data['game']['game_phase']}")
        return data['success']
    
    def submit_drawing(self, player_id: str, drawing_data: str):
        """玩家提交绘画"""
        response = requests.post(f'{BASE_URL}/submit-drawing',
            json={
                'game_id': self.game_id,
                'player_id': player_id,
                'drawing_data': drawing_data
            })
        data = response.json()
        if data['success']:
            print(f"✅ 玩家 {player_id} 绘画提交成功")
            if 'game_phase' in data.get('game', {}):
                print(f"   当前阶段: {data['game']['game_phase']}")
        else:
            print(f"❌ 玩家 {player_id} 提交失败: {data.get('error')}")
        return data['success']
    
    def test_flow(self):
        """测试完整游戏流程"""
        print("\n" + "="*60)
        print("🎮 游戏流程测试开始")
        print("="*60 + "\n")
        
        # 1. 创建游戏
        print("1️⃣  创建游戏...")
        self.create_game()
        
        # 2. 添加3个玩家
        print("\n2️⃣  添加玩家...")
        self.add_player("Bob")
        self.add_player("Charlie")
        
        # 3. 启动游戏
        print("\n3️⃣  启动游戏...")
        alice_id = self.players["Alice"]
        self.start_game(alice_id)
        
        # 检查初始阶段
        game = self.get_game_state(alice_id)
        print(f"\n   当前阶段: {game['game_phase']}")
        actual_drawer_id = game['current_drawer']
        print(f"   出题者ID: {actual_drawer_id}")
        # 找到出题者的名字
        drawer_name = "Unknown"
        for name, pid in self.players.items():
            if pid == actual_drawer_id:
                drawer_name = name
                break
        print(f"   出题者: {drawer_name}")
        print(f"   原始关键词 (仅出题者可见): {game.get('original_keywords', [])}")
        
        # 4. 出题者修改关键词
        print("\n4️⃣  出题者修改关键词...")
        fake_keywords = ["火焰", "月亮", "飞鸟"]
        self.submit_modified_keywords(actual_drawer_id, fake_keywords)
        
        # 检查其他玩家的状态
        print("\n   检查其他玩家的游戏状态:")
        bob_id = self.players["Bob"]
        bob_game = self.get_game_state(bob_id)
        print(f"   Bob 看到的关键词 (修改后): {bob_game.get('modified_keywords', [])}")
        print(f"   Bob 看到的阶段: {bob_game['game_phase']}")
        
        # 5. 所有玩家提交绘画
        print("\n5️⃣  所有玩家提交绘画...")
        for name, pid in self.players.items():
            print(f"   {name} 提交绘画...")
            # 使用简单的PNG数据URI作为绘画数据
            drawing_data = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
            self.submit_drawing(pid, drawing_data)
            time.sleep(0.5)  # 稍微延迟以模拟真实情况
        
        # 检查是否进入猜测阶段
        print("\n   检查游戏阶段是否更新...")
        game = self.get_game_state(alice_id)
        print(f"   当前阶段: {game['game_phase']}")
        
        # 6. 验证Issue A: 检查出题者在other_drawing阶段看到什么
        print("\n6️⃣  验证Issue A (出题者等待消息)...")
        if game['game_phase'] == 'other_drawing':
            print("✅ ISSUE A: 出题者在other_drawing阶段")
            drawer_game = self.get_game_state(actual_drawer_id)
            print(f"   出题者 is_drawer 标志: {drawer_game.get('is_drawer')}")
            print(f"   出题者应该看到'等待其他玩家猜测'消息")
        else:
            print(f"❌ 预期other_drawing阶段，但实际是: {game['game_phase']}")
        
        # 7. 所有玩家提交猜测
        print("\n7️⃣  所有玩家提交猜测...")
        for name, pid in self.players.items():
            if pid != actual_drawer_id:  # 出题者不参与猜测
                print(f"   {name} 提交猜测 (猜测出题者是 {drawer_name})...")
                response = requests.post(f'{BASE_URL}/submit-guess',
                    json={
                        'game_id': self.game_id,
                        'player_id': pid,
                        'guess_drawing_id': actual_drawer_id
                    })
                data = response.json()
                if data['success']:
                    print(f"   ✅ 猜测提交成功")
                    if 'game' in data and 'game_phase' in data['game']:
                        print(f"      当前阶段: {data['game']['game_phase']}")
                else:
                    print(f"   ❌ 提交失败: {data.get('error')}")
                time.sleep(0.5)
        
        # 8. 验证Issue B: 检查是否自动转到result阶段
        print("\n8️⃣  验证Issue B (自动转到result阶段)...")
        game = self.get_game_state(alice_id)
        print(f"   当前阶段: {game['game_phase']}")
        
        if game['game_phase'] == 'result':
            print("✅ ISSUE B FIXED: 自动转到result阶段！")
            print(f"   出题者分数: {game['round_scores'].get(actual_drawer_id, 0)}")
            print(f"   当前总分: {game['scores']}")
        else:
            print(f"❌ ISSUE B NOT FIXED: 仍在 {game['game_phase']} 阶段，应该是result")
        
        print("\n" + "="*60)
        print("✅ 游戏流程测试完成！")
        print("="*60)

if __name__ == '__main__':
    tester = GameFlowTester()
    try:
        tester.test_flow()
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
