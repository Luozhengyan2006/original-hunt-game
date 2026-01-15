#!/usr/bin/env python3
"""Test next round: Verify correct waiting messages in next round"""

import requests
import json
import time

BASE_URL = 'http://127.0.0.1:5000/api'

def test_next_round():
    print("\n" + "="*60)
    print("TEST: Next Round - Verify correct waiting messages")
    print("="*60)
    
    # Step 1: Create game
    print("\n1. Creating game...")
    resp = requests.post(f'{BASE_URL}/create-game', 
        json={'player_name': 'Alice', 'language': 'zh'})
    game_id = resp.json()['game_id']
    alice_id = resp.json()['player_id']
    print(f"✅ Game: {game_id}, Alice: {alice_id}")
    
    # Step 2: Add players
    print("2. Adding players...")
    resp = requests.post(f'{BASE_URL}/join-game',
        json={'game_id': game_id, 'player_name': 'Bob'})
    bob_id = resp.json()['player_id']
    resp = requests.post(f'{BASE_URL}/join-game',
        json={'game_id': game_id, 'player_name': 'Charlie'})
    charlie_id = resp.json()['player_id']
    print(f"✅ Bob: {bob_id}, Charlie: {charlie_id}")
    
    # Step 3: Start game
    print("3. Starting game...")
    requests.post(f'{BASE_URL}/start-game',
        json={'game_id': game_id, 'player_id': alice_id})
    
    # Get drawer
    resp = requests.get(f'{BASE_URL}/get-game/{game_id}?player_id={alice_id}')
    drawer_id = resp.json()['game']['current_drawer']
    all_players = {'Alice': alice_id, 'Bob': bob_id, 'Charlie': charlie_id}
    drawer_name = [name for name, pid in all_players.items() if pid == drawer_id][0]
    non_drawers = [pid for name, pid in all_players.items() if pid != drawer_id]
    print(f"✅ Drawer: {drawer_name} ({drawer_id})")
    
    # Complete first round
    print("\n4. Completing first round...")
    
    # Drawer modifies keywords
    requests.post(f'{BASE_URL}/submit-modified-keywords',
        json={'game_id': game_id, 'player_id': drawer_id, 'modified_keywords': ['火', '月', '鸟']})
    
    # All players submit drawings
    for pid in non_drawers:
        requests.post(f'{BASE_URL}/submit-drawing',
            json={'game_id': game_id, 'player_id': pid, 'drawing_data': 'test'})
        time.sleep(0.1)
    requests.post(f'{BASE_URL}/submit-drawing',
        json={'game_id': game_id, 'player_id': drawer_id, 'drawing_data': 'test'})
    
    # All players submit guesses
    for pid in non_drawers:
        requests.post(f'{BASE_URL}/submit-guess',
            json={'game_id': game_id, 'player_id': pid, 'guess_drawing_id': drawer_id})
        time.sleep(0.1)
    
    print("✅ First round completed")
    
    # Step 5: Move to next round
    print("\n5. Moving to next round...")
    resp = requests.post(f'{BASE_URL}/next-round',
        json={'game_id': game_id, 'player_id': alice_id})
    game_data = resp.json()['game']
    print(f"✅ Next round started")
    print(f"   Current round: {game_data['current_round']}")
    print(f"   Current phase: {game_data['game_phase']}")
    print(f"   New drawer: {game_data['current_drawer']}")
    
    # Step 6: Check each player's view
    print("\n6. Checking each player's correct messages in next round:")
    
    for name, pid in all_players.items():
        resp = requests.get(f'{BASE_URL}/get-game/{game_id}?player_id={pid}')
        game_state = resp.json()['game']
        is_drawer = game_state['is_drawer']
        phase = game_state['game_phase']
        
        print(f"\n   {name}:")
        print(f"      Phase: {phase}")
        print(f"      Is drawer: {is_drawer}")
        
        if phase == 'keywords_modified':
            if is_drawer:
                print(f"      ✅ Should see: '修改关键词' page (modify keywords)")
            else:
                print(f"      ✅ Should see: '等待出题者修改关键词...' message (waiting for drawer)")
        elif phase == 'other_drawing':
            if is_drawer:
                print(f"      ✅ Should see: '等待其他玩家绘画和猜测...' message")
            else:
                print(f"      ✅ Should see: Drawing page")
    
    # Verify round 2 started properly
    resp = requests.get(f'{BASE_URL}/get-game/{game_id}?player_id={alice_id}')
    game_state = resp.json()['game']
    
    if game_state['game_phase'] == 'keywords_modified' and game_state['current_round'] == 2:
        print("\n✅ NEXT ROUND TEST PASSED: Round 2 started correctly!")
    else:
        print(f"\n❌ NEXT ROUND TEST FAILED: Phase={game_state['game_phase']}, Round={game_state['current_round']}")

if __name__ == '__main__':
    test_next_round()
