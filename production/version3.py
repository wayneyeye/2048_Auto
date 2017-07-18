import sys,os
import concurrent.futures
import getpass
from selenium import webdriver #install selenium
from selenium.webdriver.common.keys import Keys
import time,random,string
#put geckodriver into the working directory
geckodriver_path=(os.path.join(os.getcwd(),'geckodriver-dir'))#this is wrong search path for modules
geckodriver_path=":"+geckodriver_path
os.environ["PATH"]+=geckodriver_path


def current_status(driver):
    result={}
    for col in range(1,5):
        for row in range(1,5):
            key="c%d_r%d" %(col,row)
            try:
                tile=driver.find_element_by_class_name("tile-position-%d-%d" %(col,row))
                value=tile.find_element_by_class_name("tile-inner").text
                result[key]=int(value)
            except:
                result[key]=0
    return result
def get_score(driver):
    try:
        value=driver.find_element_by_class_name("score-container").text
        result=int(value)
    except:
        result=0
    return result

def game_over(driver):
    element=driver.find_element_by_class_name('game-message')
    display=element.value_of_css_property('display')
    return display=='none'

def game_retry(driver):
    retry_button=driver.find_element_by_class_name("retry-button")
    retry_button.click()
    
def shadow_and_try(driver_s,gameState,try_score,depth=1):
    try_score['Max']=0
    if not game_over(driver_s):
        score=get_score(driver_s)
        game_retry(driver_s)
        return score
    if depth==0: 
        score=get_score(driver_s)
        return score
    for move in ['up','down','left','right']:
#         print(move)
        try_score[move]={}
        js_stmt="new GameManager(4, KeyboardInputManager, HTMLActuator, LocalStorageManager,%s);" %gameState
        driver_s.execute_script(js_stmt)
#         print("reset")
#         time.sleep(5)
        driver_s.find_element_by_class_name('container').send_keys(keymap[move])
#         time.sleep(5)
        gameState2=driver_s.execute_script("return localStorage.gameState;")
        if gameState==gameState2:
#             print(gameState)
#             print(gameState2)
            continue
        try_score['Max']=max(shadow_and_try(driver_s,gameState2,try_score[move],depth=depth-1),try_score['Max'])
    return try_score['Max']
def predit_next_move(try_score):
    ranklist=[]
    for move in ['up','down','left','right']:
        ranklist.append((move,try_score[move]['Max']))
    return sorted(ranklist, key=lambda movement: movement[1],reverse=True)


keymap={'up':Keys.ARROW_UP,
        'down':Keys.ARROW_DOWN,
        'left':Keys.ARROW_LEFT,
        'right':Keys.ARROW_RIGHT}
driver = webdriver.Firefox()
driver.get("https://wayneyeye.github.io/2048/")

dep=int(input("depth?"))

while game_over(driver):
    driver_s = webdriver.PhantomJS()
    driver_s.get("https://wayneyeye.github.io/2048_shadow/")
    try_score={}
    gameState=driver.execute_script("return localStorage.gameState;")
    shadow_and_try(driver_s,gameState,try_score,depth=dep)
    predict_move=predit_next_move(try_score)
    print(predict_move)
    driver_s.close()
    for j in range(4):
        print(predict_move[j][0])
        driver.find_element_by_class_name('container').send_keys(keymap[predict_move[j][0]])
        gameState2=driver.execute_script("return localStorage.gameState;")
        if gameState!=gameState2:
            break
        else:
            print("no improvement!")
