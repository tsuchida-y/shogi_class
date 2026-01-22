# ============================================================
# 将棋AIミニプロジェクト 完成版
# フェーズ1〜4 統合
# ============================================================

BOARD_SIZE = 9

# ============================================================
# 定数定義：駒の表示
# ============================================================
# 駒の内部表現（アルファベット）と画面表示（漢字）の対応表
# 大文字 = 後手の駒、小文字 = 先手の駒
# 理由: 大文字・小文字で先手/後手を区別することで、駒の所有者を簡単に判定できる
PIECES = {
    'K': '玉', 'k': '王',  # 王将・玉将
    'R': '飛', 'r': '龍',  # 飛車・龍王（成り飛車）
    'B': '角', 'b': '馬',  # 角行・龍馬（成り角）
    'G': '金', 'g': '金',  # 金将
    'S': '銀', 's': '銀',  # 銀将
    'N': '桂', 'n': '桂',  # 桂馬
    'L': '香', 'l': '香',  # 香車
    'P': '歩', 'p': '歩'   # 歩兵
}


# ============================================================
# 定数定義：駒の移動パターン
# ============================================================
# 各駒が1手で移動できる方向を(段の変化, 筋の変化)のリストで定義
# 段: 1(後手側)→9(先手側), 筋: 1(右)→9(左)
# 理由: 各駒の動きを統一的に扱うことで、移動可能位置の計算を簡潔にできる
MOVES = {
    # 王・玉（全方向に1マスずつ移動可能）
    'k': [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)],
    'K': [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)],

    # 金将（斜め後ろ以外の6方向）
    'g': [(-1,0),(0,-1),(0,1),(1,0),(-1,-1),(-1,1)],  # 先手の金（上が前方）
    'G': [(1,0),(0,-1),(0,1),(-1,0),(1,-1),(1,1)],    # 後手の金（下が前方）

    # 銀将（斜め4方向と真正面）
    's': [(-1,0),(-1,-1),(-1,1),(1,-1),(1,1)],  # 先手の銀
    'S': [(1,0),(1,-1),(1,1),(-1,-1),(-1,1)],   # 後手の銀

    # 桂馬（前方に2マス進んで左右1マスずれた位置）
    'n': [(-2,-1),(-2,1)],  # 先手の桂
    'N': [(2,-1),(2,1)],    # 後手の桂

    # 歩兵（前方に1マスのみ）
    'p': [(-1,0)],  # 先手の歩
    'P': [(1,0)],   # 後手の歩
}

# ============================================================
# 定数定義：成りのルール
# ============================================================
# 成ることができる駒のリスト
# 理由: 王・金以外の駒は成ることができるというルールを明示的に管理
PROMOTABLE_PIECES = ['P','L','N','S','R','B','p','l','n','s','r','b']

# 成り後の駒への変換マップ
# 理由: 成った後の駒の種類を辞書で管理することで、変換処理を簡潔にできる
PROMOTION_MAP = {
    'P':'G','L':'G','N':'G','S':'G',  # 後手: 歩・香・桂・銀 → 金
    'p':'g','l':'g','n':'g','s':'g',  # 先手: 歩・香・桂・銀 → 金
    'R':'r','B':'b'                   # 飛車→龍王、角行→龍馬
}

# ============================================================
# 定数定義：駒の価値（AI評価用）
# ============================================================
# 各駒の相対的な強さを点数で表現（E1-E5: 基本評価）
# 理由: AIが局面を数値評価するために、各駒に価値を設定
#       成り駒は元の駒より価値が高い
PIECE_VALUES = {
    'K':1000000,'k':1000000,  # 王: 取られたら負けなので非常に高い値
    'R':1000,'r':1300,         # 飛車・龍王: 最も強力な駒
    'B':800,'b':1000,          # 角行・龍馬
    'G':600,'g':600,           # 金将
    'S':500,'s':500,           # 銀将
    'N':300,'n':300,           # 桂馬
    'L':200,'l':200,           # 香車
    'P':100,'p':100            # 歩兵
}

# ============================================================
# 基本ユーティリティ関数
# ============================================================

