import datetime
import os
import time
import pynput
import pytesseract as pytesseract
import win32gui
from PIL import ImageGrab
from pynput.mouse import Controller
import pyautogui

starting_item = 'Cauliflower'
folder_timestamp = datetime.datetime.now().strftime("%Y-%m-%d")
output_folder_name = 'market_screenshots_%s' % folder_timestamp
debug_folder_name = 'debug_screenshots_%s' % folder_timestamp
debug_clicks_folder_name = 'debug_clicks_%s' % folder_timestamp
# item_list_file = 'item_list.txt'
item_list_file = 'resources.txt'
mouse = Controller()
keyboard = pynput.keyboard.Controller()
debug_screenshot_counter = 0
DEBUG = False
DEBUG_LIST = False
DEBUG_CLICKS = False
DEBUG_LIST_FIRST_ITEM = "Dried Dryad Sap"
DEBUG_LIMIT_PAGES = False
if DEBUG:
    afk_time = 1
else:
    afk_time = 18


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


def get_screen_shot():
    hwnd = focus_on_new_world()

    win32gui.SetForegroundWindow(hwnd)
    bbox = win32gui.GetWindowRect(hwnd)
    # print ('Caputered screenshot in memory')
    return ImageGrab.grab(bbox)


def debug_save_image(description):
    global  debug_screenshot_counter
    if DEBUG_CLICKS:
        img = get_screen_shot()
        description = description.replace(" ", "_")
        filename = "%s-%s.png" % (description, debug_screenshot_counter)
        dirname = 'output' + '/' + debug_clicks_folder_name + '/'
        dir_exists = os.path.exists(dirname)
        if not dir_exists:
            os.mkdir(dirname)
        img.save(dirname + filename)
        debug_screenshot_counter += 1


def get_pages():
    image = get_screen_shot()
    left = 1686
    top = 237
    right = 1790
    bottom = 258

    cropped_image = image.crop((left, top, right, bottom))
    cropped_image_3 = cropped_image.crop((71, 0, 103, 20))
    cropped_image_2 = cropped_image.crop((79, 0, 103, 20))
    # cropped_image_1 = cropped_image.crop((87, 0, 101, 22))

    text = ''
    pages = -1
    found_valid_number = False
    try:
        text = pytesseract.image_to_string(cropped_image_3)
        pages = int(text)
        found_valid_number = True
        # cropped_image.show()
        print(text)
        print(pages)
    except:
        print('not a valide 3 digit page number')
    else:
        pages = pages
        found_valid_number = True

    if not found_valid_number:
        try:
            custom_config = r'--oem 3 --psm 6 outputbase digits'
            text = pytesseract.image_to_string(cropped_image_2, config=custom_config)
            pages = int(text)
            # cropped_image.show()
            print(text)
            print(pages)
        except:
            print('not a valid 2 digit page number')
        else:
            pages = pages
            found_valid_number = True

    # if not found_valid_number:
    #     try:
    #         custom_config = r'--oem 3 --psm 6 outputbase digits'
    #         pages = int(text)
    #         found_valid_number = True
    #         cropped_image.show()
    #         print(text)
    #         print(pages)
    #     except:
    #         print('not a valide 1 digit page number')
    #     else:
    #         pages = pages
    #         found_valid_number = True

    # having trouble with single digits, so let's cheat and assume all single digits are 9
    if not found_valid_number:
        pages = 9

    page_count = pages
    print("found page count: %i" % page_count)
    if DEBUG_LIMIT_PAGES:
        return range(2)
    return range(page_count)


def prepare():
    pyautogui.press("c")
    time.sleep(1)
    pyautogui.press("e")
    print("prepared")
    debug_save_image("prepared")


def capture_screen_by_screen(page, commodity_type):
    focus_on_new_world()
    img = get_screen_shot()
    img.save("%s/%s%i.png" % (new_dir, commodity_type, page))
    scroll_tp_window_down()
    img = get_screen_shot()
    img.save("%s/%s%i.png" % (new_dir, commodity_type, page))
    next_tp_page()


def click_coords(x, y, message=""):
    focus_on_new_world()
    pyautogui.click(x, y)
    time.sleep(0.2)
    pyautogui.click(x, y)
    time.sleep(0.2)
    print(message)
    message = message.replace(' ', '_')
    debug_save_image(message)
    time.sleep(2)


