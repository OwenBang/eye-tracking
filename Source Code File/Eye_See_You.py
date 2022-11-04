#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#!/usr/bin/env python
# coding: utf-8

# In[5]:



from ast import While
from tkinter import *
import tkinter.font
from turtle import xcor
from winreg import QueryValue
from matplotlib.ft2font import ITALIC
import numpy as np
from PIL import Image

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import tkinter as tk

from captcha.image import ImageCaptcha
import string
import random
import time

import Eye_Tracking as MC
import threading
import pymysql
import math
import datetime


# tkinter 객체 생성
Login_Interface = Tk()
Login_Interface.title("Login_Interface")

Whole_Time = -1
IsStart = False
Puzzle_Count = -1
Stime = -1
TimerCount = -1
TimerCount_Min = -1
Avg_Attn_Rate = -1
IsAttend = False
txt_captcha = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(0))
Puzzle_Receive = False
Question_Receive = False
UserList=[]
UserAttentionRateList=[]
User = [UserList, UserAttentionRateList]
Sec = 0
User_Num = -1
IsTimerOn = False
Attention_Rate_Init = False

# ★ 중요 ★
# 서버와 연결해야하는 변수들은 '★, ☆' 표시가 되어 있습니다. ★은 시작 부분, ☆은 종료 부분입니다.
conn = pymysql.connect(host="database-1.cvdnmgvfx65g.ap-northeast-2.rds.amazonaws.com", 
                      user="admin", password="a1234567", db="management", charset="utf8")

# 기본 함수 선언
def Define_AttrRate_Color(Avg_Attn, Interface) :
    AttnRate_Type_Label_font = tkinter.font.Font(family="맑은 고딕", size=11, weight = "bold")
    
    if(Avg_Attn <= 25) :
        AttnRate_Label = Label(Interface, text=str(Avg_Attn), fg='#b00', font = AttnRate_Type_Label_font)

    elif(25 < Avg_Attn and Avg_Attn <= 40) :
        AttnRate_Label = Label(Interface, text=str(Avg_Attn), fg='#f70', font = AttnRate_Type_Label_font)
    
    elif(40 < Avg_Attn and Avg_Attn <= 50) :
        AttnRate_Label = Label(Interface, text=str(Avg_Attn), fg='#fb0', font = AttnRate_Type_Label_font)
    
    else :
        AttnRate_Label = Label(Interface, text=str(Avg_Attn), fg='#0b0', font = AttnRate_Type_Label_font)
        
    return AttnRate_Label

def Define_AttrRate_Type_Color(Avg_Attn, Interface) :
    Label_Font = tkinter.font.Font(family="맑은 고딕", size=11, weight = "bold")
    
    if(Avg_Attn <= 25) :
        AttnRate_Label = Label(Interface, text="매우 낮음", fg='#b00', font = Label_Font)

    elif(25 < Avg_Attn and Avg_Attn <= 40) :
        AttnRate_Label = Label(Interface, text="낮음", fg='#f70', font = Label_Font)
    
    elif(40 < Avg_Attn and Avg_Attn <= 50) :
        AttnRate_Label = Label(Interface, text="살짝 낮음", fg='#fb0', font = Label_Font)
    
    else :
        AttnRate_Label = Label(Interface, text="좋음", fg='#0b0', font = Label_Font)
        
    return AttnRate_Label

# 인터페이스 선언
# ★
def Admin_Interface1():
    # Interface1 시작
    Interface1 = Tk()
    Interface1.title("Interface1")
    Interface1.geometry('800x400') 

    # 참여자 목록 & 참여율 임시 생성
    # UserList와 UserAttentionRateList은 서버에서 할당 받는다. 아래는 임시 배열이다.
    global IsStart
    IsStart = False
    global UserList, UserAttentionRateList
    
#     UserList = np.array(["User1", "User2", "User3", "User4", "User5", "User6", "User7",
#                 "User8", "User9", "User10", "User11", "User12", "User13","User14"])
#     UserAttentionRateList = np.array([ 80, 78, 96, 77, 65, 78, 85,
#                             87, 45, 77, 99, 98, 33, 55])
#     User = [UserList, UserAttentionRateList]

#     UserList = np.array(["UserA", "UserB", "UserC", "UserD", "UserE", "UserF", "UserG",
#             "UserH", "UserI", "UserJ", "UserK", "UserL", "UserM","UserN"])
            