def is_sente(p):
    """
    駒が先手のものかを判定
    
    Args:
        p: 駒の文字コード（例: 'p', 'K'）
    
    Returns:
        bool: 先手の駒ならTrue、後手ならFalse
    
    実装の理由:
        小文字=先手という規則を利用して、簡潔に判定できる
    """
    return p.islower()

def is_gote(p):
    """
    駒が後手のものかを判定
    
    Args:
        p: 駒の文字コード（例: 'p', 'K'）
    
    Returns:
        bool: 後手の駒ならTrue、先手ならFalse
    
    実装の理由:
        大文字=後手という規則を利用して、簡潔に判定できる
    """
    return p.isupper()

def is_valid(r, f):
    """
    座標が盤面内（1-9の範囲）かをチェック
    
    Args:
        r: 段（1-9）
        f: 筋（1-9）
    
    Returns:
        bool: 座標が有効ならTrue
    
    実装の理由:
        盤外への移動を防ぐために、すべての座標操作でこの関数を使用
    """
    return 1 <= r <= 9 and 1 <= f <= 9

def get_piece(board, r, f):
    """
    指定位置の駒を取得
    
    Args:
        board: 盤面の辞書
        r: 段
        f: 筋
    
    Returns:
        駒の文字コード、または空きマスならNone
    
    実装の理由:
        辞書のget()メソッドを使うことで、存在しないキーでもエラーにならない
    """
    return board.get((r, f))

# ============================================================
# 盤面の初期化
# ============================================================

def create_initial_board():
    """
    将棋の初期配置を作成
    
    Returns:
        dict: {(段, 筋): '駒'} の形式の辞書
    
    実装の理由:
        辞書を使うことで、空きマスをNoneで表現する必要がなく、
        メモリ効率が良い。また、座標から駒を高速に検索できる。
    """
    b={}
    # 後手の駒配置（1-3段）
    b[(1,9)]='L'; b[(1,8)]='N'; b[(1,7)]='S'; b[(1,6)]='G'
    b[(1,5)]='K'; b[(1,4)]='G'; b[(1,3)]='S'; b[(1,2)]='N'; b[(1,1)]='L'
    b[(2,8)]='R'; b[(2,2)]='B'
    for f in range(1,10): b[(3,f)]='P'

    # 先手の駒配置（7-9段）
    b[(9,9)]='l'; b[(9,8)]='n'; b[(9,7)]='s'; b[(9,6)]='g'
    b[(9,5)]='k'; b[(9,4)]='g'; b[(9,3)]='s'; b[(9,2)]='n'; b[(9,1)]='l'
    b[(8,2)]='r'; b[(8,8)]='b'
    for f in range(1,10): b[(7,f)]='p'
    return b

def create_empty_hands():
    """
    持ち駒を管理する辞書を初期化
    
    Returns:
        dict: {'sente': [駒のリスト], 'gote': [駒のリスト]}
    
    実装の理由:
        取った駒を打つ機能を実装するため、各プレイヤーの持ち駒を
        リストで管理する。同じ駒を複数持てるのでリストが適切。
    """
    return {'sente':[], 'gote':[]}

# ============================================================
# 合法手生成（基本移動）
# ============================================================