def find_buy_icon():
    # pick 3 pixels in the buy icon
    # take screen shot
    pixel1 = (205, 170)
    pixel2 = (204, 175)
    pixel3 = (207, 175)
    rgb_target = (255, 255, 255)
    img = get_screen_shot()
    test_pixel1 = img.getpixel(pixel1)
    test_pixel2 = img.getpixel(pixel2)
    test_pixel3 = img.getpixel(pixel3)
    test_pixel1_r = test_pixel1[0]
    test_pixel1_g = test_pixel1[1]
    test_pixel1_b = test_pixel1[2]
    test_pixel2_r = test_pixel2[0]
    test_pixel2_g = test_pixel2[1]
    test_pixel2_b = test_pixel2[2]
    test_pixel3_r = test_pixel3[0]
    test_pixel3_g = test_pixel3[1]
    test_pixel3_b = test_pixel3[2]

    test_pixel1_good = False
    test_pixel2_good = False
    test_pixel3_good = False

    if abs(test_pixel1_r - 255) < 5 and abs(test_pixel1_g - 255) < 5 and abs(test_pixel1_b - 255) < 5:
        test_pixel1_good = True

    if abs(test_pixel2_r - 255) < 5 and abs(test_pixel2_g - 255) < 5 and abs(test_pixel2_b - 255) < 5:
        test_pixel2_good = True

    if abs(test_pixel3_r - 255) < 5 and abs(test_pixel3_g - 255) < 5 and abs(test_pixel3_b - 255) < 5:
        test_pixel3_good = True

    if test_pixel1_good and test_pixel2_good and test_pixel3_good:
        return True
    else:
        return False


def reset_afk_timer():
    # Oooh, looks like jumping 2 times may reset afk timer! Less varience in where we end up!
    print("Started to reset AFK timer")
    pyautogui.press("escape")
    time.sleep(1)
    pyautogui.keyDown('s')
    time.sleep(0.2)
    pyautogui.keyUp('s')
    time.sleep(2)
    pyautogui.keyDown('w')
    time.sleep(1)
    pyautogui.keyUp('w')
    time.sleep(2)
    pyautogui.press('e')
    time.sleep(0.5)
    found_buy_icon = find_buy_icon()
    # Seems like sometimes we need  to hit the e button again :(
    while not found_buy_icon:
        pyautogui.keyDown('w')
        time.sleep(0.5)
        pyautogui.keyUp('w')
        time.sleep(0.25)
        pyautogui.press('e')
        found_buy_icon = find_buy_icon()
    time.sleep(1.25)
    print("Done resetting AFK timer")
    debug_save_image("reset afk timer")


def scroll_tp_window_down():
    pyautogui.click(3758, 1031)
    time.sleep(2)
    pyautogui.click(3758, 1031)
    print("Scrolled TP windows down")
    debug_save_image("scrolled_tp_window_down")


def next_tp_page():
    pyautogui.click(3717, 252)
    time.sleep(0.5)
    print("next_tp_page")
    debug_save_image("next_tp_page")


def get_static_list_of_items():
    with open(item_list_file) as file:
        lines = file.readlines()
        lines = [line.rstrip() for line in lines]
        return lines


def click_on_consumables_category():
    click_coords(2042, 673, 'click_on_consumables_category' )


def click_on_ammo_category():
    click_coords(2042, 744, 'click_on_ammo_category')


def click_on_furniture_category():
    click_coords(2042, 811, 'click_on_furniture_category')


def click_on_resources():
    click_coords(2042, 605, 'click_on_resources')


def click_on_raw_resource():
    click_coords(2165, 386, 'click_on_raw_resource')


def click_on_refined_resource():
    click_coords(2165, 438, 'click_on_refined_resource')


def click_on_cooking_ingredients():
    click_coords(2165, 488, 'click_on_cooking_ingredients')


def click_on_craft_mods():
    click_coords(2165, 539, 'click_on_craft_mods')


def click_on_components():
    click_coords(2165, 600, 'click_on_components')


def click_on_potion_reagents():
    click_coords(2165, 643, 'click_on_potion_reagents')


def click_on_dyes():
    click_coords(2165, 698, 'click_on_dyes')


def click_on_azoth():
    click_coords(2165, 749, 'click_on_azoth')


def click_on_arcana():
    click_coords(2165, 802, 'click_on_arcana')


# def click_on_item_in_search_box(_item_name):
#     focus_on_new_world()
#     pyautogui.click(2106, 373)
#     time.sleep(0.2)
#     pyautogui.click(2106, 373)
#     print("Clicked on %s in search bar (maybe)" % _item_name)
#     time.sleep(1)
#     debug_save_image("clicked on item in search box")
#
#
# def click_on_search_box():
#     focus_on_new_world()
#     pyautogui.click(2077, 246)
#     time.sleep(0.2)
#     pyautogui.click(2077, 246)
#     print("clicked on Search bar")
#     debug_save_image("clicked on search box")
#
#
# def type_in_search_box(_item_name):
#     for letter in _item_name:
#         keyboard.press(letter)
#         time.sleep(0.05)
#     keyboard.press(Key.enter)
#     debug_save_image("Presed enter in search box")


