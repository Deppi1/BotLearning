import cv2
import numpy as np
import pygetwindow as gw
import pyautogui
import threading
import random
from screenshot import Screen
from PIL import Image
from pywinauto.keyboard import send_keys
from time import sleep, perf_counter


hookHeight = 90 # min = 15, max = 120
castingMin = 16 # Время заброса в ms
castingMax = 18 # Время заброса в ms

fishCount = 0
trashCount = 0
hookCount = 0
levelupCount = 0

restart = 0

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
        global restart
        
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
            restart = 0
            x = int(x_moment / area)
            y = int(y_moment / area)
            cv2.circle(img, (x, y), 3, (255,0,0), -1)
            cv2.putText(img, 'y = ' + str(y), (5,30), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0,255,0))
            
            # Автонажатие лкм для проводки крючка
            if(fishFind == True
               and sethook == True 
               and gw.getWindowsWithTitle('FishingPlanet')[0].isActive):
                
                if(y > hookHeight):
                    send_keys("{VK_SPACE down}")
                else:
                    send_keys("{VK_SPACE up}")
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
        global restart
        
        findZero = main.FindZeroLength(img=screenshot.ZeroZone())
        
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
            restart = 0
            x = int(x_moment / area)
            y = int(y_moment / area)
            cv2.circle(img, (x, y), 3, (255,0,0), -1)
            cv2.putText(img, 'x = ' + str(x), (5,30), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0,255,255))
            
            # Условия для скручивания лески до 0
            if (x < 30 
                and findZero == False
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
                send_keys("{VK_SPACE down}")
                print('Подматываем!')
                sleep(3)
                send_keys("{VK_SPACE up}")
                while i < 3:
                    i += 1
                    pyautogui.scroll(-1)
                    sleep(0.2)
                i = 0
                sethook = False
            elif(x < 30
                 and fishFind == True
                 and findZero == False
                 and sethook == True):
                
                send_keys("{VK_SPACE down}")
                print('Подматываем!')
                sleep(1)
                send_keys("{VK_SPACE up}")
                
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
        global restart
        
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
            restart = 0
            biteFind = True
            send_keys("{VK_SPACE down}")
            send_keys("{VK_MENU down}")
            sleep(random.randint(3, 12) / 10)
            send_keys("{VK_MENU up}")
            sleep(5)
            send_keys("{VK_SPACE up}")
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
        global restart
        
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
            
            restart = 0
            sleep(1)
            send_keys("{VK_SPACE down}")
            sleep(1)
            send_keys("{VK_SPACE up}")
            sleep(1)
            fishCount += 1
            print('+1 рыба!')
            
            sleep(1)
            print('Проверка достижений')
            main.FindChallenge(img=screenshot.ChallengeZone())
            sleep(1)
            print('Проверка повышения уровня')
            main.FindLevelUp(img=screenshot.LevelupZone())
            sleep(1)
            print('Проверка заполненности садка')
            main.FindCageFull(img=screenshot.CageZone())
            sleep(1)
            
            sethook = False
        # --------------------------------
        
        # Если серых точек > 1000
        elif (areaGray > 1000
            and sethook == True
            and gw.getWindowsWithTitle('FishingPlanet')[0].isActive):
            
            restart = 0
            sleep(1)
            send_keys("{BACKSPACE down}")
            sleep(1)
            send_keys("{BACKSPACE up}")
            sleep(1)
            trashCount += 1
            print('+1 мусор')
            
            sleep(5)
            print('Проверка достижений')
            main.FindChallenge(img=screenshot.ChallengeZone())
            sleep(1)
            print('Проверка повышения уровня')
            main.FindLevelUp(img=screenshot.LevelupZone())
            sleep(1)
            print('Проверка заполненности садка')
            main.FindCageFull(img=screenshot.CageZone())
            sleep(1)
            
            sethook = False
        # --------------------------------
            
        cv2.imshow('Find img', img)
        cv2.imshow('Find gray mask', maskGray)
        cv2.imshow('Find orange mask', maskOrange)
    # --------------------------------
    
    
    
    # Поиск полной заполненности садка
    def FindCageFull(img):
        img = cv2.medianBlur(img, 3)
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        lower = np.array([20, 180, 180])
        upper = np.array([35, 255, 255])
        mask = cv2.inRange(hsv, lower, upper)

        moments = cv2.moments(mask, 1)
        area = moments['m00']
        
        if(area > 10):
            print('Завершаем день и продаём улов!')
            sleep(5)
            send_keys("{t down}")
            sleep(1)
            send_keys("{t up}")
            sleep(1)
            pyautogui.moveRel(0, 325, duration=1)
            pyautogui.click()
            pyautogui.moveRel(-50, -225, duration=1)
            pyautogui.click()
            pyautogui.moveRel(0, 210, duration=1)
            pyautogui.click()
            print('Ждём 15 секунд перед началом нового дня!')
            sleep(15)
            sethook = False
    
        cv2.imshow('Cage img', img)
        cv2.imshow('Cage mask', mask)
    # --------------------------------

    
    
    # Поиск окна повышения уровня
    def FindLevelUp(img):
        global sethook
        global levelupCount
        
        img = cv2.medianBlur(img, 3)
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        lower = np.array([40, 200, 200])
        upper = np.array([50, 220, 220])
        mask = cv2.inRange(hsv, lower, upper)

        moments = cv2.moments(mask, 1)
        area = moments['m00']
        
        if (area > 2000
            and gw.getWindowsWithTitle('FishingPlanet')[0].isActive):
            
            sleep(2)
            pyautogui.moveRel(-300, 400, duration=1)
            pyautogui.click()
            sleep(1)
            send_keys("{VK_ESCAPE down}")
            sleep(0.5)
            send_keys("{VK_ESCAPE up}")
            sleep(1)
            levelupCount += 1
            print('+1 уровень!')
            sleep(2)
            sethook = False
        
        cv2.imshow('LevelUp img', img)
        cv2.imshow('LevelUp mask', mask)
    # --------------------------------
        
        
    
    # Поиск окна с получением награды за челлендж
    def FindChallenge(img):
        img = cv2.medianBlur(img, 3)
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        lower = np.array([40, 200, 200])
        upper = np.array([50, 220, 220])
        mask = cv2.inRange(hsv, lower, upper)

        moments = cv2.moments(mask, 1)
        area = moments['m00']
        
        if(area > 2000
           and gw.getWindowsWithTitle('FishingPlanet')[0].isActive):
            sleep(1)
            send_keys("{VK_SPACE down}")
            sleep(0.5)
            send_keys("{VK_SPACE up}")
            sleep(1)
            print('Получено достижение!')
            sethook = False
        
        cv2.imshow('Challenge img', img)
        cv2.imshow('Challenge mask', mask)
    # --------------------------------
        
        
        
    # Заброс крючка
    def HookSet():
        global sethook
        global fishCount
        global trashCount
        global hookCount
        global levelupCount
        global restart
        
        if (sethook == False
            and gw.getWindowsWithTitle('FishingPlanet')[0].isActive):
            restart = 0
            hookCount += 1
            print('\nРыб поймано: ' + str(fishCount))
            print('Мусора поймано: ' + str(trashCount))
            print('Уровней получено: ' + str(levelupCount))
            print('Ждём: 8 сек')
            sleep(8)
            print('Забрасываем!')
            print('Сделано забросов: ' + str(hookCount))
            send_keys("{VK_SPACE down}")
            sleep(random.randint(castingMin, castingMax) / 10)
            send_keys("{VK_SPACE up}")
            sethook = True
    # --------------------------------
    
    
    
if __name__ == "__main__":
    while True:
        #start_time = perf_counter()
        
        if (gw.getWindowsWithTitle('FishingPlanet')[0].isActive):
            restart += 1
            print(restart)
            if(restart > 1000):
                print('\n--- ПЕРЕЗАПУСК ---')
                send_keys("{VK_ESCAPE down}")
                send_keys("{VK_ESCAPE up}")
                sethook = False
        
        screenshot = Screen()
        screenshot.Screenshot()
        
        main.FindFish(img=screenshot.FishZone())
        main.FindLength(img=screenshot.LengthZone())
        main.FindStrength(img=screenshot.StrengthZone())
        main.FindTake(img=screenshot.TakeZone())
        main.HookSet()
        
        
            
        #end_time = perf_counter()MENUdown
        #print(f'Выполнение заняло {end_time- start_time: 0.2f} секунд.')
        
        cv2.waitKey(1)
        
        