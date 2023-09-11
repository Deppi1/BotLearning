import cv2
import numpy as np
import pygetwindow as gw
import pyautogui
import threading
import random
from screenshot import Screen
from PIL import Image

from time import sleep, perf_counter


hookHeight = 100 # min = 15, max = 120
castingMin = 16 # Время заброса в ms
castingMax = 18 # Время заброса в ms

fishCount = 0
trashCount = 0

windowName = 'FishingPlanet'
fishFind = False
biteFind = False
sethook = False



class main():
    def __init__(self):
        pass
    
    # Поиск элемнта рыбы
    def FindFish(img):
        global fishFind
        global hookHeight
        global sethook
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        # Поиск оттенков красного цвета на рыбе
        lower1 = np.array([0, 70, 20])
        upper1 = np.array([10, 255, 255])
        lower2 = np.array([160,70,20])
        upper2 = np.array([179,255,255])

        lower_mask = cv2.inRange(hsv, lower1, upper1)
        upper_mask = cv2.inRange(hsv, lower2, upper2)
        full_mask = lower_mask + upper_mask
        # --------------------------------

        # Распознаём моменты (скопление необходимых пикселей)
        moments = cv2.moments(full_mask, 1)
        x_moment = moments['m10']
        y_moment = moments['m01']
        area = moments['m00']

        if (area > 100):
            x = int(x_moment / area)
            y = int(y_moment / area)
            cv2.circle(img, (x, y), 3, (255,0,0), -1)
            cv2.putText(img, 'y = ' + str(y), (5,30), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0,255,0))
            
            # Автонажатие лкм для проводки крючка
            if(fishFind == True
               and sethook == True 
               and gw.getWindowsWithTitle('FishingPlanet')[0].isActive):
                
                if(y > hookHeight):
                    pyautogui.mouseDown(button='left')
                else:
                    pyautogui.mouseUp(button='left')
            # --------------------------------
        else:
            cv2.putText(img, 'area < 200', (5,30), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0,0,255))

        cv2.imshow('Fish Image', img)
        # --------------------------------
    # --------------------------------
    
    
    
    # Поиск и проверка длины лески
    def FindLength(img):
        global fishFind
        global sethook
        global biteFind
        img = cv2.medianBlur(img, 5)
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
        # Поиск оттенков белого цвета на цифрах длины лески
        lower = np.array([0, 0, 150])
        upper = np.array([0, 0, 255])
        mask = cv2.inRange(hsv, lower, upper)
        # --------------------------------
        
        # Распознаём моменты (скопление необходимых пикселей)
        moments = cv2.moments(mask, 1)
        x_moment = moments['m10']
        y_moment = moments['m01']
        area = moments['m00']
        
        if (area > 400):
            x = int(x_moment / area)
            y = int(y_moment / area)
            cv2.circle(img, (x, y), 3, (255,0,0), -1)
            cv2.putText(img, 'x = ' + str(x), (5,30), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0,255,255))
            
            # Условия для скручивания лески до 0
            if (x < 30 
                and main.FindZeroLength(img=screenshot.ZeroZone()) == False
                and biteFind == False
                and sethook == True
                and gw.getWindowsWithTitle('FishingPlanet')[0].isActive):
                
                fishFind = False
                cv2.putText(img, 'PULL', (5,60), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0,255,0))
                i = 0
                while i < 3:
                    i += 1
                    pyautogui.scroll(1)
                    sleep(0.2)
                i = 0
                pyautogui.mouseDown(button='left')
                print('Подматываем!')
                sleep(3)
                pyautogui.mouseUp(button='left')
                while i < 3:
                    i += 1
                    pyautogui.scroll(-1)
                    sleep(0.2)
                i = 0
                sethook = False
            else:
                fishFind = True
                cv2.putText(img, 'NOT PULL', (5,60), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0,0,255))
        # --------------------------------
        cv2.imshow('Length Image', img)
    # --------------------------------
        
        
        
    # Поиск знака '0' при полном сматывании лески
    def FindZeroLength(img):
        img = cv2.medianBlur(img, 5)
        imgHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        zeroImg = cv2.imread('zero.png')
        zeroImg = cv2.medianBlur(zeroImg, 5)
        zeroHSV = cv2.cvtColor(zeroImg, cv2.COLOR_BGR2HSV)
        
        lower = np.array([0, 0, 150])
        upper = np.array([0, 0, 255])
        maskImg = cv2.inRange(imgHSV, lower, upper)
        maskZero = cv2.inRange(zeroHSV, lower, upper)
        
        # Поиск знака '0' по шаблону
        result = cv2.matchTemplate(maskImg, maskZero, cv2.TM_CCOEFF_NORMED)
        threshold = 0.8
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        if max_val > threshold:
            return True
        else:
            return False
        # --------------------------------
    # --------------------------------
    
    
    
    # Поиск силы натяжения лески
    def FindStrength(img):
        global biteFind
        global sethook
        
        img = cv2.medianBlur(img, 5)
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # Поиск оттенков синего цвета
        lower = np.array([78, 204, 153])
        upper = np.array([138, 229, 204])
        mask = cv2.inRange(hsv, lower, upper)
        # --------------------------------
        
        moments = cv2.moments(mask, 1)
        area = moments['m00']
        
        # Тянем леску если есть клёв
        if (area > 10
            and sethook == True
            and gw.getWindowsWithTitle('FishingPlanet')[0].isActive):
            biteFind = True
            pyautogui.mouseDown(button='left')
            pyautogui.mouseDown(button='right')
            sleep(random.randint(3, 12) / 10)
            pyautogui.mouseUp(button='right')
            sleep(5)
            pyautogui.mouseUp(button='left')
        else:
            biteFind = False
        # --------------------------------     

        cv2.imshow('Strength img', img)
        cv2.imshow('Strength mask', mask)
    # --------------------------------
    
    
    
    # Поиск кнопки 'забрать' или 'отпустить' улов
    def FindTake(img):
        global sethook
        global fishCount
        global trashCount
        img = cv2.medianBlur(img, 5)
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # Поиск оранжевых оттенков для кнопки 'забрать'
        lowerOrange = np.array([13, 167, 216])
        upperOrange = np.array([15, 200, 221])
        maskOrange = cv2.inRange(hsv, lowerOrange, upperOrange)

        momentsOrange = cv2.moments(maskOrange, 1)
        areaOrange = momentsOrange['m00']
        # --------------------------------
        
        # Поиск серых оттенков для кнопки 'отпустить'
        lowerGray = np.array([0, 0, 53])
        upperGray = np.array([0, 0, 80])
        maskGray = cv2.inRange(hsv, lowerGray, upperGray)
        
        momentsGray = cv2.moments(maskGray, 1)
        areaGray = momentsGray['m00']
        # --------------------------------
        
        # Если оранжевых точек > 1000 
        if (areaOrange > 1000
            and sethook == True
            and gw.getWindowsWithTitle('FishingPlanet')[0].isActive):  
              
            pyautogui.moveTo(1440, 1120, 2)
            pyautogui.mouseDown(button='left')
            sleep(random.randint(2, 5) / 10)
            pyautogui.mouseUp(button='left')
            fishCount += 1
            print('+1 рыба!')
            sethook = False
        # --------------------------------
        
        # Если серых точек > 1000
        elif (areaGray > 1000
            and sethook == True
            and gw.getWindowsWithTitle('FishingPlanet')[0].isActive):
            
            pyautogui.moveTo(1180, 1120, 2)
            pyautogui.mouseDown(button='left')
            sleep(random.randint(2, 5) / 10)
            pyautogui.mouseUp(button='left')
            print('+1 мусор')
            sethook = False
        # --------------------------------
            
        cv2.imshow('Find img', img)
        cv2.imshow('Find gray mask', maskGray)
        cv2.imshow('Find orange mask', maskOrange)
    # --------------------------------
     
     
     
    # Заброс крючка
    def HookSet():
        global sethook
        global fishCount
        global trashCount
        
        if (sethook == False
            and gw.getWindowsWithTitle('FishingPlanet')[0].isActive):
            print('')
            print('Рыб поймано: ' + str(fishCount))
            print('Мусора поймано: ' + str(trashCount))
            pyautogui.mouseUp(button='left')
            i = random.randint(6, 8)
            print('Ждём: ' + str(i) + ' сек')
            print('Забрасываем!')
            sleep(i)
            
            pyautogui.mouseDown(button='left')
            sleep(random.randint(castingMin, castingMax) / 10)
            pyautogui.mouseUp(button='left')
            sethook = True
            
        
     
if __name__ == "__main__":
    while True:
        #start_time = perf_counter()
        
        screenshot = Screen()
        screenshot.Screenshot()
        
        main.FindFish(img=screenshot.FishZone())
        main.FindLength(img=screenshot.LengthZone())
        main.FindStrength(img=screenshot.StrengthZone())
        main.FindTake(img=screenshot.TakeZone())
        main.HookSet()
        
        #end_time = perf_counter()
        #print(f'Выполнение заняло {end_time- start_time: 0.2f} секунд.')
        
        cv2.waitKey(1)
        
        