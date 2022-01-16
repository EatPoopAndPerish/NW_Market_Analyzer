import datetime
import os
import time
import win32gui
from PIL import ImageGrab
from easygui import buttonbox
from pynput.mouse import Button, Controller
from timeit import default_timer as timer
import pyautogui
import easygui

scroll_down_delay = 1
next_page_delay = 2
folder_timestamp = datetime.datetime.now().strftime("%Y-%m-%d")
output_folder_name = 'market_screenshots_%s' % folder_timestamp
mouse = Controller()

def ask_to_skip_pages():
    user_input = easygui.enterbox("How many pages do you want to skip?")
    total_pages = int(user_input)
    return total_pages

def ask_for_page_count():
    user_input = easygui.enterbox("How many pages in this category (max 250 for AFK timer)?")
    total_pages = int(user_input)
    return total_pages

def ask_for_category():
    # message to be displayed
    text = "Please select a category"

    # window title
    title = "TP Commodity Category Selector"

    # button list
    button_list = []

    # button 1
    button1 = "Resources"

    # second button
    button2 = "Consumables"

    # third button
    button3 = "Furniture"

    # appending button to the button list
    button_list.append(button1)
    button_list.append(button2)
    button_list.append(button3)

    # creating a button box
    output = buttonbox(text, title, button_list)

    # printing the button pressed by the user
    return output

def get_screen_shot():
    toplist, winlist = [], []

    def enum_cb(hwnd, results):
        winlist.append((hwnd, win32gui.GetWindowText(hwnd)))

    win32gui.EnumWindows(enum_cb, toplist)

    new_world = [(hwnd, title) for hwnd, title in winlist if 'New World' == title]
    # just grab the hwnd for first window matching new_world
    new_world = new_world[0]
    hwnd = new_world[0]

    win32gui.SetForegroundWindow(hwnd)
    bbox = win32gui.GetWindowRect(hwnd)
    print ('Caputered screenshot in memory')
    return ImageGrab.grab(bbox)


def scroll_tp_window_down():
    pyautogui.click(3758, 1031)
    print("clicked scrolled down - sleeping for %f seconds" % scroll_down_delay)
    time.sleep(scroll_down_delay)


def next_tp_page(delay=next_page_delay):
    pyautogui.click(3717, 252)
    print("clicked next page button - sleeping for %f seconds" % next_page_delay)
    time.sleep(delay)


def wait_for_loading_and_get_image():
    while True:
        img = get_screen_shot()

        # Name column name color
        target_r = 155
        target_g = 145
        target_b = 127

        # A spot where we expect yellow after the page is scrolled down
        test_pixel_x = 2508 -img.width
        test_pixel_y = 320

        # The actual color of the pixel at that spot
        (actual_r, actual_g, actual_b) = img.getpixel((test_pixel_x, test_pixel_y))  # returns triple

        # Adding a tollerance of 10 RGB shades in any direction
        if abs(target_r - actual_r) < 10 and abs(target_g - actual_g) < 10 and abs(target_b - actual_b) < 10:
            return get_screen_shot()


def wait_for_scroll_down_and_get_image():
    while True:
        img = get_screen_shot()

        # Yellow
        target_r = 255
        target_g = 193
        target_b = 30

        # A spot where we expect yellow after the page is scrolled down
        test_pixel_x = 1850
        test_pixel_y = 810

        # The actual color of the pixel at that spot
        (actual_r, actual_g, actual_b) = img.getpixel((test_pixel_x, test_pixel_y))  # returns triple

        # Adding a tollerance of 10 RGB shades in any direction
        if abs(target_r - actual_r) < 10 and abs(target_g - actual_g) < 10 and abs(target_b - actual_b) < 22:
            return get_screen_shot()


def skip_pages(pages_to_skip):
    for i in range(pages_to_skip):
        next_tp_page(delay=1)

if __name__ == '__main__':
    pages = ask_for_page_count()
    commodity_type = ask_for_category()
    pages_to_skip = ask_to_skip_pages()
    print("User chose category:\n%s\nTotal number of pages:\n%i" % (commodity_type, pages))
    base_dir = 'output/'
    timestamp = time.time()
    new_dir = '%s/%s' % (base_dir, output_folder_name)
    # new_dir = '%s/market' % base_dir
    dir_exists = os.path.exists(new_dir)
    if not dir_exists:
        os.mkdir(new_dir)

    if pages_to_skip > 0:
        skip_pages(pages_to_skip)

    for i in range(pages):
        actual_screenshot_number = i + pages_to_skip

        # img = wait_for_loading_and_get_image()
        img = get_screen_shot()
        print("Saving screenshot %i %s..." % (actual_screenshot_number, 'a'))
        img.save("%s/%s%i%s.png" % (new_dir, commodity_type, actual_screenshot_number, 'a'))
        print("Done saving screenshot %i %s" % (actual_screenshot_number, 'a'))

        scroll_tp_window_down()
        # img = wait_for_scroll_down_and_get_image()
        img = get_screen_shot()

        print("Saving screenshot %i %s..." % (actual_screenshot_number, 'b'))
        img.save("%s/%s%i%s.png" % (new_dir, commodity_type, actual_screenshot_number, 'b'))
        print("Done saving screenshot %i %s" % (actual_screenshot_number, 'b'))

        next_tp_page()

# Currently some screenshots are missed due to loading/timing issue. Consider switching to computer vision vice stupid sleeps.