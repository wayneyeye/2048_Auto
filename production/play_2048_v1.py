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
def get_current_score_addition(driver):
    try:
        score_addition=int(driver.find_element_by_class_name("score-addition").text.lstrip('+'))
    except:
        score_addition=0
    return score_addition

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
#     print(step,end='\r')
        
def submit_record(record,l=10):
    print(len(record))
    last_records=record[-min(len(record),l):]
    for r in last_records:
        print(r,end='\r')

def submit_record_sql(record,password):
    import pymysql
    insert_rows=[(i['c1_r1'],i['c1_r2'],i['c1_r3'],i['c1_r4'],
     i['c2_r1'],i['c2_r2'],i['c2_r3'],i['c2_r4'],
     i['c3_r1'],i['c3_r2'],i['c3_r3'],i['c3_r4'],
     i['c4_r1'],i['c4_r2'],i['c4_r3'],i['c4_r4'],
     i['stepno'],i['move'],i['score_addition'],i['gamestart'],i['uuid']) for i in record]
    connection=pymysql.connect(host="192.168.1.188",user="yewenhe0904",passwd=password,db='a2048')
    try:
        with connection.cursor() as cursor:
            stmt="INSERT INTO testing VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            cursor.executemany(stmt,insert_rows)
        connection.commit()
    finally:
        connection.close()
        
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


#worker function
def play_2048(db_password,retry=1):
    #check db connection
    # print("executor init ... OK")
    try:
        import pymysql
        connection=pymysql.connect(host="192.168.1.188",user="yewenhe0904",passwd=db_password,db='a2048')
    except:
        print("Problems in DB Connection!\nQuit...")
        sys.exit(1)
    #open selenium  
    print("Connection to Mysql DB ... OK")
    from selenium import webdriver #install selenium
    from selenium.webdriver.common.keys import Keys
    import time,random,string
    import uuid
    import threading
    print("Worker (PID=%s) Started" % os.getpid())
    keymap=(Keys.ARROW_UP,Keys.ARROW_DOWN,Keys.ARROW_LEFT,Keys.ARROW_RIGHT)
    driver = webdriver.PhantomJS() #install phantomjs
    driver.get("https://wayneyeye.github.io/2048/")
    elem = driver.find_element_by_class_name('game-container')
    retry=1
    # try
    for i in range(retry):
        print("Worker (PID=%s) in Round %s" % (os.getpid(),i+1))
        record=[]
        starttime=time.strftime("%m%d%Y-%H%M%S")
        stepno=0
        while game_over(driver):
            stepno+=1
            key=random.randint(0,3)
            step_detail=current_status(driver)
            step_detail["stepno"]=stepno
            step_detail["move"]=key
            elem.send_keys(keymap[key])
            step_detail["score_addition"]=(get_current_score_addition(driver))
            step_detail["gamestart"]=starttime
            step_detail["uuid"]=uuid.uuid1().hex
            submit_step(step_detail,record)
        game_retry(driver)
        print("Worker (PID=%s) Round %s Submitting Scores" % (os.getpid(),i+1))
        record[-1]
        print("Worker (PID=%s) Round %s Highest Score: %s" % (os.getpid(),i+1,get_max_score(record)))
        submit_record_sql(record,db_password)
    driver.close()
    print("Worker (PID=%s) Closed" % os.getpid())


if __name__ == '__main__':
    import sys,os
    geckodriver_path=(os.path.join(os.getcwd(),'geckodriver-dir'))
    geckodriver_path=":"+geckodriver_path
    os.environ["PATH"]+=geckodriver_path
    import concurrent.futures
    import getpass
    password=getpass.getpass("DB password? ")
    worker_n=int(input("Number of Workers?"))
    worker_retrys=[]
    for i in range(worker_n):
        worker_retrys.append(int(input("Retry for Worker %s?" %i)))   
    with concurrent.futures.ProcessPoolExecutor(worker_n+2) as executor:
        # print("executor ... OK")
        for retry_n in worker_retrys:
            # print("executor %s ... OK" % retry_n)
            executor.submit(play_2048,password,{'retry':retry_n})