#!/usr/bin/env python3
"""
测试：快速重复创建游戏，检查是否会有重复玩家
模拟用户快速点击"创建游戏"按钮
"""
import requests
import concurrent.futures
import time

BASE_URL = 'http://localhost:5000'

print("=" * 70)
print("测试：防止重复点击导致重复玩家")
print("=" * 70)

# 测试1：快速连续调用create-game
print("\n[测试1] 快速连续调用 /api/create-game...")

def create_game_request(name):
    try:
        resp = requests.post(
            f'{BASE_URL}/api/create-game',
            json={'player_name': name}
        )
        data = resp.json()
        return {
            'success': data.get('success'),
            'game_id': data.get('game_id'),
            'player_id': data.get('player_id'),
            'name': name
        }
    except Exception as e:
        return {'success': False, 'error': str(e), 'name': name}

# 并发调用（模拟快速点击）
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
    futures = [
        executor.submit(create_game_request, '玩家1'),
        executor.submit(create_game_request, '玩家1'),
        executor.submit(create_game_request, '玩家1'),
    ]
    results = [f.result() for f in concurrent.futures.as_completed(futures)]

print(f"发出3个create-game请求（相同名字）")
print(f"结果:")

game_ids = set()
for r in results:
    if r['success']:
        game_ids.add(r['game_id'])
        print(f"  ✅ 游戏ID: {r['game_id']}, 玩家ID: {r['player_id']}")
    else:
        print(f"  ❌ 失败: {r.get('error')}")

if len(game_ids) == 3:
    print(f"\n✅ 正确: 生成了3个不同的游戏")
else:
    print(f"\n⚠️  生成了 {len(game_ids)} 个游戏")

# 测试2：尝试在同一游戏中add空名字的玩家
print("\n" + "-" * 70)
print("[测试2] 尝试用空名字创建游戏...")

resp = requests.post(
    f'{BASE_URL}/api/create-game',
    json={'player_name': ''}  # 空名字
)
data = resp.json()

if not data.get('success'):
    print(f"✅ 正确: 被拒绝，错误信息: {data.get('error')}")
else:
    print(f"❌ 问题: 接受了空名字")

# 测试3：尝试用空名字加入游戏
print("\n" + "-" * 70)
print("[测试3] 尝试用空名字加入游戏...")

# 先创建一个游戏
create_resp = requests.post(
    f'{BASE_URL}/api/create-game',
    json={'player_name': '创建者'}
)
game_id = create_resp.json().get('game_id')

# 尝试用空名字加入
join_resp = requests.post(
    f'{BASE_URL}/api/join-game',
    json={'game_id': game_id, 'player_name': ''}  # 空名字
)
join_data = join_resp.json()

if not join_data.get('success'):
    print(f"✅ 正确: 被拒绝，错误信息: {join_data.get('error')}")
else:
    print(f"❌ 问题: 接受了空名字")

# 验证游戏中只有创建者
check_resp = requests.get(
    f'{BASE_URL}/api/get-game/{game_id}',
    params={'player_id': create_resp.json().get('player_id')}
)
check_data = check_resp.json()
player_count = len(check_data['game']['players'])

if player_count == 1:
    print(f"✅ 正确: 游戏中只有1个玩家")
else:
    print(f"❌ 问题: 游戏中有 {player_count} 个玩家")

print("\n" + "=" * 70)
