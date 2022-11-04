from __future__ import division
from concurrent.futures import thread
import numpy as np
import time
import os
import dlib
import cv2
import math
import threading

# import pymysql

class IrisTracking(object):
    #시선탐지 클래스
    def __init__(self):
        self.frame = None
        self.eye_left = None
        self.calibration = Adj()

        #얼굴탐지
        self._face_detector = dlib.get_frontal_face_detector()

        #facial landmark 사용
        cwd = os.path.abspath(os.path.dirname(__file__))
        model_path = os.path.abspath(os.path.join(cwd, "shape_predictor_68_face_landmarks.dat"))
        self._predictor = dlib.shape_predictor(model_path)

    @property
    def pupils_located(self):
        #동공 판독 확인
        try:
            int(self.eye_left.pupil.x)
            int(self.eye_left.pupil.y)
            return True
        except Exception:
            return False

    def _analyze(self):
        #얼글 탐지, Eye 객체 사용
        frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        faces = self._face_detector(frame)

        try:
            landmarks = self._predictor(frame, faces[0])
            self.eye_left = Eye(frame, landmarks, 0, self.calibration)

        except IndexError:
            self.eye_left = None

    def refresh(self, frame):
        #아래 반복문에서 활용
        self.frame = frame
        self._analyze()

    def pupil_left_center_coords(self):
        #왼쪽 눈 중앙좌표 반환
        if self.pupils_located:
            x = self.eye_left.mid_eye[0]
            y = self.eye_left.mid_eye[1]
            return (x, y)
        
    def pupil_left_coords(self):
        #왼쪽 눈 동공좌표 반환
        if self.pupils_located:
            x = self.eye_left.origin[0] + self.eye_left.pupil.x
            y = self.eye_left.origin[1] + self.eye_left.pupil.y
            return (x, y)

    def annotated_frame(self):
        #화면에 동공 표시해서 반환
        frame = self.frame.copy()

        if self.pupils_located:
            color = (0, 255, 0)
            x_left, y_left = self.pupil_left_coords()
            cv2.line(frame, (x_left - 5, y_left), (x_left + 5, y_left), color)
            cv2.line(frame, (x_left, y_left - 5), (x_left, y_left + 5), color)

        return frame

class Adj(object):
    #카메라 환경을 계산해서 수치를 조정하는 클래스
    def __init__(self):
        self.nb_frames = 20
        self.l_thresholds = []
        

    def is_complete(self):
        return len(self.l_thresholds) >= self.nb_frames

    def threshold(self, side):
        if side == 0:
            return int(sum(self.l_thresholds) / len(self.l_thresholds))
        

    @staticmethod
    def iris_size(frame):
        frame = frame[5:-5, 5:-5]
        height, width = frame.shape[:2]
        nb_pixels = height * width
        nb_blacks = nb_pixels - cv2.countNonZero(frame)
        return nb_blacks / nb_pixels

    @staticmethod
    def find_best_threshold(eye_frame):
        average_iris_size = 0.48
        trials = {}

        for threshold in range(5, 100, 5):
            iris_frame = Pupil.image_processing(eye_frame, threshold)
            trials[threshold] = Adj.iris_size(iris_frame)

        best_threshold, iris_size = min(trials.items(), key=(lambda p: abs(p[1] - average_iris_size)))
        return best_threshold

    def evaluate(self, eye_frame, side):
        threshold = self.find_best_threshold(eye_frame)

        if side == 0:
            self.l_thresholds.append(threshold)
       

class Eye(object):
    #눈만 새로 판독해서 프레임 만듦, 동공 탐지 시작
    left_center_POINTS = [36, 37, 38, 39, 40, 41]

    def __init__(self, original_frame, landmarks, side, calibration):
        self.frame = None
        self.center = None
        self.origin = None
        self.mid_eye = None
        self.pupil = None
        self.landmark_points = None

        self._analyze(original_frame, landmarks, side, calibration)

    @staticmethod
    def _middle_point(p1, p2):
        
        x = int((p1.x + p2.x) / 2)
        y = int((p1.y + p2.y) / 2)
        return (x, y)

    def _isolate(self, frame, landmarks, points):
        #눈만 따로 분리
        region = np.array([(landmarks.part(point).x, landmarks.part(point).y) for point in points])
        region = region.astype(np.int32)
        self.landmark_points = region

        height, width = frame.shape[:2]
        black_frame = np.zeros((height, width), np.uint8)
        mask = np.full((height, width), 255, np.uint8)
        cv2.fillPoly(mask, [region], (0, 0, 0))
        eye = cv2.bitwise_not(black_frame, frame.copy(), mask=mask)

        margin = 5
        max_x = np.max(region[:, 0]) + margin
        min_x = np.min(region[:, 0]) - margin
        max_y = np.max(region[:, 1]) + margin
        min_y = np.min(region[:, 1]) - margin

        self.frame = eye[min_y:max_y, min_x:max_x]
        self.origin = (min_x, min_y)

        height, width = self.frame.shape[:2]
        self.center = (width / 2, height / 2)
        self.mid_eye = ((min_x + max_x) / 2, (min_y + max_y) / 2)

    def _blinking_ratio(self, landmarks, points):
        #눈을 감았는지 판단
        left = (landmarks.part(points[0]).x, landmarks.part(points[0]).y)
        right = (landmarks.part(points[3]).x, landmarks.part(points[3]).y)
        top = self._middle_point(landmarks.part(points[1]), landmarks.part(points[2]))
        bottom = self._middle_point(landmarks.part(points[5]), landmarks.part(points[4]))

        eye_w = math.hypot((left[0] - right[0]), (left[1] - right[1]))
        eye_h = math.hypot((top[0] - bottom[0]), (top[1] - bottom[1]))

        try:
            ratio = eye_w / eye_h
        except ZeroDivisionError:
            ratio = None

        return ratio

    def _analyze(self, original_frame, landmarks, side, calibration):
        #Calibration에 데이터 전달, Pupil 객체 시작
        if side == 0:
            points = self.left_center_POINTS
        else:
            return

        self.blinking = self._blinking_ratio(landmarks, points)
        self._isolate(original_frame, landmarks, points)

        if not calibration.is_complete():
            calibration.evaluate(self.frame, side)

        threshold = calibration.threshold(side)
        self.pupil = Pupil(self.frame, threshold)

