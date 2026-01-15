#!/usr/bin/env python3
"""
浏览器模拟测试 - 模拟两个浏览器标签页的行为
"""
import requests
import time
import threading

BASE_URL = 'http://localhost:5000'

def test_two_browser_tabs():
    """模拟两个浏览器标签页的游戏流程"""
    
    print("\n" + "=" * 70)
    print("浏览器标签页同步测试")
    print("=" * 70)
    
    # 结果容器
    results = {
        'tab1_sees_tab2': False,
        'final_count': 0
    }
    
    def tab1_create():
        """标签页1：创建游戏"""
        print("\n[标签页1] 创建游戏...")
        resp = requests.post(
            f'{BASE_URL}/api/create-game',
            json={'player_name': '玩家1'}
        )
        data = resp.json()
        
        if not data.get('success'):
            print("[标签页1] ❌ 创建失败")
            return None, None
        
        game_id = data.get('game_id')
        player1_id = data.get('player_id')
        
        print(f"[标签页1] ✅ 游戏已创建")
        print(f"[标签页1]    游戏ID: {game_id}")
        print(f"[标签页1]    玩家ID: {player1_id}")
        
        # 初始大厅检查
        print(f"[标签页1] 初始大厅检查...")
        resp = requests.get(
            f'{BASE_URL}/api/get-game/{game_id}',
            params={'player_id': player1_id}
        )
        data = resp.json()
        if data.get('success'):
            count = len(data['game']['players'])
            print(f"[标签页1]    玩家数量: {count}")
        
        # 保存信息供稍后使用
        return game_id, player1_id
    
    def tab2_join(game_id):
        """标签页2：加入游戏"""
        print("\n[标签页2] 加入游戏...")
        time.sleep(1)  # 模拟延迟
        
        resp = requests.post(
            f'{BASE_URL}/api/join-game',
            json={'game_id': game_id, 'player_name': '玩家2'}
        )
        data = resp.json()
        
        if not data.get('success'):
            print("[标签页2] ❌ 加入失败")
            return None
        
        player2_id = data.get('player_id')
        print(f"[标签页2] ✅ 已加入游戏")
        print(f"[标签页2]    玩家ID: {player2_id}")
        
        return player2_id
    
    def tab1_poll(game_id, player1_id):
        """标签页1：轮询大厅更新（模拟updateLobby）"""
        print(f"\n[标签页1] 开始轮询大厅状态...")
        
        for i in range(5):  # 轮询5次
            time.sleep(0.8)  # 每800ms轮询一次
            
            resp = requests.get(
                f'{BASE_URL}/api/get-game/{game_id}',
                params={'player_id': player1_id}
            )
            data = resp.json()
            
            if data.get('success'):
                count = len(data['game']['players'])
                players = [p['name'] for p in data['game']['players'].values()]
                print(f"[标签页1] [轮询{i+1}] 玩家数量: {count}, 玩家: {players}")
                
                results['final_count'] = count
                
                if count >= 2 and '玩家2' in players:
                    print(f"[标签页1] ✅ 检测到玩家2已加入！")
                    results['tab1_sees_tab2'] = True
                    break
    
    # 执行测试流程
    game_id, player1_id = tab1_create()
    if not game_id:
        print("\n[❌] 测试失败：无法创建游戏")
        return False
    
    # 在后台运行标签页1的轮询
    poll_thread = threading.Thread(target=tab1_poll, args=(game_id, player1_id))
    poll_thread.daemon = True
    poll_thread.start()
    
    # 标签页2加入（在轮询开始后）
    player2_id = tab2_join(game_id)
    if not player2_id:
        print("\n[❌] 测试失败：玩家2无法加入")
        return False
    
    # 等待轮询线程完成
    poll_thread.join(timeout=6)
    
    # 输出结果
    print("\n" + "=" * 70)
    print("测试结果")
    print("=" * 70)
    
    if results['tab1_sees_tab2']:
        print("✅ [PASS] 大厅同步成功！")
        print(f"         标签页1成功检测到玩家2加入")
        print(f"         最终玩家数量: {results['final_count']}")
        return True
    else:
        print("❌ [FAIL] 大厅同步失败")
        print(f"         标签页1未能检测到玩家2")
        print(f"         最终玩家数量: {results['final_count']}")
        return False

if __name__ == '__main__':
    try:
        success = test_two_browser_tabs()
        print("\n" + "=" * 70)
        if success:
            print("整体测试结果: ✅ 通过")
        else:
            print("整体测试结果: ❌ 失败")
        print("=" * 70)
        
        import sys
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[❌] 测试异常: {e}")
        import traceback
        traceback.print_exc()
        import sys
        sys.exit(1)
