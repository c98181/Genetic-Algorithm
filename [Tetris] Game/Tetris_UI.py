# encoding: utf-8
import os, sys, random
import time
import pygame 
from Tetris_Game import *
from pygame.locals import *
from Tetris_drew import *

tetris = Tetris()


# 視窗大小.
canvas_width = 800
canvas_height = 600

# 顏色.
colorDict = {
    1:(0,0,0), # 黑色.
    2:(255,255,255), # 白色.
    3:(255,0,0), # 紅色.
    4:(107,130,114), # 灰色.
    5:(20,31,23), # 黑灰色.
    6:(0, 255, 0), # 綠色.
    7:(200, 200, 200) # 灰綠色.
}
   
# ColorVer:
colorVerDict = {
    1:(204,102,51), # 橘色   - N1.
    2:(153,102,153), # 紫色   - N2.
    3:(51,102,204), # 藍色   - L1.
    4:(204,51,51), # 紅色   - L2.
    5:(51,204,255), # 淡藍色 - T.
    6:(204,204,51), # 黃色   - O.
    7:(51,153,102) # 綠色   - I.
} 

# 主遊戲畫面陣列.(10x20)
bricks_box = []
for i in range(10):
    bricks_box.append([0]*20)
# 下一個方塊圖形陣列(4x4).
bricks_next_box = []
for i in range(4):
    bricks_next_box.append([0]*4)  
bricks_saved_box = []
for i in range(4):
    bricks_saved_box.append([0]*4)  
# 初始.
pygame.init()
# 顯示Title.
pygame.display.set_caption(u"俄羅斯方塊遊戲")
# 建立畫佈大小.
# 全螢幕模式.
canvas = pygame.display.set_mode((canvas_width, canvas_height), pygame.DOUBLEBUF and pygame.FULLSCREEN )
# 視窗模式.
#canvas = pygame.display.set_mode((canvas_width, canvas_height))

# 時脈.
clock = pygame.time.Clock()

# 查看系統支持那些字體
# print(pygame.font.get_fonts())

# 設定字型-黑體.
font = pygame.font.SysFont("modern-tetris", 20)


# 將繪圖方塊放入陣列.
for y in range(20):
    for x in range(10):
        bricks_box[x][y] = Box(pygame, canvas, "brick_x_" + str(x) + "_y_" + str(y), [ 0, 0, 26, 26], colorDict[5])

# 將繪圖方塊放入陣列.
for y in range(4):
    for x in range(4):
        bricks_next_box[x][y] = Box(pygame, canvas, "brick_next_x_" + str(x) + "_y_" + str(y), [ 0, 0, 26, 26], colorDict[5])

for y in range(4):
    for x in range(4):
        bricks_saved_box[x][y] = Box(pygame, canvas, "brick_saved_x_" + str(x) + "_y_" + str(y), [ 0, 0, 26, 26], colorDict[5])

# 背景區塊.
background = Box(pygame, canvas, "background", [ 278, 18, 282, 562], colorDict[4])

# 下一格方塊區塊.
background_bricks_next = Box(pygame, canvas, "background_bricks_next", [ 590, 50, 114, 114], colorDict[4])

# 暫存區方塊區塊.
background_bricks_saved = Box(pygame, canvas, "background_saved_next", [ 590, 214, 114, 114], colorDict[4])


#-------------------------------------------------------------------------
# 函數:秀字.
# 傳入:
#   text    : 字串.
#   x, y    : 坐標.
#   color   : 顏色.
#-------------------------------------------------------------------------
def showFont( text, x, y, color):
    global canvas    
    text = font.render(text, True, color) 
    canvas.blit( text, (x,y))

class Button:
    """Create a button, then blit the surface in the while loop"""
    def __init__(self, text,  pos, font, bg="black"):
        self.x, self.y = pos
        self.font = font
        self.change_text(text, bg)
 
    def change_text(self, text, bg="black"):
        """Change the text whe you click"""
        self.text = self.font.render(text, 1, pygame.Color("Black"))
        self.size = (self.text.get_size()[0] + 10 , self.text.get_size()[1] + 10)
        self.surface = pygame.Surface(self.size)
        self.surface.fill(bg)
        self.surface.blit(self.text, (5, 5))
        self.rect = pygame.Rect(self.x, self.y, self.size[0], self.size[1])
 
    def show(self):
        canvas.blit(self.surface, (self.x, self.y))
 
    def click(self, event):
        x, y = pygame.mouse.get_pos()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if pygame.mouse.get_pressed()[0]:
                if self.rect.collidepoint(x, y):
                    return True
        else:
            return False


 
def choose_mode():
    normal_mode = Button(
        "Normal Mode",
        (100, 100),
        font,
        bg="white")

    ai_mode = Button(
        "AI Mode",
        (100, 250),
        font,
        bg="white")

    training_mode = Button(
        "Training Mode",
        (100, 400),
        font,
        bg="white")
    """ The infinite loop where things happen """
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if(normal_mode.click(event)):
                return 1
            elif(ai_mode.click(event)):
                return 2
            elif(training_mode.click(event)):
                return 3
        normal_mode.show()
        ai_mode.show() 
        training_mode.show()
        clock.tick(120)
        pygame.display.update()
#-------------------------------------------------------------------------
def mainloop():
    while(1):
        canvas.fill(colorDict[1])
        mode = choose_mode()
        if(mode == 1):
            normal_mode()
        elif(mode == 2):
            ai_mode()
        else:
            training_mode()


# 更新下一個磚塊.
#-------------------------------------------------------------------------
def updateNextBricksPicture():
    global tetris
    tetris.updateNextBricks()

    # ColorVer:設定背景顏色.
    background_bricks_next.color = colorDict[1] # 黑色.

    # 更新背景區塊.
    background_bricks_next.update()

    # 更新磚塊圖.
    pos_y = 52
    for y in range(4):
        pos_x = 592
        for x in range(4):
            if(tetris.bricks_next[x][y] != 0):
                bricks_next_box[x][y].rect[0] = pos_x
                bricks_next_box[x][y].rect[1] = pos_y

                # ColorVer:依照方塊編號設定顏色.
                if (tetris.bricks_next[x][y] <= 7):
                    bricks_next_box[x][y].color = colorVerDict[tetris.bricks_next[x][y]]
                elif (tetris.bricks_next[x][y] == 9):
                    bricks_next_box[x][y].color = colorDict[2]

                bricks_next_box[x][y].update()
            pos_x = pos_x + 28        
        pos_y = pos_y + 28            
