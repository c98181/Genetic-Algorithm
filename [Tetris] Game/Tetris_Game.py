# encoding: utf-8
import os, sys, random
import time
import numpy as np
import random
from Tetris_dqnAgent import DQNAgent
from Tetris_logs import CustomTensorBoard
from datetime import datetime
from statistics import mean, median
from tqdm import tqdm


class Tetris:
    BRICK_DOWN_SPEED = 0.5 # 常數-磚塊正常下降速度.
    brick_down_speed = 0.5# 磚塊下降速度.
    board = [] # 方塊陣列(10x20).
    bricks = [] # 方塊陣列(4x4).
    bricks_next = [] # 下一個方塊陣列(4x4).
    bricks_saved = [] # 儲存的方塊陣列(4x4).
    #? 方塊編碼
    brick_dict = { 
        "10": ( 4, 8, 9,13), "11": ( 9,10,12,13),   # N1.
        "20": ( 5, 8, 9,12), "21": ( 8, 9,13,14),   # N2.
        "30": ( 8,12,13,14), "31": ( 4, 5, 8,12), "32": (8,  9, 10, 14), "33": (5,  9, 12, 13), # L1.
        "40": (10,12,13,14), "41": ( 4, 8,12,13), "42": (8,  9, 10, 12), "43": (4,  5,  9, 13), # L2.
        "50": ( 9,12,13,14), "51": ( 4, 8, 9,12), "52": (8,  9, 10, 13), "53": (5,  8,  9, 13), # T.
        "60": ( 8, 9,12,13),    # O.
        "70": (12,13,14,15), "71": ( 0, 4, 8,12)    #I.
    }
    score_dict = {
        "1": 40, "2": 100, "3": 300, "4": 1200
    }
    def __init__(self):
        #? 初始化各種用到的陣列
        for i in range(10):
            self.board.append([0]*20)
        for i in range(4):
            self.bricks.append([0]*4)
            self.bricks_next.append([0]*4)
            self.bricks_saved.append([0]*4)
        #? 初始化容器
        # 方塊在容器的位置.
        self.container_x = 3 # (-2~6)(  為6的時候不能旋轉方塊).
        self.container_y =-4 # (-3~16)(-3表示在上邊界外慢慢往下掉).
        # 方塊編號(1~7).
        self.brick_id = 1
        # 方塊狀態(0~3).
        self.brick_state = 0
        # 下一個磚塊編號(1~7).
        self.brick_next_id = random.randint( 1, 7)
        self.brick_saved_id = 0

        #? 初始化遊戲參數
        self.round = 0
        self.debug_message = False # 除錯訊息.
        self.score_max = 0 # 最大連線數.
        self.score = 0 # 本場連線數.
        self.dqn_init()
    def dqn_init(self):
        episodes = 2000
        max_steps = None
        epsilon_stop_episode = 1500
        mem_size = 20000
        discount = 0.95
        batch_size = 512
        epochs = 1
        render_every = 50
        log_every = 50
        replay_start_size = 2000
        train_every = 1
        n_neurons = [32, 32]
        render_delay = None
        activations = ['relu', 'relu', 'linear']

        self.agent = DQNAgent(4,n_neurons=n_neurons, activations=activations,
                     epsilon_stop_episode=epsilon_stop_episode, mem_size=mem_size,
                     discount=discount, replay_start_size=replay_start_size)

        self.agent.l()
    def get_next_states(self):
        '''Get all possible next states'''
        states = {}
        # For all rotations
        if self.brick_id == 6: 
            rotations = [0]
        elif self.brick_id  == 1 or self.brick_id  == 2 or self.brick_id  == 7:
            rotations = [0, 1]
        else:
            rotations = [0, 1, 2, 3]
        for rotation in rotations:
            piece = self.transformToBricks(self.brick_id, rotation)
            min_x = 0
            max_x = 0
            for x in range(4):
                for y in range(4):
                    if(piece[x][y]!=0):
                        max_x = max(x,max_x)
            # For all positions
            for x in range(min_x, 10 - max_x):
                pos = [x, 0]

                # Drop piece
                while self.ifTouchBottom(piece, pos):
                    pos[1] += 1
                pos[1] -= 1

                # Valid move
                if pos[1] >= 0:
                    board_temp = self.copy_to_board(piece, pos)
                    states[(x, rotation)] = self.get_board_props(board_temp)
                    
        return states
    def get_board_props(self, board):
        '''Get properties of the board'''
        board_set = self.transform_to_list(board)
        move = self.deleteline(board_set)
        ans = list(list(i) for i in move[1])
        for i in move[0]:
            for j in range(len(ans)):
                if (ans[j][1] < i):
                    ans[j][1] += 1
        lines = len(move[0])
        holes = self.holes(ans)
        total_bumpiness = self.bumpiness(ans)
        sum_height = self.height(ans)
        return [lines, holes, total_bumpiness, sum_height]
    def get_best_action(self):
        next_state = self.get_next_states()
        best_state = self.agent.best_state(next_state.values())
        best_action = None
        for action, state in next_state.items():
            if state == best_state:
                best_action = action
                break
        return best_action[0]-3,best_action[1]


    #-------------------------------------------------------------------------
    #? 函數:取得磚塊索引陣列.
    # 傳入:
    #   brickId : 方塊編號(1~7).
    #   state   : 方塊狀態(0~3).
    def getBrickIndex(self, brickId, state):
        brickKey = str(brickId)+str(state) # 組合字串.
        return self.brick_dict[brickKey] # 回傳方塊陣列.
    #-------------------------------------------------------------------------
    def height(self, a):
        test = 0
        h = [20, 20, 20, 20, 20, 20, 20, 20, 20, 20]

        for i in range(len(a)):
            if (a[i][1] < h[a[i][0]]):
                h[a[i][0]] = a[i][1]

        test = 200-sum(h)
        return test
    def bumpiness(self, a): 
        total_bumpiness = 0
        h = [19, 19, 19, 19, 19, 19, 19, 19, 19, 19]
        for i in a:
            if (i[1] < h[i[0]]):
                h[i[0]] = i[1]
        for i in range(1,10):
            total_bumpiness += abs(h[i]-h[i-1])
        
        return total_bumpiness

    # 最大高度

    def max_height(self, a):
        test = 3000
        for i in range(len(a)):
            if (a[i][1]) < test:
                test = a[i][1]
        return 20-test

    # 空洞數
    def holes(self, a):
        t = self.height(a)
        t -= len(a)

        return t

