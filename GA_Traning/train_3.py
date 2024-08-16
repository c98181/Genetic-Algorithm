import numpy as np
import pygad
import random
import time
import multiprocessing


def height(a): # 方塊總高
    test = 0
    h = [19, 19, 19, 19, 19, 19, 19, 19, 19, 19]
    for i in a:
        if (i[1] < h[i[0]]):
            h[i[0]] = i[1]
    test = 190-sum(h)
    return test


def bumpness(a): 
    test = 0
    h = [19, 19, 19, 19, 19, 19, 19, 19, 19, 19]
    for i in a:
        if (i[1] < h[i[0]]):
            h[i[0]] = i[1]
    for i in range(1,10):
        test += abs(h[i]-h[i-1])
    return test


def holes(a): # 版面上的洞數 = 總高 - 總方塊數
    t = height(a)
    t -= len(a)
    return t

# 計算行列上變換次數和井數
def column_row_transition_and_wells(a):   
    # 初始回傳值
    data = [0, 0, 0] 
    #建立版面邊界
    board = [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], [
        1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]
    # 將方塊填入版面
    for i in a:
        board[i[1]][i[0]+1] = 1 
    # 計算行變換和井數    
    for i in range(1, 11): 
        temp = board[0][i]
        count = 1
        for j in range(1, 20):
            if temp != board[j][i]:
                data[0] += 1
                temp = board[j][i]
            if temp == 0 and board[j][i+1] == 1 and board[j][i-1] == 1:
                data[2] += count
                count += 1
            else:
                count = 1
    # 計算列變換
    for i in range(1, 19): 
        temp = board[i][0]
        for j in range(1, 12):
            if temp != board[i][j]:
                data[1] += 1
                temp = board[i][j]

    return data

# 實作消除整理版面的函式
def deleteline(a): 
    
    line = []
    x = set(a)
    judge = set()
    # 由上至下檢測是否應刪除
    for k in range(0, 19): 
        
        judge.clear()
        for i in range(10):
            judge.add((i, k))
        if (len(judge.intersection(x))) == 10:
            x = x.difference(judge)
            line.append(k)
    y = list(list(i) for i in x)
    # 讓方塊下落
    for i in line: 
        for j in y:
            if j[1] < i:
                j[1] += 1
    ans = tuple(tuple(i) for i in y)
    return len(line), ans

# AI的核心，對版面的線性評估公式
def grading(board, a): 

    next = deleteline(board)
    l = column_row_transition_and_wells(next[1])
    score = 0
    score -= (a[0])*l[0]
    score -= (a[1])*l[1]
    score += (a[2])*l[2]
    score -= (a[3])*holes(next[1])
    score += (a[4])*(next[0])
    score -= (bumpness(next[1]))*(a[5])
    return score


d = dict() 
# 各方塊與其變異的各種角度
d[0] = {((0, 0), (1, 0), (2, 0), (1, 1)), ((0, 0), (0, 1), (0, 2), (1, 1)),
        ((1, 0), (0, 1), (1, 1), (2, 1)), ((1, 0), (0, 1), (1, 1), (1, 2))}
d[10] = {((0, 0), (1, 0), (2, 0), (3, 0)), ((0, 0), (0, 1), (0, 2), (0, 3))}
d[30] = {((0, 0), (1, 0), (2, 0), (0, 1)), ((0, 0), (0, 1), (0, 2), (1, 2)),
         ((2, 0), (0, 1), (1, 1), (2, 1)), ((0, 0), (1, 0), (1, 1), (1, 2))}
d[20] = {((0, 0), (1, 0), (2, 0), (2, 1)), ((0, 0), (1, 0), (0, 1), (0, 2)),
         ((0, 0), (0, 1), (1, 1), (2, 1)), ((0, 2), (1, 2), (1, 1), (1, 0))}
d[50] = {((0, 0), (1, 0), (1, 1), (2, 1)), ((0, 1), (0, 2), (1, 1), (1, 0))}
d[40] = {((1, 0), (2, 0), (0, 1), (1, 1)), ((0, 0), (0, 1), (1, 1), (1, 2))}
d[60] = {((1, 0), (1, 1), (0, 0), (0, 1))}


d[61] = {((0, 0), (0, 1), (2, 0), (2, 1)), ((0, 0), (1, 0), (0, 2), (1, 2))}
d[11] = {((0, 0), (1, 0), (2, 0), (3, 0)), ((0, 0), (0, 1), (0, 2), (0, 3))}
d[41] = {((1, 1), (2, 0), (0, 1), (3, 0)), ((0, 0), (0, 1), (1, 2), (1, 3))}
d[51] = {((0, 3), (0, 2), (1, 1), (1, 0)), ((0, 0), (1, 0), (3, 1), (2, 1))}
d[21] = {((0, 1), (1, 0), (2, 0), (2, 1)), ((0, 0), (1, 0), (0, 1), (1, 2)),
         ((0, 0), (0, 1), (1, 1), (2, 0)), ((0, 2), (1, 2), (1, 1), (0, 0))}
d[31] = {((0, 0), (1, 0), (2, 1), (0, 1)), ((1, 0), (0, 1), (0, 2), (1, 2)),
         ((2, 0), (0, 0), (1, 1), (2, 1)), ((0, 0), (1, 0), (1, 1), (0, 2))}
d[1] = {((0, 1), (1, 0), (2, 1), (1, 2))}

# 向下移
def block_set_movedown(a): 
   
    ans = set()
    for i in a:
        temp = list(i)
        temp[1] += 1
        ans.add(tuple(temp))
    return ans