#     UserAttentionRateList = np.array([ 80, 78, 96, 77, 65, 78, 85,
#                             87, 45, 77, 99, 98, 33, 55])
    
    global User
    User = [UserList, UserAttentionRateList]
            

    # 아래는 서버와 관련 x

    
    # ==================================== 참여자 리스트 UI 생성 ====================================
    # Interface에 표시할 User_Label & UserAttentionRate_Label선언
    User_Label = Label(Interface1, text="NULL")
    UserAttentionRate_Label = Label(Interface1, text="NULL")
    X = 50
    Y = 100

    UserList_Label = Label(Interface1, text="참여자 리스트")
    UserList_Label.configure(font=("맑은 고딕", 15, "bold"))
    UserList_Label.place(x=100,y=60)

    
    def Request_Puzzle(UserName) : # 해당 유저에게 퍼즐을 요청합니다.    
        # ★ 서버 연결 요소 ----------------------------------------------------------------------------------------------★   
            # 참여자 중 이름이 'UserName'인 유저에게 퍼즐 인증을 요청합니다.
        curs = conn.cursor()
        sql = "update customer set Puzzle_Receive=1 where UserName = %s and IsStart=1"
        curs.execute(sql,UserName)
        conn.commit()
        # ☆ 서버 연결 요소 ----------------------------------------------------------------------------------------------☆ 
        print(UserName + "님에게 퍼즐 요청함!")
        return
    
    # UserList의 인자들을 Interface에 표시한다. User1~7은 왼쪽에, User8~14는 오른쪽에 배치한다.
    def User_List_Print():
        global UserList, UserAttentionRateList
        count = 1
        X = 50
        Y = 100
        for x in UserList:
            if(count == 8) :    # 8번째 User인 경우 위치를 오른쪽으로 이동한다.     
                X = 200
                Y = 100
        
            # User_Label 생성
            User_Label = Label(Interface1, text= x)
            User_Label.place(x=X,y=Y)
            # UserAttentionRate Label 생성
            UserAttentionRate_Label0 = Label(Interface1, text="      ")
            UserAttentionRate_Label0.place(x=X + 50, y=Y)
            UserAttentionRate_Label1 = Define_AttrRate_Color(int(UserAttentionRateList[count - 1]), Interface1)
            UserAttentionRate_Label1.place(x=X + 50, y=Y)
            UserAttentionRate_Label2 = Label(Interface1, text = "%")
            UserAttentionRate_Label2.place(x=X + 75, y=Y)
            # 참여율이 낮은 User에게 [퍼즐 인증]버튼 제공
            if UserAttentionRateList[count - 1] <= 50 :
                curs = conn.cursor()
                sql = "select Puzzle_Receive from customer where UserName = %s"
                curs.execute(sql, x)
                row = curs.fetchone()
                Puzzle_Receive_X = row[0] 
                #print(Puzzle_Receive_X, x)
                
                if Puzzle_Receive_X == 0 : 
                    User_Puzzle_Button = tkinter.Button(Interface1, overrelief="solid", width=20)
                 
                else :
                    User_Puzzle_Button = tkinter.Button(Interface1, overrelief="solid", width=20, state = tkinter.DISABLED)
                    
                User_Puzzle_Button.config(width = 3, height = 1, command= lambda i = x: Request_Puzzle(i), text = "퍼즐")
                User_Puzzle_Button.place(x =X + 95, y = Y)
                    
                    
            
            Y += 25 
            count += 1
    
    # ==================================== 참여자 리스트 UI 종료 ====================================


    # ================================== 참여율 (오름차순) UI 생성 ==================================

    #참여율에 따른 오름차순 정렬
    def Sorted_User_List_Print() :
        global UserList, UserAttentionRateList, User_Num
        User_Sort = np.vstack((UserList, UserAttentionRateList))
        User_Sort = User_Sort[:,User_Sort[1].argsort()]

        UserList_Ascending_Label = Label(Interface1, text="참석율 (오름차순)")
        UserList_Ascending_Label.configure(font=("맑은 고딕", 15, "bold"))
        UserList_Ascending_Label.place(x=550,y=60)

        count = 1
        X = 600
        Y = 100

        for i in range(User_Num):
            
            # Ascending_User_Label 생성
    
            Ascending_User_Label = Label(Interface1, text= User_Sort[0][i])
            Ascending_User_Label.place(x=X,y=Y)

            # Ascending_User_AR_Label 생성  | AR = Attention Rate
            
            Ascending_User_AR_Label0 = Label(Interface1, text="       ")
            Ascending_User_AR_Label0.place(x=X + 50, y=Y)
            Ascending_User_AR_Label1 = Define_AttrRate_Color(int(User_Sort[1][i]), Interface1)
            Ascending_User_AR_Label1.place(x=X + 50, y=Y)
        
            Ascending_User_AR_Label2 = Label(Interface1, text = "%")
            Ascending_User_AR_Label2.place(x=X + 75, y=Y)
    
            Y += 25 
            count += 1


    # ================================== 참여율 (오름차순) UI 종료 ==================================


    # ====================================== 질문하기 버튼 생성 =====================================
    def Request_Question() : # 서버에 질문할 유저 선정하고 이를 요청합니다. 질문받는 인원은 전체 인원의 1/3(소숫점 아래 버림)입니다.
        #Question_Num = (int)((3) / 3)
        Question_User_List = []
        for x in range(0,2):
            rand = random.randint(0,2)
            while rand in Question_User_List:
                rand = random.randint(0,2)
            Question_User_List.append(rand)   
            print(rand)
      
    # ★ 서버 연결 요소 ----------------------------------------------------------------------------------------------★   
        # 위에서 사용한 Question_User_List[]에는, 질문을 받을 User의 번호가 정렬되지 않은 상태로 표시되어 있습니다. (범위 : 0~User_Num-1)
            # 예시 : Question_User_List[] = [4, 0, 9]
        # 이에 해당되는 참여자 목록을 DB에 전달하고, DB를 통해 해당 참여자들에게 질문이 들어왔다는 것을 전송하면 됩니다.  
        curs = conn.cursor()
        for i in Question_User_List:
            sql = "update customer set Question_Receive = 1 where UserId = %s and IsStart=1"
            curs.execute(sql,i+1)
            conn.commit()
            
            sql = "update customer set Is_Question = true where UserId"
            curs.execute(sql)
            conn.commit()
            DB()
    # ☆ 서버 연결 요소 ----------------------------------------------------------------------------------------------☆         
    # ====================================== 질문하기 버튼 종료 =====================================

    # ====================================== 조회하기 생성 시작 =====================================
    Input_Name = StringVar()
    Question_Input_Name = StringVar()
    
    def Search_Error() :
        Search_Error = Tk()
        Search_Error.title("Search_Error")
        Search_Error.geometry('150x30') 
        Input_Text_Label = Label(Search_Error, text = "존재하지 않는 유저입니다.")
        Input_Text_Label.place(x=1, y=0)
        Search_Error.mainloop()
    
    def Search() : 
        Error = True
        for x in UserList : 
            if Input_Name.get() == x : 
                print("조회하는 이름 : " + x)
                Admin_Interface2(x)
                Error = False
                break;
            
        if Error == True:
             Search_Error()   
    
    global Qustion_Content 
    
    def Question_Insert() : 
        global Question_Content
        Question_Content = Question_Input_Name.get()
        
        Question_Content_Label = Label(Interface1, text = "작성된 질문 : " + Question_Content)
        Question_Content_Label.place(x=200, y=350)
        # ★ 서버 연결 요소 ----------------------------------------------------------------------------------------------★   
        # 위의 Question_Content은 사용자가 입력한 [질문 내용]입니다. (string형)
        # 입력한 질문 내용을 DB에 전달하면 됩니다.
        curs = conn.cursor()
        sql = "update customer set Question_Detail=%s"
        curs.execute(sql,Question_Content)
        conn.commit()
        
        DB()
        # ☆ 서버 연결 요소 ----------------------------------------------------------------------------------------------☆         
        return
    
    def DB() : 
        curs = conn.cursor()
        conn.commit()
        
    Input_Text_Label = Label(Interface1, text = "참여자 상세 조회하기")
    Input_Text_Label.place(x=50, y=300)
    
    Input_Text = Entry(Interface1, textvariable = Input_Name, width = 10)
    Input_Text.place(x=50,y=325)

    Input_Text_Button = tkinter.Button(Interface1, overrelief="solid", width=20)
    Input_Text_Button.config(width = 3, height = 1, command=Search, text = "조회")
    Input_Text_Button.place(x = 125, y = 320)
    
    Question_Input_Text_Label = Label(Interface1, text = "질문 내용 입력하기")
    Question_Input_Text_Label.place(x=200, y=300)
    
    Question_Input_Text = Entry(Interface1, textvariable = Question_Input_Name, width = 25)
    Question_Input_Text.place(x=200,y=325)

    Question_Input_Text_Button = tkinter.Button(Interface1, overrelief="solid", width=20)
    Question_Input_Text_Button.config(width = 3, height = 1, command=Question_Insert, text = "입력")
    Question_Input_Text_Button.place(x = 380, y = 320)
    
    # ====================================== 조회하기 생성 종료 =====================================
    
    # ====================================== 회의버튼 생성 시작 =====================================
    def Start_Conference() : # 회의 시작
        # ★ 서버 연결 요소 ----------------------------------------------------------------------------------------------★    
        # 1. DB에 회의가 시작되었음을 나타내는 변수를 전송합니다. 
        dt_now = datetime.datetime.now()
        curs = conn.cursor()
        sql = "update manager set IsStart=1,StartTime=%s"
        curs.execute(sql,dt_now)
        conn.commit()
        
        #datetime manager->customer전달
        #
        sql = "update customer set Date=%s where IsStart=1"
        curs.execute(sql,dt_now)
        conn.commit()
        #
        
        sql = "update manager set Number=Number+1 "
        curs.execute(sql)
        conn.commit()
        
        sql ="update customer set UserAttentionRate=0, Puzzle_Receive=0,Puzzle_IsCorrect=0,Puzzle_Succ=0,Puzzle_Fail=0,Question_Receive=0"
        curs.execute(sql)
        conn.commit()
        
        
        
        # ☆ 서버 연결 요소 ----------------------------------------------------------------------------------------------☆  
        
        global Whole_Time, Sec
        Whole_Time = -1
        
        global IsStart
        IsStart = True
        Whole_Time_Count()
        print("회의 시작")
        Sec = 0
        
        Start_Button = tkinter.Button(Interface1, overrelief="solid", width=20, state = tkinter.DISABLED)
        Start_Button.config(width = 7, height = 1, command=Start_Conference, text = "회의 시작")
        Start_Button.place(x = 400, y = 20)
        
        End_Button = tkinter.Button(Interface1, overrelief="solid", width=20)
        End_Button.config(width = 7, height = 1, command=End_Conference, text = "회의 종료")
        End_Button.place(x = 400, y = 50)
        
        Input_Text = Entry(Interface1, textvariable = Input_Name, width = 10, state = tkinter.DISABLED)
        Input_Text.place(x=50,y=325)

        Input_Text_Button = tkinter.Button(Interface1, overrelief="solid", width=20, state = tkinter.DISABLED)
        Input_Text_Button.config(width = 3, height = 1, command=Search, text = "조회")
        Input_Text_Button.place(x = 125, y = 320)
        
        Question = tkinter.Button(Interface1, overrelief="solid", width=20)
        Question.config(width = 7, height = 3, command=Request_Question, text = "질문하기")
        Question.place(x=610,y=300)
        Repeat_Print()
        

    def Repeat_Print() : 
        if IsStart == True:
            global UserList, UserAttentionRateList, User_Num, User
            Interface1.after(1000, Repeat_Print)
            Puzzle_Button_Delete()
             # ★ 서버 연결 요소 ----------------------------------------------------------------------------------------------★
            # 0. 참여자의 최대 인원 수는 14명으로 설정하였습니다. 14명을 초과하지 않도록 주의 요망!!!
            # 1. 모든 참여자들의 'Name' 리스트 배열 : UserList[]
                # 예시
                # UserList = np.array(["UserA", "UserB", "UserC", "UserD", "UserE", "UserF", "UserG",
                #    "UserH", "UserI", "UserJ", "UserK", "UserL", "UserM","UserN"])    
            # 아래는 예시 변수입니다. 서버로부터 입력을 받으면, 아래 변수는 지워도 됩니다.
            
            curs = conn.cursor()
            tmpList=[]
            sql = "select UserName from customer where IsStart=1"
            curs.execute(sql)
            rows = curs.fetchall()
            for row in rows:
                tmpList.append(row[0])
            UserList = np.array(tmpList)

            # 2. UserList[]에 해당하는 각 참여자의 '평균 참여율' 리스트 배열 : UserAttentionRateList[]
                 # 예시
                 #   UserAttentionRateList = np.array([ 80, 78, 96, 77, 65, 78, 85,
                 #           87, 45, 77, 99, 98, 33, 55])  
            tmpList=[]
            sql = "select UserAttentionRate from customer where IsStart=1"
            curs.execute(sql)
            rows = curs.fetchall()
            for row in rows:
                tmpList.append(row[0])
            UserAttentionRateList = np.array(tmpList)     
            # ☆ 서버 연결 요소 ----------------------------------------------------------------------------------------------☆
            
            # 3. User[][] 는 UserList[]와 UserAttentionRateList를 묶은 이중배열입니다. (작성 완료함!)
            # 서버로부터 UserList[]와 UserAttentionRateList를 받은 경우, 이를 지속적으로 갱신해야합니다. 
            User = [UserList, UserAttentionRateList] 
            
            User_Num = len(User[0])
            
            User_List_Print()
            Sorted_User_List_Print()  

        else :
            return    

    def Puzzle_Button_Delete():
        count = 1
        X = 50
        Y = 100
        for x in UserList:
            if(count == 8) :    # 8번째 User인 경우 위치를 오른쪽으로 이동한다.     
                X = 200
                Y = 100
                
            Cover_Label_font = tkinter.font.Font(family="맑은 고딕", size=13)
            Cover_Label = Label(Interface1, text= "     ",font = Cover_Label_font)
            Cover_Label.place(x =X + 95, y = Y)                
            Y += 25 
            count += 1
            
        curs = conn.cursor()
        conn.commit()
            
    def End_Conference() : # 회의 종료
        # ★ 서버 연결 요소 ----------------------------------------------------------------------------------------------★    
        # 1. DB에 회의가 종료되었음을 나타내는 변수를 전송합니다. 
        curs = conn.cursor()
        sql = "update manager set IsStart=0"
        curs.execute(sql)
        
        # 2. 회의 시간을 전송합니다. 회의 시간에 대한 값는 아래 Whole_Time에 있습니다.
        global Whole_Time
        sql = "update manager set Whole_Time=%s"
        curs.execute(sql,Whole_Time)
        conn.commit()
        
        #참여자 IsStart 0으로 초기화
        curs = conn.cursor()
        sql ="update customer set IsStart=0"
        curs.execute(sql)
        conn.commit()
        
        
        # ☆ 서버 연결 요소 ----------------------------------------------------------------------------------------------☆
        print("회의 종료")
        global IsStart
        IsStart = False
        Start_Button = tkinter.Button(Interface1, overrelief="solid", width=20)
        Start_Button.config(width = 7, height = 1, command=Start_Conference, text = "회의 시작")
        Start_Button.place(x = 400, y = 20)
        
        End_Button = tkinter.Button(Interface1, overrelief="solid", width=20,  state = tkinter.DISABLED)
        End_Button.config(width = 7, height = 1, command=End_Conference, text = "회의 종료")
        End_Button.place(x = 400, y = 50)
        
        Input_Text = Entry(Interface1, textvariable = Input_Name, width = 10)
        Input_Text.place(x=50,y=325)

        Input_Text_Button = tkinter.Button(Interface1, overrelief="solid", width=20)
        Input_Text_Button.config(width = 3, height = 1, command=Search, text = "조회")
        Input_Text_Button.place(x = 125, y = 320)
     
        # 회의 종료 후 자동으로 결과 인터페이스  전화
        Admin_Interface3()
        
    def Whole_Time_Count() : 
        global Whole_Time
        global IsStart
        Whole_Time_H = -1
        Whole_Time_Min = -1
        Whole_Time_Sec = -1
        if IsStart == True:
            Interface1.after(1000, Whole_Time_Count)
            Whole_Time += 1
            Whole_Time_H = (int)((Whole_Time) / 3600)
            Whole_Time_Min = (int)(((Whole_Time) / 60) % 60) 
            Whole_Time_Sec = (int)((Whole_Time) % 60 - 1)
            Exit_Label=tkinter.Label(Interface1, text = 
                                     "회의 시간 :  " +  f"{Whole_Time_H }시간 " + f"{Whole_Time_Min }분 " +  f"{Whole_Time_Sec + 1}초  ")
            Exit_Label.place(x=50, y=35)
        else :
            return
 
    if IsStart == False : 
        Start_Button = tkinter.Button(Interface1, overrelief="solid", width=20)
        End_Button = tkinter.Button(Interface1, overrelief="solid", width=20, state = tkinter.DISABLED)
    else :
        Start_Button = tkinter.Button(Interface1, overrelief="solid", width=20, state = tkinter.DISABLED)
        End_Button = tkinter.Button(Interface1, overrelief="solid", width=20)
        
    Start_Button.config(width = 7, height = 1, command=Start_Conference, text = "회의 시작")
    Start_Button.place(x = 400, y = 20)
    
    End_Button.config(width = 7, height = 1, command=End_Conference, text = "회의 종료")
    End_Button.place(x = 400, y = 50)
    # ====================================== 회의버튼 생성 종료 =====================================
    
    Interface1.mainloop()

