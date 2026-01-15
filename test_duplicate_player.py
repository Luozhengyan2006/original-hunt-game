#!/usr/bin/env python3
"""
测试创建游戏时的玩家列表
"""
import requests
import json

BASE_URL = 'http://localhost:5000'

print("创建游戏...")
create_resp = requests.post(
    f'{BASE_URL}/api/create-game',
    json={'player_name': '张三'}
)
create_data = create_resp.json()

if not create_data.get('success'):
    print("创建失败")
    exit(1)

game_id = create_data.get('game_id')
player_id = create_data.get('player_id')

print(f"游戏ID: {game_id}")
print(f"玩家ID: {player_id}")
print()

# 获取游戏状态
print("获取游戏状态...")
get_resp = requests.get(
    f'{BASE_URL}/api/get-game/{game_id}',
    params={'player_id': player_id}
)
get_data = get_resp.json()

if get_data.get('success'):
    game = get_data['game']
    players = game.get('players', {})
    
    print(f"玩家总数: {len(players)}")
    print(f"玩家列表:")
    for pid, player_info in players.items():
        print(f"  - {player_info['name']} (ID: {pid})")
    
    # 检查是否有重复
    names = [p['name'] for p in players.values()]
    if len(names) != len(set(names)):
        print("\n⚠️ 发现重复的玩家名称！")
        print(f"玩家名称: {names}")
    else:
        print("\n✅ 没有重复的玩家")
else:
    print(f"获取失败: {get_data.get('error')}")
