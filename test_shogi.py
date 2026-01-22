import shogi

def test_two_pawns():
    """二歩のテスト"""
    board = {}
    board[(5, 5)] = 'p'  # 先手の歩が5筋にある
    hands = {'sente': ['P'], 'gote': []}
    
    moves = shogi.get_all_legal_moves(board, hands, 'sente')
    # 5筋への歩打ちは不可
    assert ('drop', 'P', (4, 5)) not in moves
    # 他の筋への歩打ちは可
    assert ('drop', 'P', (4, 6)) in moves
    print("✓ 二歩チェック: OK")

def test_dead_drop():
    """行き所のない駒のテスト"""
    board = {}
    hands = {'sente': ['P', 'L', 'N'], 'gote': []}
    
    moves = shogi.get_all_legal_moves(board, hands, 'sente')
    # 歩を1段目に打てない
    assert ('drop', 'P', (1, 5)) not in moves
    # 香車を1段目に打てない
    assert ('drop', 'L', (1, 5)) not in moves
    # 桂馬を1-2段目に打てない
    assert ('drop', 'N', (1, 5)) not in moves
    assert ('drop', 'N', (2, 5)) not in moves
    # 3段目なら打てる
    assert ('drop', 'P', (3, 5)) in moves
    assert ('drop', 'N', (3, 5)) in moves
    print("✓ 行き所のない駒チェック: OK")

def test_self_check():
    """自殺手(自玉が王手になる手)のテスト"""
    board = {}
    board[(5, 5)] = 'k'  # 先手の王
    board[(5, 3)] = 'R'  # 後手の飛車(5筋を睨む)
    board[(5, 4)] = 'g'  # 先手の金(王を守っている)
    hands = {'sente': [], 'gote': []}
    
    moves = shogi.get_all_legal_moves(board, hands, 'sente')
    
    # 金の移動先候補を取得
    gold_possible_moves = shogi.get_legal_moves(board, 5, 4, 'sente')
    
    # 金が5筋から離れる手（王の守りを外す手）は不可能
    for to in gold_possible_moves:
        if to[1] != 5 and to != (5, 3):  # 5筋から離れ、かつ飛車を取らない手
            assert ('move', (5, 4), to) not in moves, f"金が{to}に動けてしまっています（王手になるはず）"
    
    print("✓ 自殺手チェック: OK")

def test_promotion():
    """成りのテスト"""
    board = {}
    board[(4, 5)] = 'p'  # 先手の歩
    hands = {'sente': [], 'gote': []}
    
    # 3段目に進む(敵陣に入る)
    new_board, _ = shogi.make_move(board, (4, 5), (3, 5), hands, turn='sente')
    # 自動的に成っている
    assert new_board[(3, 5)] == 'g'  # 金になっている
    assert new_board.get((4, 5)) is None
    print("✓ 自動成り: OK")

def test_check_detection():
    """王手判定のテスト"""
    board = {}
    board[(5, 5)] = 'k'  # 先手の王
    board[(5, 1)] = 'R'  # 後手の飛車
    hands = {'sente': [], 'gote': []}
    
    # 王手がかかっている
    assert shogi.is_check(board, 'sente') == True
    
    # 飛車を別の場所に置く
    del board[(5, 1)]  # 削除する（Noneを代入しない）
    board[(1, 1)] = 'R'
    assert shogi.is_check(board, 'sente') == False
    print("✓ 王手判定: OK")

def test_uchifuzume():
    """打ち歩詰めのテスト"""
    # 打ち歩詰めの典型的な形
    board = {}
    board[(1, 5)] = 'K'  # 後手の王（1段目の中央）
    board[(2, 4)] = 'g'  # 先手の金（左斜め前）
    board[(2, 6)] = 'g'  # 先手の金（右斜め前）
    board[(1, 4)] = 'g'  # 先手の金（左横）
    board[(1, 6)] = 'g'  # 先手の金（右横）
    # (2,5)に歩を打つと詰むが、これは打ち歩詰めなので禁止
    hands = {'sente': ['P'], 'gote': []}
    
    moves = shogi.get_all_legal_moves(board, hands, 'sente')
    # (2,5)に歩を打つ手があるかチェック
    drop_25 = ('drop', 'P', (2, 5)) in moves
    
    if drop_25:
        print(f"  警告: (2,5)への歩打ちが合法手になっています")
        # デバッグ: この手が打ち歩詰めか確認
        test_board, _ = shogi.drop_piece(board, hands, 'P', (2, 5), 'sente')
        print(f"  王手状態: {shogi.is_check(test_board, 'gote')}")
        gote_moves = shogi.get_all_legal_moves(test_board, {'sente': [], 'gote': []}, 'gote')
        print(f"  後手の合法手数: {len(gote_moves)}")
    
    # 打ち歩詰めなので不可
    assert ('drop', 'P', (2, 5)) not in moves, "打ち歩詰めが禁止されていません"
    print("✓ 打ち歩詰めチェック: OK")

