#!/usr/bin/env python3
"""
调试版本：直接测试各个步骤
"""
import requests
import json

BASE_URL = 'http://localhost:5000'

# 创建游戏
print("创建游戏...")
create_resp = requests.post(
    f'{BASE_URL}/api/create-game',
    json={'player_name': '玩家1'}
)
print(f"状态码: {create_resp.status_code}")
print(f"响应: {create_resp.text}")
create_data = create_resp.json()

if not create_data.get('success'):
    print("创建失败")
    exit(1)

game_id = create_data.get('game_id')
player1_id = create_data.get('player_id')

print(f"游戏ID: {game_id}")
print(f"玩家1 ID: {player1_id}")
print()

# 加入游戏
print("玩家2加入...")
join_resp = requests.post(
    f'{BASE_URL}/api/join-game',
    json={'game_id': game_id, 'player_name': '玩家2'}
)
print(f"状态码: {join_resp.status_code}")
print(f"响应: {join_resp.text}")
join_data = join_resp.json()

if not join_data.get('success'):
    print(f"加入失败: {join_data.get('error')}")
    exit(1)

player2_id = join_data.get('player_id')
print(f"玩家2 ID: {player2_id}")
print()

# 获取游戏状态
print("检查游戏状态...")
get_resp = requests.get(
    f'{BASE_URL}/api/get-game/{game_id}',
    params={'player_id': player1_id}
)
print(f"状态码: {get_resp.status_code}")
get_data = get_resp.json()

if get_data.get('success'):
    print(f"游戏状态: {get_data['game'].get('status')}")
    print(f"玩家数: {len(get_data['game']['players'])}")
else:
    print(f"失败: {get_data.get('error')}")
print()

# 开始游戏
print("开始游戏...")
start_resp = requests.post(
    f'{BASE_URL}/api/start-game',
    json={'game_id': game_id, 'player_id': player1_id}
)
print(f"状态码: {start_resp.status_code}")
print(f"响应: {start_resp.text}")
start_data = start_resp.json()

if start_data.get('success'):
    print(f"游戏已开始")
    print(f"出题者: {start_data['game'].get('current_drawer')}")
else:
    print(f"失败: {start_data.get('error')}")
