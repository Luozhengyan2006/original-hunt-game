#!/usr/bin/env python3
"""
详细测试创建游戏流程 - 跟踪所有步骤
"""
import requests
import json

BASE_URL = 'http://localhost:5000'

print("=" * 70)
print("详细追踪创建游戏流程")
print("=" * 70)

# 步骤1：创建游戏
print("\n[步骤1] 发送创建游戏请求...")
print("请求: POST /api/create-game")
print("数据: {player_name: '创建者', language: 'zh'}")

create_resp = requests.post(
    f'{BASE_URL}/api/create-game',
    json={'player_name': '创建者', 'language': 'zh'}
)

print(f"\n响应状态: {create_resp.status_code}")
create_data = create_resp.json()
print("响应内容:")
print(json.dumps(create_data, indent=2, ensure_ascii=False))

if not create_data.get('success'):
    print("\n❌ 创建失败")
    exit(1)

game_id = create_data.get('game_id')
player_id = create_data.get('player_id')

# 步骤2：立即获取游戏状态（模拟前端updateLobby）
print("\n" + "-" * 70)
print("[步骤2] 创建后立即获取游戏状态...")
print(f"请求: GET /api/get-game/{game_id}?player_id={player_id}")

get_resp = requests.get(
    f'{BASE_URL}/api/get-game/{game_id}',
    params={'player_id': player_id}
)

print(f"\n响应状态: {get_resp.status_code}")
get_data = get_resp.json()

if get_data.get('success'):
    game = get_data['game']
    players = game.get('players', {})
    
    print(f"游戏ID: {game_id}")
    print(f"玩家总数: {len(players)}")
    print(f"玩家ID (创建者玩家ID): {player_id}")
    print(f"\n玩家列表:")
    
    for idx, (pid, player_info) in enumerate(players.items(), 1):
        is_creator = " [创建者]" if pid == player_id else ""
        print(f"  {idx}. {player_info['name']} (ID: {pid}){is_creator}")
    
    print(f"\n分析:")
    if len(players) == 1:
        print("✅ 正确: 只有1个玩家（创建者）")
    elif len(players) == 2:
        # 检查是否是重复
        player_list = list(players.values())
        if player_list[0]['name'] == player_list[1]['name']:
            print("❌ 问题: 发现2个玩家但名称相同（重复）")
        else:
            print("⚠️  发现2个不同的玩家（不应该发生）")
    else:
        print(f"❌ 问题: 玩家数不对（{len(players)}）")
        
else:
    print(f"❌ 获取失败: {get_data.get('error')}")

print("\n" + "=" * 70)