def get_legal_moves(board, r, f, turn):
    """
    指定位置の駒が移動できるマス目のリストを生成
    
    Args:
        board: 盤面
        r: 駒の現在位置の段
        f: 駒の現在位置の筋
        turn: 'sente' または 'gote'
    
    Returns:
        list: 移動可能な座標のリスト [(段, 筋), ...]
    
    実装の理由:
        - MOVESの定義を使って基本移動を計算
        - 飛車・角・香車は長距離移動なので別処理
        - 味方の駒がいる場所や盤外には移動できない
    """
    moves=[]
    p=get_piece(board,r,f)
    if not p: return moves
    
    # 手番と駒の所有者が一致しない場合は空リストを返す
    if (turn=='sente' and not is_sente(p)) or (turn=='gote' and is_sente(p)):
        return moves

    # 基本移動（王、金、銀、桂、歩）
    if p in MOVES:
        for dr,df in MOVES[p]:
            nr,nf=r+dr,f+df
            if is_valid(nr,nf):
                t=get_piece(board,nr,nf)
                # 移動先が空きマス、または相手の駒がある場合のみ移動可能
                if not t or is_sente(t)!=is_sente(p):
                    moves.append((nr,nf))

    # 長距離移動（飛車・角・香車）
    # 理由: これらの駒は障害物にぶつかるまで直線的に移動できる
    if p.lower() in ['r','b','l']:
        dirs=[]
        if p.lower()=='r': dirs=[(-1,0),(1,0),(0,-1),(0,1)]  # 飛車: 縦横4方向
        if p.lower()=='b': dirs=[(-1,-1),(-1,1),(1,-1),(1,1)]  # 角: 斜め4方向
        if p.lower()=='l': dirs=[(-1,0)] if p.islower() else [(1,0)]  # 香車: 前方のみ
        
        for dr,df in dirs:
            nr,nf=r,f
            while True:
                nr+=dr; nf+=df
                if not is_valid(nr,nf): break  # 盤外に出たら終了
                t=get_piece(board,nr,nf)
                if t:
                    # 駒がある場合、相手の駒なら取れるのでリストに追加して終了
                    if is_sente(t)!=is_sente(p): moves.append((nr,nf))
                    break
                moves.append((nr,nf))
    return moves

# ============================================================
# 駒の成り処理
# ============================================================

def demote(p):
    """
    取った駒を持ち駒用に変換（成りを解除）
    
    Args:
        p: 駒の文字コード
    
    Returns:
        str: 反転した駒（大文字↔小文字）
    
    実装の理由:
        取った駒は成りが解除され、相手の持ち駒として使われる。
        大文字↔小文字を反転させることで、所有者を変更できる。
    """
    return p.lower() if p.isupper() else p.upper()

def can_promote(piece, frm, to, turn):
    """
    駒が成れる条件を満たしているかを判定
    
    Args:
        piece: 駒の文字コード
        frm: 移動元の座標 (段, 筋)
        to: 移動先の座標 (段, 筋)
        turn: 'sente' または 'gote'
    
    Returns:
        bool: 成れる条件を満たしていればTrue
    
    実装の理由:
        将棋のルールでは、敵陣(先手なら1-3段、後手なら7-9段)に
        入るか、敵陣から出る移動で成ることができる。
        このシステムでは条件を満たせば自動的に成る仕様。
    """
    if piece not in PROMOTABLE_PIECES:
        return False
    
    frm_r, _ = frm
    to_r, _ = to
    
    if turn == 'sente':
        # 先手: 1-3段が敵陣
        return frm_r <= 3 or to_r <= 3
    else:
        # 後手: 7-9段が敵陣
        return frm_r >= 7 or to_r >= 7

# ============================================================
# 盤面操作：駒の移動と打つ
# ============================================================
    
def make_move(board, frm, to, hands, promote=False, turn='sente'):
    """
    駒を移動させ、新しい盤面と持ち駒を返す（P3: 駒の移動）
    
    Args:
        board: 現在の盤面
        frm: 移動元の座標 (段, 筋)
        to: 移動先の座標 (段, 筋)
        hands: 持ち駒
        promote: 成るかどうか（現在は未使用、自動成り）
        turn: 'sente' または 'gote'
    
    Returns:
        tuple: (新しい盤面, 新しい持ち駒) または (None, None)
    
    実装の理由:
        - イミュータブル設計: 元の盤面を変更せず、新しい盤面を作成
          これによりミニマックス探索で元の盤面を保持できる
        - 相手の駒を取った場合、自動的に持ち駒に追加
        - 敵陣への出入りで自動的に成る
    """
    # エラーチェック: 移動元に駒があるか
    if frm not in board:
        return None, None
    
    # 盤面と持ち駒のコピーを作成（元のデータを変更しない）
    b=board.copy()
    h={'sente':hands['sente'][:],'gote':hands['gote'][:]}
    
    # 移動元から駒を取り出す
    p=b.pop(frm)

    # 相手の駒を取る場合、持ち駒に追加
    if to in b:
        captured = b.pop(to)
        h[turn].append(demote(captured))  # 成りを解除して持ち駒に
    
    # 自動成り: 成れる条件を満たしていれば必ず成る
    if can_promote(p, frm, to, turn):
        p=PROMOTION_MAP[p]

    # 新しい位置に駒を配置
    b[to]=p
    return b,h