# ★
def Admin_Interface2(I_UserName):
    Interface2 = Tk()
    Interface2.title("Interface2")
    Interface2.geometry("850x450")
    Interface2.resizable(False, False)
    # ====================================== 변수 선언 & 입력 시작 ======================================
    # 변수 선언
    UserName = "NULL"
    User_Avg_AttnRate = -1
    Puzzle_Succ = -1
    Puzzle_Fail = -1

    Date = -1
    Year = -1
    Month = -1
    Day = -1
    Avg_AttnRate = -1
    Max_AttnRate = -1
    Max_AttnRate_User = "NULL"
    Min_AttnRate = -1
    Min_AttnRate_User = "NULL"

    AttnRate_Type = "NULL"
    Whole_Time = -1

    # ★ 서버 연결 요소 ----------------------------------------------------------------------------------------------★
            # 현재 받아야하는 유저의 이름은 I-UserName으로 지정되어있습니다. (string 값이 존재)     
            # Admin_Interface2는 입력받은 I_UserName의 정보를 가져와서 이를 통계내는 인터페이스입니다.  
            # 사용자 이름인 I_UserName을 DB로 전송하여, 해당 참여자의 정보와 전체 유저의 정보 일부를 DB로부터 가져와야 합니다.
    curs = conn.cursor(pymysql.cursors.DictCursor)
    sql = "select*from customer where UserName = %s"
    curs.execute(sql,I_UserName)
    I_UserData = curs.fetchone()
            # 아래는 DB로부터 받아야하는 데이터 내용입니다.
                # 1. User_Image = 해당 유저의 이미지
                # 2. UserData = [I_UserName의 참여도,I_UserName의 금일 퍼즐 성공 횟수, I_UserName의 금일 퍼즐 실패 횟수]
                    # 예시 : UserData = [63, 0, 2]
    UserData = [I_UserData['UserAttentionRate'],I_UserData['Puzzle_Succ'],I_UserData['Puzzle_Fail']] 
                # 3. User_AttnRate_Graph = [0시점, 1/4시점, 2/4시점, 3/4시점, 4/4시점]
                    # 금일 시간을 4등분 하였을 때, 각각의 지점에서의 해당 유저의 평균 출석율을 의미합니다. 
                    # 예를 들어 금일 회의시간이 100분인 경우, '2/4시점'의 값은 0~50분까지의 평균 출석율값을 의미합니다.
                    # 단, '0시점'은 회의 0~1분 사이의 출석율로 결정합니다.
                    # User_AttnRate_Graph = [1분에서의 참여율, 
                                         #  (Whole_Time / 4)분에서의 참여율, 
                                         #  (Whole_Time / 4 * 2)분에서의 참여율,
                                         #  (Whole_Time / 4 * 3)분에서의 참여율,
                                         #  Whole_Time분에서의 참여율]
                    # 예시 : User_AttnRate_Graph = [78, 56, 67, 74, 51]
                    
                # 4. Whole_Time = 금일 전체 회의 시간, 서버에서 가져오기
                    # 예시 : Whole_Time = 120
    sql = "select Whole_Time from manager"
    curs.execute(sql)
    row = curs.fetchone()
    Whole_Time = row['Whole_Time'] 
    
    sql = "select Number from manager"
    curs.execute(sql)
    row=curs.fetchone()
    Now_confer = row['Number']
    
    User_AttnRate_Graph=[]
    sql = "select Attend_Rate from attendance where UserName=%s and Minute=1 and Number=%s"
    curs.execute(sql,(I_UserName,Now_confer))
    row = curs.fetchone()
    print(row)
    #print(start_t)
    print(Now_confer)
    print(I_UserName)
    User_AttnRate_Graph.append(row['Attend_Rate'])
    
    for i in range(1,5):
        Ref_Time = math.ceil((Whole_Time-2)/4)
        sql = "select Attend_Rate from attendance where UserName=%s and Minute=%s and Number=%s"
        Ref_Time = Ref_Time*i
        tmp_data = (I_UserName,Ref_Time,Now_confer)
        curs.execute(sql,tmp_data)
        row = curs.fetchone()
        User_AttnRate_Graph.append(row['Attend_Rate'])
        print(row)
    print(User_AttnRate_Graph)   
    
    
            # 5. Statistics = [금일 날짜, 전체 참여자의 평균 참여율, 
                              # 금일 평균 참여율 중 가장 높은 값의 참여율, 해당 최고 참여율의 사용자명, 
                              # 금일 평균 참여율 중 가장 낮은 값의 참여율, 해당 최저 참여율의 사용자명]
                # 예시 :  Statistics = [20220328, 59, 88, "UserB", 23, "UserC"]  
    sql = "select AVG(UserAttentionRate),MAX(UserAttentionRate),MIN(UserAttentionRate) from customer"
    
    curs.execute(sql)
    rows = curs.fetchone()
    tmp_avg = rows['AVG(UserAttentionRate)']
    tmp_max = rows['MAX(UserAttentionRate)']
    tmp_min = rows['MIN(UserAttentionRate)']
    
    sql ="select StartTime from manager"
    curs.execute(sql)
    rows = curs.fetchone()
    tmp_date = rows['StartTime'].date()

    sql = "select UserName from customer where UserAttentionRate = (select MAX(UserAttentionRate) from customer)"
    curs.execute(sql)
    rows = curs.fetchone()
    tmp_maxUser = rows['UserName']
    sql = "select UserName from customer where UserAttentionRate = (select MIN(UserAttentionRate) from customer)"
    curs.execute(sql)
    rows = curs.fetchone()
    tmp_minUser = rows['UserName']
    Statistics=[]
    Statistics.append(tmp_date)
    Statistics.append(tmp_avg)
    Statistics.append(tmp_max)
    Statistics.append(tmp_maxUser)
    Statistics.append(tmp_min)
    Statistics.append(tmp_minUser)
        
        
       # ☆ 서버 연결 요소 ----------------------------------------------------------------------------------------------☆  
       
    # 아래는 입력 예시입니다. 만일 서버로부터 변수를 입력받는 경우 아래 내용은 주석처리해야합니다.        
    # User_Image = 유저의 이미지
    User_Image=tkinter.PhotoImage(file="User_Image.png", master = Interface2)
    # UserDate = [사용자 참여도, 퍼즐성공, 퍼즐실패]
    #.29 UserData = [63, 0, 2]
    # User_AttnRate_Graph = [0시점, 1/4시점, 2/4시점, 3/4시점, 4/4시점]
    #.29 User_AttnRate_Graph = [70, 65, 81, 48, 83]
    # Whole_Time = 전체 회의 시간
    #.29 Whole_Time = 120
    # Statistics = [날짜, 평균 참여율, 최고 참여율, 최고 참여율 사용자, 최저 참여율, 최저 참여율 사용자]
    #.29 Statistics = [20220328, 59, 88, "UserB", 23, "UserC"]
    
    UserName          = I_UserName
    User_Avg_AttnRate = UserData[0]
    Puzzle_Succ       = UserData[1]
    Puzzle_Fail       = UserData[2]

    Date              = Statistics[0]
    Year=Date.year
    Month=Date.month
    Day=Date.day
    #.29 Year  = int(Date / 10000)
    #.29 Month = int((Date % 10000) / 100)
    #.29 Day   = int(Date % 100)

    Avg_AttnRate      = Statistics[1]
    Max_AttnRate      = Statistics[2]
    Max_AttnRate_User = Statistics[3]
    Min_AttnRate      = Statistics[4]
    Min_AttnRate_User = Statistics[5]
    # 입력 예시 종료
    # 서버 활성화 시, 위의 변수들의 주석 처리가 필요하다. 

    if(User_Avg_AttnRate <= 25) :
        AttnRate_Type = "매우 낮음"

    elif(25 < User_Avg_AttnRate and User_Avg_AttnRate <= 40) :
        AttnRate_Type = "낮음"
        
    elif(40 < User_Avg_AttnRate and User_Avg_AttnRate <= 50) :
        AttnRate_Type = "살짝 낮음"
        
    else :
        AttnRate_Type = "좋음"    
    # ====================================== 변수 선언 & 입력 종료 ======================================


    # 인터페이스의 좌측 상단 라벨 생성
    Interface2_Label_font = tkinter.font.Font(family="맑은 고딕", size=15, weight = "bold",  )

    Interface2_Label = Label(Interface2, text= UserName + " 님의 " 
                + str(Year) + "년 " + str(Month) + "월 " + str(Day) + "일 참여내역", font = Interface2_Label_font)
    Interface2_Label.place(x=50, y=30)


    # ======================================= 유저 이미지 생성 시작 ======================================
    User_Image_Label=tkinter.Label(Interface2, image=User_Image, width=200, height=200)
    User_Image_Label.place(x=100, y=70)
    # ======================================= 유저 이미지 생성 종료 ======================================


    # ======================================= 금일 유저 통계 시작 =======================================

    User_Stat_X = 70
    User_Stat_Y = 300
    User_Stat_Label_font = tkinter.font.Font(family="맑은 고딕", size=12)

    User_Stat_Label1 = Label(Interface2, text="참여도 :                  " + "( 평균 :       % )", font = User_Stat_Label_font)
    User_Stat_Label1.place(x=User_Stat_X, y=User_Stat_Y)  

    User_Stat_Label2 = Label(Interface2, text="퍼즐인증 성공 / 실패 횟수 : " + str(Puzzle_Succ) + " / " + str(Puzzle_Fail) + " 회 ", font = User_Stat_Label_font)
    User_Stat_Label2.place(x=User_Stat_X, y=User_Stat_Y + 25)

    AttnRate_Type_Label_font=tkinter.font.Font(family="맑은 고딕", size=12, weight = "bold")

    AttnRate_Type_Label =  Define_AttrRate_Type_Color(User_Avg_AttnRate, Interface2)
    AttnRate_Type_Label.place(x=User_Stat_X + 65, y=User_Stat_Y)

    Avg_AttnRate_Label = Define_AttrRate_Color(User_Avg_AttnRate, Interface2)
    Avg_AttnRate_Label.place(x=User_Stat_X + 210, y=User_Stat_Y)


    # ======================================= 금일 유저 통계 종료 =======================================


    # ================================== 금일 전체 참여율 통계 생성 시작 ==================================
    Today_Stat_X = 480
    Today_Stat_Y = 250

    Today_Stat_Label1_font = tkinter.font.Font(family="맑은 고딕", size=12, weight = "bold")
    Today_Stat_Label1 = Label(Interface2, text= 
                            str(Year) + "년 " + str(Month) + "월 " + str(Day) + "일"
                            + " 회의 참여율 통계", font = Today_Stat_Label1_font)
    Today_Stat_Label1.place(x= Today_Stat_X + 50, y= Today_Stat_Y + 40)

    Today_Stat_Label2_font = tkinter.font.Font(family="맑은 고딕", size=11)
    Today_Stat_Label2 = Label(Interface2, text= " 금일 평균 참여율 :      %", font = Today_Stat_Label2_font)
    Today_Stat_Label2.place(x= Today_Stat_X + 50 , y= Today_Stat_Y + 75)

    Today_Stat_Label3 = Label(Interface2, text= " 최고 참여율 :      %" + " (           )", font = Today_Stat_Label2_font)
    Today_Stat_Label3.place(x=Today_Stat_X + 50, y=Today_Stat_Y + 100)

    Today_Stat_Label4 = Label(Interface2, text= " 최저 참여율 :      %" + " (           )", font = Today_Stat_Label2_font)
    Today_Stat_Label4.place(x=Today_Stat_X + 50, y=Today_Stat_Y + 125)



    Today_User_AttnRate_font = tkinter.font.Font(family="맑은 고딕", size=11, weight = "bold")


    Today_Avg_AttnRate_Label = Define_AttrRate_Color(Avg_AttnRate, Interface2)
    Today_Avg_AttnRate_Label.place(x=Today_Stat_X + 185, y=Today_Stat_Y + 75)
    Today_Max_User_Label = Define_AttrRate_Color(Max_AttnRate, Interface2)
    Today_Max_User_Label.place(x=Today_Stat_X + 150, y=Today_Stat_Y + 100)
    Today_Min_User_Label = Define_AttrRate_Color(Min_AttnRate, Interface2)
    Today_Min_User_Label.place(x=Today_Stat_X + 150, y=Today_Stat_Y + 125)

    Today_UserName_font = tkinter.font.Font(family="맑은 고딕", size=11, weight = "bold")
    Today_Max_UserName_Label = Label(Interface2, text= Max_AttnRate_User , font = Today_UserName_font)
    Today_Max_UserName_Label.place(x=Today_Stat_X + 200, y=Today_Stat_Y + 100)
    Today_Min_UserName_Label = Label(Interface2, text= Min_AttnRate_User , font = Today_UserName_font)
    Today_Min_UserName_Label.place(x=Today_Stat_X + 200, y=Today_Stat_Y + 125)

    # ================================== 금일 전체 참여율 통계 생성 종료 ==================================



    # ==================================== 유저 참여율 그래프 생성 시작 ===================================
    fig = plt.figure()
    fig.set_size_inches(2.9, 2.5)

    plt.plot([0, Whole_Time/4 * 1,  Whole_Time/4 * 2,  Whole_Time/4 * 3,  Whole_Time/4 * 4 ],User_AttnRate_Graph, color='blue', marker='o', linestyle='solid')
    plt.hlines(0,0,Whole_Time,color="None")
    plt.hlines(25,0,Whole_Time,color="red")
    plt.hlines(40,0,Whole_Time,color="yellow")
    plt.hlines(50,0,Whole_Time,color="green")
    plt.hlines(100,0,Whole_Time*1.3,color="None")

    plt.xlabel('time')
    plt.ylabel('Attention Rate')
    plt.grid(True)


    canvas = FigureCanvasTkAgg(fig, master=Interface2)
    canvas.draw()
    canvas.get_tk_widget().place(x=500, y=30)

    # ==================================== 유저 참여율 그래프 생성 종료 ===================================


    Interface2.mainloop()
 
