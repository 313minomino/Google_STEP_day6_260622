#!/usr/bin/env python3

import sys
from common import print_tour, read_input


# =========================
# MAIN SOLVE
# =========================
def solve(cities: list) -> list:

    # 初期解（貪欲）
    tour = greedy_build(cities)

    # -------------------------
    # 局所改善ループ
    # -------------------------
    for _ in range(10):  # 適当な反復

        bad_edges = find_bad_edges(tour, cities, k=5)

        if not bad_edges:
            break

        improved = False

        for edge in bad_edges:
            new_tour = repair_local(tour, cities, edge)

            if evaluate(new_tour, cities) < evaluate(tour, cities):
                tour = new_tour
                improved = True

        # 毎回グローバル整形
        tour = two_opt_once(tour, cities)

        if not improved:
            break

    return tour


# =========================
# GREEDY INITIAL TOUR
# =========================
def greedy_build(cities):
    n = len(cities)
    visited = {0}
    tour = [0]
    current = 0

    while len(tour) < n:
        best = None
        best_d = float("inf")

        for i in range(n):
            if i in visited:
                continue
            d = dist(cities, current, i)
            if d < best_d:
                best_d = d
                best = i

        visited.add(best)
        tour.append(best)
        current = best

    return tour


# =========================
# BAD EDGE SELECTION
# =========================
def find_bad_edges(tour, cities, k=5):
    edges = []

    for i in range(len(tour) - 1):
        a, b = tour[i], tour[i + 1]
        score = edge_penalty(a, b, cities)
        edges.append((score, i))

    edges.sort(reverse=True)

    return [i for score, i in edges[:k] if score > 1]


# =========================
# EDGE PENALTY (core signal)
# =========================
def edge_penalty(a, b, cities):
    x1, y1 = cities[a]
    x2, y2 = cities[b]

    # 長さベース + 折れ感
    return abs(x1 - x2) + abs(y1 - y2)


# =========================
# LOCAL REPAIR (IMPORTANT PART)
# =========================
def repair_local(tour, cities, bad_i):

    n = len(tour)

    start = max(0, bad_i - 3)
    end = min(n, bad_i + 4)

    section = tour[start:end]
    base = tour[:]

    best = base
    best_score = evaluate(base, cities)

    # -------------------------
    # ① reverse（最重要）
    # -------------------------
    cand = base[:]
    cand[start:end] = list(reversed(section))

    score = evaluate(cand, cities)
    if score < best_score:
        best = cand
        best_score = score

    # -------------------------
    # ② swap（局所構造修正）
    # -------------------------
    for i in range(start, end):
        for j in range(end, min(len(tour), end + 10)):

            cand = base[:]
            cand[i], cand[j] = cand[j], cand[i]

            score = evaluate(cand, cities)
            if score < best_score:
                best = cand
                best_score = score

    return best


# =========================
# GLOBAL 2-OPT (1 pass)
# =========================
def two_opt_once(tour, cities):

    best = tour
    best_score = tour_distance(tour, cities)

    n = len(tour)

    for i in range(n - 1):
        for j in range(i + 2, n - 1):

            new = tour[:]
            new[i+1:j+1] = reversed(new[i+1:j+1])

            score = tour_distance(new, cities)

            if score < best_score:
                best = new
                best_score = score

    return best


# =========================
# EVALUATION
# =========================
def evaluate(tour, cities):
    return tour_distance(tour, cities)


def tour_distance(tour, cities):
    total = 0
    n = len(tour)

    for i in range(n):
        a = tour[i]
        b = tour[(i + 1) % n]
        total += dist(cities, a, b)

    return total


def dist(cities, i, j):
    x1, y1 = cities[i]
    x2, y2 = cities[j]
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5


# =========================
# RUN
# =========================
if __name__ == "__main__":
    assert len(sys.argv) > 1
    tour = solve(read_input(sys.argv[1]))
    print_tour(tour)