def drop_piece(board, hands, piece, to, turn):
    """
    持ち駒を盤上に打つ（P3: 持ち駒を打つロジック）
    
    Args:
        board: 現在の盤面
        hands: 持ち駒
        piece: 打つ駒の文字コード（大文字）
        to: 打つ場所の座標 (段, 筋)
        turn: 'sente' または 'gote'
    
    Returns:
        tuple: (新しい盤面, 新しい持ち駒) または (None, None)
    
    実装の理由:
        - 持ち駒システムは将棋の特徴的なルール
        - 打つ駒は成っていない状態で配置される
        - 持ち駒から削除し、盤上に配置する
    """
    # エラーチェック: 持ち駒があるか、打つ場所が空きマスか
    if piece not in hands[turn] or get_piece(board,*to): 
        return None,None
    
    # コピーを作成
    b=board.copy()
    h={'sente':hands['sente'][:],'gote':hands['gote'][:]}
    
    # 盤上に配置（先手なら小文字、後手なら大文字）
    b[to]=piece.lower() if turn=='sente' else piece.upper()
    
    # 持ち駒から削除
    h[turn].remove(piece)
    
    return b,h

# ============================================================
# 王手判定（P4: 王手判定機能）
# ============================================================

def find_king(board, turn):
    """
    指定した側の王の位置を探す
    
    Args:
        board: 盤面
        turn: 'sente' または 'gote'
    
    Returns:
        tuple: 王の座標 (段, 筋) またはNone
    
    実装の理由:
        王手判定や詰み判定で王の位置が必要なため
    """
    k='k' if turn=='sente' else 'K'
    for pos,p in board.items():
        if p==k: return pos

def is_check(board, turn):
    """
    王手がかかっているか判定（P4: 王手判定機能）
    
    Args:
        board: 盤面
        turn: 'sente' または 'gote'（チェックされる側）
    
    Returns:
        bool: 王手がかかっていればTrue
    
    実装の理由:
        相手の全駒の移動可能位置に自分の王があるかをチェック。
        これにより王手状態を判定できる。
    """
    kp=find_king(board,turn)
    if not kp:
        return False
    
    opp='gote' if turn=='sente' else 'sente'
    
    # 相手の全駒について、その駒が王を取れるかチェック
    for (r,f),p in board.items():
        if (opp=='sente' and is_sente(p)) or (opp=='gote' and is_gote(p)):
            if kp in get_legal_moves(board,r,f,opp):
                return True
    return False

# ============================================================
# 特殊ルールの実装（P5: 特殊ルールによる制限）
# ============================================================

def is_safe(board, hands, move, turn):
    """
    P5-①: その手を指した後に自玉が王手にならないかチェック
    
    Args:
        board: 現在の盤面
        hands: 持ち駒
        move: ('move', 元, 先) または ('drop', 駒, 位置)
        turn: 'sente' または 'gote'
    
    Returns:
        bool: 安全な手（王手にならない）ならTrue
    
    実装の理由:
        将棋では自分の王が取られる手は指せない。
        仮想的に手を指してみて、王手状態にならないかを確認。
    """
    if move[0]=='move':
        b,_=make_move(board,move[1],move[2],hands,turn=turn)
    else:
        b,_=drop_piece(board,hands,move[1],move[2],turn)
    
    # 盤面が正しく生成されたかチェック
    if b is None:
        return False
    
    # 自分の王が王手状態でないことを確認
    return not is_check(b,turn)

def has_pawn_on_file(board, f, turn):
    """
    P5-②: 二歩禁止ルール（同じ筋に既に歩があるかチェック）
    
    Args:
        board: 盤面
        f: 筋（1-9）
        turn: 'sente' または 'gote'
    
    Returns:
        bool: 同じ筋に既に歩があればTrue
    
    実装の理由:
        将棋では同じ筋に自分の歩を2つ配置できない。
        歩を打つ前にこのチェックが必要。
    """
    pawn='p' if turn=='sente' else 'P'
    return any(ff==f and p==pawn for (rr,ff),p in board.items())