# 向上移
def block_set_moveup(a): 
    
    ans = set()
    for i in a:
        temp = list(i)
        temp[1] -= 1
        ans.add(tuple(temp))
    return ans

# 向右移
def block_set_moveright(a): 
    
    ans = set()
    for i in a:
        temp = list(i)
        temp[0] += 1
        ans.add(tuple(temp))
    return ans

# 檢測是否有方塊重疊
def move_valid(block, board): 
    ans = True
    if len(block.intersection(board)) != 0:
        ans = False
    return ans

# 向左移
def block_set_moveleft(a): 
    ans = set()
    for i in a:
        temp = list(i)
        temp[0] -= 1
        ans.add(tuple(temp))
    return ans

#利用傳入的當前版面、方塊種類、是否變異、利用傳入的當前版面、方塊種類、是否變異
#樣本的參數和當前分數等，回傳所有可能性中最佳的下個版面
def nextboard(board, block_type, block_normal_or_strange, argu, sco): 
    # 邊界
    wall = ((-1, -1), (10, -1), (-1, 0), (10, 0), (-1, 1), (10, 1), (-1, 2), (10, 2), (-1, 3), (10, 3), (-1, 4), (10, 4), (-1, 5), (10, 5), (-1, 6), (10, 6), (-1, 7), (10, 7), (-1, 8), (10, 8), (-1, 9), (10, 9), (-1, 10), (10, 10), (-1, 11), (10, 11), (-1, 12), (10, 12), (-1, 13), (10, 13),
            (-1, 14), (10, 14), (-1, 15), (10, 15), (-1, 16), (10, 16), (-1, 17), (10, 17), (-1, 18), (10, 18), (0, -1), (0, 18), (1, -1), (1, 18), (2, -1), (2, 18), (3, -1), (3, 18), (4, -1), (4, 18), (5, -1), (5, 18), (6, -1), (6, 18), (7, -1), (7, 18), (8, -1), (8, 18), (9, -1), (9, 18))
    wall_set = set(wall)
    # 將版面轉為集合，加速運算
    board_set = set(board)
    # 整體版面
    template = wall_set | board_set
    # 取得對應的方塊集合
    block_different_angle = d[10*block_type+block_normal_or_strange]
    # 初始化分數
    sc = -10000
    changedboard = tuple()
    # 用於檢測遊戲是否結束
    line_deleted = -1
    # 由左至右窮舉版面可能性並評分
    for block in block_different_angle:
        block_set = set(block)
        while (move_valid(block_set, template)):
            tempblock = block_set.copy()
            # 將方塊落至最底
            while (move_valid(template, tempblock)):
                tempblock = block_set_movedown(tempblock)
            tempblock = block_set_moveup(tempblock)
            a = grading(tuple(tempblock)+tuple(board_set), argu)
            # 留下分數較高者
            if (a > sc):
                sc = a
                t = deleteline(tuple(tempblock)+tuple(board_set))
                changedboard = t[1]
                line_deleted = t[0]
            # 右移
            block_set = block_set_moveright(block_set)
    #計分
    newscore = [0, sco]
    if line_deleted == -1:
        newscore[0] = -1
    elif line_deleted == 0:
        newscore[1] += 1
    elif line_deleted == 1:
        newscore[1] += 40
    elif line_deleted == 2:
        newscore[1] += 100
    elif line_deleted == 3:
        newscore[1] += 300
    elif line_deleted == 4:
        newscore[1] += 1200
    return changedboard, newscore

# 實作暫存功能
def save(board, block, mutation_rate, solution, score):
    ans = block.copy()
    a = nextboard(board, block[0], 0, solution, score)
    b = nextboard(board, block[1], 0, solution, score)
    if grading(a[0], solution) >= grading(b[0], solution):
        ans.remove(block[0])
        ans.append(random.randint(0, 6))
        return a+tuple([ans])
    else:
        ans.remove(block[1])
        ans.append(random.randint(0, 6))
        return b+tuple([ans])

# 運行tetris
def fitness_func(x,solution, solution_idx):

    totalscore = 0
    block = [0, 0, 0]
    block[0] = np.random.randint(0, 6)
    block[1] = np.random.randint(0, 6)
    block[2] = np.random.randint(0, 6)
    for i in range(1):
        board = tuple()
        score = 0
        tmpblock = block.copy()
        cnt = 0
        while (cnt < 2000):
            now = save(board, tmpblock, 0, solution, score)
            if now[1][0] == -1:
                break
            board = now[0]
            score = now[1][1]
            tmpblock = now[2]
            cnt += 1
        totalscore += score
    print(solution)
    print(totalscore)
    print(solution_idx)
    return totalscore

# 基因演算法執行
ga_instance = pygad.GA(num_generations=100,
                       num_parents_mating=20,
                       fitness_func=fitness_func,
                       sol_per_pop=100,
                       num_genes=6,
                       init_range_low=-5,
                       init_range_high=5,
                       mutation_probability=0.05,
                       parallel_processing = multiprocessing.cpu_count())

if __name__ == "__main__":
    t1 = time.time()
    ga_instance.run()
    t2 = time.time()
    # 畫出對樣本分數的追蹤圖
    ga_instance.plot_fitness()
    # 印出最好的樣本
    solution, solution_fitness, solution_idx = ga_instance.best_solution()
    print("Total time : {time}".format(time=t2-t1))
    print("Parameters of the best solution : {solution}".format(solution=solution))
    print("Fitness value of the best solution = {solution_fitness}".format(
        solution_fitness=solution_fitness))
    print("Index of the best solution : {solution_idx}".format(
        solution_idx=solution_idx))