class Pupil(object):
    #홍채를 찾고, 동공 추정
    def __init__(self, eye_frame, threshold):
        self.iris_frame = None
        self.threshold = threshold
        self.x = None
        self.y = None

        self.detect_iris(eye_frame)

    @staticmethod
    def image_processing(eye_frame, threshold):
        #눈에서 홍채 분리
        kernel = np.ones((3, 3), np.uint8)
        new_frame = cv2.bilateralFilter(eye_frame, 10, 15, 15)
        new_frame = cv2.erode(new_frame, kernel, iterations=3)
        new_frame = cv2.threshold(new_frame, threshold, 255, cv2.THRESH_BINARY)[1]

        return new_frame

    def detect_iris(self, eye_frame):
        #홍채 탐지, 중앙을 계산해서 동공 찾기
        self.iris_frame = self.image_processing(eye_frame, self.threshold)

        contours, _ = cv2.findContours(self.iris_frame, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)[-2:]
        contours = sorted(contours, key=cv2.contourArea)

        try:
            moments = cv2.moments(contours[-2])
            self.x = int(moments['m10'] / moments['m00'])
            self.y = int(moments['m01'] / moments['m00'])
        except (IndexError, ZeroDivisionError):
            pass


        

iris = IrisTracking()
webcam = cv2.VideoCapture(0)
left_list = list()      #왼쪽 눈 중앙에서 이동한 위치까지의 거리 저장
flag = 0
cnt = 0
temp = 0
x = 1.2                   #오차율, 테스트 필요

now = time
sec = now.localtime().tm_sec
ex_sec = -1

IsAttend = False
left_center = iris.pupil_left_center_coords()       #왼쪽 눈 중앙
left_pupil = iris.pupil_left_coords()               #왼쪽 동공 위치
key = cv2.waitKey(1) & 0xFF
_, frame = webcam.read()
# conn = pymysql.connect(host="database-1.cvdnmgvfx65g.ap-northeast-2.rds.amazonaws.com", 
#                       user="admin", password="a1234567", db="management", charset="utf8")
# curs = conn.cursor()

# #db 단위시간 연결 test용 변수
# total_meeting_time = 0