# ★    
def Admin_Interface3():
    # Interface3 시작
    Interface3 = Tk()
    Interface3.title("Interface3")
    Interface3.geometry('800x300') 
    
    Question_Content = {}
    Question_Answer = {}
    # ========================= 고정된 내용 생성 : Title + Attributes 시작 ==========================
    # Title
    Title = Label(Interface3, text="자동 출결 미인증 참여자 목록")
    Title.configure(font=("맑은 고딕", 15, "bold"))
    Title.place(x=30,y=10)

    # Attributes
    Att1 = Label(Interface3, text="참여자명")
    Att1.configure(font=("맑은 고딕", 10))
    Att1.place(x=30,y=90)

    Att2 = Label(Interface3, text="평균 참여율")
    Att2.configure(font=("맑은 고딕", 10))
    Att2.place(x=120,y=90)

    Att3 = Label(Interface3, text="퍼즐 실패 / 시도 횟수")
    Att3.configure(font=("맑은 고딕", 10))
    Att3.place(x=250,y=90)

    Att4 = Label(Interface3, text="전체 출결 횟수")
    Att4.configure(font=("맑은 고딕", 10))
    Att4.place(x=420,y=90)

    Att5 = Label(Interface3, text="질문 여부")
    Att5.configure(font=("맑은 고딕", 10))
    Att5.place(x=550,y=90)

    Att6 = Label(Interface3, text="출석")
    Att6.configure(font=("맑은 고딕", 10))
    Att6.place(x=670,y=90)
    # ========================= 고정된 내용 생성 : Title + Attributes 종료 ==========================



    # ★ 서버 연결 요소 ----------------------------------------------------------------------------------------------★     
    # 출석율이 낮아 출석 인증이 되지 않은 참여자 목록을 표시합니다.
    # AbsenceReviewList = 자동 출결 미인증 참여자 목록
    curs = conn.cursor(pymysql.cursors.DictCursor)
    sql = "select* from customer where (UserAttentionRate <= 50 or Puzzle_Fail >= 1 or Is_Question = true)"
    # 평균 참석율50%이하 혹은 퍼즐 실패 횟수 1 이상 존재 혹은 질문을 받음
    curs.execute(sql)
    rows = curs.fetchall()
    AbsenceReviewList=[]
    tmp_list=[]

    for row in rows:
        tmp_list=[]
        tmp_list.append(row['UserName'])
        tmp_list.append(row['UserAttentionRate'])
        tmp_list.append(row['Puzzle_Fail'])
        tmp_list.append(row['Puzzle_IsCorrect'])
        tmp_list.append(row['AdminAttend'])
        tmp_list.append(row['TotalCourse'])
        tmp_list.append(row['Is_Question'])
        tmp_list.append(row['IsAttend'])
        AbsenceReviewList.append(tmp_list)
    
        # 예시 : AbsenceReviewList = (
                                    # [참여자1, 오늘 평균 참여율, 오늘 퍼즐 실패 횟수, 오늘 퍼즐 시도 횟수, 젠체 출석 인정 횟수, 전체 수업 횟수, 질문 여부, 출석 여부]
                                    # [참여자3, 오늘 평균 참여율, 오늘 퍼즐 실패 횟수, 오늘 퍼즐 시도 횟수, 젠체 출석 인정 횟수, 전체 수업 횟수, 질문 여부, 출석 여부]
                                    # [참여자5, 오늘 평균 참여율, 오늘 퍼즐 실패 횟수, 오늘 퍼즐 시도 횟수, 젠체 출석 인정 횟수, 전체 수업 횟수, 질문 여부, 출석 여부]
                                    # [참여자8, 오늘 평균 참여율, 오늘 퍼즐 실패 횟수, 오늘 퍼즐 시도 횟수, 젠체 출석 인정 횟수, 전체 수업 횟수, 질문 여부, 출석 여부]
                                    # ...
                                    # )                                                              
    # ☆ 서버 연결 요소 ----------------------------------------------------------------------------------------------☆  
        
    # 아래는 임시 입력 값입니다. 서버로부터 변수를 입력받으면 주석처리 해야 햡니다.    
