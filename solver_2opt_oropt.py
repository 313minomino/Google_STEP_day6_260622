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
    
    # 次のノードを見つけ、visitedとtourに追加する
    # 全てのノードを回るまで続ける
    while len(tour) < len(cities):
        # print("今は",current)
        # 次のノードを見つける
        next = near_node(current, cities, visited)
        # print(next,"に行く")
        # 次のノードをvisitedにいれて、currentにする
        visited.add(next)
        tour.append(next)
        current = next

    # 2-opt
    improved = True
    while improved == True:
        improved = two_opt(tour, cities)

    # or-opt
    improved = True
    while improved:
        improved_tour = or_opt(tour, cities)
        if improved_tour == tour:
            break
        tour = improved_tour
        
    return tour


# 次のノードを見つける
# 今いるノードから近いかつ、visitedにないノードを見つける
def near_node(current:int, cities:list, visited:set) -> int:
    short_distance = float('inf')
    nearest_node = None
    for i in range(len(cities)):
        # 訪問していなければ
        if i not in visited:
            # 二点間の距離を取得
            to_i_distance = distance(cities,current,i)
            # print(i,"との距離は",to_i_distance)
            # 距離が今まで探索した中で一番短ければ
            if to_i_distance < short_distance:
                short_distance = to_i_distance
                nearest_node = i
    return nearest_node

# 2点間の距離を求める
def distance(cities:list,node1:int,node2:int) -> float:
    x1 = cities[node1][0]
    y1 = cities[node1][1]
    x2 = cities[node2][0]
    y2 = cities[node2][1]
    distance = ((x1 - x2)**2 + (y1 - y2)**2) ** 0.5
    return distance

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

    
if __name__ == '__main__':
    assert len(sys.argv) > 1
    tour = solve(read_input(sys.argv[1]))
    print_tour(tour)
