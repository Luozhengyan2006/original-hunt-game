#!/usr/bin/env python3
"""
完整的浏览器标签页模拟测试：
- 标签1：创建游戏，开始游戏
- 标签2：加入游戏，轮询大厅，检测游戏开始时自动进入
"""
import requests
import time
import threading

BASE_URL = 'http://localhost:5000'

def test_auto_enter_game():
    """测试玩家在大厅轮询时自动进入游戏"""
    
    print("\n" + "=" * 70)
    print("[TEST] 玩家在大厅轮询时自动进入游戏")
    print("=" * 70)
    
    results = {
        'player2_detected_game_start': False,
        'player2_final_phase': None
    }
    
    # 步骤1：创建游戏
    print("\n[步骤1] 玩家1创建游戏...")
    create_resp = requests.post(
        f'{BASE_URL}/api/create-game',
        json={'player_name': '玩家1'}
    )
    create_data = create_resp.json()
    game_id = create_data.get('game_id')
    player1_id = create_data.get('player_id')
    print(f"[OK] 游戏ID: {game_id}, 玩家1 ID: {player1_id}")
    
    # 步骤2：玩家2加入
    print("\n[步骤2] 玩家2加入游戏...")
    join_resp = requests.post(
        f'{BASE_URL}/api/join-game',
        json={'game_id': game_id, 'player_name': '玩家2'}
    )
    join_data = join_resp.json()
    player2_id = join_data.get('player_id')
    print(f"[OK] 玩家2 ID: {player2_id}")
    
    def player2_polling():
        """模拟玩家2在大厅中轮询"""
        print("\n[玩家2] 开始轮询大厅状态...")
        for i in range(10):  # 轮询10次
            time.sleep(0.8)
            
            poll_resp = requests.get(
                f'{BASE_URL}/api/get-game/{game_id}',
                params={'player_id': player2_id}
            )
            poll_data = poll_resp.json()
            
            if poll_data.get('success'):
                status = poll_data['game'].get('status')
                phase = poll_data['game'].get('game_phase')
                player_count = len(poll_data['game']['players'])
                
                print(f"[玩家2] [轮询{i+1}] 状态={status}, 阶段={phase}, 玩家数={player_count}")
                
                if status == 'playing' and phase is not None:
                    print(f"[玩家2] ✅ 检测到游戏已开始！阶段={phase}")
                    results['player2_detected_game_start'] = True
                    results['player2_final_phase'] = phase
                    break
    
    # 在后台启动玩家2的轮询
    poll_thread = threading.Thread(target=player2_polling, daemon=True)
    poll_thread.start()
    
    # 等待玩家2开始轮询
    time.sleep(1)
    
    # 步骤3：玩家1开始游戏
    print("\n[步骤3] 玩家1开始游戏...")
    start_resp = requests.post(
        f'{BASE_URL}/api/start-game',
        json={'game_id': game_id, 'player_id': player1_id}
    )
    start_data = start_resp.json()
    
    if start_data.get('success'):
        print(f"[OK] 游戏已开始，出题者={start_data['game'].get('current_drawer')}")
    else:
        print(f"[FAIL] 开始游戏失败: {start_data.get('error')}")
        return False
    
    # 等待轮询线程检测到游戏开始
    poll_thread.join(timeout=8)
    
    # 输出结果
    print("\n" + "=" * 70)
    if results['player2_detected_game_start']:
        print("✅ [PASS] 玩家2在轮询时成功检测到游戏开始！")
        print(f"         最终阶段: {results['player2_final_phase']}")
        return True
    else:
        print("❌ [FAIL] 玩家2未能检测到游戏开始")
        return False

if __name__ == '__main__':
    try:
        success = test_auto_enter_game()
        print("=" * 70)
        import sys
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[FAIL] 测试异常: {e}")
        import traceback
        traceback.print_exc()
        import sys
        sys.exit(1)
