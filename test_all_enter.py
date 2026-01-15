#!/usr/bin/env python3
"""
测试所有玩家能否进入游戏
模拟：创建游戏 -> 多个玩家加入 -> 一个玩家开始游戏 -> 其他玩家自动转移
"""
import requests
import time
import threading

BASE_URL = 'http://localhost:5000'

def test_all_players_enter_game():
    """测试所有玩家都能进入游戏"""
    
    print("\n" + "=" * 70)
    print("[TEST] 所有玩家能否进入游戏")
    print("=" * 70)
    
    results = {
        'game_id': None,
        'players': {},
        'game_started': False,
        'all_entered': False
    }
    
    # Step 1: 创建游戏
    print("\n[1] 玩家A创建游戏...")
    create_resp = requests.post(
        f'{BASE_URL}/api/create-game',
        json={'player_name': '玩家A'}
    )
    create_data = create_resp.json()
    
    if not create_data.get('success'):
        print("[FAIL] 创建游戏失败")
        return False
    
    game_id = create_data.get('game_id')
    playerA_id = create_data.get('player_id')
    results['game_id'] = game_id
    results['players']['A'] = playerA_id
    
    print(f"[OK] 游戏已创建: {game_id}")
    print(f"[OK] 玩家A ID: {playerA_id}")
    
    # Step 2: 玩家B、C加入
    print("\n[2] 玩家B、C加入游戏...")
    for name, key in [('玩家B', 'B'), ('玩家C', 'C')]:
        join_resp = requests.post(
            f'{BASE_URL}/api/join-game',
            json={'game_id': game_id, 'player_name': name}
        )
        join_data = join_resp.json()
        if join_data.get('success'):
            player_id = join_data.get('player_id')
            results['players'][key] = player_id
            print(f"[OK] {name} 已加入: {player_id}")
        else:
            print(f"[FAIL] {name} 加入失败: {join_data}")
            return False
    
    # Step 3: 玩家A开始游戏
    print("\n[3] 玩家A开始游戏...")
    start_resp = requests.post(
        f'{BASE_URL}/api/start-game',
        json={'game_id': game_id, 'player_id': playerA_id}
    )
    start_data = start_resp.json()
    
    if not start_data.get('success'):
        print(f"[FAIL] 开始游戏失败: {start_data.get('error')}")
        return False
    
    print(f"[OK] 游戏已开始")
    print(f"[OK] 当前阶段: {start_data['game'].get('game_phase')}")
    print(f"[OK] 出题者: {start_data['game'].get('current_drawer')}")
    
    results['game_started'] = True
    
    # Step 4: 检查游戏状态 - 验证所有玩家都能看到游戏已开始
    print("\n[4] 验证所有玩家都能进入游戏...")
    
    all_entered = True
    for player_key, player_id in results['players'].items():
        get_resp = requests.get(
            f'{BASE_URL}/api/get-game/{game_id}',
            params={'player_id': player_id}
        )
        get_data = get_resp.json()
        
        if get_data.get('success'):
            status = get_data['game'].get('status')
            phase = get_data['game'].get('game_phase')
            print(f"[OK] 玩家{player_key} - 状态: {status}, 阶段: {phase}")
            
            if status != 'playing':
                all_entered = False
                print(f"[FAIL] 玩家{player_key}还未进入游戏（status={status}）")
        else:
            all_entered = False
            print(f"[FAIL] 无法获取玩家{player_key}的游戏状态")
    
    results['all_entered'] = all_entered
    
    # Output results
    print("\n" + "=" * 70)
    if all_entered and results['game_started']:
        print("✅ [PASS] 所有玩家都能进入游戏!")
        return True
    else:
        print("❌ [FAIL] 不是所有玩家都能进入游戏")
        return False

if __name__ == '__main__':
    try:
        success = test_all_players_enter_game()
        print("=" * 70)
        import sys
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[FAIL] 测试异常: {e}")
        import traceback
        traceback.print_exc()
        import sys
        sys.exit(1)
