#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试游戏大厅同步 - 模拟两个玩家的操作
"""
import requests
import json
import time
import sys
import io

# 设置UTF-8输出
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

BASE_URL = 'http://localhost:5000'

def test_lobby_sync():
    """测试两个玩家在大厅中的同步"""
    
    print("=" * 50)
    print("游戏大厅同步测试")
    print("=" * 50)
    
    # 第一步: 玩家1创建游戏
    print("\n[步骤1] 玩家1创建游戏...")
    create_response = requests.post(
        f'{BASE_URL}/api/create-game',
        json={'player_name': '玩家1'},
        headers={'Content-Type': 'application/json'}
    )
    
    if not create_response.ok:
        print(f"❌ 创建游戏失败: {create_response.status_code}")
        print(create_response.text)
        return False
    
    create_data = create_response.json()
    if not create_data.get('success'):
        print(f"❌ 创建游戏失败: {create_data.get('error')}")
        return False
    
    game_id = create_data.get('game_id')
    player1_id = create_data.get('player_id')
    
    print(f"✅ 游戏已创建")
    print(f"   游戏代码: {game_id}")
    print(f"   玩家1 ID: {player1_id}")
    
    # 第二步: 玩家1检查初始大厅状态
    print("\n[步骤2] 玩家1检查初始大厅状态...")
    lobby_response1 = requests.get(
        f'{BASE_URL}/api/get-game/{game_id}',
        params={'player_id': player1_id}
    )
    
    lobby_data1 = lobby_response1.json()
    if lobby_data1['success']:
        players_count = len(lobby_data1['game']['players'])
        print(f"✅ 大厅状态: {players_count} 个玩家")
        print(f"   玩家列表: {list(lobby_data1['game']['players'].values())}")
    
    # 第三步: 玩家2加入游戏
    print("\n[步骤3] 玩家2加入游戏...")
    time.sleep(0.5)
    
    join_response = requests.post(
        f'{BASE_URL}/api/join-game',
        json={
            'game_id': game_id,
            'player_name': '玩家2'
        },
        headers={'Content-Type': 'application/json'}
    )
    
    if not join_response.ok:
        print(f"❌ 玩家2加入失败: {join_response.status_code}")
        print(join_response.text)
        return False
    
    join_data = join_response.json()
    if not join_data.get('success'):
        print(f"❌ 玩家2加入失败: {join_data.get('error')}")
        return False
    
    player2_id = join_data.get('player_id')
    print(f"✅ 玩家2已加入")
    print(f"   玩家2 ID: {player2_id}")
    
    # 第四步: 玩家1立即检查大厅状态（应该能看到玩家2）
    print("\n[步骤4] 玩家1立即检查大厅状态...")
    time.sleep(0.2)
    
    lobby_response2 = requests.get(
        f'{BASE_URL}/api/get-game/{game_id}',
        params={'player_id': player1_id}
    )
    
    lobby_data2 = lobby_response2.json()
    if lobby_data2['success']:
        players_count = len(lobby_data2['game']['players'])
        players_list = [p['name'] for p in lobby_data2['game']['players'].values()]
        print(f"✅ 大厅状态: {players_count} 个玩家")
        print(f"   玩家列表: {players_list}")
        
        if players_count >= 2:
            print(f"✅ 成功！玩家1能看到玩家2已加入")
        else:
            print(f"❌ 失败！玩家1看不到玩家2，只看到 {players_count} 个玩家")
            return False
    else:
        print(f"❌ 获取大厅状态失败: {lobby_data2.get('error')}")
        return False
    
    # 第五步: 玩家2检查大厅状态
    print("\n[步骤5] 玩家2检查大厅状态...")
    
    lobby_response3 = requests.get(
        f'{BASE_URL}/api/get-game/{game_id}',
        params={'player_id': player2_id}
    )
    
    lobby_data3 = lobby_response3.json()
    if lobby_data3['success']:
        players_count = len(lobby_data3['game']['players'])
        players_list = [p['name'] for p in lobby_data3['game']['players'].values()]
        print(f"✅ 大厅状态: {players_count} 个玩家")
        print(f"   玩家列表: {players_list}")
    else:
        print(f"❌ 获取大厅状态失败: {lobby_data3.get('error')}")
        return False
    
    # 第六步: 尝试开始游戏
    print("\n[步骤6] 开始游戏...")
    start_response = requests.post(
        f'{BASE_URL}/api/start-game',
        json={
            'game_id': game_id,
            'player_id': player1_id
        },
        headers={'Content-Type': 'application/json'}
    )
    
    start_data = start_response.json()
    if start_data.get('success'):
        print(f"✅ 游戏已开始")
        game_info = start_data.get('game', {})
        print(f"   当前阶段: {game_info.get('phase')}")
        print(f"   绘图者: {game_info.get('current_drawer')}")
    else:
        print(f"⚠️ 开始游戏失败: {start_data.get('error')}")
    
    print("\n" + "=" * 50)
    print("测试完成！")
    print("=" * 50)
    
    return True

if __name__ == '__main__':
    try:
        success = test_lobby_sync()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