#     AbsenceReviewList = (["UserA", 33, 1, 2, 5, 5, True],
#                         ["UserD", 60, 1, 1, 5, 5, False],
#                         ["UserF", 45, 0, 1, 4, 5, False],
#                         ["UserG", 13, 0, 3, 5, 5, True],
#                         ["UserI", 44, 2, 2, 5, 5, False]
#                         )

    User_Num = len(AbsenceReviewList)
    
       
    # ============================== 자동 출결 미인증 참여자 목록 생성 ===============================

    def Question_Result(Question_UserName, Question_Content, Question_Answer) :
        Question_Interface = Tk()
        Question_Interface.title("Question_Content")
        Question_Interface.geometry('300x100') 
        Input_Text_Label1 = Label(Question_Interface, text = "질문 내용 : " + Question_Content)
        Input_Text_Label1.place(x=1, y=0)
        Input_Text_Label2 = Label(Question_Interface, text = Question_UserName + "의 답변 : " + Question_Answer)
        Input_Text_Label2.place(x=1, y=25)
        Question_Interface.mainloop()
    Y = 120
    
    def Attend_True(Review_UserName) :
        Attend_True_Interface = Tk()
        Attend_True_Interface.title("Attend_True")
        Attend_True_Interface.geometry('300x100') 
        Input_Text_Label1 = Label(Attend_True_Interface , text = "'" + Review_UserName + "'님이 [출석]되었습니다.")
        Input_Text_Label1.place(x=1, y=0)
        # ★ 서버 연결 요소 ----------------------------------------------------------------------------------------------★
        # Attend_True는 참여자의 출석 여부를 [출석]으로 입력하는 함수입니다.
        # [출석]이 된 유저의 이름은 'Review_UserName'입니다.
        curs = conn.cursor()
        sql = "update customer set IsAttend=1 where UserName=%s"
        curs.execute(sql,Review_UserName)
        conn.commit()
        # DB에 금일 'Review_UserName'가 출석되었다고 입력하면 됩니다.
        
          # 모든 유저의 출석 Default값은 '출석'입니다. 따라서 원래는 해당 함수는 필요가 없습니다.
          # 다만, 버튼을 잘못 눌러 일부 참여자를 [미출석]으로 한 경우를 대비하여,
          # 해당 버튼에서 [출석]으로 변동되는 기능을 활성화하였습니다.
          
        # ☆ 서버 연결 요소 ----------------------------------------------------------------------------------------------☆
        print("'" + Review_UserName + "'님이 [출석]되었습니다.")      
        Attend_True_Interface .mainloop()
        
    def Attend_False(Review_UserName) :
        Attend_False_Interface = Tk()
        Attend_False_Interface.title("Attend_False")
        Attend_False_Interface.geometry('300x100') 
        Input_Text_Label1 = Label(Attend_False_Interface, text = "'" + Review_UserName + "'님이 [미출석]되었습니다.")
        Input_Text_Label1.place(x=1, y=0)
        # ★ 서버 연결 요소 ----------------------------------------------------------------------------------------------★
        # Attend_False는 참여자의 출석 여부를 [미출석]으로 입력하는 함수입니다.
        # [미출석]이 된 유저의 이름은 'Review_UserName'입니다.
        curs = conn.cursor()
        sql = "update customer set IsAttend=0 where UserName=%s"
        curs.execute(sql,Review_UserName)
        conn.commit()
        # DB에 금일 'Review_UserName'가 미출석되었다고 입력하면 됩니다.
          # 모든 유저의 출석 Default값은 '출석'입니다. 
          # '미출석'의 경우 현재 함수인 Attend_False()에서 입력을 받아야 설정됩니다.
        # ☆ 서버 연결 요소 ----------------------------------------------------------------------------------------------☆
        print("'" + Review_UserName + "'님이 [미출석]되었습니다.")
        
        Attend_False_Interface.mainloop()    
        
    Y = 120

    for i in range(User_Num) :
        
        # 참여자명
        Name = Label(Interface3, text= AbsenceReviewList[i][0])
        Name.place(x=30,y=Y)
        
        # 평균 참여율
        AvgAttn = Label(Interface3, text= str(AbsenceReviewList[i][1]) + "%") 
        AvgAttn.place(x=120,y=Y)
        
        # 퍼즐 실패 / 시도 횟수
        Fail_and_Try = Label(Interface3, text= str(AbsenceReviewList[i][2]) + " / " + str(AbsenceReviewList[i][3])) 
        Fail_and_Try.place(x=250,y=Y)
        
        # 전체 출결 횟수
        Attn = Label(Interface3, text= str(AbsenceReviewList[i][4]) + " / " + str(AbsenceReviewList[i][5])) 
        Attn.place(x=420,y=Y)

    #Input_Text_Button = tkinter.Button(Interface1, overrelief="solid", width=20)
    #Input_Text_Button.config(width = 3, height = 1, command=Search, text = "조회")
    #Input_Text_Button.place(x = 125, y = 320)
    
        # 질문 여부
        if AbsenceReviewList[i][6] == True : 
            Question = tkinter.Button(Interface3, overrelief="solid", width=20)
            
            # ★ 서버 연결 요소 ----------------------------------------------------------------------------------------------★
            # 금일 회의에서 질문은 받은 유저입니다. DB에 해당 유저가 받은 질문 내용과 답변을 수신받아 출력해야합니다.
            # 1. 해당 유저의 이름 = AbsenceReviewList[i][0]
            curs = conn.cursor()
            sql ="select Question_Detail,Question_Answer from customer where UserName=%s"
            curs.execute(sql,AbsenceReviewList[i][0])
            tmp_rows = curs.fetchone()
            # 2. 질문 내용 => DB에서 받은 질문 내용을 입력
            #    유저 'AbsenceReviewList[i][0]'가 받은 질문 내용을 아래 Qustion_Content[i]에 대입해야 합니다.
            Question_Content[i] = tmp_rows[0]
            # 3. 질문 답변 => 아래 Qeustion_Answer에 입력
            #    유저 'AbsenceReviewList[i][0]'가 입력한 질문 답변을 아래 Question_Answer[i]에 대입해야 합니다.
            Question_Answer[i] = tmp_rows[1]
            # ☆ 서버 연결 요소 ----------------------------------------------------------------------------------------------☆
            Question.config(width = 3, height = 1, command = lambda x = i: Question_Result(AbsenceReviewList[x][0],Question_Content[x],Question_Answer[x]), text="보기")
            Question.place(x=550,y=Y)
                 
        else :
            Question_Label = Label(Interface3, text= "X")
            Question_Label.place(x=550,y=Y)
            
        # 출석
        ReviewAttn_True = tkinter.Button(Interface3, overrelief="solid", width=20)
        ReviewAttn_True.config(width = 3, height = 1, command = lambda x = i: Attend_True(AbsenceReviewList[x][0]), text="출석")
        ReviewAttn_True.place(x=650,y=Y)
        ReviewAttn_False = tkinter.Button(Interface3, overrelief="solid", width=20)
        ReviewAttn_False.config(width = 5, height = 1, command = lambda x = i: Attend_False(AbsenceReviewList[x][0]), text="미출석")
        ReviewAttn_False.place(x=690,y=Y)
        
        Y += 25
    # ============================== 자동 출결 미인증 참여자 목록 종료 ===============================


    Interface3.mainloop()
  
