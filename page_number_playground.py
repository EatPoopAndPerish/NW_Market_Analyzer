import datetime
import os
import time

import cv2
import numpy
import numpy as np
import pynput
import pytesseract as pytesseract
import win32gui
from PIL import ImageGrab
from PIL import Image
from pynput.mouse import Controller
import pyautogui


def focus_on_new_world():

    toplist, winlist = [], []

    def enum_cb(hwnd, results):
        winlist.append((hwnd, win32gui.GetWindowText(hwnd)))

    win32gui.EnumWindows(enum_cb, toplist)

    new_world = [(hwnd, title) for hwnd, title in winlist if 'New World' == title]
    # just grab the hwnd for first window matching new_world
    new_world = new_world[0]
    hwnd = new_world[0]
    win32gui.SetForegroundWindow(hwnd)
    # print ("focused on New World")
    return hwnd


def get_page_numbers():

    cropped_image_1 = Image.open('resources/image_clips/test_1.png')
    cropped_image_2 = Image.open('resources/image_clips/test_2.png')
    cropped_image_3 = Image.open('resources/image_clips/test_3.png')

    # cropped_image_1.show()
    # cropped_image_2.show()
    # cropped_image_3.show()

    yellows = [[255, 255, x] for x in range(190, 255)]
    max_yellow_x_coord = 0

    for image in [cropped_image_1, cropped_image_2, cropped_image_3]:
        max_yellow_x_coord = 0
        width, height = image.size
        for yellow in yellows:
            im = np.array(image)
            y, x = np.where(np.all(im == yellow, axis=2))
            y.sort()
            x.sort()
            try:
                max_yellow_x_coord = max(max_yellow_x_coord, max(x))
            except:
                pass
        pil_image = image.crop((max_yellow_x_coord + 21, 0, width, height))

        ### WORKS WELL ###
        opencvImage = cv2.cvtColor(numpy.array(pil_image), cv2.COLOR_RGB2BGR)
        gray_image = cv2.cvtColor(opencvImage, cv2.COLOR_BGR2GRAY)
        bwimage = cv2.adaptiveThreshold(gray_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 25, 0) # works pretty well


        ### Also works well ###
        opencvImage = cv2.cvtColor(numpy.array(pil_image), cv2.COLOR_RGB2BGR)
        alpha = 3
        beta = 0
        adjusted = cv2.convertScaleAbs(opencvImage, alpha=alpha, beta=beta)
        new_pil_image = Image.fromarray(adjusted)


        opencvImage = cv2.cvtColor(numpy.array(pil_image), cv2.COLOR_RGB2BGR)
        alpha = 3
        beta = 0
        adjusted = cv2.convertScaleAbs(opencvImage, alpha=alpha, beta=beta)

        gray_image = cv2.cvtColor(adjusted, cv2.COLOR_BGR2GRAY)
        bwimage = cv2.adaptiveThreshold(gray_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 25, 0) # works pretty well



        new_pil_image = Image.fromarray(gray_image)
        new_pil_bw_image = Image.fromarray(bwimage)

        new_pil_image.show()
        new_pil_bw_image.show()
    return


    #
    #
    #
    # text = ''
    # pages = -1
    # found_valid_number = False
    # try:
    #     custom_config = r'--oem 3 --psm 6 outputbase digits'
    #     text = pytesseract.image_to_string(cropped_image_3, config=custom_config)
    #     pages = int(text)
    #     found_valid_number = True
    #     # cropped_image.show()
    #     # print(text)
    #     # print(pages)
    # except:
    #     print('not a valide 3 digit page number')
    # else:
    #     pages = pages
    #     found_valid_number = True
    #
    # if not found_valid_number:
    #     try:
    #         custom_config = r'--oem 3 --psm 6 outputbase digits'
    #         text = pytesseract.image_to_string(cropped_image_2, config=custom_config)
    #         pages = int(text)
    #         # cropped_image.show()
    #         # print(text)
    #         # print(pages)
    #     except:
    #         print('not a valid 2 digit page number')
    #     else:
    #         pages = pages
    #         found_valid_number = True
    #
    #
    # if not found_valid_number:
    #     pages = 9
    #
    # page_count = pages
    # print("found page count: %i" % page_count)
    #
    # if DEBUG_LIMIT_PAGES:
    #     return range(2)
    # return range(page_count)


if __name__ == '__main__':
    get_page_numbers()