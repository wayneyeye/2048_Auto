def next_move(desired, priority):
    import random
    choice=['up','down','left','right']
    choice.remove(desired)
    chance_not_desired=(1-priority)/4
    cut_values=[priority+chance_not_desired,priority+2*chance_not_desired,priority+3*chance_not_desired]
#     print(cut_values)
    dice=random.random()
    if dice<=cut_values[0]:
        return desired
    elif dice<=cut_values[1]:
        return choice[0]
    elif dice<=cut_values[2]:
        return choice[1]
    else:
        return choice[2]

def game_over(driver):
    element=driver.find_element_by_class_name('game-message')
    display=element.value_of_css_property('display')
    return display=='none'
def game_retry(driver):
    retry_button=driver.find_element_by_class_name("retry-button")
    retry_button.click()

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
def submit_step(step,record,skip=False):
    if skip:
        flag=True
        if len(record)==0:
            record.append(step)
        else:
            for col in range(1,5):
                if flag==False:
                    break
                for row in range(1,5):
                    key="c%d_r%d" %(col,row)
                    if step[key]!=record[-1][key]:
                        flag=False
                        break
            if flag==False:
                record.append(step)
    else:
        record.append(step)
        
def get_max_score(record):
    grid=[]
    score=0
    for col in range(1,5):
        for row in range(1,5):
            key="c%d_r%d" %(col,row)
            try:
                grid.append(record[-1][key])
            except:
                grid.append(0)
    score=max(grid)
    return (score)

def submit_record(record,password):
    current_round_score=get_max_score(record)
    for s in record:
        insert_step_in_db(s,current_round_score,password)
def find_cut_val(step,div):
    return(max(1,max(step['c1_r1'],step['c1_r2'],step['c1_r3'],step['c1_r4'],
                         step['c2_r1'],step['c2_r2'],step['c2_r3'],step['c2_r4'],
                         step['c3_r1'],step['c3_r2'],step['c3_r3'],step['c3_r4'],
                         step['c4_r1'],step['c4_r2'],step['c4_r3'],step['c4_r4'])/div))
            
def find_step_expected(step,password,cut=1):
    step2=step.copy()
    for col in range(1,5):
        for row in range(1,5):
            key="c%d_r%d" %(col,row)
            if step2[key]<=cut and step2[key]>0:
                step2[key]=0
    import pymysql
    connection=pymysql.connect(host="192.168.1.188",user="yewenhe0904",passwd=password,db='a2048')
    try:
        with connection.cursor() as cursor:
            sql='''SELECT move, AVG(expected_score) as exp FROM testing_v2
            WHERE '''
            stmt=''
            for col in range(1,5):
                for row in range(1,5):
                    key="c%d_r%d" %(col,row)
                    if step[key]<=cut and step[key]>0:
                        p=(" %s>%%s AND" % key)
                    else:
                        p=(" %s=%%s AND" % key)
                    stmt+=p
            stmt+=' 1=1'
            sql=sql+stmt
            sql+=' GROUP BY move ORDER BY 2 DESC'
            condition=(step2['c1_r1'],step2['c1_r2'],step2['c1_r3'],step2['c1_r4'],
                         step2['c2_r1'],step2['c2_r2'],step2['c2_r3'],step2['c2_r4'],
                         step2['c3_r1'],step2['c3_r2'],step2['c3_r3'],step2['c3_r4'],
                         step2['c4_r1'],step2['c4_r2'],step2['c4_r3'],step2['c4_r4'])
            cursor.execute(sql,condition)
            result=cursor.fetchall()
    finally:
        connection.close()           
    return(result)
            
def insert_step_in_db(step,score,password):
    import pymysql
    connection=pymysql.connect(host="192.168.1.188",user="yewenhe0904",passwd=password,db='a2048')
    try:
        with connection.cursor() as cursor:
            sql='''INSERT INTO testing_v2
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) '''
            condition=(step['c1_r1'],step['c1_r2'],step['c1_r3'],step['c1_r4'],
                         step['c2_r1'],step['c2_r2'],step['c2_r3'],step['c2_r4'],
                         step['c3_r1'],step['c3_r2'],step['c3_r3'],step['c3_r4'],
                         step['c4_r1'],step['c4_r2'],step['c4_r3'],step['c4_r4'],
                       step['move'],score)
            cursor.execute(sql,condition)
        connection.commit()
    finally:
        connection.close()


#worker function
def play_2048(db_password,retry=1,obeyance=0):
    #check db connection
    import pymysql
    try:
        connection=pymysql.connect(host="192.168.1.188",user="yewenhe0904",passwd=db_password,db='a2048')
    except:
        print("Problems in DB Connection!\nQuit...")
        sys.exit(1)
    from selenium import webdriver #install selenium
    from selenium.webdriver.common.keys import Keys
    import time,random,string
    print("Worker (PID=%s) Started" % os.getpid())
    keymap={'up':Keys.ARROW_UP,
        'down':Keys.ARROW_DOWN,
        'left':Keys.ARROW_LEFT,
        'right':Keys.ARROW_RIGHT}
    driver = webdriver.PhantomJS()
    driver.get("https://wayneyeye.github.io/2048/")
    elem = driver.find_element_by_class_name('game-container')
    password=db_password
    for i in range(retry):
        record=[]
        while game_over(driver):
            step_detail=current_status(driver)
            cut=find_cut_val(step_detail,8)
            step_pred=find_step_expected(step_detail,password,cut)
            if len(step_pred)>0:
                move_pred=step_pred[0][0]
                key=next_move(move_pred,obeyance)
                print("Worker (PID=%s) Round %s Matched! ---- %s" % (os.getpid(),i+1,key))
            else:
                key=random.choice(('up','down','left','right'))
            step_detail["move"]=key
            elem.send_keys(keymap[key])
            submit_step(step_detail,record,skip=True)
        game_retry(driver)
        print("Worker (PID=%s) Round %s Submitting Scores" % (os.getpid(),i+1))
        submit_record(record,password=password)
        print("Worker (PID=%s) Round %s Highest Score: %s" % (os.getpid(),i+1,get_max_score(record)))
    driver.close()
    print("Worker (PID=%s) Closed" % os.getpid())



if __name__ == '__main__':
    import sys,os
    #put geckodriver into the working directory
    geckodriver_path=(os.path.join(os.getcwd(),'geckodriver-dir'))#this is wrong search path for modules
    geckodriver_path=":"+geckodriver_path
    os.environ["PATH"]+=geckodriver_path
    import concurrent.futures
    import getpass
    password=getpass.getpass("DB password? ")
    worker_n=int(input("Number of workers?"))
    worker_retrys=[]
    number_of_retry=int(input("Retry for worker?"))
    for i in range(worker_n):
        worker_retrys.append(number_of_retry)   
    for mega in range(10):
        for o in range(0,75,5):
            print("obeyance = %s" %o)
            with concurrent.futures.ProcessPoolExecutor(worker_n+2) as executor:
                for retry_n in worker_retrys:
                    executor.submit(play_2048,password,retry_n,o/100)