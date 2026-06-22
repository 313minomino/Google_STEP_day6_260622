# 第５回　Google Mapsはすごい（経路最適化）

## コードの目的
- N個のノードを順に全て時の最短のルートを発見し、その距離を出力する
- 独自のヒューリスティックを用いて最適なノードを発見する

## 独自のヒューリスティック
- 自分が最短経路を直感的に考える時、以下の図のように考えて①に行くか②に行くかを考えていることに気づいた。
![fig1](images/fig1.png")
- ①に行くか②に行くかを考える時、
  - ①だとCのためにわざわざ左に戻っている
  - ②だとBのためにわざわざ上に戻っている
- ①と②のどちらが最短かを考える時、戻っている長さで比較していた。
- 例えばこの図であれば、②の方が最短形をになると考えた。
![fig1](images/fig2.png")

- これをコードに落とし込む時以下のステップで行うことにした
  - まずは各エッジをx,y軸に投射する
    ![fig1](images/fig3.png")
  - その投射ができるだけ重複しないようなノードを選択していく
- 例えばこの例だと①より②の方が3回以上通っている数が少ないので、②の方が最短経路だと判断する。


## アルゴリズム
### 次に辿るべきノードを見つけ、全てのノードを回るまで見つける
`def solve(cities:list) -> list:`  
たどったノードは、訪れたノードを記録するvisitedと、最終的にたどったパスを記録するtourに追加する。

### 次に行くべきノードを探す
`def bestscore_node(current:int, cities:list, visited:set, used_edge:list) -> int:`
- まず候補都市の絞り込む
- 距離が近い上位10個のノードに対してスコアを計算する
- 探索した中で最もスコアが低いものを次に行くべきノードとする

#### 候補都市の絞り込み
- 現在の都市から未訪問の都市までの距離を計算し、距離が近い上位10都市を候補とする
- これにより、全ての未訪問都市を評価する場合と比較して計算量を削減しつつ、近傍探索の性質を維持している

##### 2点間の距離を求める
`def distance(cities:list,node1:int,node2:int) -> float:`
- 二点間の距離はこのように計算する<br>
`distance = ((x1 - x2)**2 + (y1 - y2)**2) ** 0.5`

#### スコアの付け方 
- ①ノードまでの距離、②エッジをx,y軸に投射した際の重複、③直前の移動方向と次に移動しようとしている方向とのなす角の3つの要素に、それぞれ重みをつけた合計をscoreにし、scoreが低いものを次のノードに選ぶ
- 探索の序盤と終盤では望ましい経路が異なるため、探索の進行度(progress)に応じて、序盤は重複回避を重視、終盤は折り返し回避を重視するように重みを変化させている。
```python
distance = distance_calc(cities, current, i)
overlap_penalty = (calc_overlap_penalty(current,j,cities,used_edge))**1.5
turn_penalty = calc_turn_penalty(current,j,cities,used_edge)

# ペナルティの重みづけ
progress = len(visited) / len(cities)
OVERLAP_WEIGHT = 1 - 0.8 * progress
TURN_WEIGHT    = 0.3 + 0.7 * progress

# スコアを計算
score = distance*(1+OVERLAP_WEIGHT * overlap_penalty + TURN_WEIGHT * turn_penalty)
```

#### 経路の重複ペナルティ
`def calc_overlap_penalty(current:int,candidate:int,cities:list,used_edges:list) -> float:`
- 新しく追加しようとしている辺と、過去に通過した辺との重複度を計算する
- 各辺を x 軸と y 軸へ射影し、区間の重複長を求めることで、同じ領域を何度も往復する経路を抑制する
- 重複部分を計算する処理は以下の関数で行われている
`def edge_overlap(cities:list, edge1:tuple,edge2:tuple):`
`def overlap_length(node1_interval, node2_interval) -> float:`

#### 折り返しペナルティ
`def calc_turn_penalty(current, candidate, cities, used_edges) -> float:`
- 直前の移動方向と、次に移動しようとしている方向とのなす角を計算し向きが変わるほど大きなペナルティを与える
 - 角度が0°   → 0
 - 角度が90°  → 500
 - 角度が180° → 1000
- ベクトルの内積を用いて角度を計算した

#### 孤立ノードの先読み評価
- 候補都市の周辺に存在する未訪問都市の数を調べる。
- 近傍の未訪問都市が少ない場合、その都市は後回しにすると取り残され、大きなジャンプが発生する可能性が高い。
- そのため近傍ノード数が少ない都市にボーナスを与えることで、孤立ノードを早めに回収することを試みている。