Attend_Time = 0
Whole_Time = 0
Attend_Rate = 0.0
def main():
    global iris, webcam, left_list, flag, cnt, temp, x, now, sec, ex_sec 
    global IsAttend, left_center, left_pupil
    global key
    global _, frame 
    global Attend_Time, Whole_Time, Attend_Rate 
    while True :
        if key & 0xFF == ord('q'):
            return 
        
        _, frame = webcam.read()
        frame = cv2.flip(frame, 1)
        iris.refresh(frame)

        frame = iris.annotated_frame()
        left_center = iris.pupil_left_center_coords()       #왼쪽 눈 중앙
        left_pupil = iris.pupil_left_coords()               #왼쪽 동공 위치

        key = cv2.waitKey(1) & 0xFF
        

        cv2.imshow("eye", frame)
        
        #동공 좌표 5군데 입력
        #'i'입력시 좌표 저장
        if cnt < 5:
            if(cnt == 0):
                if(temp == cnt):
                    print("\n중앙 좌표 입력, Press 'i'")
                temp = 1
                if key & 0xFF == ord('i') or key & 0xFF == ord('I'):
                    if(left_center is None):
                        print("\n다시 입력하세요")
                    else:
                        left_list.append([left_center[0] - left_pupil[0], left_center[1] - left_pupil[1]])
                        print(left_center[0], left_pupil[0], left_center[1], left_pupil[1], left_center[0] - left_pupil[0], left_center[1] - left_pupil[1])
                        cnt += 1
            elif(cnt == 1):
                if(temp == cnt):
                    print("\n좌상단 좌표 입력, Press 'i'")
                temp = 2
                if key & 0xFF == ord('i') or key & 0xFF == ord('I'):
                    if(left_center is None):
                        print("\n다시 입력하세요")
                    else:
                        left_list.append([left_center[0] - left_pupil[0], left_center[1] - left_pupil[1]])
                        print(left_center[0], left_pupil[0], left_center[1], left_pupil[1], left_center[0] - left_pupil[0], left_center[1] - left_pupil[1])
                        cnt += 1
            elif(cnt == 2):
                if(temp == cnt):
                    print("\n우상단 좌표 입력, Press 'i'")
                temp = 3
                if key & 0xFF == ord('i') or key & 0xFF == ord('I'):
                    if(left_center is None):
                        print("\n다시 입력하세요")
                    else:
                        left_list.append([left_center[0] - left_pupil[0], left_center[1] - left_pupil[1]])
                        print(left_center[0], left_pupil[0], left_center[1], left_pupil[1], left_center[0] - left_pupil[0], left_center[1] - left_pupil[1])
                        cnt += 1
            elif(cnt == 3):
                if(temp == cnt):
                    print("\n좌하단 좌표 입력, Press 'i'")
                temp = 4
                if key & 0xFF == ord('i') or key & 0xFF == ord('I'):
                    if(left_center is None):
                        print("\n다시 입력하세요")
                    else:
                        left_list.append([left_center[0] - left_pupil[0], left_center[1] - left_pupil[1]])
                        print(left_center[0], left_pupil[0], left_center[1], left_pupil[1], left_center[0] - left_pupil[0], left_center[1] - left_pupil[1])
                        cnt += 1
            else:
                if(temp == cnt):
                    print("\n우하단 좌표 입력, Press 'i'")
                temp = 5
                if key & 0xFF == ord('i') or key & 0xFF == ord('I'):
                    if(left_center is None):
                        print("\n다시 입력하세요")
                    else:
                        left_list.append([left_center[0] - left_pupil[0], left_center[1] - left_pupil[1]])
                        print(left_center[0], left_pupil[0], left_center[1], left_pupil[1], left_center[0] - left_pupil[0], left_center[1] - left_pupil[1])
                        cnt += 1
                        flag = 1
        
        else :      
            # #출석 인정 범위에 동공이 들어올 때와 아닐 때 계산해서 출력
            if flag == 1:
                sec = now.localtime().tm_sec
                #초당 1회 출력
                if sec != ex_sec:
                    ex_sec = sec
                    if(left_center is None):
                        if(IsAttend == True):
                            print("출석인정")
                            Attend_Time += 1
                            Whole_Time += 1
                        else:
                            print("출석비인정")
                            Whole_Time += 1
                    else:
                        #동공 왼쪽으로 빠짐
                        if (left_pupil[0] < left_center[0] - left_list[1][0] * x and left_pupil[0] < left_center[0] - left_list[3][0] * x):
                            print("출석비인정1")
                            print(left_center[0] - left_list[1][0] * x)
                            Whole_Time += 1
                            IsAttend = False

                        #동공 오른쪽으로 빠짐
                        elif (left_pupil[0] > left_center[0] - left_list[2][0] * x and left_pupil[0] > left_center[0] - left_list[4][0] * x):
                            print("출석비인정2")
                            print(left_center[0] - left_list[2][0] * x)
                            Whole_Time += 1
                            IsAttend = False

                        #동공 위쪽으로 빠짐 
                        elif (left_pupil[1] < left_center[1] - left_list[1][1] * x and left_pupil[1] < left_center[1] - left_list[2][1] * x):
                            print("출석비인정3")
                            print(left_center[1] - left_list[1][1] * x)
                            Whole_Time += 1
                            IsAttend = False

                        #동공 아래쪽으로 빠짐
                        elif (left_pupil[1] > left_center[1] - left_list[3][1] * x and left_pupil[1] > left_center[1] - left_list[4][1] * x):
                            print("출석비인정4")
                            print(left_center[1] - left_list[3][1] * x)
                            Whole_Time += 1
                            IsAttend = False

                        else:
                            print("출석인정")
                            Attend_Time += 1
                            Whole_Time += 1
                            IsAttend = True
                    # total_meeting_time = total_meeting_time+1
                    # sql_data = (IsAttend,total_meeting_time,"test1")   
                    # sql = "update customer set IsAttend = %s, Total_Meeting_Time = %s where UserName = %s"
                    # curs.execute(sql,sql_data)
                    # conn.commit()
            if Whole_Time != 0 :
                Attend_Rate = round((Attend_Time / Whole_Time) * 100, 1)
                
            if key == 27:
                webcam.release()
                return
          
#threading(main).start()
cv2.destroyAllWindows()