if __name__ == '__main__':
    # get_pages()
    # exit()
    # Setting up the output scaffolding
    base_dir = 'output/'
    timestamp = time.time()
    new_dir = '%s/%s' % (base_dir, output_folder_name)
    debug_dir = '%s/%s' % (base_dir, debug_folder_name)
    dir_exists = os.path.exists(new_dir)
    debug_dir_exists = os.path.exists(debug_dir)

    # Creating directories
    if not dir_exists:
        os.mkdir(new_dir)

    if not debug_dir_exists:
        os.mkdir(debug_dir)

    # on your marks...
    focus_on_new_world()
    prepare()


    # Get consumable prices
    click_on_consumables_category()
    for page in get_pages():
        capture_screen_by_screen(page, 'consumables')

    # anti-AFK
    reset_afk_timer()
    time.sleep(2)

    # Get ammo pages, get 30, that should be enough
    click_on_ammo_category()
    for page in get_pages():
        capture_screen_by_screen(page, 'ammo')

    # anti-AFK
    reset_afk_timer()
    time.sleep(2)

    # Get furniture, get 100 pages
    click_on_furniture_category()
    for page in get_pages():
        capture_screen_by_screen(page, 'furniture')

    # anti-AFK
    reset_afk_timer()
    time.sleep(2)

    # Get resource prices per subcategory
    click_on_resources()

    click_on_raw_resource()
    for page in get_pages():
        capture_screen_by_screen(page, 'raw_resources')

    # anti-AFK
    reset_afk_timer()
    time.sleep(2)

    # Get resource prices per subcategory
    click_on_resources()

    click_on_refined_resource()
    for page in get_pages():
        capture_screen_by_screen(page, 'refined_resources')

    # anti-AFK
    reset_afk_timer()
    time.sleep(2)

    # Get resource prices per subcategory
    click_on_resources()

    click_on_cooking_ingredients()
    for page in get_pages():
        capture_screen_by_screen(page, 'cooking_ingredients')

    # anti-AFK
    reset_afk_timer()
    time.sleep(2)

    # Get resource prices per subcategory
    click_on_resources()

    click_on_craft_mods()
    for page in get_pages():
        capture_screen_by_screen(page, 'craft_mods')

    # anti-AFK
    reset_afk_timer()
    time.sleep(2)

    # Get resource prices per subcategory
    click_on_resources()

    click_on_components()
    for page in get_pages():
        capture_screen_by_screen(page, 'components')

    # anti-AFK
    reset_afk_timer()
    time.sleep(2)

    # Get resource prices per subcategory
    click_on_resources()

    click_on_potion_reagents()
    for page in get_pages():
        capture_screen_by_screen(page, 'potion_reagents')

    # anti-AFK
    reset_afk_timer()
    time.sleep(2)

    # Get resource prices per subcategory
    click_on_resources()

    click_on_dyes()
    for page in get_pages():
        capture_screen_by_screen(page, 'dyes')

    # anti-AFK
    reset_afk_timer()
    time.sleep(2)

    # Get resource prices per subcategory
    click_on_resources()

    click_on_azoth()
    for page in get_pages():
        capture_screen_by_screen(page, 'azoth')

    # anti-AFK
    reset_afk_timer()
    time.sleep(2)

    # Get resource prices per subcategory
    click_on_resources()

    click_on_arcana()
    for page in get_pages():
        capture_screen_by_screen(page, 'arcana')





    # # The following loop will get straggling items that must be put in a list
    # now = datetime.datetime.now()
    # next_afk_time = now + datetime.timedelta(minutes=afk_time)
    # if DEBUG_LIST:
    #     first_index = static_item_list.index(DEBUG_LIST_FIRST_ITEM)
    #     static_item_list = static_item_list[first_index:]
    # static_item_list.index(DEBUG_LIST_FIRST_ITEM)
    # for item_name in static_item_list:
    #     if DEBUG:
    #         if counter >= 40:
    #             exit(0)
    #     counter += 1
    #
    #     now = datetime.datetime.now()
    #     if now > next_afk_time:
    #         reset_afk_timer()
    #         time.sleep(2)
    #         # reset_afk_timer()
    #         # time.sleep(2)
    #         now = datetime.datetime.now()
    #         next_afk_time = now + datetime.timedelta(minutes=afk_time)
    #
    #     click_on_search_box()
    #
    #     type_in_search_box(item_name)
    #
    #     img = get_screen_shot()
    #     print("Saving debug screenshot %s..." % item_name)
    #     img.save("%s/%s.png" % (debug_dir, item_name))
    #     print("Done saving debug screenshot for %s" % item_name)
    #
    #     click_on_item_in_search_box(item_name)
    #
    #     get_screen_shot()
    #
    #     img = get_screen_shot()
    #     print("Saving screenshot %s ..." % item_name)
    #     img.save("%s/%s.png" % (new_dir, item_name))
    #     print("Done saving screenshot %s" % (item_name))
