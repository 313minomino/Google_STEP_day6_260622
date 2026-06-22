#!/usr/bin/env python3

import sys

from common import print_tour, read_input

def solve(cities:list) -> list:
    # Build a trivial solution.
    # Visit the cities in the order they appear in the input.

    #一番最初のノードを先に入れておく
    visited = {0}
    tour = [0]
    current = 0
    # 今まで通ったエッジを保持
    used_edges = []# (a,b)だったらa->bのエッジ 
    
    # 次のノードを見つけ、visitedとtourに追加する
    # 全てのノードを回るまで続ける
    while len(tour) < len(cities):
        #print("今は",current)
        # 次のノードを見つける
        next_node = bestscore_node(current, cities, visited, used_edges)

        #print(next_node,"に行く")
        # 次のノードをvisitedにいれて、currentにする
        used_edges.append((current, next_node))
        visited.add(next_node)
        tour.append(next_node)
        current = next_node

    # # 2-opt
    # improved = True
    # while improved:
    #     improved = two_opt(tour, cities)

    # # or-opt
    # improved = True
    # while improved:
    #     improved_tour = or_opt(tour, cities)
    #     if improved_tour == tour:
    #         break
    #     tour = improved_tour

    return tour


# 次のノードを見つける
def bestscore_node(current:int, cities:list, visited:set, used_edge:list) -> int:
    # 距離が近いノード10個を抽出
    candidates = []
    for i in range(len(cities)):
        # 訪問していなければ
        if i not in visited:
            # 二点間の距離を取得
            candidates.append((distance_calc(cities, current, i),i))
    candidates.sort()
    top_candidates = candidates[:10]

    # 距離が近いノードのスコアを確認
    best_score = float('inf')
    next_node = None
    for distance, j in top_candidates:
        # ペナルティを取得
        overlap_penalty = (calc_overlap_penalty(current,j,cities,used_edge))**1.5
        turn_penalty = calc_turn_penalty(current,j,cities,used_edge)

        # ペナルティの重みづけ
        progress = len(visited) / len(cities)
        OVERLAP_WEIGHT = 1 - 0.8 * progress
        TURN_WEIGHT    = 0.3 + 0.7 * progress
        # 距離による重みづけ
        if distance <= 50:
            distance_factor = 0.05
        elif distance <= 80:
            distance_factor = 0.3
        else:
            distance_factor = 1.0

        # スコアを計算
        # score = (distance/10) + distance_factor*(OVERLAP_WEIGHT * overlap_penalty + TURN_WEIGHT * turn_penalty)
        score = distance*(1+OVERLAP_WEIGHT * overlap_penalty + TURN_WEIGHT * turn_penalty)
        # print(j,"についてスコア",score,"：距離",distance/10,"重複",OVERLAP_WEIGHT * (overlap_penalty),"折り返し",TURN_WEIGHT * turn_penalty)

        # 探索した中で一番スコアが低いものを返す
        if score < best_score:
            best_score = score
            next_node = j
    return next_node

# 2点間の距離を求める
def distance_calc(cities:list,node1:int,node2:int) -> float:
    x1 = cities[node1][0]
    y1 = cities[node1][1]
    x2 = cities[node2][0]
    y2 = cities[node2][1]
    distance = ((x1 - x2)**2 + (y1 - y2)**2) ** 0.5
    return distance

# 「x軸とy軸への射影で、同じ区間を何度も通りたくない
# 新しい辺を追加するとき、その辺が今まで通った全ての辺と x軸・y軸上でどれだけ重複するかを計算し、その重複長が小さい候補を優先する」
# current → candidateという新しい辺が過去の全辺とどれだけ重複するか
def calc_overlap_penalty(current,candidate,cities,used_edges):
    new_edge = (current,candidate)# 今評価中の候補
    overlap_penalty = 0
    count = 0
    # 過去に通った部分を計算
    LOOK_BACK = 500
    for old_edge in used_edges[-LOOK_BACK:]:    
        x_overlap, y_overlap = edge_overlap(cities,new_edge,old_edge)
        overlap_penalty += x_overlap + y_overlap
        count += 1
    if count > 0:
        overlap_penalty /= count
    return overlap_penalty

# 2つのエッジをx軸とy軸に投射して、大小関係を明確にする。
def edge_overlap(cities:list, edge1:tuple,edge2:tuple):
    # エッジのノードを取り出す
    node1, node2 = edge1
    node3, node4 = edge2

    # ノードの座標を取り出す
    x1 = cities[node1][0]
    y1 = cities[node1][1]
    x2 = cities[node2][0]
    y2 = cities[node2][1]
    x3 = cities[node3][0]
    y3 = cities[node3][1]
    x4 = cities[node4][0]
    y4 = cities[node4][1]

    # エッジが通るノードのうちxやy軸上での大小関係を明確にする
    # overlap_lengthに(小,大)というtupleを送るための準備
    node1_x_interval = (min(x1, x2),max(x1, x2))
    node2_x_interval = (min(x3, x4),max(x3, x4))
    node1_y_interval = (min(y1, y2),max(y1, y2))
    node2_y_interval = (min(y3, y4),max(y3, y4))

    # z,y軸のそれぞれの重複を計算
    x_overlap = overlap_length(node1_x_interval, node2_x_interval)
    y_overlap = overlap_length(node1_y_interval, node2_y_interval)

    return x_overlap, y_overlap

# 2つのエッジの重複部分の長さを返す
    # eg)x軸の投射が(3,8)と、(5,10)の2本のエッジを比べた時
    # 3-----8
    #     5-----10
    # 重複部分は、
    # 5---8
    # なので、長さは「8-5=3」