#-------------------------------------------------------------------------    
# 更新下一個磚塊.
#-------------------------------------------------------------------------
def updateSavedBricksPicture():
    global tetris

    # ColorVer:設定背景顏色.
    background_bricks_saved.color = colorDict[1] # 黑色.

    # 更新背景區塊.
    background_bricks_saved.update()

    # 更新磚塊圖.
    pos_y = 216
    for y in range(4):
        pos_x = 592
        for x in range(4):
            if(tetris.bricks_saved[x][y] != 0):
                bricks_saved_box[x][y].rect[0] = pos_x
                bricks_saved_box[x][y].rect[1] = pos_y

                # ColorVer:依照方塊編號設定顏色.
                if (tetris.bricks_saved[x][y] <= 7):
                    bricks_saved_box[x][y].color = colorVerDict[tetris.bricks_saved[x][y]]
                elif (tetris.bricks_saved[x][y] == 9):
                    bricks_saved_box[x][y].color = colorDict[2]

                bricks_saved_box[x][y].update()
            pos_x = pos_x + 28        
        pos_y = pos_y + 28            

#-------------------------------------------------------------------------  
# 主迴圈.
#-------------------------------------------------------------------------
def normal_mode():
    global tetris
    tetris.start()
    running = True
    time_temp = time.time()
    time_round = 0
    time_now = 0
    pygame.mixer.music.load("rush-e.mp3")
    pygame.mixer.music.play(loops=-1)
    while running:
        # 計算時脈.
        time_now = time_now + (time.time() - time_temp)
        time_round = time_round + (time.time() - time_temp)
        time_temp = time.time()
        #---------------------------------------------------------------------
        # 判斷輸入.
        #---------------------------------------------------------------------
        for event in pygame.event.get():
            # 離開遊戲.
            if event.type == pygame.QUIT:
                running = False        
            # 判斷按下按鈕
            if event.type == pygame.KEYDOWN:
                #-----------------------------------------------------------------
                # 判斷按下ESC按鈕
                if event.key == pygame.K_ESCAPE:
                    running = False
                # 除錯訊息開關.
                elif event.key == pygame.K_d:
                    tetris.debug_message = not tetris.debug_message             
                elif event.key == pygame.K_s:
                    tetris.savedBricks()
                    updateSavedBricksPicture()   
                #-----------------------------------------------------------------
                # 變換方塊-上.
                elif event.key == pygame.K_UP:
                    # 在右邊界不能旋轉.
                    if (tetris.container_x == 8):
                        break
                    # 判斷磚塊N1、N2、I.
                    if (tetris.brick_id == 1 or tetris.brick_id == 2 or tetris.brick_id == 7):
                        # 長條方塊旋轉例外處理.
                        if (tetris.brick_id == 7):
                            if (tetris.container_x < 0 or tetris.container_x == 7):
                                break
                        # 旋轉方塊.
                        tetris.brick_state = tetris.brick_state + 1
                        if (tetris.brick_state > 1):
                            tetris.brick_state = 0                    
                        # 轉換定義方塊到方塊陣列.
                        tetris.bricks =  tetris.transformToBricks(tetris.brick_id, tetris.brick_state)
                        # 碰到磚塊. 不能換
                        if (not tetris.ifTouchBottom(tetris.bricks,[tetris.container_x, tetris.container_y])):
                            brick_state = brick_state - 1
                            if (brick_state < 0):
                                brick_state = 1
                    # 判斷磚跨L1、L2、T.                                
                    elif (tetris.brick_id == 3 or tetris.brick_id == 4 or tetris.brick_id == 5):
                        # 旋轉方塊.
                        tetris.brick_state = tetris.brick_state + 1
                        if (tetris.brick_state > 3):
                            tetris.brick_state = 0                    
                        # 轉換定義方塊到方塊陣列.
                        tetris.bricks =  tetris.transformToBricks(tetris.brick_id, tetris.brick_state)
                        # 碰到磚塊. 不能換
                        if (not tetris.ifTouchBottom(tetris.bricks,[tetris.container_x, tetris.container_y])):
                            tetris.brick_state = tetris.brick_state - 1
                            if (tetris.brick_state < 0):
                                tetris.brick_state = 3
                #-----------------------------------------------------------------
                # 快速下降-下.
                elif event.key == pygame.K_DOWN:
                    # 磚塊快速下降.
                    tetris.brick_down_speed /= 20
                #-----------------------------------------------------------------
                # 移動方塊-左.
                elif event.key == pygame.K_LEFT:
                    tetris.container_x = tetris.container_x - 1
                    if (tetris.container_x < 0):
                        if (tetris.container_x == -1):
                            if (tetris.bricks[0][0] != 0 or tetris.bricks[0][1] != 0 or tetris.bricks[0][2] != 0 or tetris.bricks[0][3] != 0):
                                tetris.container_x = tetris.container_x + 1
                        elif (tetris.container_x == -2): 
                            if (tetris.bricks[1][0] != 0 or tetris.bricks[1][1] != 0 or tetris.bricks[1][2] != 0 or tetris.bricks[1][3] != 0):
                                tetris.container_x = tetris.container_x + 1
                        else:
                            tetris.container_x = tetris.container_x + 1
                    # 碰到磚塊.
                    if (not tetris.ifTouchBottom(tetris.bricks,[tetris.container_x, tetris.container_y])):
                        tetris.container_x = tetris.container_x + 1
                #-----------------------------------------------------------------
                # 移動方塊-右.
                elif event.key == pygame.K_RIGHT:
                    tetris.container_x = tetris.container_x + 1
                    if (tetris.container_x > 6):
                        if (tetris.container_x == 7):
                            if (tetris.bricks[3][0] != 0 or tetris.bricks[3][1] != 0 or tetris.bricks[3][2] != 0 or tetris.bricks[3][3] != 0):
                                tetris.container_x = tetris.container_x - 1;                        
                        elif (tetris.container_x == 8):
                            if (tetris.bricks[2][0] != 0 or tetris.bricks[2][1] != 0 or tetris.bricks[2][2] != 0 or tetris.bricks[2][3] != 0):
                                tetris.container_x = tetris.container_x - 1                        
                        else:
                            tetris.container_x = tetris.container_x - 1
                    # 碰到磚塊.
                    if (not tetris.ifTouchBottom(tetris.bricks,[tetris.container_x, tetris.container_y])):
                        tetris.container_x = tetris.container_x - 1                    
            #-----------------------------------------------------------------
            # 判斷放開按鈕
            if event.type == pygame.KEYUP:
                # 快速下降-下.
                if event.key == pygame.K_DOWN:
                    # 恢復正常下降速度.
                    tetris.brick_down_speed = tetris.BRICK_DOWN_SPEED
            
        #---------------------------------------------------------------------    
        # 清除畫面.
        canvas.fill(colorDict[7])

        # 遊戲中.
        # 處理磚塊下降.
        if(time_now >= tetris.brick_down_speed):
            # 往下降.
            tetris.container_y = tetris.container_y + 1; 
            # 碰到磚塊.
            if (not tetris.ifTouchBottom(tetris.bricks,[tetris.container_x, tetris.container_y])):
                #產生新塊.
                tetris.nextRound()    
            else:
                tetris.bricks =  tetris.transformToBricks(tetris.brick_id, tetris.brick_state)     
            # 清除時脈.
            time_now = 0
        #---------------------------------------------------------------------
        if(time_round >= 20):
            tetris.faster()
            time_round = 0
        updateNextBricksPicture()  
        updateSavedBricksPicture()
        # 更新繪圖.
        pos_y = 20
        
        # ColorVer:設定背景顏色.
        background.color = colorDict[1]
        # 更新背景區塊.
        background.update()
        for y in range(20):
            pos_x = 280
            for x in range(10):
                if(tetris.board[x][y] != 0):
                    bricks_box[x][y].rect[0] = pos_x
                    bricks_box[x][y].rect[1] = pos_y
                    # ColorVer:依照方塊編號設定顏色.
                    bricks_box[x][y].color = colorVerDict[tetris.board[x][y]]
                    bricks_box[x][y].update()
                else:
                    bricks_box[x][y].color = colorDict[5]

                pos_x = pos_x + 28
            pos_y = pos_y + 28    
        
        # 更新掉落中方塊
        for y in range(4):
            for x in range(4):            
                if (tetris.bricks[x][y] != 0):
                    posX = tetris.container_x + x
                    posY = tetris.container_y + y
                    if (posX >= 0 and posY >= 0):
                        bricks_box[posX][posY].rect[0] = (posX * 28) + 280
                        bricks_box[posX][posY].rect[1] = (posY * 28) + 20
                        # ColorVer:依照方塊編號設定顏色.
                        if (tetris.bricks[x][y] <= 7):
                            bricks_box[posX][posY].color = colorVerDict[tetris.bricks[x][y]]
                        elif (tetris.bricks[x][y]==9):
                            bricks_box[posX][posY].color = colorDict[2] #white
                        bricks_box[posX][posY].update()
        
        #---------------------------------------------------------------------    
        # 除錯訊息.
        if(tetris.debug_message == True):
            # 更新容器.
            str_x = ""
            pos_x = 15
            pos_y = 20
            for y in range(20):
                str_x = ""
                for x in range(10):
                    str_x = str_x + str(tetris.board[x][y]) + " "
                showFont( str_x, pos_x, pos_y, colorDict[3])
                pos_y = pos_y + 28
                
            # 更新方塊
            posX = 0
            posY = 0    
            for y in range(4):
                str_x = ""
                for x in range(4):            
                    if (tetris.bricks[x][y] != 0):
                        posX = tetris.container_x + x
                        posY = tetris.container_y + y
                        if (posX >= 0 and posY >= 0):
                            str_x = str_x + str(tetris.bricks[x][y]) + " "
                    else:
                        str_x = str_x + "  "
                pos_x = 15 + (tetris.container_x * 26)
                pos_y = 20 + (posY * 28)
                showFont( str_x, pos_x, pos_y, colorDict[2])

        # ColorVer:顯示訊息.
        showFont( u"Next Brick", 588, 16, colorDict[1])
        showFont( u"Saved Brick", 588, 180, colorDict[1])
        showFont( u"Max Score", 588, 340, colorDict[1])
        showFont( str(int(tetris.score_max)), 588, 370, colorDict[1])

        showFont( u"Score", 588, 410, colorDict[1])
        showFont( str(int(tetris.score)), 588, 440, colorDict[1])

        # 顯示FPS.
        # 除錯訊息.
        if(tetris.debug_message):    
            showFont( u"FPS:" + str(clock.get_fps()), 6, 0, colorDict[7])    

        # 更新畫面.
        pygame.display.update()
        clock.tick(240)
