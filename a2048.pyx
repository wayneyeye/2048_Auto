import sys,os
import time,random,string

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
    
def game_keepgoing(driver):
    keep_button=driver.find_element_by_class_name("keep-playing-button")
    keep_button.click()

import numpy as np
import pandas as pd
import random,time,math,json,string

class GridView:
    def __init__(self):
        self.score=0
        self.lose=False
    
    def randomInsert(self):
        available_length=0
        available_cells=[]
        for r in range(4):
            for c in range(4):
                if self.grid_array[r,c]==0:
                    available_length+=1
                    available_cells.append({"r":r,"c":c})
        if available_length>0:
            insertCell=math.floor(random.random()*available_length)
        self.grid_array[available_cells[insertCell]["r"],available_cells[insertCell]["c"]]\
        =2 if random.random()<0.9 else 4
    
    def initGame(self):
        self.grid_array=np.array([[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]])
        self.score_array=np.array([[6,4,3,2.5],[4,3.5,2.5,2],[3,2.5,2,1.5],[2.5,2,1.5,1]])
        self.score=0
        self.lose=False
        self.randomInsert()
        self.randomInsert()
        self.grid_History=[self.grid_array.copy()]

    
    def ifLose(self):
        for r in range(4):
            for c in range(4):
                if self.grid_array[r,c]==0:
                    return False
        for r in range(3):
            for c in range(4):
                if self.grid_array[r,c]==self.grid_array[r+1,c]:
                    return False
        for r in range(4):
            for c in range(3):
                if self.grid_array[r,c]==self.grid_array[r,c+1]:
                    return False
        return True
                    
    
    def setTest(self,arr):
        self.grid_array=arr
        self.grid_History=[self.grid_array]
    
    def xScore(self):
        t=0
        for r in range(4):
            for c in range(4):
                t+=(self.grid_array[r,c]*self.score_array[r,c])
        return t
    
    def moveUP(self,event):
        for i in range(3):
            for c in range(4):
                for r in range(1,4):
                    if self.grid_array[r-1,c]==0:
                        self.grid_array[r-1,c],self.grid_array[r,c]=self.grid_array[r,c],self.grid_array[r-1,c]
        
        for c in range(4):
            for r in range(1,4):
                if self.grid_array[r-1,c]==self.grid_array[r,c]:
                    self.grid_array[r-1,c]=2*self.grid_array[r-1,c]
                    self.score+=2*self.grid_array[r,c]
                    self.grid_array[r,c]=0
        
        for c in range(4):
            for r in range(1,4):
                if self.grid_array[r-1,c]==0:
                    self.grid_array[r-1,c],self.grid_array[r,c]=self.grid_array[r,c],self.grid_array[r-1,c]
        if (self.grid_array!=self.grid_History[-1]).any() and not self.lose:
            self.randomInsert()
            self.grid_History.append(self.grid_array.copy())
            self.lose=self.ifLose()
            
        self.score+=self.xScore()

    
    def moveDOWN(self,event):
        for i in range(3):
            for c in range(4):
                for r in range(2,-1,-1):
                    if self.grid_array[r+1,c]==0:
                        self.grid_array[r+1,c],self.grid_array[r,c]=self.grid_array[r,c],self.grid_array[r+1,c]
        
        for c in range(4):
            for r in range(2,-1,-1):
                if self.grid_array[r+1,c]==self.grid_array[r,c]:
                    self.grid_array[r+1,c]=2*self.grid_array[r+1,c]
                    self.score+=2*self.grid_array[r,c]
                    self.grid_array[r,c]=0
        
        for c in range(4):
            for r in range(2,-1,-1):
                if self.grid_array[r+1,c]==0:
                    self.grid_array[r+1,c],self.grid_array[r,c]=self.grid_array[r,c],self.grid_array[r+1,c]
        if (self.grid_array!=self.grid_History[-1]).any() and not self.lose:
            self.randomInsert()
            self.grid_History.append(self.grid_array.copy())
            self.lose=self.ifLose()
        self.score+=self.xScore()

            
    def moveLEFT(self,event):
        for i in range(3):
            for r in range(4):
                for c in range(1,4):
                    if self.grid_array[r,c-1]==0:
                        self.grid_array[r,c-1],self.grid_array[r,c]=self.grid_array[r,c],self.grid_array[r,c-1]
        
        for r in range(4):
            for c in range(1,4):
                if self.grid_array[r,c-1]==self.grid_array[r,c]:
                    self.grid_array[r,c-1]=2*self.grid_array[r,c-1]
                    self.score+=2*self.grid_array[r,c]
                    self.grid_array[r,c]=0
        
        for r in range(4):
            for c in range(1,4):
                if self.grid_array[r,c-1]==0:
                    self.grid_array[r,c-1],self.grid_array[r,c]=self.grid_array[r,c],self.grid_array[r,c-1]
        if (self.grid_array!=self.grid_History[-1]).any() and not self.lose:
            self.randomInsert()
            self.grid_History.append(self.grid_array.copy())
            self.lose=self.ifLose()
        self.score+=self.xScore()
        
        
    def moveRIGHT(self,event):
        for i in range(3):
            for r in range(4):
                for c in range(2,-1,-1):
                    if self.grid_array[r,c+1]==0:
                        self.grid_array[r,c+1],self.grid_array[r,c]=self.grid_array[r,c],self.grid_array[r,c+1]
        
        for r in range(4):
            for c in range(2,-1,-1):
                if self.grid_array[r,c+1]==self.grid_array[r,c]:
                    self.grid_array[r,c+1]=2*self.grid_array[r,c+1]
                    self.score+=2*self.grid_array[r,c]
                    self.grid_array[r,c]=0
        
        for r in range(4):
            for c in range(2,-1,-1):
                if self.grid_array[r,c+1]==0:
                    self.grid_array[r,c+1],self.grid_array[r,c]=self.grid_array[r,c],self.grid_array[r,c+1]
        if (self.grid_array!=self.grid_History[-1]).any() and not self.lose:
            self.randomInsert()
            self.grid_History.append(self.grid_array.copy())
            self.lose=self.ifLose()
        self.score+=self.xScore()

            
    def inStreamControl(self,inS):
        for m in inS:
            if m==0:
                self.moveUP(None)
            elif m==1:
                self.moveDOWN(None)
            elif m==2:
                self.moveLEFT(None)
            elif m==3:
                self.moveRIGHT(None)
            if self.lose:
                return self.getScore()
        return self.getScore()
    def getScore(self):
        return self.score
    def setGame_json(self,state):
        state_py=json.loads(state)
        self.score=state_py['score']
        self.lose=state_py['over']
        for r in range(4):
            for c in range(4):
                if state_py['grid']['cells'][c][r]:
                    self.grid_array[r,c]=state_py['grid']['cells'][c][r]['value']
                else:
                    self.grid_array[r,c]=0
        self.grid_History=[self.grid_array.copy()]

    def getMax(self):
        t=[]
        for r in range(4):
            for c in range(4):
                t.append(self.grid_array[r,c])
        t.sort(reverse=True)
        return t
    
    def probeGame(self,inS,gamestate):
        outcome_dict={'move':[],'first':[],'score':[]}
        exclude_first=[]
        for ins_try in [0,1,2,3]:
            self.setGame_json(gamestate)
            score=self.inStreamControl([ins_try])
