#!/usr/bin/env python3
"""
测试跨标签页加入游戏
"""
import requests
import json

BASE_URL = 'http://localhost:5000'

print("=" * 60)
print("测试跨标签页加入游戏")
print("=" * 60)

# 步骤1: 标签页1 - 创建游戏
print("\n[步骤1] 标签页1创建游戏...")
resp1 = requests.post(f'{BASE_URL}/api/create-game', json={'player_name': 'Alice'})
data1 = resp1.json()

if data1.get('success'):
    game_id = data1.get('game_id')
    player1_id = data1.get('player_id')
    print(f"✅ 游戏创建成功")
    print(f"   游戏代码: {game_id}")
    print(f"   玩家1 ID: {player1_id}")
else:
    print(f"❌ 创建失败: {data1}")
    exit(1)

# 步骤2: 标签页2 - 使用游戏代码加入（模拟新标签页，使用新的session）
print(f"\n[步骤2] 标签页2使用游戏代码加入: {game_id}")

# 使用新的session模拟新标签页
session2 = requests.Session()
resp2 = session2.post(f'{BASE_URL}/api/join-game', json={
    'game_id': game_id,
    'player_name': 'Bob'
})
data2 = resp2.json()

if data2.get('success'):
    player2_id = data2.get('player_id')
    print(f"✅ 加入成功")
    print(f"   玩家2 ID: {player2_id}")
else:
    print(f"❌ 加入失败: {data2}")
    print(f"   错误信息: {data2.get('error')}")
    exit(1)

# 步骤3: 验证两个玩家都在游戏中
print("\n[步骤3] 验证玩家列表...")
resp3 = requests.get(f'{BASE_URL}/api/get-game/{game_id}', params={'player_id': player1_id})
data3 = resp3.json()

if data3.get('success'):
    players = data3['game']['players']
    player_count = len(players)
    player_names = [p['name'] for p in players.values()]
    print(f"✅ 游戏中有 {player_count} 个玩家")
    print(f"   玩家列表: {player_names}")
    
    if player_count == 2 and 'Bob' in player_names:
        print("\n" + "=" * 60)
        print("✅ 测试通过！跨标签页加入游戏功能正常")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ 测试失败！玩家数量或名单不对")
        print("=" * 60)
        exit(1)
else:
    print(f"❌ 获取游戏数据失败: {data3}")
    exit(1)
