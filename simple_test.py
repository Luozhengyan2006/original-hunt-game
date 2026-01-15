#!/usr/bin/env python3
import requests
BASE_URL = 'http://127.0.0.1:5000/api'

try:
    # 创建游戏
    resp = requests.post(f'{BASE_URL}/create-game', json={'player_name': 'Alice', 'language': 'zh'})
    game_id = resp.json()['game_id']
    alice_id = resp.json()['player_id']
    print(f'✓ Created game {game_id}')

    # 添加玩家
    resp = requests.post(f'{BASE_URL}/join-game', json={'game_id': game_id, 'player_name': 'Bob'})
    bob_id = resp.json()['player_id']
    print(f'✓ Added Bob')

    # 启动游戏
    resp = requests.post(f'{BASE_URL}/start-game', json={'game_id': game_id, 'player_id': alice_id})
    print(f'✓ Started game')

    # 获取初始状态
    resp = requests.get(f'{BASE_URL}/get-game/{game_id}?player_id={alice_id}')
    game = resp.json()['game']
    drawer = game['current_drawer']
    print(f'✓ Drawer: {drawer}')
    print(f'  Game phase: {game["game_phase"]}')

    # 出题者修改关键词
    resp = requests.post(f'{BASE_URL}/submit-modified-keywords', json={
        'game_id': game_id, 
        'player_id': drawer, 
        'modified_keywords': ['火', '月', '鸟']
    })
    print(f'✓ Modified keywords')

    # 所有玩家提交绘画
    non_drawer = alice_id if alice_id != drawer else bob_id
    resp = requests.post(f'{BASE_URL}/submit-drawing', json={
        'game_id': game_id, 
        'player_id': non_drawer, 
        'drawing_data': 'test'
    })
    resp = requests.post(f'{BASE_URL}/submit-drawing', json={
        'game_id': game_id, 
        'player_id': drawer, 
        'drawing_data': 'test'
    })
    print(f'✓ Submitted drawings')

    # 所有玩家提交猜测
    resp = requests.post(f'{BASE_URL}/submit-guess', json={
        'game_id': game_id, 
        'player_id': non_drawer, 
        'guess_drawing_id': drawer
    })
    print(f'✓ Submitted guesses')

    # 检查阶段
    resp = requests.get(f'{BASE_URL}/get-game/{game_id}?player_id={alice_id}')
    game = resp.json()['game']
    print(f'✓ Phase before next: {game["game_phase"]}')

    # 进入下一轮
    resp = requests.post(f'{BASE_URL}/next-round', json={'game_id': game_id, 'player_id': alice_id})
    print(f'✓ Next round called')
    game = resp.json()['game']
    print(f'  New phase: {game["game_phase"]}')
    print(f'  New round: {game["current_round"]}')
    print(f'  New drawer: {game["current_drawer"]}')

    # 检查Bob的视图
    resp = requests.get(f'{BASE_URL}/get-game/{game_id}?player_id={bob_id}')
    game = resp.json()['game']
    print(f'✓ Bob view: phase={game["game_phase"]}, is_drawer={game["is_drawer"]}')
    
except Exception as e:
    print(f'ERROR: {e}')
    import traceback
    traceback.print_exc()