def ai_start():
    tetris.start()
    tetris.BRICK_DOWN_SPEED = 0.05
    pygame.event.post(pygame.event.Event(KEYDOWN, key=K_s))
    
def ai_mode():
    global tetris
    ai_start()
    running = True
    time_temp = time.time()
    time_round = 0
    time_now = 0
    pygame.mixer.music.load("rush-e.mp3")
    pygame.mixer.music.play(loops=-1)
    while running:
        # 計算時脈.
        tetris.brick_down_speed = tetris.BRICK_DOWN_SPEED
        time_now = time_now + (time.time() - time_temp)
        time_round = time_round + (time.time() - time_temp)
        time_temp = time.time()
        #---------------------------------------------------------------------
        # 判斷輸入.
        #---------------------------------------------------------------------
        for event in pygame.event.get():
            # 離開遊戲.
            if event.type == pygame.QUIT:
                running = False        
            # 判斷按下按鈕
            if event.type == pygame.KEYDOWN:
                #-----------------------------------------------------------------
                # 判斷按下ESC按鈕
                if event.key == pygame.K_ESCAPE:
                    running = False
                # 除錯訊息開關.
                elif event.key == pygame.K_d:
                    tetris.debug_message = not tetris.debug_message             
                elif event.key == pygame.K_s:
                    tetris.savedBricks()
                    updateSavedBricksPicture()   
                #-----------------------------------------------------------------
                # 變換方塊-上.
                elif event.key == pygame.K_UP:
                    # 在右邊界不能旋轉.
                    if (tetris.container_x == 8):
                        break
                    # 判斷磚塊N1、N2、I.
                    if (tetris.brick_id == 1 or tetris.brick_id == 2 or tetris.brick_id == 7):
                        # 長條方塊旋轉例外處理.
                        if (tetris.brick_id == 7):
                            if (tetris.container_x < 0 or tetris.container_x == 7):
                                break
                        # 旋轉方塊.
                        tetris.brick_state = tetris.brick_state + 1
                        if (tetris.brick_state > 1):
                            tetris.brick_state = 0                    
                        # 轉換定義方塊到方塊陣列.
                        tetris.bricks =  tetris.transformToBricks(tetris.brick_id, tetris.brick_state)
                        # 碰到磚塊. 不能換
                        if (not tetris.ifTouchBottom(tetris.bricks,[tetris.container_x, tetris.container_y])):
                            brick_state = brick_state - 1
                            if (brick_state < 0):
                                brick_state = 1
                    # 判斷磚跨L1、L2、T.                                
                    elif (tetris.brick_id == 3 or tetris.brick_id == 4 or tetris.brick_id == 5):
                        # 旋轉方塊.
                        tetris.brick_state = tetris.brick_state + 1
                        if (tetris.brick_state > 3):
                            tetris.brick_state = 0                    
                        # 轉換定義方塊到方塊陣列.
                        tetris.bricks =  tetris.transformToBricks(tetris.brick_id, tetris.brick_state)
                        # 碰到磚塊. 不能換
                        if (not tetris.ifTouchBottom(tetris.bricks,[tetris.container_x, tetris.container_y])):
                            tetris.brick_state = tetris.brick_state - 1
                            if (tetris.brick_state < 0):
                                tetris.brick_state = 3
                #-----------------------------------------------------------------
                # 移動方塊-左.
                elif event.key == pygame.K_LEFT:
                    tetris.container_x = tetris.container_x - 1
                    if (tetris.container_x < 0):
                        if (tetris.container_x == -1):
                            if (tetris.bricks[0][0] != 0 or tetris.bricks[0][1] != 0 or tetris.bricks[0][2] != 0 or tetris.bricks[0][3] != 0):
                                tetris.container_x = tetris.container_x + 1
                        elif (tetris.container_x == -2): 
                            if (tetris.bricks[1][0] != 0 or tetris.bricks[1][1] != 0 or tetris.bricks[1][2] != 0 or tetris.bricks[1][3] != 0):
                                tetris.container_x = tetris.container_x + 1
                        else:
                            tetris.container_x = tetris.container_x + 1
                    # 碰到磚塊.
                    if (not tetris.ifTouchBottom(tetris.bricks,[tetris.container_x, tetris.container_y])):
                        tetris.container_x = tetris.container_x + 1
                #-----------------------------------------------------------------
                # 移動方塊-右.
                elif event.key == pygame.K_RIGHT:
                    tetris.container_x = tetris.container_x + 1
                    if (tetris.container_x > 6):
                        if (tetris.container_x == 7):
                            if (tetris.bricks[3][0] != 0 or tetris.bricks[3][1] != 0 or tetris.bricks[3][2] != 0 or tetris.bricks[3][3] != 0):
                                tetris.container_x = tetris.container_x - 1;                        
                        elif (tetris.container_x == 8):
                            if (tetris.bricks[2][0] != 0 or tetris.bricks[2][1] != 0 or tetris.bricks[2][2] != 0 or tetris.bricks[2][3] != 0):
                                tetris.container_x = tetris.container_x - 1                        
                        else:
                            tetris.container_x = tetris.container_x - 1
                    # 碰到磚塊.
                    if (not tetris.ifTouchBottom(tetris.bricks,[tetris.container_x, tetris.container_y])):
                        tetris.container_x = tetris.container_x - 1                    
            #-----------------------------------------------------------------
        
            
        #---------------------------------------------------------------------    
        # 清除畫面.
        canvas.fill(colorDict[7])

        # 遊戲中.
        # 處理磚塊下降.
        if(time_now >= tetris.brick_down_speed):
            # 往下降.
            tetris.container_y = tetris.container_y + 1; 
            # 碰到磚塊.
            if (not tetris.ifTouchBottom(tetris.bricks ,[tetris.container_x, tetris.container_y])):
                #產生新塊.
                tetris.nextRound()  
                pygame.event.clear()
                ai_next = tetris.newrobot(tetris.container_x,tetris.brick_state)
                if(ai_next[0] == 1):
                    pygame.event.post(pygame.event.Event(KEYDOWN, key=K_s))
                    pygame.event.post(pygame.event.Event(KEYUP, key=K_s))
                for i in range(ai_next[1]):
                    pygame.event.post(pygame.event.Event(KEYDOWN, key=K_UP))
                    pygame.event.post(pygame.event.Event(KEYUP, key=K_UP))
                if( ai_next[2] < 0):
                    for i in range(-ai_next[2]):
                        pygame.event.post(pygame.event.Event(KEYDOWN, key=K_LEFT))
                        pygame.event.post(pygame.event.Event(KEYUP, key=K_LEFT))
                else:
                    for i in range(ai_next[2]):
                        pygame.event.post(pygame.event.Event(KEYDOWN, key=K_RIGHT))
                        pygame.event.post(pygame.event.Event(KEYUP, key=K_RIGHT))
            else:
                tetris.bricks =  tetris.transformToBricks(tetris.brick_id, tetris.brick_state)      
            # 清除時脈.
            time_now = 0
        
        if(time_round >= 10):
            tetris.faster()
            time_round = 0
        #---------------------------------------------------------------------
        updateNextBricksPicture()  
        updateSavedBricksPicture()
        # 更新繪圖.
        pos_y = 20
        
        # ColorVer:設定背景顏色.
        background.color = colorDict[1]
        # 更新背景區塊.
        background.update()
        for y in range(20):
            pos_x = 280
            for x in range(10):
                if(tetris.board[x][y] != 0):
                    bricks_box[x][y].rect[0] = pos_x
                    bricks_box[x][y].rect[1] = pos_y
                    # ColorVer:依照方塊編號設定顏色.
                    bricks_box[x][y].color = colorVerDict[tetris.board[x][y]]
                    bricks_box[x][y].update()
                else:
                    bricks_box[x][y].color = colorDict[5]

                pos_x = pos_x + 28
            pos_y = pos_y + 28    
        
        # 更新掉落中方塊
        for y in range(4):
            for x in range(4):            
                if (tetris.bricks[x][y] != 0):
                    posX = tetris.container_x + x
                    posY = tetris.container_y + y
                    if (posX >= 0 and posY >= 0):
                        bricks_box[posX][posY].rect[0] = (posX * 28) + 280
                        bricks_box[posX][posY].rect[1] = (posY * 28) + 20
                        # ColorVer:依照方塊編號設定顏色.
                        if (tetris.bricks[x][y] <= 7):
                            bricks_box[posX][posY].color = colorVerDict[tetris.bricks[x][y]]
                        elif (tetris.bricks[x][y]==9):
                            bricks_box[posX][posY].color = colorDict[2] #white
                        bricks_box[posX][posY].update()
        
        #---------------------------------------------------------------------    
        # 除錯訊息.
        if(tetris.debug_message == True):
            # 更新容器.
            str_x = ""
            pos_x = 15
            pos_y = 20
            for y in range(20):
                str_x = ""
                for x in range(10):
                    str_x = str_x + str(tetris.board[x][y]) + " "
                showFont( str_x, pos_x, pos_y, colorDict[3])
                pos_y = pos_y + 28
                
            # 更新方塊
            posX = 0
            posY = 0    
            for y in range(4):
                str_x = ""
                for x in range(4):            
                    if (tetris.bricks[x][y] != 0):
                        posX = tetris.container_x + x
                        posY = tetris.container_y + y
                        if (posX >= 0 and posY >= 0):
                            str_x = str_x + str(tetris.bricks[x][y]) + " "
                    else:
                        str_x = str_x + "  "
                pos_x = 15 + (tetris.container_x * 26)
                pos_y = 20 + (posY * 28)
                showFont( str_x, pos_x, pos_y, colorDict[2])

        # ColorVer:顯示訊息.
        showFont( u"Next Brick", 588, 16, colorDict[1])
        showFont( u"Saved Brick", 588, 180, colorDict[1])
        showFont( u"Max Score", 588, 340, colorDict[1])
        showFont( str(int(tetris.score_max)), 588, 370, colorDict[1])

        showFont( u"Score", 588, 410, colorDict[1])
        showFont( str(int(tetris.score)), 588, 440, colorDict[1])

        # 顯示FPS.
        # 除錯訊息.
        if(tetris.debug_message):    
            showFont( u"FPS:" + str(clock.get_fps()), 6, 0, colorDict[7])    

        # 更新畫面.
        pygame.display.update()
        clock.tick(240)