def is_uchifuzume(board, hands, pos, turn):
    """
    P5-③: 打ち歩詰め禁止ルール
    
    Args:
        board: 盤面
        hands: 持ち駒
        pos: 歩を打つ位置 (段, 筋)
        turn: 'sente' または 'gote'
    
    Returns:
        bool: 打ち歩詰めならTrue（禁止）
    
    実装の理由:
        歩を打って相手の王を詰ませる手は禁止（ただし歩を動かして
        詰ませるのは可）。これは将棋独特のルール。
        判定方法: 
        1. 歩を打った後に相手が王手状態
        2. 相手に逃げる手がない（詰み）
        この2つを満たす場合が打ち歩詰め
    """
    piece = 'P' if turn == 'sente' else 'p'  # 持ち駒の表記
    
    # 持ち駒に歩がなければ打ち歩詰めではない
    if piece not in hands[turn]:
        return False
    
    # 歩を打った後の盤面を作成
    test_board, test_hands = drop_piece(board, hands, piece, pos, turn)
    if not test_board:
        return False
    
    opp = 'gote' if turn == 'sente' else 'sente'
    
    # 1. 王手がかかっていなければ打ち歩詰めではない
    if not is_check(test_board, opp):
        return False
    
    # 2. 相手が合法手を持っている(詰んでいない)なら打ち歩詰めではない
    opp_moves = []
    for (r,f), p in test_board.items():
        if (opp == 'sente' and is_sente(p)) or (opp == 'gote' and is_gote(p)):
            for to in get_legal_moves(test_board, r, f, opp):
                m = ('move', (r,f), to)
                # 相手の手を指した後、相手の王が安全かチェック
                if m[0] == 'move':
                    b2, _ = make_move(test_board, m[1], m[2], test_hands, turn=opp)
                    if b2 and not is_check(b2, opp):
                        opp_moves.append(m)
    
    # 3. 相手に逃げ道がない(詰み)で、かつ打った駒が歩なら打ち歩詰め
    if len(opp_moves) == 0:
        return True
    
    return False

def is_dead_drop(piece, r, turn):
    """
    P5-④: 行き所のない駒の禁止（動けない位置への駒打ち）
    
    Args:
        piece: 打つ駒の文字コード
        r: 打つ位置の段
        turn: 'sente' または 'gote'
    
    Returns:
        bool: 行き所のない打ち方ならTrue（禁止）
    
    実装の理由:
        歩・香車を1段目（後退できない場所）に打つことや、
        桂馬を動けない位置に打つことは禁止。
    """
    if piece.lower() in ['p','l']:
        # 歩・香車: 先手なら1段目、後手なら9段目に打てない
        return r==1 if turn=='sente' else r==9
    if piece.lower()=='n':
        # 桂馬: 先手なら1-2段目、後手なら8-9段目に打てない
        return r<=2 if turn=='sente' else r>=8
    return False


# ============================================================
# 全合法手の生成
# ============================================================

def get_all_legal_moves(board, hands, turn):
    """
    すべての合法手を生成（盤上の駒の移動 + 持ち駒を打つ手）
    
    Args:
        board: 盤面
        hands: 持ち駒
        turn: 'sente' または 'gote'
    
    Returns:
        list: 合法手のリスト [('move', 元, 先), ('drop', 駒, 位置), ...]
    
    実装の理由:
        AIが次の手を選ぶためには、すべての合法手を知る必要がある。
        特殊ルール（王手回避、二歩、打ち歩詰め等）でフィルタリング。
    """
    moves=[]
    
    # 1. 盤上の駒を動かす手
    for (r,f),p in board.items():
        if (turn=='sente' and is_sente(p)) or (turn=='gote' and is_gote(p)):
            for to in get_legal_moves(board,r,f,turn):
                m=('move',(r,f),to)
                # 自殺手（自玉が王手になる手）は除外
                if is_safe(board,hands,m,turn): 
                    moves.append(m)

    # 2. 持ち駒を打つ手
    for piece in hands[turn]:
        for r in range(1,10):
            for f in range(1,10):
                # 駒がある場所には打てない
                if get_piece(board,r,f): continue
                
                # P5-②: 二歩チェック
                if piece.lower()=='p' and has_pawn_on_file(board,f,turn): continue
                
                # P5-④: 行き所のない駒チェック
                if is_dead_drop(piece,r,turn): continue

                # P5-③: 打ち歩詰めチェック
                if piece.lower() == 'p' and is_uchifuzume(board, hands, (r,f), turn):
                    continue

                m=('drop',piece,(r,f))
                # 自殺手チェック
                if is_safe(board,hands,m,turn): 
                    moves.append(m)
    
    return moves