#             print(self.grid_History[-2])
#             print(self.grid_array)
            if (len(self.grid_History)==1):
                exclude_first.append(ins_try)
        
            
        for ins in inS:
            if ins[0] in exclude_first:
                continue
            else:
                self.setGame_json(gamestate)
                score=self.inStreamControl(ins)
                outcome_dict['move'].append('-'.join([str(i) for i in ins]))
                outcome_dict['first'].append(ins[0])
                outcome_dict['score'].append(score)
        df=pd.DataFrame.from_dict(outcome_dict)
        grouped=df.groupby(['move','first'])
        df=grouped.mean()
        df.reset_index(level=['first'], inplace=True)
        grouped2=df.groupby(['first'])
        df_max=grouped2.max()
        df_min=grouped2.min()
        df=pd.concat([df_max,df_min],axis=1)
        df.columns=['max','min']
        return df
        
def genInsStream(depth=4,probe=0,rep=3):
    instructionStream=[]
    instructionStreamT=[]
    instructionHead=[]
    for d in range(depth):
        if len(instructionStream)==0:
            for s in range(4):
                instructionStreamT.append([s])
        else:
            for head in instructionStream:
                for s in range(4):
#                     [i for i in head,s]
                    instructionStreamT.append([i for i in head]+[s])
        instructionStream=instructionStreamT
        instructionStreamT=[]
    for head in instructionStream:
        randomTail=[]
        for p in range(probe):
            randomTail.append(random.randint(0,3))
        for r in range(rep):
            instructionStreamT.append([i for i in head]+randomTail)
    instructionStream=instructionStreamT
    return instructionStream