def ai_mode2():
    global tetris
    ai_start()
    running = True
    time_temp = time.time()
    time_round = 0
    time_now = 0
    pygame.mixer.music.load("rush-e.mp3")
    pygame.mixer.music.play(loops=-1)
    while running:
        # 計算時脈.
        tetris.brick_down_speed = tetris.BRICK_DOWN_SPEED
        time_now = time_now + (time.time() - time_temp)
        time_round = time_round + (time.time() - time_temp)
        time_temp = time.time() 
        #---------------------------------------------------------------------
        # 判斷輸入.
        #---------------------------------------------------------------------
        for event in pygame.event.get():
            # 離開遊戲.
            if event.type == pygame.QUIT:
                running = False        
            # 判斷按下按鈕
            if event.type == pygame.KEYDOWN:
                #-----------------------------------------------------------------
                # 判斷按下ESC按鈕
                if event.key == pygame.K_ESCAPE:
                    running = False
                # 除錯訊息開關.
                elif event.key == pygame.K_d:
                    tetris.debug_message = not tetris.debug_message             
                elif event.key == pygame.K_s:
                    tetris.savedBricks()
                    updateSavedBricksPicture()   
                #-----------------------------------------------------------------
                # 變換方塊-上.
                elif event.key == pygame.K_UP:
                    # 在右邊界不能旋轉.
                    if (tetris.container_x == 8):
                        break
                    # 判斷磚塊N1、N2、I.
                    if (tetris.brick_id == 1 or tetris.brick_id == 2 or tetris.brick_id == 7):
                        # 長條方塊旋轉例外處理.
                        if (tetris.brick_id == 7):
                            if (tetris.container_x < 0 or tetris.container_x == 7):
                                break
                        # 旋轉方塊.
                        tetris.brick_state = tetris.brick_state + 1
                        if (tetris.brick_state > 1):
                            tetris.brick_state = 0                    
                        # 轉換定義方塊到方塊陣列.
                        tetris.bricks =  tetris.transformToBricks(tetris.brick_id, tetris.brick_state)
                        # 碰到磚塊. 不能換
                        if (not tetris.ifTouchBottom(tetris.bricks,[tetris.container_x, tetris.container_y])):
                            brick_state = brick_state - 1
                            if (brick_state < 0):
                                brick_state = 1
                    # 判斷磚跨L1、L2、T.                                
                    elif (tetris.brick_id == 3 or tetris.brick_id == 4 or tetris.brick_id == 5):
                        # 旋轉方塊.
                        tetris.brick_state = tetris.brick_state + 1
                        if (tetris.brick_state > 3):
                            tetris.brick_state = 0                    
                        # 轉換定義方塊到方塊陣列.
                        tetris.bricks =  tetris.transformToBricks(tetris.brick_id, tetris.brick_state)
                        # 碰到磚塊. 不能換
                        if (not tetris.ifTouchBottom(tetris.bricks,[tetris.container_x, tetris.container_y])):
                            tetris.brick_state = tetris.brick_state - 1
                            if (tetris.brick_state < 0):
                                tetris.brick_state = 3
                #-----------------------------------------------------------------
                # 移動方塊-左.
                elif event.key == pygame.K_LEFT:
                    tetris.container_x = tetris.container_x - 1
                    if (tetris.container_x < 0):
                        if (tetris.container_x == -1):
                            if (tetris.bricks[0][0] != 0 or tetris.bricks[0][1] != 0 or tetris.bricks[0][2] != 0 or tetris.bricks[0][3] != 0):
                                tetris.container_x = tetris.container_x + 1
                        elif (tetris.container_x == -2): 
                            if (tetris.bricks[1][0] != 0 or tetris.bricks[1][1] != 0 or tetris.bricks[1][2] != 0 or tetris.bricks[1][3] != 0):
                                tetris.container_x = tetris.container_x + 1
                        else:
                            tetris.container_x = tetris.container_x + 1
                    # 碰到磚塊.
                    if (not tetris.ifTouchBottom(tetris.bricks,[tetris.container_x, tetris.container_y])):
                        tetris.container_x = tetris.container_x + 1
                #-----------------------------------------------------------------
                # 移動方塊-右.
                elif event.key == pygame.K_RIGHT:
                    tetris.container_x = tetris.container_x + 1
                    if (tetris.container_x > 6):
                        if (tetris.container_x == 7):
                            if (tetris.bricks[3][0] != 0 or tetris.bricks[3][1] != 0 or tetris.bricks[3][2] != 0 or tetris.bricks[3][3] != 0):
                                tetris.container_x = tetris.container_x - 1;                        
                        elif (tetris.container_x == 8):
                            if (tetris.bricks[2][0] != 0 or tetris.bricks[2][1] != 0 or tetris.bricks[2][2] != 0 or tetris.bricks[2][3] != 0):
                                tetris.container_x = tetris.container_x - 1                        
                        else:
                            tetris.container_x = tetris.container_x - 1
                    # 碰到磚塊.
                    if (not tetris.ifTouchBottom(tetris.bricks,[tetris.container_x, tetris.container_y])):
                        tetris.container_x = tetris.container_x - 1                    
            #-----------------------------------------------------------------
        
            
        #---------------------------------------------------------------------    
        # 清除畫面.
        canvas.fill(colorDict[7])

        # 遊戲中.
        # 處理磚塊下降.
        if(time_now >= tetris.brick_down_speed):
            # 往下降.
            tetris.container_y = tetris.container_y + 1; 
            # 碰到磚塊.
            if (not tetris.ifTouchBottom(tetris.bricks,[tetris.container_x, tetris.container_y])):
                #產生新塊.
                tetris.nextRound() 
                pygame.event.clear()
                ai_move = tetris.get_best_action()
                print(ai_move)
                for i in range(ai_move[1]):
                    pygame.event.post(pygame.event.Event(KEYDOWN, key=K_UP))
                    pygame.event.post(pygame.event.Event(KEYUP, key=K_UP))
                if( ai_move[0] < 0):
                    for i in range(-ai_move[0]):
                        pygame.event.post(pygame.event.Event(KEYDOWN, key=K_LEFT))
                        pygame.event.post(pygame.event.Event(KEYUP, key=K_LEFT))
                else:
                    for i in range(ai_move[0]):
                        pygame.event.post(pygame.event.Event(KEYDOWN, key=K_RIGHT))
                        pygame.event.post(pygame.event.Event(KEYUP, key=K_RIGHT)) 
            else:
                tetris.bricks =  tetris.transformToBricks(tetris.brick_id, tetris.brick_state)      
            # 清除時脈.
            time_now = 0
        
        if(time_round >= 10):
            tetris.faster()
            time_round = 0
        #---------------------------------------------------------------------
        updateNextBricksPicture()  
        updateSavedBricksPicture()
        # 更新繪圖.
        pos_y = 20
        
        # ColorVer:設定背景顏色.
        background.color = colorDict[1]
        # 更新背景區塊.
        background.update()
        for y in range(20):
            pos_x = 280
            for x in range(10):
                if(tetris.board[x][y] != 0):
                    bricks_box[x][y].rect[0] = pos_x
                    bricks_box[x][y].rect[1] = pos_y
                    # ColorVer:依照方塊編號設定顏色.
                    bricks_box[x][y].color = colorVerDict[tetris.board[x][y]]
                    bricks_box[x][y].update()
                else:
                    bricks_box[x][y].color = colorDict[5]

                pos_x = pos_x + 28
            pos_y = pos_y + 28    
        
        # 更新掉落中方塊
        for y in range(4):
            for x in range(4):            
                if (tetris.bricks[x][y] != 0):
                    posX = tetris.container_x + x
                    posY = tetris.container_y + y
                    if (posX >= 0 and posY >= 0):
                        bricks_box[posX][posY].rect[0] = (posX * 28) + 280
                        bricks_box[posX][posY].rect[1] = (posY * 28) + 20
                        # ColorVer:依照方塊編號設定顏色.
                        if (tetris.bricks[x][y] <= 7):
                            bricks_box[posX][posY].color = colorVerDict[tetris.bricks[x][y]]
                        elif (tetris.bricks[x][y]==9):
                            bricks_box[posX][posY].color = colorDict[2] #white
                        bricks_box[posX][posY].update()
        
        #---------------------------------------------------------------------    
        # 除錯訊息.
        if(tetris.debug_message == True):
            # 更新容器.
            str_x = ""
            pos_x = 15
            pos_y = 20
            for y in range(20):
                str_x = ""
                for x in range(10):
                    str_x = str_x + str(tetris.board[x][y]) + " "
                showFont( str_x, pos_x, pos_y, colorDict[3])
                pos_y = pos_y + 28
                
            # 更新方塊
            posX = 0
            posY = 0    
            for y in range(4):
                str_x = ""
                for x in range(4):            
                    if (tetris.bricks[x][y] != 0):
                        posX = tetris.container_x + x
                        posY = tetris.container_y + y
                        if (posX >= 0 and posY >= 0):
                            str_x = str_x + str(tetris.bricks[x][y]) + " "
                    else:
                        str_x = str_x + "  "
                pos_x = 15 + (tetris.container_x * 26)
                pos_y = 20 + (posY * 28)
                showFont( str_x, pos_x, pos_y, colorDict[2])

        # ColorVer:顯示訊息.
        showFont( u"Next Brick", 588, 16, colorDict[1])
        showFont( u"Saved Brick", 588, 180, colorDict[1])
        showFont( u"Max Score", 588, 340, colorDict[1])
        showFont( str(int(tetris.score_max)), 588, 370, colorDict[1])

        showFont( u"Score", 588, 410, colorDict[1])
        showFont( str(int(tetris.score)), 588, 440, colorDict[1])

        # 顯示FPS.
        # 除錯訊息.
        if(tetris.debug_message):    
            showFont( u"FPS:" + str(clock.get_fps()), 6, 0, colorDict[7])    

        # 更新畫面.
        pygame.display.update()
        clock.tick(240)