# ★    
def User_Interface1(I_UserName) : 


    t = threading.Thread(target=MC.main)
    t.start()
    
    Interface4 = Tk()
    Interface4.title("User_Interface")
    Interface4.geometry("300x250")
    
    Interface4.resizable(False, False)

    # ====================================== 변수 선언 & 입력 시작 ======================================
    # 변수 선언
    global Puzzle_Receive
    global Question_Receive 
    global IsStart, IsAttend, Question_Receive
    global Attention_Rate_Init
    IsStart = False
    IsStart_Answer = False
    UserName = "NULL"
    global IsAttend
    IsAttend = False
    IsAttend_Answer = "NULL"
    global Avg_Attn_Rate
    Avg_Attn_Rate = -1

    global IsTimerOn
    IsTimerOn = False
    global TimerCount
    global TimerCount_Min
    TimerCount = -1
    TimerCount_Min = -1
    Puzzle_Receive = False
    Puzzle_IsCorrect = False

    Question_Receive = False
    IsQuestion = "N"
    Question_Detail = "NULL"
    Question_Answer = "NULL"
    

    #UserData = [True, True, 50]
    Q_Data = [True, True, False, True, " [Hello, World!]를 입력해주세요."]
    
    # 이미지
    Icon_Image=tkinter.PhotoImage(file="Puzzle_Button.png",  master=Interface4)


    UserName         = I_UserName
    # IsStart          = UserData[0]
    # if IsStart == True :
    #         IsStart_Answer = "Y"
    # else :
    #     IsStart_Answer = "N"
    # IsAttend         = UserData[1]
    # if IsAttend == True :
    #     IsAttend_Answer = "Y"
    # else :
    #     IsAttend_Answer = "N"
    # Avg_Attn_Rate    = UserData[2]
    
    # Puzzle_Receive   = Q_Data[0]
    # Puzzle_IsCorrect = Q_Data[1]

    # Question_Receive = Q_Data[2]

    # if Question_Receive == True :
    #     IsQuestion = "Y"
    # else :
    #     IsQuestion = "N"
    # Question_Detail  = Q_Data[3]

    AttnRate_Type_Label_font=tkinter.font.Font(family="맑은 고딕", size=12, weight = "bold")
    


    # ====================================== 변수 선언 & 입력 종료 ======================================

    Label_X = 10
    Label_Y = 50
    
    Puzzle_Button = tkinter.Button(Interface4, overrelief="solid", width=20, state=tkinter.DISABLED)
    Puzzle_Button.config(width = 30, height = 30, command= lambda: IsPuzzleReceive(UserName),image = Icon_Image)
    Puzzle_Button.place(x = Label_X + 90, y = Label_Y + 60)
    
    def Puzzle_Count() : 
        global TimerCount, IsTimerOn, Puzzle_Receive
        global TimerCount_Min
        if TimerCount > -1 and Puzzle_Receive == True:
            Interface4.after(1000, Puzzle_Count)
            
            TimerCount_Min = (int)(TimerCount+1)/60
            Exit_Label=tkinter.Label(Interface4, text = "퍼즐 남은 시간 : " + f"{TimerCount + 1}초  ")
            Exit_Label.place(x=160, y=115)
        else :
            Exit_Label=tkinter.Label(Interface4, text = "                                                ")
            Exit_Label.place(x=160, y=115)
            Puzzle_Button = tkinter.Button(Interface4, overrelief="solid", width=20, state=tkinter.DISABLED)
            Puzzle_Button.config(width = 30, height = 30, command= lambda: IsPuzzleReceive(UserName),image = Icon_Image)
            Puzzle_Button.place(x = Label_X + 90, y = Label_Y + 60)
            
            if Puzzle_Receive == True : 
                curs = conn.cursor()
                sql = "update customer set Puzzle_Receive=false where UserName=%s"
                curs.execute(sql, I_UserName)
                tmp_rst = curs.fetchone()
                conn.commit()
                
                curs = conn.cursor()
                sql = "update customer set Puzzle_Fail=Puzzle_Fail+1 where UserName=%s"
                curs.execute(sql, I_UserName)
                tmp_rst = curs.fetchone()
                conn.commit()
                Puzzle_Receive = False
                IsTimerOn = False
                
            return
  
    # ====================================== 인터페이스 생성 시작 =======================================
    def Print_Interface() :
        global IsStart, IsAttend, Puzzle_Receive, Question_Receive
        Label_X = 10
        Label_Y = 50
        Label_font = tkinter.font.Font(family="맑은 고딕", size=12)
        
        if IsStart == True :
            IsStart_Answer = "Y"
        else :
            IsStart_Answer = "N"
            
        if IsAttend == True :
            IsAttend_Answer = "Y"
        else :
            IsAttend_Answer = "N"

        if Question_Receive == True :
            IsQuestion = "Y"
        else :
            IsQuestion = "N"
        Question_Detail  = Q_Data[4]


        Label_User = Label(Interface4, text="사용자 이름 : " + UserName, font = Label_font)
        Label_User.place(x=Label_X, y=Label_Y - 50) 
    
        Label0 = Label(Interface4, text="현재 회의 여부 : " + IsStart_Answer, font = Label_font)
        Label0.place(x=Label_X, y=Label_Y - 25)  


        Label1 = Label(Interface4, text="현재 동공인식 여부 : " + IsAttend_Answer, font = Label_font)
        Label1.place(x=Label_X, y=Label_Y)  


        Label2 = Label(Interface4, text="현재 회의 참여율 :          % ", font = Label_font)
        Label2.place(x=Label_X, y=Label_Y + 25)
        Avg_AttnRate_Label = Define_AttrRate_Color(Avg_Attn_Rate, Interface4)
        Avg_AttnRate_Label.place(x=Label_X + 150, y=Label_Y + 25)

        Label3 = Label(Interface4, text= "퍼즐 알람 : ", font = Label_font)
        Label3.place(x=Label_X, y=Label_Y + 65)

        global IsTimerOn, TimerCount
        if Puzzle_Receive == True : 
            if IsTimerOn == False :
                IsTimerOn = True
                TimerCount = 29
                Puzzle_Button = tkinter.Button(Interface4, overrelief="solid", width=20)
                Puzzle_Button.config(width = 30, height = 30, command= lambda: IsPuzzleReceive(UserName),image = Icon_Image)
                Puzzle_Button.place(x = Label_X + 90, y = Label_Y + 60)
                
                curs = conn.cursor()
                sql = "update customer set Puzzle_IsCorrect=Puzzle_IsCorrect+1 where UserName=%s"
                curs.execute(sql,I_UserName)
                conn.commit()
            Puzzle_Count()
        
        # if Puzzle_Receive == True :
        #     Puzzle_Button = tkinter.Button(Interface4, overrelief="solid", width=20)
        # else :
        #    Puzzle_Button = tkinter.Button(Interface4, overrelief="solid", width=20, state=tkinter.DISABLED)
        
        # Puzzle_Button.config(width = 30, height = 30, command= lambda: IsPuzzleReceive(UserName),image = Icon_Image)
        # Puzzle_Button.place(x = Label_X + 90, y = Label_Y + 60)

        Label4 = Label(Interface4, text= "질의 여부 : " + IsQuestion, font = Label_font)
        Label4.place(x=Label_X, y=Label_Y + 95)

        Label3 = Label(Interface4, text= "질문 내용 보기 : ", font = Label_font)
        Label3.place(x=Label_X, y=Label_Y + 125)
    
        if Question_Receive == True : 
            Question_Button = tkinter.Button(Interface4, overrelief="solid", width=20)
        else :
            Question_Button = tkinter.Button(Interface4, overrelief="solid", width=20, state=tkinter.DISABLED)
        Question_Button.config(width = 30, height = 30, command= lambda: IsQuestionReceive(UserName, Question_Detail),image = Icon_Image)
        Question_Button.place(x = Label_X + 125, y = Label_Y + 120)
        
        curs = conn.cursor()
        conn.commit()


    # 타이머 작동 : 타이머가 작동되지 않은 상황에서 퍼즐을 수신한 경우
    # if IsTimerOn == False and Puzzle_Receive == True:
    #     IsTimerOn = True
    #     TimerCount = 120   
       
    def DB():
        curs = conn.cursor()
        conn.commit()
       
    def Repeat_Print() :
        Interface4.after(1000, Repeat_Print)
        # ★★★ 해당 부분은 메인 프로그램으로부터 데이터를 받습니다. ★★★
        # 서버가 아닌, 메인 프로그램과의 연결 필수!!!!
        # 메인 프로그램으로부터 받는 데이터는 아래와 같습니다.
            # 1. 유저 평균 참여율 : Avg_Attn_Rate
            # 2. 유저 참석 여부 : IsAttend
        global Avg_Attn_Rate
        global IsAttend
        global IsStart 
        global Puzzle_Receive   
        global Puzzle_IsCorrect 
        global Question_Receive 
        global Question_Content 
        global Sec
        global Puzzle_Receive, IsTimerOn, TimerCount
        global Attention_Rate_Init
    
        Avg_Attn_Rate = MC.Attend_Rate
        IsAttend = MC.IsAttend
        
        if IsStart == True and Attention_Rate_Init == False:
            MC.Attend_Time = 0 
            MC.Whole_Time = 0
            Attention_Rate_Init = True
            
        if IsStart == False :
            Attention_Rate_Init = False   
        
        if Puzzle_Receive == True and IsTimerOn == True :
            TimerCount -= 1
            
            
        #.30
        curs = conn.cursor()
        sql ="select IsStart from manager"
        curs.execute(sql)
        rows = curs.fetchone()
        IsStart = rows[0]
        conn.commit()
        
        new_num=-1
        if IsStart == True :
            
            curs = conn.cursor()
            sql ="update customer set IsStart=1"
            curs.execute(sql)
            conn.commit()
            
            sql = "select Number from manager"
            curs.execute(sql)
            rows = curs.fetchone()
            new_num=rows[0] #현재 몇번째 회의가 진행중인지 
            
            sql = "select StartTime from manager"
            curs.execute(sql)
            rows = curs.fetchone()
            tmp_time = rows[0]
            
            sql ="update customer set Date=%s where IsStart=1"
            curs.execute(sql,tmp_time)
            conn.commit()
            
            
        # ★ 서버 연결 요소 ----------------------------------------------------------------------------------------------★
        # 메인 프로그램을 통해 전송받는 값 중 '현재 동공인식 여부'와 '현재 회의 참여율'를 DB에 전송해야 합니다.
        # 즉, '현재 동공인식 여부'와 '현재 회의 참여율'인 IsAttend과 MC.Attend_Rate를 참여자인 UserName의 DB에 전송해야합니다.
        # 1. 참여자 명 = UserName
        # 2. 현재 동공인식 여부 = IsAttend
        # 3. 현재 회의 참여율 = MC.Attend_Rate

        curs = conn.cursor()
        sql = "update customer set IsAttend=%s, UserAttentionRate=%s where UserName = %s"
        curs.execute(sql,(IsAttend,MC.Attend_Rate,UserName))
        conn.commit()

        DB()
        # ☆ 서버 연결 요소 ----------------------------------------------------------------------------------------------☆
        
        
        # ★ 서버 연결 요소 ----------------------------------------------------------------------------------------------★
        # 1분 단위로, 현재 유저의 '회의 참여율'를 DB에 전송해야 합니다.
        #*분마다->sec/60
        # int형 변수 Sec가 '초'를 의미하며, 60Sec이 될 떄마다 전송하면 됩니다.
        # 아래 주석 처리된 if문을 사용하여, 1분 단위로 참여자의 값을 입력하면 됩니다.
        