def overlap_length(node1_interval, node2_interval) -> float:
    node1_left, node1_right = node1_interval
    node2_left, node2_right = node2_interval

    # 重複なし
    # 「1L---1R  2L---2R」のときと1,2が逆の時
    if node1_right <= node2_left or node2_right <= node1_left:
        return 0
    
    # 重複あり
    # 2つのエッジの一部が被っている。とか、包含しているとか
    else:
        sorted_x = sorted([node1_left, node1_right, node2_left, node2_right])
        return sorted_x[2] - sorted_x[1]

# 孤立に対するペナルティ（孤立しているとペナルティを下げる）
def future_cost_penalty(node:int, cities:list, visited:set) -> float:
    NEAE_DISTANCE = 100 #近いの定義
    near_count = 0

    for k in range(len(cities))
        if k not in visited and k != node:
            distance = distance_calc(cities, node, k)
            if distance <= NEAE_DISTANCE:
                near_count += 1

    if near_count == 0:
        return -500
    elif near_count <= 2:
        return -100
    elif near_count <= 3:
        return -50
    else:
        return 0

# 「前の辺」と「今から追加しようとしている辺」の向きが逆になっていたらペナルティにする
def calc_turn_penalty(current, candidate, cities, used_edges):
    
    # 最初のエッジの時は、ペナルティは0
    if len(used_edges) == 0:
        return 0
    
    # 直前のエッジを取り出す
    prev_from, prev_to = used_edges[-1]

    # 座標にする
    from_x, from_y = cities[prev_from]  #A
    to_x, to_y = cities[prev_to]        #B
    new_x, new_y = cities[candidate]    #c

    # 前回のエッジの移動方向 AB
    prev_dx = to_x - from_x
    prev_dy = to_y - from_y

    # 今回のエッジの移動方向 BC
    new_dx = new_x - to_x
    new_dy = new_y - to_y

    # ベクトルの大きさを計算
    prev_len = (prev_dx**2 + prev_dy**2)**0.5   #|AB| = √(dx² + dy²)
    new_len = (new_dx**2 + new_dy**2)**0.5      #|BC| = √(dx² + dy²)

    # 大きさが0だと割れないので、0の場合は0を返す
    if prev_len == 0 or new_len == 0:
        return 0
    
    # cosθを求める
    # 内積の公式「a・b = |a||b| cosθ」を用いる
    # cosθ が
        #   1 なら同じ方向（0°）
        #   0 なら直角（90°）
        #  -1 なら逆方向（180°）
    cos_theta = (prev_dx*new_dx + prev_dy*new_dy)/(prev_len*new_len)

    # cos_theta = max(-1,min(1,cos_theta))

    # 向きが変わるほど大きなペナルティを与える
        # 0°   → 0
        # 90°  → 500
        # 180° → 1000
    return 200 * (1-cos_theta)
    

    # penalty = 0
    # #ペナルティの計算
    # if prev_dx * new_dx < 0:
    #     penalty += min(abs(prev_dx),abs(new_dx))  
    # if prev_dy * new_dy < 0:
    #     penalty += min(abs(prev_dy),abs(new_dy))

    # return penalty       

# 2-opt
def two_opt(tour:list,cities:list) -> list:
    improved = False
    # エッジを1つ取り出す
    for i in range(len(tour)):
        current1 = tour[i]
        if i == len(tour) - 1:
            next1 = tour[0]
        else:
            next1 = tour[i+1]

        # 比較したいエッジを取り出す
        for j in range(i + 2, len(tour)):
            current2 = tour[j]
            if j == len(tour) - 1:
                next2 = tour[0]
            else:
                next2 = tour[j+1]
                
            # 2つのエッジの現在の距離の合計を計算
            old_distance = distance(cities,current1,next1) + distance(cities,current2,next2)
            # 4つの点を組み替えた時の距離の合計を計算
            new_distance = distance(cities,current1,current2) + distance(cities,next1,next2)
            # もし新たな距離の方が良ければ変更する
            if old_distance > new_distance:
                # print("変更",i,"と",j)
                tour[i+1:j+1] = tour[i+1:j+1][::-1]
                improved = True
    return improved

# or-opt
def or_opt(tour:list, cities:list) -> list:
    improved = False

    # 切り取る区間を決める
    for size in [1,2,3]:
        for i in range(len(tour)-size+1):
            section_candidate = tour[i:i+size]# 切り取る部分
            tour_candidate = tour[:i] + tour[i+size:]# 残りの部分

            if len(tour_candidate) == 0:
                continue

            # 切り取る部分
            first = tour[i]
            last = tour[i + size -1]
            # 切り取る部分の前後
            prev = tour[i - 1]
            next = tour[(i + size) % len(tour)]

            # 切り取った部分 (section_candidate) を tour_candidate のどこに挿入するか。0なら先頭。
            for j in range(len(tour_candidate)):
                # 挿入場所
                insert_prev = tour_candidate[j - 1]
                insert_next = tour_candidate[j]

                # 変更前の距離
                old_distance = distance(cities, prev, first) + distance(cities, last, next) + distance(cities, insert_prev, insert_next)
                # 変更する候補の距離
                new_distance = distance(cities, prev, next) + distance(cities, insert_prev, first) + distance(cities, last, insert_next)

                if new_distance < old_distance:
                    return tour_candidate[:j] + section_candidate + tour_candidate[j:]
    return tour

def tour_distance(tour:list, cities:list) -> int:
    total = 0
    for i in range(len(tour)):
        node1 = tour[i]
        node2 = tour[(i+1) % len(tour)]# 最後のノードの時は次が0になる。

        total += distance(cities, node1, node2)
    return total



    
if __name__ == '__main__':
    assert len(sys.argv) > 1
    tour = solve(read_input(sys.argv[1]))
    print_tour(tour)
