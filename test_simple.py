#!/usr/bin/env python3
"""
简单的游戏大厅同步测试 - ASCII输出，无Unicode
"""
import requests
import json

BASE_URL = 'http://localhost:5000'

print("=" * 50)
print("[TEST] Game Lobby Sync")
print("=" * 50)

# Step 1: Create game
print("\n[STEP 1] Player 1 creates game...")
create_resp = requests.post(
    f'{BASE_URL}/api/create-game',
    json={'player_name': 'Player1'},
)
create_data = create_resp.json()

if create_data.get('success'):
    game_id = create_data.get('game_id')
    player1_id = create_data.get('player_id')
    print(f"[OK] Game created")
    print(f"     Game ID: {game_id}")
    print(f"     Player 1 ID: {player1_id}")
else:
    print(f"[FAIL] {create_data}")
    exit(1)

# Step 2: Player 1 checks initial lobby
print("\n[STEP 2] Player 1 checks lobby...")
get1_resp = requests.get(f'{BASE_URL}/api/get-game/{game_id}', params={'player_id': player1_id})
get1_data = get1_resp.json()
players1_count = len(get1_data['game']['players']) if get1_data['success'] else 0
print(f"[OK] Lobby: {players1_count} players")

# Step 3: Player 2 joins
print("\n[STEP 3] Player 2 joins...")
join_resp = requests.post(
    f'{BASE_URL}/api/join-game',
    json={'game_id': game_id, 'player_name': 'Player2'},
)
join_data = join_resp.json()
if join_data.get('success'):
    player2_id = join_data.get('player_id')
    print(f"[OK] Player 2 joined: {player2_id}")
else:
    print(f"[FAIL] {join_data}")
    exit(1)

# Step 4: Player 1 checks lobby again
print("\n[STEP 4] Player 1 checks lobby again...")
get2_resp = requests.get(f'{BASE_URL}/api/get-game/{game_id}', params={'player_id': player1_id})
get2_data = get2_resp.json()
players2_count = len(get2_data['game']['players']) if get2_data['success'] else 0
players_list = [p['name'] for p in get2_data['game']['players'].values()] if get2_data['success'] else []
print(f"[OK] Lobby: {players2_count} players")
print(f"     Players: {players_list}")

# Verify result
if players2_count >= 2 and 'Player2' in players_list:
    print("\n[PASS] Lobby sync working! Player 1 sees Player 2.")
else:
    print("\n[FAIL] Lobby sync not working.")
    exit(1)

print("\n" + "=" * 50)
print("[DONE] Test completed successfully")
print("=" * 50)
