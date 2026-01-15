#!/usr/bin/env python3
"""
完整的游戏流程测试 - 创建、加入、开始
"""
import requests
import json

BASE_URL = 'http://localhost:5000'

print("=" * 60)
print("[TEST] Complete Game Flow with Lobby Sync")
print("=" * 60)

# Step 1: Player 1 creates game
print("\n[STEP 1] Player 1 creates game with name...")
create_resp = requests.post(
    f'{BASE_URL}/api/create-game',
    json={'player_name': 'Alice'},
)
create_data = create_resp.json()

if create_data.get('success'):
    game_id = create_data.get('game_id')
    player1_id = create_data.get('player_id')
    print(f"[OK] Game created")
    print(f"     Game ID: {game_id}")
    print(f"     Player 1 (Alice) ID: {player1_id}")
else:
    print(f"[FAIL] {create_data}")
    exit(1)

# Step 2: Player 1 checks initial lobby
print("\n[STEP 2] Player 1 checks initial lobby...")
get1_resp = requests.get(f'{BASE_URL}/api/get-game/{game_id}', params={'player_id': player1_id})
get1_data = get1_resp.json()
if get1_data.get('success'):
    players = get1_data['game']['players']
    print(f"[OK] Lobby has {len(players)} player(s)")
    for pid, player in players.items():
        print(f"     - {player['name']}")
else:
    print(f"[FAIL] {get1_data}")
    exit(1)

# Step 3: Player 2 joins
print("\n[STEP 3] Player 2 (Bob) joins...")
join_resp = requests.post(
    f'{BASE_URL}/api/join-game',
    json={'game_id': game_id, 'player_name': 'Bob'},
)
join_data = join_resp.json()
if join_data.get('success'):
    player2_id = join_data.get('player_id')
    print(f"[OK] Player 2 (Bob) joined: {player2_id}")
else:
    print(f"[FAIL] {join_data}")
    exit(1)

# Step 4: Player 1 checks lobby (should see both players now)
print("\n[STEP 4] Player 1 checks lobby (should see Bob joined)...")
get2_resp = requests.get(f'{BASE_URL}/api/get-game/{game_id}', params={'player_id': player1_id})
get2_data = get2_resp.json()
if get2_data.get('success'):
    players = get2_data['game']['players']
    print(f"[OK] Lobby has {len(players)} player(s)")
    for pid, player in players.items():
        print(f"     - {player['name']}")
    
    if len(players) >= 2:
        print("[OK] Alice can see Bob joined!")
    else:
        print("[FAIL] Alice cannot see Bob")
        exit(1)
else:
    print(f"[FAIL] {get2_data}")
    exit(1)

# Step 5: Player 3 joins
print("\n[STEP 5] Player 3 (Charlie) joins...")
join3_resp = requests.post(
    f'{BASE_URL}/api/join-game',
    json={'game_id': game_id, 'player_name': 'Charlie'},
)
join3_data = join3_resp.json()
if join3_data.get('success'):
    player3_id = join3_data.get('player_id')
    print(f"[OK] Player 3 (Charlie) joined: {player3_id}")
else:
    print(f"[FAIL] {join3_data}")
    exit(1)

# Step 6: Check lobby has all 3 players
print("\n[STEP 6] Final lobby check...")
get3_resp = requests.get(f'{BASE_URL}/api/get-game/{game_id}', params={'player_id': player1_id})
get3_data = get3_resp.json()
if get3_data.get('success'):
    players = get3_data['game']['players']
    print(f"[OK] Lobby has {len(players)} player(s)")
    for pid, player in players.items():
        print(f"     - {player['name']}")
else:
    print(f"[FAIL] {get3_data}")
    exit(1)

# Step 7: Start game
print("\n[STEP 7] Start game...")
start_resp = requests.post(
    f'{BASE_URL}/api/start-game',
    json={'game_id': game_id, 'player_id': player1_id},
)
start_data = start_resp.json()
if start_data.get('success'):
    game_info = start_data.get('game', {})
    print(f"[OK] Game started")
    print(f"     Phase: {game_info.get('phase')}")
    print(f"     Current round: {game_info.get('current_round')}")
    print(f"     Drawer: {game_info.get('current_drawer')}")
else:
    print(f"[FAIL] {start_data}")
    exit(1)

print("\n" + "=" * 60)
print("[PASS] All tests completed successfully!")
print("=" * 60)