def test_capture():
    """駒を取る動作のテスト"""
    board = {}
    board[(4, 5)] = 'p'  # 先手の歩（4段目）
    board[(3, 5)] = 'P'  # 後手の歩（3段目＝敵陣）
    hands = {'sente': [], 'gote': []}
    
    # 相手の歩を取る（敵陣に入るので成る）
    new_board, new_hands = shogi.make_move(board, (4, 5), (3, 5), hands, turn='sente')
    
    # 駒が移動している
    assert new_board.get((4, 5)) is None
    assert new_board[(3, 5)] == 'g'  # 敵陣なので成っている
    # 持ち駒に追加されている（demoteで反転されるので'p'になる）
    assert 'p' in new_hands['sente'], f"持ち駒が正しくありません: {new_hands['sente']}"
    print("✓ 駒取り&持ち駒: OK")

def test_checkmate():
    """詰み判定のテスト"""
    # 1. 詰んでいない状態（王手だが逃げられる）
    board = {}
    board[(5, 5)] = 'K'  # 後手の王
    board[(5, 1)] = 'r'  # 先手の飛車で王手
    hands = {'sente': [], 'gote': []}
    # 王手だが逃げられる
    assert shogi.is_check(board, 'gote') == True
    assert shogi.is_checkmate(board, hands, 'gote') == False
    
    # 2. 詰んでいる状態（頭金）
    board = {}
    board[(1, 5)] = 'K'  # 後手の王
    board[(2, 5)] = 'g'  # 先手の金で頭金
    # 両脇も塞ぐ
    board[(1, 4)] = 'g'  
    board[(1, 6)] = 'g'  
    hands = {'sente': [], 'gote': []}
    
    # この状態でも王が(2,4)や(2,6)に逃げられるので詰みではない
    # より確実な詰み形: 王を完全に囲む
    board = {}
    board[(9, 5)] = 'k'  # 先手の王（9段目＝後退できない）
    board[(8, 5)] = 'G'  # 後手の金で頭金
    board[(9, 4)] = 'G'  # 逃げ道を塞ぐ
    board[(9, 6)] = 'G'  # 逃げ道を塞ぐ
    board[(8, 4)] = 'G'  # 斜め前も塞ぐ
    board[(8, 6)] = 'G'  # 斜め前も塞ぐ
    hands = {'sente': [], 'gote': []}
    
    # 詰んでいる
    result = shogi.is_checkmate(board, hands, 'sente')
    if not result:
        # デバッグ: 合法手を確認
        legal = shogi.get_all_legal_moves(board, hands, 'sente')
        print(f"  デバッグ: 詰んでいないはずの合法手: {legal}")
    assert result == True, "詰み形が正しく判定されていません"
    
    # 3. 王手でない場合は詰みではない
    board = {}
    board[(5, 5)] = 'k'  
    hands = {'sente': [], 'gote': []}
    assert shogi.is_checkmate(board, hands, 'sente') == False
    
    print("✓ 詰み判定: OK")

def test_drop_piece():
    """駒を打つ基本機能のテスト"""
    board = {}
    board[(5, 5)] = 'k'  # 先手の王
    hands = {'sente': ['P', 'G'], 'gote': []}
    
    # 歩を打つ
    new_board, new_hands = shogi.drop_piece(board, hands, 'P', (4, 5), 'sente')
    assert new_board[(4, 5)] == 'p'  # 先手の駒は小文字
    assert 'P' not in new_hands['sente']  # 持ち駒から削除されている
    assert len(new_hands['sente']) == 1  # 金だけ残っている
    
    # 駒がある場所には打てない
    result_board, result_hands = shogi.drop_piece(new_board, new_hands, 'G', (5, 5), 'sente')
    assert result_board is None  # 失敗
    assert result_hands is None
    print("✓ 駒打ち機能: OK")

def test_promotion_edge_cases():
    """成りのエッジケースのテスト"""
    board = {}
    hands = {'sente': [], 'gote': []}
    
    # 敵陣内での移動でも成る
    board[(3, 5)] = 'p'
    new_board, _ = shogi.make_move(board, (3, 5), (2, 5), hands, turn='sente')
    assert new_board[(2, 5)] == 'g'  # 成っている
    
    # 敵陣から出る移動でも成る
    board = {}
    board[(3, 5)] = 'p'
    new_board, _ = shogi.make_move(board, (3, 5), (4, 5), hands, turn='sente')
    assert new_board[(4, 5)] == 'g'  # 成っている
    
    # 既に成っている駒は再度成らない
    board = {}
    board[(4, 5)] = 'g'  # 既に成り金
    new_board, _ = shogi.make_move(board, (4, 5), (3, 5), hands, turn='sente')
    assert new_board[(3, 5)] == 'g'  # そのまま金
    print("✓ 成りのエッジケース: OK")

def test_king_safety():
    """王が存在しない場合のエラーハンドリング"""
    board = {}
    board[(5, 5)] = 'p'  # 王がいない
    hands = {'sente': [], 'gote': []}
    
    # 王がいない場合、王手判定はFalse
    assert shogi.is_check(board, 'sente') == False
    print("✓ 王不在時の処理: OK")

def run_all_tests():
    print("=== 将棋ルールテスト開始 ===\n")
    test_two_pawns()
    test_dead_drop()
    test_self_check()
    test_promotion()
    test_promotion_edge_cases()
    test_check_detection()
    test_checkmate()
    test_uchifuzume()
    test_capture()
    test_drop_piece()
    test_king_safety()
    print("\n=== 全テスト完了 ===")

if __name__ == "__main__":
    run_all_tests()