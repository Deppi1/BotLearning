import pygetwindow as gw
import pyautogui
from PIL import Image
import numpy as np
import cv2

class Screen():
    def __init__(self):
        self.screenshot = None
    
    # Поиск окна и создание скриншота
    def Screenshot(self):
        
        window = gw.getWindowsWithTitle('FishingPlanet')
    
        if len(window) > 0:
            left, top, width, height = window[0].left, window[0].top, window[0].width, window[0].height
            self.screenshot = pyautogui.screenshot(region=(left, top, width, height))
        else:
            print(f"Window not find")
    # ---------------------------------------------
            
    # Обрезание скриншота для зоны поплавка
    def FishZone(self):
        imgCrop = self.screenshot.crop((1711, 247, 1832, 381))
        return cv2.cvtColor(np.array(imgCrop), cv2.COLOR_RGB2BGR)
    # ---------------------------------------------
    
    # Обрезание скриншота для зоны с длиной лески
    def LengthZone(self):
        imgCrop = self.screenshot.crop((1542, 963, 1640, 1035))
        return cv2.cvtColor(np.array(imgCrop), cv2.COLOR_RGB2BGR)
    # ---------------------------------------------

    # Обрезание скриншота для первой цифры длины лески
    def ZeroZone(self):
        imgCrop = self.screenshot.crop((1542, 963, 1590, 1035))
        return cv2.cvtColor(np.array(imgCrop), cv2.COLOR_RGB2BGR)
    # ---------------------------------------------
    
    # Обрезание скриншота для зоны натяжения лески
    def StrengthZone(self):
        imgCrop = self.screenshot.crop((1774, 496, 1810, 913))
        return cv2.cvtColor(np.array(imgCrop), cv2.COLOR_RGB2BGR) 
    # --------------------------------------------
    
    # Обрезание скриншота для зоны кнопки 'ЗАБРАТЬ'
    def TakeZone(self):
        imgCrop = self.screenshot.crop((984, 965, 1050, 1010))
        return cv2.cvtColor(np.array(imgCrop), cv2.COLOR_RGB2BGR) 
    # --------------------------------------------
    