# ============================================================
# AI評価関数（E1-E7: 局面の良し悪しを数値化）
# ============================================================

def evaluate_board(board, turn):
    """
    盤面の評価値を計算（AIが局面を判断するための数値）
    
    Args:
        board: 盤面
        turn: 'sente' または 'gote'（評価する側）
    
    Returns:
        int: 評価値（正の値が有利、負の値が不利）
    
    実装の理由:
        AIが「どちらが有利か」を判断するために、盤面を数値化する。
        複数の要素を組み合わせて総合評価する。
    """
    score=0
    
    # E1-E5: 基本的な駒の価値
    # 理由: 駒の数と質が局面評価の基本。強い駒を多く持つほど有利。
    for p in board.values():
        v=PIECE_VALUES[p]
        score+=v if (turn=='sente' and is_sente(p)) or (turn=='gote' and is_gote(p)) else -v
    
    # E6: 玉の安全度（自玉の周囲8マスが攻撃されているかをチェック）
    # 理由: 王が危険な状態は大きなマイナス。守りの評価を追加。
    king_pos = find_king(board, turn)
    if king_pos:
        safety_bonus = 0
        for dr, df in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]:
            nr, nf = king_pos[0] + dr, king_pos[1] + df
            if is_valid(nr, nf):
                piece = get_piece(board, nr, nf)
                # 自分の駒で守られている場合ボーナス
                if piece and ((turn == 'sente' and is_sente(piece)) or (turn == 'gote' and is_gote(piece))):
                    safety_bonus += 10
                
                # 相手の駒に攻撃されている場合ペナルティ
                opp = 'gote' if turn == 'sente' else 'sente'
                for (r,f), p in board.items():
                    if (opp == 'sente' and is_sente(p)) or (opp == 'gote' and is_gote(p)):
                        if (nr, nf) in get_legal_moves(board, r, f, opp):
                            safety_bonus -= 15
                            break
        score += safety_bonus
    
    # E7: 駒の働き（相手陣への近さと中央配置のボーナス）
    # 理由: 攻撃的な配置を評価。敵陣に近い駒や中央の駒は活躍しやすい。
    for (r, f), p in board.items():
        if (turn == 'sente' and is_sente(p)) or (turn == 'gote' and is_gote(p)):
            # 相手陣に近いほどボーナス（玉以外）
            if p.lower() != 'k':
                if turn == 'sente':
                    # 先手は1段に近いほど良い
                    score += (10 - r) * 2
                else:
                    # 後手は9段に近いほど良い
                    score += (r - 0) * 2
            
            # 中央（5筋付近）にいる駒にボーナス
            # 理由: 中央の駒は左右どちらにも動きやすく、活用しやすい
            center_bonus = max(0, 3 - abs(f - 5))
            score += center_bonus * 5
    
    return score

# ============================================================
# AIアルゴリズム（A1-A3: ミニマックス法+αβ枝刈り）
# ============================================================