#         curs = conn.cursor(pymysql.cursors.DictCursor)
#         sql ="select StartTime from manager"
#         curs.execute(sql)
#         rows = curs.fetchone()
#         start_t= rows['StartTime']
        #06_02 이제 필요없는 부분 
        
                # 내용
        # ☆ 서버 연결 요소 ----------------------------------------------------------------------------------------------☆
   
        # ★ 서버 연결 요소 ----------------------------------------------------------------------------------------------★
        # DB로 부터 아래 데이터를 받습니다.
        # DB 속 참여자 'UserName'의 데이터 목록인 Q_Data를 DB로부터 전송받으면 됩니다.
        # 1. 참여자 명 = UserName
        # 2. Q_Data = [회의시작여부, 퍼즐 수신여부, 퍼즐 정답여부, 질문 수신여부, 질문 내용]
            # 예시 : Q_Data = [True, False, False, "금일 질문 내용"]
        curs = conn.cursor()
        sql = "select IsStart,Puzzle_Receive,Puzzle_IsCorrect,Question_Receive,Question_Detail from customer where UserName = %s"
        curs.execute(sql,UserName)
        tmp_rst = curs.fetchone()
        Q_Data[0] = tmp_rst[0]
        Q_Data[1] = tmp_rst[1]
        Q_Data[2] = tmp_rst[2]
        Q_Data[3] = tmp_rst[3]
        Q_Data[4] = tmp_rst[4]

        #*Q_Data = [True, True, False, True, " [Hello, World!]를 입력해주세요."]
        # ☆ 서버 연결 요소 ----------------------------------------------------------------------------------------------☆
        
        IsStart = Q_Data[0]
        Puzzle_Receive   = Q_Data[1]
        Puzzle_IsCorrect = Q_Data[2]
        Question_Receive = Q_Data[3]
        Question_Content = Q_Data[4]
        
        if MC.cnt >= 5 and IsStart == True:
            Sec += 1
#        
        if Sec != 0 and Sec % 1 == 0 and IsStart == True:
            curs = conn.cursor()
            sql ="insert into attendance(UserName, Number, Minute, Attend_Rate) values(%s,%s,%s,%s)"
            curs.execute(sql,(UserName,new_num,Sec,Avg_Attn_Rate))
            print("Sec 시간 : " + str(Sec/1))
            conn.commit()
        
        # 서버로부터 데이터를 받는 것과 동일한 환경을 테스트하기 위해, 일부 값을 랜덤화하였습니다.       
        Print_Interface() 
	    
    Repeat_Print()

    # ======================================= 금일 유저 통계 종료 =======================================

    # ========================================= 퍼즐 & 질문 버튼 함수 생성 시작 ========================================
    def IsPuzzleReceive(I_UserName) :
        # ★ 서버 연결 요소 ----------------------------------------------------------------------------------------------★
        # 퍼즐을 수신받은 경우 [퍼즐]버튼이 활성화됩니다.
        # IsPuzzleReceive()는 해당 [퍼즐]버튼을 눌렀을 때 실행되는 함수입니다.
        # 따라서 해당 유저의 금일 퍼즐 인증 횟수를 1 증가시키면 됩니다.
        # 1. 참여자 명 : I_UserName 
        # curs = conn.cursor()
        # sql = "update customer set Puzzle_IsCorrect=Puzzle_IsCorrect+1 where UserName=%s"
        # curs.execute(sql,I_UserName)
        # conn.commit()
        # ☆ 서버 연결 요소 ----------------------------------------------------------------------------------------------☆
        Puzzle_Interface(I_UserName)
        
    def IsQuestionReceive(I_UserName, I_Question_Detail) :
        # ★ 서버 연결 요소 ----------------------------------------------------------------------------------------------★
        # 질문을 수신받은 경우 [질문]버튼이 활성화됩니다.
        # IsQuestionReceive()는 해당 [질문]버튼을 눌렀을 때 실행되는 함수입니다.
        # 따라서 해당 유저의 금일 질문 횟수 여부를 True로 변경시키면 됩니다.
        # 1. 참여자 명 : I_UserName 
        curs = conn.cursor()
        I_Data = (I_Question_Detail,I_UserName)
        sql = "update customer set Question_Receive = 1,Question_Detail = %s where UserName=%s"
        curs.execute(sql,I_Data)
        conn.commit()
        # ☆ 서버 연결 요소 ----------------------------------------------------------------------------------------------☆
        Question_Interface(I_UserName, I_Question_Detail)
    # ========================================= 퍼즐 & 질문 버튼 함수 생성 종료 ========================================
    Interface4.mainloop()