# 行列方向上變換次數與井數計算
    def column_row_transition_and_wells(self,a):
        # 初始化輸出
        data = [0, 0, 0]
        # 初始化版面
        board = [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], [
            1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]
        # 填入方格
        for i in range(len(a)):
            board[a[i][1]+1][a[i][0]+1] = 1
        # 計算行方向上變換次數與井數
        for i in range(1, 11):
            temp = board[0][i]
            for j in range(1, 22):
                if (temp != board[j][i]):
                    data[0] += 1
                    temp = board[j][i]
        for i in range(1, 11):
            count = 1
            for j in range(1, 21):
                if (board[j][i] == 0 and board[j][i+1] == 1 and board[j][i-1] == 1):
                    data[2] += count
                    count += 1
                else:
                    count = 1
        # 計算列方向上變換次數
        for i in range(1, 21):
            temp = board[i][0]
            for j in range(1, 12):
                if (temp != board[i][j]):
                    data[1] += 1
                    temp = board[i][j]

        return data

    # 找出要刪除的行數
    def deleteline(self,a):
        line = []
        y = set(tuple(i)for i in a)

        judge = set()
        for i in range(10):
            judge.add((i, 20))
            judge.add((i, -1))
        x = y.difference(judge)
        for k in range(1, 20): #不用判斷最上面那行:1~19
            judge.clear()
            for i in range(10):
                judge.add((i, k))
            # print(judge)
            if (len(judge.intersection(x))) == 10:
                x = x.difference(judge)
                line.append(k)

        return line, x

    # 對版面評分，此AI的核心
    def grading(self, board):
        move1 = self.deleteline(board)
        ans = list(list(i) for i in move1[1])
        for i in move1[0]:
            for j in range(len(ans)):
                if (ans[j][1] < i):
                    ans[j][1] += 1
        l = self.column_row_transition_and_wells(ans)
        score = 0
        score += (-9.348695305)*l[0]
        score += (-3.217888287)*l[1]
        score += (-3.385597225)*l[2]
        score += (-7.899265427)*self.holes(ans)
        score += 3.41812681*len(move1[0])
        score += (self.max_height(ans))*(-4.500158825)
        return score

    def transform_to_list(self,board):
        board_list = list()
        for x in range(10):
            for y in range(20):
                if(board[x][y]!=0):
                    board_list.append((x,y))
        return board_list
    # 計算出最佳的版面，回傳動作至LabView
    def pythontakeall(self, block_type,x,block_state):
        set_board = set()
        board = self.transform_to_list(self.board)
        for i in range(len(board)):
            set_board.add(tuple(board[i][0:2]))
        # 加入邊界
        for i in range(10):
            set_board.add((i, 20))
            set_board.add((i, -1))
        if block_type == 6:
            score = [0, 0, 0, 0, 0, 0, 0, 0, 0] #60
            block = np.array([[1, 0], [1, 1], [0, 0], [0, 1]]) #方塊形狀
            for i in range(9):
                # 此迴圈遍搜所有落點
                if (len(set_board.intersection(set(tuple(i)for i in block)))) == 0:
                    # 與版面無交集代表可放置
                    tmpblock = block.copy()
                    while len(set_board.intersection(set(tuple(i)for i in tmpblock))) == 0:
                        # 將方塊落至最底
                        tmpblock[:, 1] = tmpblock[:, 1]+1
                    tmpblock[:, 1] = tmpblock[:, 1]-1
                    l = tmpblock.tolist()
                    a = l+board
                    # 將版面與方塊結合，放入評分公式
                    score[i] = self.grading(a)
                block[:, 0] = block[:, 0]+1 #block的 x 值+1: move right
            index = score.index(max(score))
            action = score[x]
            score.sort(reverse=True)
            rank = 1
            for i in range(len(score)):
                if score[i] == action:
                    break
                else:
                    rank += 1
            # 找出最大值，回傳對應動作
            return [max(score), 0, index-3, rank]
        elif block_type == 7:
            score0 = [0, 0, 0, 0, 0, 0, 0] #70
            score1 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0] #71
            block = np.array([[0, 0], [1, 0], [2, 0], [3, 0]]) #4長條
            for i in range(7):
                if (len(set_board.intersection(set(tuple(i)for i in block)))) == 0:
                    tmpblock = block.copy()
                    while len(set_board.intersection(set(tuple(i)for i in tmpblock))) == 0:
                        tmpblock[:, 1] = tmpblock[:, 1]+1
                    tmpblock[:, 1] = tmpblock[:, 1]-1
                    l = tmpblock.tolist()
                    a = l+board
                    score0[i] = self.grading(a)
                block[:, 0] = block[:, 0]+1
            block = np.array([[0, 0], [0, 1], [0, 2], [0, 3]])
            for i in range(10):
                if (len(set_board.intersection(set(tuple(i)for i in block)))) == 0:
                    tmpblock = block.copy()
                    while len(set_board.intersection(set(tuple(i)for i in tmpblock))) == 0:
                        tmpblock[:, 1] = tmpblock[:, 1]+1
                    tmpblock[:, 1] = tmpblock[:, 1]-1
                    l = tmpblock.tolist()
                    a = l+board
                    score1[i] = self.grading(a)
                block[:, 0] = block[:, 0]+1
            totalscore = score0 + score1

            index = totalscore.index(max(totalscore))
            if block_state == 0:
                action = totalscore[x]
            else:
                action = totalscore[8+x]
            totalscore.sort(reverse=True)
            rank = 1
            for i in range(len(totalscore)):
                if totalscore[i] == action:
                    break
                else:
                    rank += 1

            if index < 7:
                return [max(totalscore), 0, index-3, rank]
            else:
                return [max(totalscore), 1, index-7-3, rank]
        elif block_type == 1:
            score0 = [0, 0, 0, 0, 0, 0, 0, 0, 0] #10
            score1 = [0, 0, 0, 0, 0, 0, 0, 0] #11
            block = np.array([[0, 0], [0, 1], [1, 1], [1, 2]]) #10
            for i in range(9):
                if (len(set_board.intersection(set(tuple(i)for i in block)))) == 0:
                    tmpblock = block.copy()
                    while len(set_board.intersection(set(tuple(i)for i in tmpblock))) == 0:
                        tmpblock[:, 1] = tmpblock[:, 1]+1
                    tmpblock[:, 1] = tmpblock[:, 1]-1
                    l = tmpblock.tolist()
                    a = l+board
                    score0[i] = self.grading(a)
                block[:, 0] = block[:, 0]+1
            block = np.array([[1, 0], [2, 0], [0, 1], [1, 1]]) #11
            for i in range(8):
                if (len(set_board.intersection(set(tuple(i)for i in block)))) == 0:
                    tmpblock = block.copy()
                    while len(set_board.intersection(set(tuple(i)for i in tmpblock))) == 0:
                        tmpblock[:, 1] = tmpblock[:, 1]+1
                    tmpblock[:, 1] = tmpblock[:, 1]-1
                    l = tmpblock.tolist()
                    a = l+board
                    score1[i] = self.grading(a)
                block[:, 0] = block[:, 0]+1
            totalscore = score0+score1
            index = totalscore.index(max(totalscore))
            action = totalscore[block_state*9+x]
            totalscore.sort(reverse=True)
            rank = 1
            for i in range(len(totalscore)):
                if totalscore[i] == action:
                    break
                else:
                    rank += 1
            if index < 9:
                return [max(totalscore), 0, index-3, rank]
            else:
                return [max(totalscore), 1, index-9-3, rank]
        elif block_type == 2:
            score0 = [0, 0, 0, 0, 0, 0, 0, 0, 0]
            score1 = [0, 0, 0, 0, 0, 0, 0, 0]
            block = np.array([[0, 1], [0, 2], [1, 1], [1, 0]])
            for i in range(9):
                if (len(set_board.intersection(set(tuple(i)for i in block)))) == 0:
                    tmpblock = block.copy()
                    while len(set_board.intersection(set(tuple(i)for i in tmpblock))) == 0:
                        tmpblock[:, 1] = tmpblock[:, 1]+1
                    tmpblock[:, 1] = tmpblock[:, 1]-1
                    l = tmpblock.tolist()
                    a = l+board
                    score0[i] = self.grading(a)
                block[:, 0] = block[:, 0]+1
            block = np.array([[0, 0], [1, 0], [1, 1], [2, 1]])
            for i in range(8):
                if (len(set_board.intersection(set(tuple(i)for i in block)))) == 0:
                    tmpblock = block.copy()
                    while len(set_board.intersection(set(tuple(i)for i in tmpblock))) == 0:
                        tmpblock[:, 1] = tmpblock[:, 1]+1
                    tmpblock[:, 1] = tmpblock[:, 1]-1
                    l = tmpblock.tolist()
                    a = l+board
                    score1[i] = self.grading(a)
                block[:, 0] = block[:, 0]+1
            totalscore = score0+score1

            index = totalscore.index(max(totalscore))
            action = totalscore[block_state*9+x]
            totalscore.sort(reverse=True)
            rank = 1
            for i in range(len(totalscore)):
                if totalscore[i] == action:
                    break
                else:
                    rank += 1
            if index < 9:
                return [max(totalscore), 0, index-3, rank]
            else:
                return [max(totalscore), 1, index-9-3, rank]
        elif block_type == 3:
            score0 = [0, 0, 0, 0, 0, 0, 0, 0]
            score1 = [0, 0, 0, 0, 0, 0, 0, 0, 0]
            score2 = [0, 0, 0, 0, 0, 0, 0, 0]
            score3 = [0, 0, 0, 0, 0, 0, 0, 0, 0]
            block = np.array([[0, 0], [0, 1], [1, 1], [2, 1]]) #30
            for i in range(8):
                if (len(set_board.intersection(set(tuple(i)for i in block)))) == 0:
                    tmpblock = block.copy()
                    while len(set_board.intersection(set(tuple(i)for i in tmpblock))) == 0:
                        tmpblock[:, 1] = tmpblock[:, 1]+1
                    tmpblock[:, 1] = tmpblock[:, 1]-1
                    l = tmpblock.tolist()
                    a = l+board
                    score0[i] = self.grading(a)
                block[:, 0] = block[:, 0]+1
            
            block = np.array([[0, 0], [1, 0], [0, 1], [0, 2]]) #31
            for i in range(9):
                if (len(set_board.intersection(set(tuple(i)for i in block)))) == 0:
                    tmpblock = block.copy()
                    while len(set_board.intersection(set(tuple(i)for i in tmpblock))) == 0:
                        tmpblock[:, 1] = tmpblock[:, 1]+1
                    tmpblock[:, 1] = tmpblock[:, 1]-1
                    l = tmpblock.tolist()
                    a = l+board
                    score1[i] = self.grading(a)
                block[:, 0] = block[:, 0]+1

            block = np.array([[0, 0], [1, 0], [2, 0], [2, 1]]) #32
            for i in range(8):
                if (len(set_board.intersection(set(tuple(i)for i in block)))) == 0:
                    tmpblock = block.copy()
                    while len(set_board.intersection(set(tuple(i)for i in tmpblock))) == 0:
                        tmpblock[:, 1] = tmpblock[:, 1]+1
                    tmpblock[:, 1] = tmpblock[:, 1]-1
                    l = tmpblock.tolist()
                    a = l+board
                    score2[i] = self.grading(a)
                block[:, 0] = block[:, 0]+1

            block = np.array([[0, 2], [1, 2], [1, 1], [1, 0]]) #33
            for i in range(9):
                if (len(set_board.intersection(set(tuple(i)for i in block)))) == 0:
                    tmpblock = block.copy()
                    while len(set_board.intersection(set(tuple(i)for i in tmpblock))) == 0:
                        tmpblock[:, 1] = tmpblock[:, 1]+1
                    tmpblock[:, 1] = tmpblock[:, 1]-1
                    l = tmpblock.tolist()
                    a = l+board
                    score3[i] = self.grading(a)
                block[:, 0] = block[:, 0]+1

            totalscore = score0+score1+score2+score3
            index = totalscore.index(max(totalscore))
            if(block_state == 0):
                action = totalscore[x]
            elif(block_state == 1):
                action = totalscore[8+x]
            elif(block_state == 2):
                action = totalscore[17+x]
            else:
                action = totalscore[25+x]
            totalscore.sort(reverse=True)
            rank = 1
            for i in range(len(totalscore)):
                if totalscore[i] == action:
                    break
                else:
                    rank += 1
            if index < 8:
                return [max(totalscore), 0, index-3, rank]
            elif index < 17:
                return [max(totalscore), 1, index-8-3, rank]
            elif index < 25:
                return [max(totalscore), 2, index-17-3, rank]
            else:
                return [max(totalscore), 3, index-25-3, rank]
        elif block_type == 4:
            score0 = [0, 0, 0, 0, 0, 0, 0, 0]
            score1 = [0, 0, 0, 0, 0, 0, 0, 0, 0]
            score2 = [0, 0, 0, 0, 0, 0, 0, 0]
            score3 = [0, 0, 0, 0, 0, 0, 0, 0, 0]
            block = np.array([[2, 0], [0, 1], [1, 1], [2, 1]]) #40
            for i in range(8):
                if (len(set_board.intersection(set(tuple(i)for i in block)))) == 0:
                    tmpblock = block.copy()
                    while len(set_board.intersection(set(tuple(i)for i in tmpblock))) == 0:
                        tmpblock[:, 1] = tmpblock[:, 1]+1
                    tmpblock[:, 1] = tmpblock[:, 1]-1
                    l = tmpblock.tolist()
                    a = l+board
                    score0[i] = self.grading(a)
                block[:, 0] = block[:, 0]+1
            
            block = np.array([[0, 0], [1, 2], [0, 1], [0, 2]]) #41
            for i in range(9):
                if (len(set_board.intersection(set(tuple(i)for i in block)))) == 0:
                    tmpblock = block.copy()
                    while len(set_board.intersection(set(tuple(i)for i in tmpblock))) == 0:
                        tmpblock[:, 1] = tmpblock[:, 1]+1
                    tmpblock[:, 1] = tmpblock[:, 1]-1
                    l = tmpblock.tolist()
                    a = l+board
                    score1[i] = self.grading(a)
                block[:, 0] = block[:, 0]+1

            block = np.array([[0, 0], [1, 0], [2, 0], [0, 1]]) #42
            for i in range(8):
                if (len(set_board.intersection(set(tuple(i)for i in block)))) == 0:
                    tmpblock = block.copy()
                    while len(set_board.intersection(set(tuple(i)for i in tmpblock))) == 0:
                        tmpblock[:, 1] = tmpblock[:, 1]+1
                    tmpblock[:, 1] = tmpblock[:, 1]-1
                    l = tmpblock.tolist()
                    a = l+board
                    score2[i] = self.grading(a)
                block[:, 0] = block[:, 0]+1

            block = np.array([[0, 0], [1, 2], [1, 1], [1, 0]]) #43
            for i in range(9):
                if (len(set_board.intersection(set(tuple(i)for i in block)))) == 0:
                    tmpblock = block.copy()
                    while len(set_board.intersection(set(tuple(i)for i in tmpblock))) == 0:
                        tmpblock[:, 1] = tmpblock[:, 1]+1
                    tmpblock[:, 1] = tmpblock[:, 1]-1
                    l = tmpblock.tolist()
                    a = l+board
                    score3[i] = self.grading(a)
                block[:, 0] = block[:, 0]+1

            totalscore = score0+score1+score2+score3
            index = totalscore.index(max(totalscore))
            if(block_state == 0):
                action = totalscore[x]
            elif(block_state == 1):
                action = totalscore[8+x]
            elif(block_state == 2):
                action = totalscore[17+x]
            else:
                action = totalscore[25+x]
            totalscore.sort(reverse=True)
            rank = 1
            for i in range(len(totalscore)):
                if totalscore[i] == action:
                    break
                else:
                    rank += 1
            if index < 8:
                return [max(totalscore), 0, index-3, rank]
            elif index < 17:
                return [max(totalscore), 1, index-8-3, rank]
            elif index < 25:
                return [max(totalscore), 2, index-17-3, rank]
            else:
                return [max(totalscore), 3, index-25-3, rank]
        elif block_type == 5:
            score0 = [0, 0, 0, 0, 0, 0, 0, 0]
            score1 = [0, 0, 0, 0, 0, 0, 0, 0, 0]
            score2 = [0, 0, 0, 0, 0, 0, 0, 0]
            score3 = [0, 0, 0, 0, 0, 0, 0, 0, 0]
            block = np.array([[1, 0], [0, 1], [1, 1], [2, 1]]) #50
            for i in range(8):
                if (len(set_board.intersection(set(tuple(i)for i in block)))) == 0:
                    tmpblock = block.copy()
                    while len(set_board.intersection(set(tuple(i)for i in tmpblock))) == 0:
                        tmpblock[:, 1] = tmpblock[:, 1]+1
                    tmpblock[:, 1] = tmpblock[:, 1]-1
                    l = tmpblock.tolist()
                    a = l+board
                    score0[i] = self.grading(a)
                block[:, 0] = block[:, 0]+1
            
            block = np.array([[0, 0], [0, 1], [0, 2], [1, 1]]) #51
            for i in range(9):
                if (len(set_board.intersection(set(tuple(i)for i in block)))) == 0:
                    tmpblock = block.copy()
                    while len(set_board.intersection(set(tuple(i)for i in tmpblock))) == 0:
                        tmpblock[:, 1] = tmpblock[:, 1]+1
                    tmpblock[:, 1] = tmpblock[:, 1]-1
                    l = tmpblock.tolist()
                    a = l+board
                    score1[i] = self.grading(a)
                block[:, 0] = block[:, 0]+1

            block = np.array([[0, 0], [1, 0], [2, 0], [1, 1]]) #52
            for i in range(8):
                if (len(set_board.intersection(set(tuple(i)for i in block)))) == 0:
                    tmpblock = block.copy()
                    while len(set_board.intersection(set(tuple(i)for i in tmpblock))) == 0:
                        tmpblock[:, 1] = tmpblock[:, 1]+1
                    tmpblock[:, 1] = tmpblock[:, 1]-1
                    l = tmpblock.tolist()
                    a = l+board
                    score2[i] = self.grading(a)
                block[:, 0] = block[:, 0]+1

            block = np.array([[1, 0], [0, 1], [1, 1], [1, 2]]) #53
            for i in range(9):
                if (len(set_board.intersection(set(tuple(i)for i in block)))) == 0:
                    tmpblock = block.copy()
                    while len(set_board.intersection(set(tuple(i)for i in tmpblock))) == 0:
                        tmpblock[:, 1] = tmpblock[:, 1]+1
                    tmpblock[:, 1] = tmpblock[:, 1]-1
                    l = tmpblock.tolist()
                    a = l+board
                    score3[i] = self.grading(a)
                block[:, 0] = block[:, 0]+1

            totalscore = score0+score1+score2+score3
            index = totalscore.index(max(totalscore))
            if(block_state == 0):
                action = totalscore[x]
            elif(block_state == 1):
                action = totalscore[8+x]
            elif(block_state == 2):
                action = totalscore[17+x]
            else:
                action = totalscore[25+x]
            totalscore.sort(reverse=True)
            rank = 1
            for i in range(len(totalscore)):
                if totalscore[i] == action:
                    break
                else:
                    rank += 1
            if index < 8:
                return [max(totalscore), 0, index-3, rank]
            elif index < 17:
                return [max(totalscore), 1, index-8-3, rank]
            elif index < 25:
                return [max(totalscore), 2, index-17-3, rank]
            else:
                return [max(totalscore), 3, index-25-3, rank]

    # 實作暫存功能，比較暫存區的方塊與當前方塊，回傳動作至labview
    def newrobot(self, x, block_type):
        original = self.pythontakeall(self.brick_id,x,block_type)
        if(self.brick_saved_id != 0):
            saved = self.pythontakeall(self.brick_saved_id,x,block_type)
        else:
            return original
        
        if (original[0] >= saved[0]):
            original[0] = 0
            return original
        else:
            saved[0] = 1
            return saved
    #-------------------------------------------------------------------------
    #? 轉換定義方塊到方塊陣列.
    # 傳入:
    #   brickId : 方塊編號(1~7).
    #   state   : 方塊狀態(0~3).
    def transformToBricks(self,id,state):
        # 清除方塊陣列.
        block = []
        for i in range(4):
            block.append([0]*4)
            
        # 取得磚塊索引陣列.
        p_brick = self.getBrickIndex(id, state)
       
        # 轉換方塊到方塊陣列.
        for i in range(4):        
            bx = int(p_brick[i] % 4)
            by = int(p_brick[i] / 4)
            block[bx][by] = id
        return block
           
    #-------------------------------------------------------------------------

    #-------------------------------------------------------------------------
    #? 判斷是否碰到底了
    # 傳出:
    #   true    : 還沒
    #   false   : 碰到了
    def ifTouchBottom(self,block, pos):
        posX = 0
        posY = 0
        for x in range(4):
            for y in range(4):
                if (block[x][y] != 0):
                    posX = pos[0] + x
                    posY = pos[1] + y
                    if (posX >= 0 and posY >= 0):
                        try:
                            if (self.board[posX][posY] != 0):
                                return False
                        except:
                            return False
        return True
    #-------------------------------------------------------------------------

    #-------------------------------------------------------------------------
    #? 複製方塊到容器內.
    def copy_to_board(self,block,pos):
        posX = 0
        posY = 0
        board_temp = []
        for i in range(10):
            board_temp.append([0]*20)
        for x in range(10):
            for y in range(20):
                if(self.board[x][y] != 0):
                    board_temp[x][y] = self.board[x][y]
        for x in range(4):
            for y in range(4):
                if (block[x][y] != 0):
                    posX = pos[0] + x
                    posY = pos[1] + y
                    if (posX >= 0 and posY >= 0):
                            board_temp[posX][posY] = block[x][y]
        return board_temp
    #-------------------------------------------------------------------------
        
    #-------------------------------------------------------------------------
    #? 初始遊戲.
    
    def resetGame(self):

        # 清除磚塊陣列.
        for x in range(10):
            for y in range(20):
                self.board[x][y] = 0
        # 清除方塊陣列.
        for x in range(4):
            for y in range(4):
                self.bricks[x][y] = 0
        # 初始磚塊下降速度.
        self.BRICK_DOWN_SPEED = 0.5
        self.brick_down_speed = self.BRICK_DOWN_SPEED
        round = 0
        # 最大連線數.
        if(self.score > self.score_max):
            self.score_max = self.score
        # 連線數.
        self.score = 0
    #-------------------------------------------------------------------------
    def faster(self):
        if(self.BRICK_DOWN_SPEED > 0.00001):
            self.BRICK_DOWN_SPEED /= 2
            self.round += 1
            self.score_dict["1"] = 40 * (self.round+1)
            self.score_dict["2"] = 100 * (self.round+1)
            self.score_dict["3"] = 300 * (self.round+1)
            self.score_dict["4"] = 1200 * (self.round+1)
    #---------------------------------------------------------------------------
    #? 判斷與設定要清除的方塊.
    # 傳出:
    #   連線數
    def ifClearBrick(self):
        pointNum = 0
        lineNum = 0
        for y in range(20):
            for x in range(10):
                if (self.board[x][y] > 0):
                    pointNum = pointNum + 1
                if (pointNum == 10):
                    for i in range(10):
                        lineNum = lineNum + 1
                        self.board[i][y] = 9
            pointNum = 0
        return lineNum
    #---------------------------------------------------------------------------

    #-------------------------------------------------------------------------
    #? 更新下一個磚塊.
    def updateNextBricks(self):
        self.bricks_next = self.transformToBricks(self.brick_next_id,0)
    #-------------------------------------------------------------------------

    #-------------------------------------------------------------------------
    #? 更新下一個磚塊.
    def updatSavedBricks(self):
        self.bricks_saved = self.transformToBricks(self.brick_saved_id,0)
    #-------------------------------------------------------------------------

    #-------------------------------------------------------------------------
    #? 更新下一個磚塊.
    def savedBricks(self):
        if(self.brick_saved_id == 0):
            self.brick_id, self.brick_saved_id = self.brick_next_id, self.brick_id
            self.brick_next_id = random.randint( 1, 7)
            self.updateNextBricks()  
        else:
            self.brick_id, self.brick_saved_id = self.brick_saved_id, self.brick_id
        self.brick_state = 0
        self.bricks =  self.transformToBricks(self.brick_id, self.brick_state)
        self.container_x = 3
        self.container_y = -4
        self.updatSavedBricks()
    #-------------------------------------------------------------------------

    #-------------------------------------------------------------------------
    #? 執行下一輪.
    def nextRound(self):
        # GameOver.
        if (self.checkGameLogic()):
            print(str(self.score))
            self.resetGame()

        # 複製方塊到容器內.
        self.container_y = self.container_y - 1
        self.board = self.copy_to_board(self.bricks, [self.container_x, self.container_y])  
        
        #------------------------------------------------    
        # 判斷與設定要清除的方塊.
        lines = (int)(self.ifClearBrick() / 10)        
        if (lines > 0):
            # 消除連線數量累加.
            self.score =  self.score + self.score_dict[str(lines)]
            self.clearBrick()

        # 初始方塊位置.
        self.container_x = 3
        self.container_y = -4

        # 現在出現方塊、初始方塊狀態.
        self.brick_id = self.brick_next_id
        self.brick_state = 0
        self.bricks =  self.transformToBricks(self.brick_id, self.brick_state)
        self.brick_next_id = random.randint( 1, 7)
        self.updateNextBricks()   
    #-------------------------------------------------------------------------

    #-------------------------------------------------------------------------
    # 清除的方塊.
    #-------------------------------------------------------------------------
    def clearBrick(self):
        # 一列一列判斷清除方塊.
        temp = 0    
        for x in range(10):
            for i in range(19):
                for y in range(20):
                    if (self.board[x][y] == 9):
                        if (y > 0):
                            temp = self.board[x][y - 1]
                            self.board[x][y - 1] = self.board[x][y]
                            self.board[x][y] = temp
                            y = y - 1
                self.board[x][0] = 0
    #-------------------------------------------------------------------------
    def checkGameLogic(self):
        if (self.container_y < 0): return True
        else : return False
    def start(self):
        self.brick_down_speed = 0.5
        self.container_x = 3 
        self.container_y =-4 
        self.brick_id = random.randint( 1, 7)
        self.brick_state = 0
        self.score_max = 0 
        self.score = 0 
        self.bricks =  self.transformToBricks(self.brick_id, self.brick_state)
        self.updateNextBricks()
    #-------------------------------------------------------------------------
    def random_board(self):
        for x in range(10):
            time = random.randint(1, 7)
            for y in range(time):
                self.board[x][19-y] = random.randint(1, 7)
    def start_quiz(self):
        self.brick_down_speed = 0.5
        self.container_x = 3 
        self.container_y = -4 
        self.brick_id = random.randint( 1, 7)
        self.brick_state = 0
        self.score_max = 0 
        self.score = 0 
        self.random_board()
        self.bricks =  self.transformToBricks(self.brick_id, self.brick_state)
        self.updateNextBricks()
    def nextQuiz(self):
        for x in range(10):
            for y in range(20):
                self.board[x][y] = 0
        self.random_board()
        # 複製方塊到容器內.
        self.brick_down_speed = 0.5
        self.container_x = 3 
        self.container_y = -4 
        self.brick_state = 0
        self.brick_id = random.randint( 1, 7)
        self.board = self.copy_to_board(self.bricks,[self.container_x, self.container_y])  
        self.random_board()
        self.bricks =  self.transformToBricks(self.brick_id, self.brick_state)
        self.updateNextBricks()
        