def minimax(board, hands, depth, alpha, beta, maxi, turn):
    """
    ミニマックス法+αβ枝刈りで最善手を探索（A1, A3）
    
    Args:
        board: 盤面
        hands: 持ち駒
        depth: 探索する深さ（残り手数）
        alpha: αβ枝刈り用のα値
        beta: αβ枝刈り用のβ値
        maxi: True=最大化プレイヤー、False=最小化プレイヤー
        turn: 'sente' または 'gote'
    
    Returns:
        tuple: (評価値, 最善手)
    
    実装の理由:
        ミニマックス法: 自分は最善を尽くし、相手も最善を尽くすと仮定して
                       最適な手を見つけるアルゴリズム
        αβ枝刈り: 探索の無駄を省き、より深く読めるようにする最適化技術
                  これにより約√b倍の効率化（bは平均合法手数）
    """
    # 終端条件: 深さ0で評価値を返す
    if depth==0:
        return evaluate_board(board,turn),None
    
    # 合法手を生成
    moves=get_all_legal_moves(board,hands,turn)
    if not moves:
        # 合法手がない場合、詰みまたはステイルメイト
        return (-1000000 if maxi else 1000000),None

    opp='gote' if turn=='sente' else 'sente'
    best=None

    # 最大化プレイヤー（自分のターン）
    if maxi:
        val=-1e9
        for m in moves:
            # 手を実行して新しい盤面を作成
            nb,nh = make_move(board,m[1],m[2],hands,turn=turn) if m[0]=='move' else drop_piece(board,hands,m[1],m[2],turn)
            # 再帰的に評価
            s,_=minimax(nb,nh,depth-1,alpha,beta,False,opp)
            if s>val: val,best=s,m
            
            # αβ枝刈り
            alpha=max(alpha,s)
            if beta<=alpha: 
                break  # これ以上探索しても無駄（相手がより良い手を選ぶため）
        return val,best
    
    # 最小化プレイヤー（相手のターン）
    else:
        val=1e9
        for m in moves:
            nb,nh = make_move(board,m[1],m[2],hands,turn=turn) if m[0]=='move' else drop_piece(board,hands,m[1],m[2],turn)
            s,_=minimax(nb,nh,depth-1,alpha,beta,True,opp)
            if s<val: val,best=s,m
            
            # αβ枝刈り
            beta=min(beta,s)
            if beta<=alpha: 
                break  # これ以上探索しても無駄
        return val,best

def ai_choose_move(board, hands, turn, depth=3):
    """
    AIが指す手を決定（A2: 探索深さの設定）
    
    Args:
        board: 盤面
        hands: 持ち駒
        turn: 'sente' または 'gote'
        depth: 探索する深さ（デフォルト3手先）
    
    Returns:
        最善手 ('move', 元, 先) または ('drop', 駒, 位置)
    
    実装の理由:
        depth=3は3手先まで読むことを意味する。
        深くするほど強くなるが、計算時間が指数関数的に増加する。
    """
    _,move=minimax(board,hands,depth,-1e9,1e9,True,turn)
    return move

# ============================================================
# ゲーム終了判定（T3: 詰み判定）
# ============================================================

def is_checkmate(board, hands, turn):
    """
    詰みの判定（T3: 手番・状態管理）
    
    Args:
        board: 盤面
        hands: 持ち駒
        turn: 'sente' または 'gote'（詰まされる側）
    
    Returns:
        bool: 詰んでいればTrue
    
    実装の理由:
        詰み = 王手状態 + 逃げる手がない
        これでゲーム終了を判定できる。
    """
    # 王手がかかっていない場合、詰みではない
    if not is_check(board, turn):
        return False
    
    # 合法手が一つもなければ詰み
    return len(get_all_legal_moves(board, hands, turn)) == 0

# ============================================================
# ユーザーインターフェース（表示・入力）
# ============================================================

def format_hands(hands, turn):
    """
    持ち駒を「金×2 歩」のような形式で整形
    
    Args:
        hands: 持ち駒
        turn: 'sente' または 'gote'
    
    Returns:
        str: 整形された持ち駒の文字列
    
    実装の理由:
        同じ駒が複数ある場合は「×個数」で表示し、見やすくする。
    """
    if not hands[turn]:
        return "なし"

    result = {}
    for p in hands[turn]:
        result[p] = result.get(p, 0) + 1

    return " ".join(
        f"{PIECES[p]}×{c}" if c > 1 else f"{PIECES[p]}"
        for p, c in result.items()
    )