def training_mode():
    global tetris
    tetris.start_quiz()
    running = True
    time_temp = time.time()
    end = 0
    time_now = 0
    choice = 0
    while running:
        # 計算時脈.
        time_now = time_now + (time.time() - time_temp)
        time_temp = time.time()
        #---------------------------------------------------------------------
        # 判斷輸入.
        #---------------------------------------------------------------------
        for event in pygame.event.get():
            # 離開遊戲.
            if event.type == pygame.QUIT:
                running = False        
            # 判斷按下按鈕
            if event.type == pygame.KEYDOWN:
                #-----------------------------------------------------------------
                # 判斷按下ESC按鈕
                if event.key == pygame.K_ESCAPE:
                    running = False
                # 除錯訊息開關.
                elif event.key == pygame.K_d:
                    tetris.debug_message = not tetris.debug_message             
                elif event.key == pygame.K_s:
                    tetris.savedBricks()
                    updateSavedBricksPicture()   
                #-----------------------------------------------------------------
                # 變換方塊-上.
                elif event.key == pygame.K_UP:
                    # 在右邊界不能旋轉.
                    if (tetris.container_x == 8):
                        break
                    # 判斷磚塊N1、N2、I.
                    if (tetris.brick_id == 1 or tetris.brick_id == 2 or tetris.brick_id == 7):
                        # 長條方塊旋轉例外處理.
                        if (tetris.brick_id == 7):
                            if (tetris.container_x < 0 or tetris.container_x == 7):
                                break
                        # 旋轉方塊.
                        tetris.brick_state = tetris.brick_state + 1
                        if (tetris.brick_state > 1):
                            tetris.brick_state = 0                    
                        # 轉換定義方塊到方塊陣列.
                        tetris.bricks =  tetris.transformToBricks(tetris.brick_id, tetris.brick_state)
                        # 碰到磚塊. 不能換
                        if (not tetris.ifTouchBottom(tetris.bricks,[tetris.container_x, tetris.container_y])):
                            brick_state = brick_state - 1
                            if (brick_state < 0):
                                brick_state = 1
                    # 判斷磚跨L1、L2、T.                                
                    elif (tetris.brick_id == 3 or tetris.brick_id == 4 or tetris.brick_id == 5):
                        # 旋轉方塊.
                        tetris.brick_state = tetris.brick_state + 1
                        if (tetris.brick_state > 3):
                            tetris.brick_state = 0                    
                        # 轉換定義方塊到方塊陣列.
                        tetris.bricks =  tetris.transformToBricks(tetris.brick_id, tetris.brick_state)
                        # 碰到磚塊. 不能換
                        if (not tetris.ifTouchBottom(tetris.bricks,[tetris.container_x, tetris.container_y])):
                            tetris.brick_state = tetris.brick_state - 1
                            if (tetris.brick_state < 0):
                                tetris.brick_state = 3
                #-----------------------------------------------------------------
                # 快速下降-下.
                elif event.key == pygame.K_DOWN:
                    # 磚塊快速下降.
                    tetris.brick_down_speed /= 20
                #-----------------------------------------------------------------
                # 移動方塊-左.
                elif event.key == pygame.K_LEFT:
                    tetris.container_x = tetris.container_x - 1
                    if (tetris.container_x < 0):
                        if (tetris.container_x == -1):
                            if (tetris.bricks[0][0] != 0 or tetris.bricks[0][1] != 0 or tetris.bricks[0][2] != 0 or tetris.bricks[0][3] != 0):
                                tetris.container_x = tetris.container_x + 1
                        elif (tetris.container_x == -2): 
                            if (tetris.bricks[1][0] != 0 or tetris.bricks[1][1] != 0 or tetris.bricks[1][2] != 0 or tetris.bricks[1][3] != 0):
                                tetris.container_x = tetris.container_x + 1
                        else:
                            tetris.container_x = tetris.container_x + 1
                    # 碰到磚塊.
                    if (not tetris.ifTouchBottom(tetris.bricks,[tetris.container_x, tetris.container_y])):
                        tetris.container_x = tetris.container_x + 1
                #-----------------------------------------------------------------
                # 移動方塊-右.
                elif event.key == pygame.K_RIGHT:
                    tetris.container_x = tetris.container_x + 1
                    if (tetris.container_x > 6):
                        if (tetris.container_x == 7):
                            if (tetris.bricks[3][0] != 0 or tetris.bricks[3][1] != 0 or tetris.bricks[3][2] != 0 or tetris.bricks[3][3] != 0):
                                tetris.container_x = tetris.container_x - 1;                        
                        elif (tetris.container_x == 8):
                            if (tetris.bricks[2][0] != 0 or tetris.bricks[2][1] != 0 or tetris.bricks[2][2] != 0 or tetris.bricks[2][3] != 0):
                                tetris.container_x = tetris.container_x - 1                        
                        else:
                            tetris.container_x = tetris.container_x - 1
                    # 碰到磚塊.
                    if (not tetris.ifTouchBottom(tetris.bricks,[tetris.container_x, tetris.container_y])):
                        tetris.container_x = tetris.container_x - 1                    
            #-----------------------------------------------------------------
            # 判斷放開按鈕
            if event.type == pygame.KEYUP:
                # 快速下降-下.
                if event.key == pygame.K_DOWN:
                    # 恢復正常下降速度.
                    tetris.brick_down_speed = tetris.BRICK_DOWN_SPEED
            
        #---------------------------------------------------------------------    
        # 清除畫面.
        canvas.fill(colorDict[7])

        # 遊戲中.
        # 處理磚塊下降.
        if(time_now >= tetris.brick_down_speed):
            # 往下降.
            tetris.container_y = tetris.container_y + 1; 
            # 碰到磚塊.
            if (not tetris.ifTouchBottom(tetris.bricks,[tetris.container_x, tetris.container_y]) and end == 0):
                #產生新塊.
                x = tetris.container_x
                block_type = tetris.brick_state
                tetris.container_x = 3
                tetris.container_y = -4
                tetris.brick_state = 0
                pygame.event.clear()
                ai_next = tetris.newrobot(x, block_type)
                choice = ai_next[3]
                tetris.score += (35 - ai_next[3])*10
                pygame.event.clear()
                if(ai_next[0] == 1):
                    pygame.event.post(pygame.event.Event(KEYDOWN, key=K_s))
                    pygame.event.post(pygame.event.Event(KEYUP, key=K_s))
                for i in range(ai_next[1]):
                    pygame.event.post(pygame.event.Event(KEYDOWN, key=K_UP))
                    pygame.event.post(pygame.event.Event(KEYUP, key=K_UP))
                if( ai_next[2] < 0):
                    for i in range(-ai_next[2]):
                        pygame.event.post(pygame.event.Event(KEYDOWN, key=K_LEFT))
                        pygame.event.post(pygame.event.Event(KEYUP, key=K_LEFT))
                else:
                    for i in range(ai_next[2]):
                        pygame.event.post(pygame.event.Event(KEYDOWN, key=K_RIGHT))
                        pygame.event.post(pygame.event.Event(KEYUP, key=K_RIGHT))
                end = 1
            if (not tetris.ifTouchBottom(tetris.bricks,[tetris.container_x, tetris.container_y]) and end == 1):
                tetris.nextQuiz()  
                end = 0
                pygame.event.set_allowed(pygame.KEYDOWN)
                pygame.event.set_allowed(pygame.KEYUP)
            else:
                tetris.bricks =  tetris.transformToBricks(tetris.brick_id, tetris.brick_state)      
            # 清除時脈.
            time_now = 0
        #---------------------------------------------------------------------
        updateNextBricksPicture()  
        updateSavedBricksPicture()
        # 更新繪圖.
        pos_y = 20
        
        # ColorVer:設定背景顏色.
        background.color = colorDict[1]
        # 更新背景區塊.
        background.update()
        for y in range(20):
            pos_x = 280
            for x in range(10):
                if(tetris.board[x][y] != 0):
                    bricks_box[x][y].rect[0] = pos_x
                    bricks_box[x][y].rect[1] = pos_y
                    # ColorVer:依照方塊編號設定顏色.
                    bricks_box[x][y].color = colorVerDict[tetris.board[x][y]]
                    bricks_box[x][y].update()
                else:
                    bricks_box[x][y].color = colorDict[5]

                pos_x = pos_x + 28
            pos_y = pos_y + 28    
        
        # 更新掉落中方塊
        for y in range(4):
            for x in range(4):            
                if (tetris.bricks[x][y] != 0):
                    posX = tetris.container_x + x
                    posY = tetris.container_y + y
                    if (posX >= 0 and posY >= 0):
                        bricks_box[posX][posY].rect[0] = (posX * 28) + 280
                        bricks_box[posX][posY].rect[1] = (posY * 28) + 20
                        # ColorVer:依照方塊編號設定顏色.
                        if (tetris.bricks[x][y] <= 7):
                            bricks_box[posX][posY].color = colorVerDict[tetris.bricks[x][y]]
                        elif (tetris.bricks[x][y]==9):
                            bricks_box[posX][posY].color = colorDict[2] #white
                        bricks_box[posX][posY].update()
        
        #---------------------------------------------------------------------    
        # 除錯訊息.
        if(tetris.debug_message == True):
            # 更新容器.
            str_x = ""
            pos_x = 15
            pos_y = 20
            for y in range(20):
                str_x = ""
                for x in range(10):
                    str_x = str_x + str(tetris.board[x][y]) + " "
                showFont( str_x, pos_x, pos_y, colorDict[3])
                pos_y = pos_y + 28
                
            # 更新方塊
            posX = 0
            posY = 0    
            for y in range(4):
                str_x = ""
                for x in range(4):            
                    if (tetris.bricks[x][y] != 0):
                        posX = tetris.container_x + x
                        posY = tetris.container_y + y
                        if (posX >= 0 and posY >= 0):
                            str_x = str_x + str(tetris.bricks[x][y]) + " "
                    else:
                        str_x = str_x + "  "
                pos_x = 15 + (tetris.container_x * 26)
                pos_y = 20 + (posY * 28)
                showFont( str_x, pos_x, pos_y, colorDict[2])

        # ColorVer:顯示訊息.
        showFont( u"Next Brick", 588, 16, colorDict[1])
        showFont( u"Saved Brick", 588, 180, colorDict[1])
        showFont( u"Max Score", 588, 340, colorDict[1])
        showFont( str(int(tetris.score_max)), 588, 370, colorDict[1])
        if(end == 1):
            showFont( u"You Choice is No."+str(choice), 0, 16, colorDict[1])
        showFont( u"Score", 588, 410, colorDict[1])
        showFont( str(int(tetris.score)), 588, 440, colorDict[1])

        # 顯示FPS.
        # 除錯訊息.
        if(tetris.debug_message):    
            showFont( u"FPS:" + str(clock.get_fps()), 6, 0, colorDict[7])    

        # 更新畫面.
        pygame.display.update()
        clock.tick(240)

mainloop()
# 離開遊戲.
pygame.mixer.music.stop()
pygame.mixer.quit()
pygame.quit()
quit()