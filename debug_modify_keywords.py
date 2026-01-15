#!/usr/bin/env python3
"""Debug: Check what modify-keywords endpoint returns"""

import requests
import json

BASE_URL = 'http://127.0.0.1:5000/api'

# Setup
resp = requests.post(f'{BASE_URL}/create-game', json={'player_name': 'Alice', 'language': 'zh'})
game_id = resp.json()['game_id']
alice_id = resp.json()['player_id']

resp = requests.post(f'{BASE_URL}/join-game', json={'game_id': game_id, 'player_name': 'Bob'})
bob_id = resp.json()['player_id']

requests.post(f'{BASE_URL}/start-game', json={'game_id': game_id, 'player_id': alice_id})

# Get drawer
resp = requests.get(f'{BASE_URL}/get-game/{game_id}?player_id={alice_id}')
drawer_id = resp.json()['game']['current_drawer']
drawer_name = "Alice" if drawer_id == alice_id else "Bob"

print(f"Game: {game_id}")
print(f"Drawer: {drawer_name} ({drawer_id})")

# Call modify keywords and check response
print("\nCalling modify-keywords endpoint...")
resp = requests.post(f'{BASE_URL}/submit-modified-keywords',
    json={'game_id': game_id, 'player_id': drawer_id, 'modified_keywords': ['火', '月', '鸟']})

print(f"Response status: {resp.status_code}")
print(f"Response JSON: {json.dumps(resp.json(), ensure_ascii=False, indent=2)}")