def print_board(board, hands=None):
    """
    盤面と持ち駒を画面に表示（T2: 対局メインループ）
    
    Args:
        board: 盤面
        hands: 持ち駒（省略可）
    
    実装の理由:
        - 視覚的にわかりやすい盤面表示
        - 先手の駒を青色にすることで、どちらの駒か一目でわかる
        - 持ち駒も併せて表示し、局面全体を把握できる
    """
    BLUE  = "\033[34m"
    RESET = "\033[0m"
    
    print("    ９８７６５４３２１")
    print("   +-----------------+")
    for r in range(1,10):
        row=f"{r}段|"
        for f in range(9,0,-1):
            piece = board.get((r, f))
            kanji = PIECES.get(piece, '・')

            if piece and piece.islower():
                # 先手（自分）の駒を青色にする
                row += f"{BLUE}{kanji}{RESET}"
            else:
                # 後手の駒 or 空マス
                row += kanji
        print(row+"|")
    print("   +-----------------+")

    if hands is not None:
        print(f"{BLUE}先手の持ち駒:{RESET} {format_hands(hands, 'sente')}")
        print(f"後手の持ち駒: {format_hands(hands, 'gote')}")
    print()

def parse_input(s):
    """
    ユーザー入力を解析（T4: ユーザー入力インターフェース）
    
    Args:
        s: 入力文字列
           "move 7 7 7 6" → 7七の駒を7六に移動
           "drop P 5 5" → 歩を5五に打つ
    
    Returns:
        tuple: ('move', 元, 先) または ('drop', 駒, 位置)
    
    実装の理由:
        文字列を解析して、プログラムが理解できる形式に変換する。
    """
    p=s.split()
    if p[0]=='move': 
        return ('move',(int(p[1]),int(p[2])),(int(p[3]),int(p[4])))
    if p[0]=='drop': 
        return ('drop',p[1],(int(p[2]),int(p[3])))

# ============================================================
# メインゲームループ（T2: 対局メインループ）
# ============================================================

def play_game():
    """
    対局を実行するメイン関数
    
    実装の理由:
        1. 初期盤面と持ち駒を作成
        2. ループで交互に手を指す
           - 先手(プレイヤー): 入力を受け取り実行
           - 後手(AI): 思考して最善手を実行
        3. 詰みまたは合法手なしで終了
        
        このループ構造により、対局が自然に進行する。
    """
    board=create_initial_board()
    hands=create_empty_hands()
    turn='sente'
    print("あなたは先手です(下)")
    
    while True:
        print_board(board, hands)
        
        # T3: 詰みチェック
        if is_checkmate(board, hands, turn):
            winner = '後手(AI)' if turn == 'sente' else '先手(あなた)'
            print(f"\n{'='*40}")
            print(f"  詰み！ {winner}の勝ちです！")
            print(f"{'='*40}\n")
            break
        
        # 先手のターン（人間プレイヤー）
        if turn=='sente':
            legal=get_all_legal_moves(board,hands,turn)
            if not legal:
                print(f"\n{'='*40}")
                print("  合法手がありません。後手の勝ちです。")
                print(f"{'='*40}\n")
                break
            
            # 合法手が入力されるまで繰り返す
            while True:
                m=parse_input(input("> "))
                if m in legal: break
                print("不正な手")
            
            # 手を実行
            board,hands = make_move(board,m[1],m[2],hands,turn=turn) if m[0]=='move' else drop_piece(board,hands,m[1],m[2],turn)
        
        # 後手のターン（AIプレイヤー）
        else:
            print("AI思考中...")
            m=ai_choose_move(board,hands,turn)
            if not m:
                print(f"\n{'='*40}")
                print("  AIに指せる手がありません。先手の勝ちです。")
                print(f"{'='*40}\n")
                break
            print("AI:",m)
            
            # 手を実行
            board,hands = make_move(board,m[1],m[2],hands,turn=turn) if m[0]=='move' else drop_piece(board,hands,m[1],m[2],turn)
        
        # 手番交代
        turn='gote' if turn=='sente' else 'sente'


if __name__=="__main__":
    play_game()