# ★
def Puzzle_Interface(I_UserName) :
    global Puzzle_Count
    global Stime
    global txt_captcha
    global Puzzle_Receive
    global IsTimerOn
    Puzzle_Count = 4
    Stime = 3
    
    Puzzle = Tk()
    Puzzle.title("Puzzle_Interface")
    Puzzle.geometry('300x300') 

    Puzzle_Answer = StringVar()

    Captcha_Image = ImageCaptcha(width=160, height=90, fonts =['C:\Windows\Fonts\Arial.ttf'])

    length_of_string = 4
    txt_captcha = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(length_of_string))
    print(txt_captcha)

    Captcha_Image.generate(txt_captcha)
    Captcha_Image.write(txt_captcha, "captcha_result.png")
    User_Image=tkinter.PhotoImage(file="captcha_result.png", master = Puzzle)

    User_Image_Label=tkinter.Label(Puzzle, image=User_Image, width=150, height=150)
    User_Image_Label.place(x=5, y=0)

    Input_Text = Entry(Puzzle, textvariable = Puzzle_Answer, width = 10)
    Input_Text.place(x=5,y=170)
    
    
    def DB():
        curs = conn.cursor()
        conn.commit()
    
    def Answer(text_, UserName) :
        global Puzzle_Count
        global txt_captcha
        global IsTimerOn
        
        print("text_  : " + text_)
        print("txt_captcha : " + txt_captcha)
        if text_ == txt_captcha :
            print("일치합니다.\n퍼즐 인증 성공!")  
            Input_Text.delete(0, "end")
            
            
            Label_Reset=tkinter.Label(Puzzle, text = "                                                        ")
            Label_Reset.place(x=5, y=215)
            Label_=tkinter.Label(Puzzle, text = "일치합니다. 퍼즐 인증 성공!                                ")
            Label_.place(x=5, y=215)
            print("현재 참여자 이름 : " + UserName)
            # ★ 서버 연결 요소 ----------------------------------------------------------------------------------------------★
            # 현재 유저의 Puzzle 성공 횟수를 1증가 시킵니다.
            # 현재 유저명 : UserName
            curs = conn.cursor()
            sql = "update customer set Puzzle_Succ=Puzzle_Succ+1 where UserName=%s"
            curs.execute(sql,UserName)
            conn.commit()
            
            curs = conn.cursor()
            sql = "update customer set Puzzle_Receive=0"
            curs.execute(sql)
            tmp_rst = curs.fetchone()
            IsTimerOn = False
            # ☆ 서버 연결 요소 ----------------------------------------------------------------------------------------------☆
            DB()
            Exit()
            return
        
        elif Puzzle_Count <= 0  :
            Label_Reset=tkinter.Label(Puzzle, text = "                                                   ")
            Label_Reset.place(x=5, y=215) 
            Label_=tkinter.Label(Puzzle, text = "남은 횟수를 모두 소진하였습니다. 퍼즐 인증 실패! ")
            Label_.place(x=5, y=215)
            print("남은 횟수를 모두 소진하였습니다.             \n퍼즐 인증 실패!")
            
            # ★ 서버 연결 요소 ----------------------------------------------------------------------------------------------★
            # 현재 유저의 Puzzle 성공 횟수를 1증가 시킵니다.
            # 현재 유저명 : UserName
            curs = conn.cursor()
            sql = "update customer set Puzzle_Fail=Puzzle_Fail+1 where UserName=%s"
            curs.execute(sql,UserName)
            conn.commit()
            
            curs = conn.cursor()
            sql = "update customer set Puzzle_Receive=0"
            curs.execute(sql)
            tmp_rst = curs.fetchone()
            IsTimerOn = False
            # ☆ 서버 연결 요소 ----------------------------------------------------------------------------------------------☆
            DB()
            Exit()
            return
        
        else : 
            print("문장과 일치하지 않습니다. 남은 횟수 : " + str(Puzzle_Count) + " / 5")
            Input_Text.delete(0, "end")
            Label_=tkinter.Label(Puzzle, text = "문장과 일치하지 않습니다. 남은 횟수 : " + str(Puzzle_Count) + " / 5")
            Label_.place(x=5, y=215)
            Puzzle_Count -= 1
            
    def Puzzle_Change() : 
        global txt_captcha
        txt_captcha = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(length_of_string))
        Captcha_Image.generate(txt_captcha)
        Captcha_Image.write(txt_captcha, "captcha_result.png")
        User_Image=tkinter.PhotoImage(file="captcha_result.png", master = Puzzle)
        print(txt_captcha)
        
        User_Image_Label=tkinter.Label(Puzzle, image=User_Image, width=150, height=150)
        User_Image_Label.place(x=5, y=0)
        
        Input_Text.place(x=5,y=170)
        Input_Text_Button.place(x = 90, y = 170)


    Input_Text_Button = tkinter.Button(Puzzle, overrelief="solid", width=20)
    Input_Text_Button.config(width = 3, height = 1, command=lambda:Answer(Input_Text.get(), I_UserName), text = "입력")
    Input_Text_Button.place(x = 90, y = 170)

    Text_Refill_Button = tkinter.Button(Puzzle, overrelief="solid", width=20)
    Text_Refill_Button.config(width = 10, height = 1, command=lambda:Puzzle_Change(), text = "이미지 변경")
    Text_Refill_Button.place(x = 170, y = 90)

    Stime = 3

    def Exit() :
     
        Input_Text_Button = tkinter.Button(Puzzle, overrelief="solid", width=20, state=tkinter.DISABLED)
        Input_Text_Button.config(width = 3, height = 1, command=lambda:Answer(), text = "입력")
        Input_Text_Button.place(x = 90, y = 170)
        
        Text_Refill_Button = tkinter.Button(Puzzle, overrelief="solid", width=20, state=tkinter.DISABLED)
        Text_Refill_Button.config(width = 10, height = 1, command=lambda:Puzzle_Change(), text = "이미지 변경")
        Text_Refill_Button.place(x = 170, y = 90)

        Input_Text.config(state = tkinter.DISABLED)
        Input_Text.place(x=5,y=170)
        global Stime
        global Puzzle_Receive
        
        Puzzle_Receive = False
        if Stime > 0:
            Puzzle.after(1000, Exit)
            Stime -= 1
            Exit_Label=tkinter.Label(Puzzle, text =f"{Stime + 1}초 뒤 꺼집니다.")
            Exit_Label.place(x=5, y=250)
        
        else : 
            Puzzle.destroy()
    Puzzle.mainloop()
    

# ★
def Question_Interface(I_UserName, I_Question_Detail) :
    global Question_Receive 
    Question = Tk()
    Question.title("Question_Interface")
    Question.geometry('500x200') 
   
    Question_Answer = StringVar()
    global Stime
    
    
    Question_Detail_Label=tkinter.Label(Question, text = "질문 내용 : " + I_Question_Detail)
    Question_Detail_Label.place(x=5, y=5)
    
    Input_Text = Entry(Question, textvariable = Question_Answer, width = 30)
    Input_Text.place(x=5,y=35)
    
    def Answer(text_, UserName) :
        global Question_Receive
        print("질문 입력 내용 : " + text_)
        # ★ 서버 연결 요소 ----------------------------------------------------------------------------------------------★
        # 질문의 대답을 DB에 전달해야 합니다.
        # 현재 유저명 : UserName
        # 전달해야할 대답(string) : text_
        curs = conn.cursor()
        I_Data = (text_,UserName)
        sql = "update customer set Question_Answer= %s where UserName=%s"
        curs.execute(sql,I_Data)
        conn.commit()
        # ☆ 서버 연결 요소 ----------------------------------------------------------------------------------------------☆
        Answer_Label=tkinter.Label(Question, text = "질문 입력이 완료되었습니다.")
        Answer_Label.place(x=5, y=75)
        
        curs = conn.cursor()
        sql = "update customer set Question_Receive=0 where UserName=%s"
        curs.execute(sql, UserName)
        tmp_rst = curs.fetchone()
        conn.commit()
        Question_Receive = False
        
        Exit()
        return
    
    Stime = 3
    
    def Exit() :     
        
        Input_Text_Button = tkinter.Button(Question, overrelief="solid", width=20, state=tkinter.DISABLED)
        Input_Text_Button.config(width = 3, height = 1, command=lambda:Answer(), text = "입력")
        Input_Text_Button.place(x = 220, y = 33)

        Input_Text.config(state=tkinter.DISABLED)
        Input_Text.place(x=5,y=35)
        global Stime
        global Question_Receive
        
        Question_Receive = False
        if Stime > 0:
            Question.after(1000, Exit)
            Stime -= 1
            Exit_Label=tkinter.Label(Question, text =f"{Stime + 1}초 뒤 꺼집니다.")
            Exit_Label.place(x=5, y=100)
        
        else : 
            Question.destroy()
            
    Input_Text_Button = tkinter.Button(Question, overrelief="solid", width=20)
    Input_Text_Button.config(width = 3, height = 1, command=lambda:Answer(Input_Text.get(), I_UserName), text = "입력")
    Input_Text_Button.place(x = 220, y = 33)
    Question.mainloop()
    

# 사용자 id와 password를 저장하는 변수 생성
user_id, password = StringVar(), StringVar()

# 참여자 로그인
# 참여자 목록을 서버로부터 받습니다. 
# User_List = 참여자 목록 배열
    # 예시 : User_List = ["UserA", "UserB", "UserC", "UserD", "UserE"]
# 아래는 예시 변수입니다. 서버에서 입력받는 경우 아래를 주석처리 하면 됩니다.

User_List = ["UserA", "UserB", "UserC", "UserD", "UserE"]
    
# 사용자 id와 password를 비교하는 함수
def Login():
    if user_id.get() == "Admin" and password.get() == "1":
        Login_Interface.destroy()
        print("Logged as Admin IN Successfully")
        Admin_Interface1()
        
    elif password.get() == "1":
        for x in User_List :
            if user_id.get() == x :    
                Login_Interface.destroy()
                print("Logged as User IN Successfully") 
                User_Interface1(x)   
        else :        
            print("Check your Username/Password")     
        
    else:
        print("Check your Username/Password")

# id와 password, 그리고 확인 버튼의 UI를 만드는 부분
tk.Label(Login_Interface, text = "Username : ").grid(row = 0, column = 0, padx = 10, pady = 10)
tk.Label(Login_Interface, text = "Password : ").grid(row = 1, column = 0, padx = 10, pady = 10)
tk.Entry(Login_Interface, textvariable =     user_id).grid(row = 0, column = 1, padx = 10, pady = 10)
tk.Entry(Login_Interface, textvariable = password, show='*').grid(row = 1, column = 1, padx = 10, pady = 10)
tk.Button(Login_Interface, text = "Login", command = Login).grid(row = 2, column = 1, padx = 10, pady = 10)

Login_Interface.mainloop()







# In[ ]:





# In[ ]:




