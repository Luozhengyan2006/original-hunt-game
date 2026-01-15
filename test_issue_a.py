#!/usr/bin/env python3
"""Test Issue A specifically: Verify drawer sees correct waiting message in other_drawing phase"""

import requests
import json
import time

BASE_URL = 'http://127.0.0.1:5000/api'

def test_issue_a():
    print("\n" + "="*60)
    print("TEST: Issue A - Drawer waiting message in other_drawing phase")
    print("="*60)
    
    # Step 1: Create game (Alice is creator)
    print("\n1. Creating game as Alice...")
    resp = requests.post(f'{BASE_URL}/create-game', 
        json={'player_name': 'Alice', 'language': 'zh'})
    game_id = resp.json()['game_id']
    alice_id = resp.json()['player_id']
    print(f"✅ Game: {game_id}, Alice: {alice_id}")
    
    # Step 2: Add Bob and Charlie
    print("2. Adding Bob and Charlie...")
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
    
    # Get drawer and non-drawer info
    resp = requests.get(f'{BASE_URL}/get-game/{game_id}?player_id={alice_id}')
    drawer_id = resp.json()['game']['current_drawer']
    all_players = {'Alice': alice_id, 'Bob': bob_id, 'Charlie': charlie_id}
    drawer_name = [name for name, pid in all_players.items() if pid == drawer_id][0]
    non_drawers = [pid for name, pid in all_players.items() if pid != drawer_id]
    print(f"✅ Drawer: {drawer_name} ({drawer_id})")
    
    # Step 4: Drawer modifies keywords
    print(f"4. {drawer_name} modifying keywords...")
    requests.post(f'{BASE_URL}/submit-modified-keywords',
        json={'game_id': game_id, 'player_id': drawer_id, 'modified_keywords': ['火', '月', '鸟']})
    
    # Verify phase is other_drawing
    resp = requests.get(f'{BASE_URL}/get-game/{game_id}?player_id={drawer_id}')
    phase = resp.json()['game']['game_phase']
    is_drawer = resp.json()['game']['is_drawer']
    print(f"✅ Phase: {phase}, Drawer flag: {is_drawer}")
    
    # Step 5: Check what drawer sees
    print(f"\n5. Checking {drawer_name}'s view in other_drawing phase:")
    resp = requests.get(f'{BASE_URL}/get-game/{game_id}?player_id={drawer_id}')
    game_state = resp.json()['game']
    print(f"   Game phase: {game_state['game_phase']}")
    print(f"   Is drawer: {game_state['is_drawer']}")
    print(f"   Current drawer ID: {game_state['current_drawer']}")
    
    # Step 6: Non-drawers submit drawing
    print(f"\n6. Non-drawers submit drawings...")
    for pid in non_drawers:
        name = [n for n, p in all_players.items() if p == pid][0]
        print(f"   {name} submits drawing...")
        requests.post(f'{BASE_URL}/submit-drawing',
            json={'game_id': game_id, 'player_id': pid, 'drawing_data': 'test'})
        time.sleep(0.3)
        
        # Check phase after each submission
        resp = requests.get(f'{BASE_URL}/get-game/{game_id}?player_id={drawer_id}')
        current_phase = resp.json()['game']['game_phase']
        print(f"      Phase: {current_phase}")
    
    # Step 7: Drawer submits drawing
    print(f"\n7. {drawer_name} submits drawing...")
    resp = requests.post(f'{BASE_URL}/submit-drawing',
        json={'game_id': game_id, 'player_id': drawer_id, 'drawing_data': 'test'})
    new_phase = resp.json()['game']['game_phase']
    print(f"✅ Phase after drawer submission: {new_phase}")
    
    # Step 8: Final verification
    print(f"\n8. Final check - {drawer_name}'s view:")
    resp = requests.get(f'{BASE_URL}/get-game/{game_id}?player_id={drawer_id}')
    final_phase = resp.json()['game']['game_phase']
    final_is_drawer = resp.json()['game']['is_drawer']
    print(f"   Phase: {final_phase}")
    print(f"   Is drawer: {final_is_drawer}")
    
    if final_phase == 'guessing' and final_is_drawer:
        print("\n✅ ISSUE A: Drawer correctly in guessing phase")
        print("   Frontend should show waiting message for drawer during guessing")
    else:
        print(f"\n❌ Unexpected state: Phase={final_phase}, is_drawer={final_is_drawer}")

if __name__ == '__main__':
    test_issue_a()
