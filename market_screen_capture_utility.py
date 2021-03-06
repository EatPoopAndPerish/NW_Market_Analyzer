import datetime
import os
import time

import cv2
import numpy
import numpy as np
import pynput
import pytesseract as pytesseract
import win32gui
from PIL import ImageGrab, Image
from pynput.keyboard import Key
from pynput.mouse import Controller, Button
import pyautogui
from PIL import ImageEnhance

# Scaffolding Variables
folder_timestamp = datetime.datetime.now().strftime("%Y-%m-%d")
output_folder_name = 'market_screenshots_%s' % folder_timestamp
static_item_list = './resources/item_lists/important_items.txt'
mouse = Controller()
keyboard = pynput.keyboard.Controller()
sleep_time_before_clicking_subcategory = 4
sleep_time_after_clicking_resource_subcategory = 4
page_sense_iterator = 0 # dirty hack workaround...

# Skip variables
SKIP_ALL_RESOURCES = True
SKIP_RAW_RESOURCES = False
SKIP_REFINED_RESOURCES = False
SKIP_COOKING_INGREDIENTS = False
SKIP_CRAFT_MODS = False
SKIP_COMPONENTS = False
SKIP_POTION_REAGENTS = False
SKIP_DYES = False
SKIP_AZOTH = False
SKIP_ARCANA = False

SKIP_CONSUMABLES = True
SKIP_AMMO = True
SKIP_FURNITURE = True
SKIP_LIST = False

# Debug variables
debug_screenshot_counter = 0 # dirty hack workaround
debug_folder_name = 'debug_screenshots_%s' % folder_timestamp
debug_clicks_folder_name = 'debug_clicks_%s' % folder_timestamp
DEBUG_AFK_RESETTER = False
DEBUG_LIST = False
DEBUG_CLICKS = False
DEBUG_PAGE_SENSE = False
DEBUG_NEXT_TP_PAGE = False
DEBUG_TP_WINDOW_DOWN = False
DEBUG_LIMIT_PAGES = False
DEBUG_LIST_FIRST_ITEM = "Corrupted Lodestone"
if DEBUG_AFK_RESETTER:
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
    global debug_screenshot_counter
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


def crop_total_page_number_from_clip(image):
    yellows = [[255, 255, x] for x in range(190, 255)]
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
    res = image.crop((max_yellow_x_coord + 22, 0, width, height))

    ### method 1 disabled, return candidate 1 if you want  to switch back
    # enhancer = ImageEnhance.Brightness(res)
    # candidate1 = enhancer.enhance(2)

    opencvImage = cv2.cvtColor(numpy.array(res), cv2.COLOR_RGB2BGR)
    temp_image = cv2.convertScaleAbs(opencvImage, alpha=3, beta=0)
    candidate2 = Image.fromarray(temp_image)
    if DEBUG_PAGE_SENSE:
        global page_sense_iterator
        base_dir = 'output/'
        new_dir = '%s/%s' % (base_dir, 'pages')
        dir_exists = os.path.exists(new_dir)

        # Creating directories
        if not dir_exists:
            os.mkdir(new_dir)
        # candidate1.show()
        # candidate2.show()
        candidate2.save("%s/%s%i.png" % (new_dir, 'page_clips', page_sense_iterator))
        page_sense_iterator += 1
    return candidate2


def get_pages():
    image = get_screen_shot()

    left = 1672
    top = 208
    right = left + 113
    bottom = top + 34

    rough_cropped_image = image.crop((left, top, right, bottom))

    cropped_image = crop_total_page_number_from_clip(rough_cropped_image)

    custom_config = r'--oem 3 --psm 6 outputbase digits'
    try:
        text = pytesseract.image_to_string(cropped_image, config=custom_config)
        pages = int(text)

    except:
        print("Failed to read a number")
        # just assume 200 pages if we can't parse a page number... temp workaround until I learn how to clean image clips
        if cropped_image.width < 23: # I think this is a safe way to detect 1 digit numbers? Haven't done the analysis yet.
            print("Can't read the fucking number, but it feels like a 1 digit number, guessing 9... good luck ;)")
            pages = 9
        elif cropped_image.width < 32:
            print("Can't read the fucking number, but it feels like a 2 digit number, guessing 99... good luck ;)")
            pages = 99
        else:
            print("Can't read the fucking number, but it feels like a 3 digit number, guessing 210... good luck ;)")
            pages = 210 # can't do much more than 200 at a time anyway because of the AFK timer


    #TODO  sometimes pytesseract mistakes 1xx for 4xx, this is a temporary workaround
    if 400 < pages < 499:
        pages = pages - 300
    print("Detected %i pages" % pages)

    #TODO sometimes we just get huge numbers, let's repeate the detect image width method to get something more resonable:
    if pages > 210:
        print("Number too large or doesn't make sense, using the widthe detection method...")
        print("Failed to read a number")
        # just assume 200 pages if we can't parse a page number... temp workaround until I learn how to clean image clips
        if cropped_image.width < 23: # I think this is a safe way to detect 1 digit numbers? Haven't done the analysis yet.
            print("Can't read the fucking number, but it feels like a 1 digit number, guessing 9... good luck ;)")
            pages = 9
        elif cropped_image.width < 32:
            print("Can't read the fucking number, but it feels like a 2 digit number, guessing 99... good luck ;)")
            pages = 99
        else:
            print("Can't read the fucking number, but it feels like a 3 digit number, guessing 210... good luck ;)")
            pages = 210 # can't do much more than 200 at a time anyway because of the AFK timer

    if DEBUG_LIMIT_PAGES:
        return range(2)

    return range(pages)


def prepare():
    pyautogui.press("c")
    time.sleep(1)
    pyautogui.press("e")
    print("prepared")
    debug_save_image("prepared")


def screen_cap_scroll_down_screen_cap(page, commodity_type, total_pages=0, current_page=0):
    focus_on_new_world()
    total_pages += 1
    print("page %i / %i" % (current_page + 1, total_pages))
    img = get_screen_shot()
    img.save("%s/%s%i.png" % (new_dir, commodity_type, page))
    scroll_tp_window_down()
    img = get_screen_shot()
    img.save("%s/%s%i.png" % (new_dir, commodity_type, page))
    next_tp_page()


def reset_mouse_position():
    mouse.move(1000, 1000)


def click_coords(x, y, message="", subcategory=False):
    focus_on_new_world()
    # If it's a subcategory, the UI scrolls and loads pretty and slow
    if subcategory:
        time.sleep(2)
    mouse.position = (x, y)
    time.sleep(0.5)
    mouse.click(Button.left)
    # pyautogui.click(x, y)
    time.sleep(0.2)
    # If a top level category, it's safe and more consistent to click twice
    if not subcategory:
        pyautogui.click(x, y)
        time.sleep(0.2)
    print(message)
    message = message.replace(' ', '_')
    debug_save_image(message)
    reset_mouse_position()
    time.sleep(2)


def find_buy_icon():
    # TODO SKIP THIS UNTIL A REFACOR, OR BETTER YET, FIND A BETTER DESIGN
    return True
    # pick 3 pixels in the buy icon
    # take screen shot
    #  This doesn't really work :(
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
    counter = 0
    while not found_buy_icon:
        # best effort workaround. If We're not in the TP at this point, we're fucked :(
        if counter > 4:
            break
        pyautogui.keyDown('w')
        time.sleep(0.5)
        pyautogui.keyUp('w')
        time.sleep(0.25)
        pyautogui.press('e')
        found_buy_icon = find_buy_icon()
        counter += 1
    time.sleep(1.25)
    print("Done resetting AFK timer")
    debug_save_image("reset afk timer")


def scroll_tp_window_down():
    pyautogui.click(1841, 1011)
    time.sleep(2)
    pyautogui.click(1841, 1011)
    print("Scrolled TP windows down")
    if DEBUG_TP_WINDOW_DOWN:
        debug_save_image("scrolled_tp_window_down")


def next_tp_page():
    pyautogui.click(1800, 225)
    time.sleep(0.5)
    print("next_tp_page")
    if DEBUG_NEXT_TP_PAGE:
        debug_save_image("next_tp_page")


def get_static_list_of_items():
    with open(static_item_list) as file:
        lines = file.readlines()
        lines = [line.rstrip() for line in lines]
        return lines


# def calculate_x_coord(coord):
#     if FULL_SCREEN_MODE:
#         return coord - 1920
#     else:
#         return coord - 1920
#
# def calculate_y_coord(coord):
#     if FULL_SCREEN_MODE:
#         return coord - 25
#     else:
#         return coord


def click_on_consumables_category():
    click_coords(123, 670, 'click_on_consumables_category' )


def click_on_ammo_category():
    click_coords(123, 740, 'click_on_ammo_category')


def click_on_furniture_category():
    click_coords(123, 814, 'click_on_furniture_category')


def click_on_resources():
    click_coords(123, 592, 'click_on_resources')


def click_on_raw_resource():
    time.sleep(sleep_time_before_clicking_subcategory)
    click_coords(212, 370, 'click_on_raw_resource', subcategory=True)
    time.sleep(sleep_time_after_clicking_resource_subcategory)


def click_on_refined_resource():
    time.sleep(sleep_time_before_clicking_subcategory)
    click_coords(212, 424, 'click_on_refined_resource', subcategory=True)
    time.sleep(sleep_time_after_clicking_resource_subcategory)


def click_on_cooking_ingredients():
    time.sleep(sleep_time_before_clicking_subcategory)
    click_coords(212, 479, 'click_on_cooking_ingredients', subcategory=True)
    time.sleep(sleep_time_after_clicking_resource_subcategory)


def click_on_craft_mods():
    time.sleep(sleep_time_before_clicking_subcategory)
    click_coords(212, 530, 'click_on_craft_mods', subcategory=True)
    time.sleep(sleep_time_after_clicking_resource_subcategory)


def click_on_components():
    time.sleep(sleep_time_before_clicking_subcategory)
    click_coords(212, 585, 'click_on_components', subcategory=True)
    time.sleep(sleep_time_after_clicking_resource_subcategory)


def click_on_potion_reagents():
    time.sleep(sleep_time_before_clicking_subcategory)
    click_coords(212, 639, 'click_on_potion_reagents', subcategory=True)
    time.sleep(sleep_time_after_clicking_resource_subcategory)


def click_on_dyes():
    time.sleep(sleep_time_before_clicking_subcategory)
    click_coords(212, 695, 'click_on_dyes', subcategory=True)
    time.sleep(sleep_time_after_clicking_resource_subcategory)


def click_on_azoth():
    time.sleep(sleep_time_before_clicking_subcategory)
    click_coords(212, 748, 'click_on_azoth', subcategory=True)
    time.sleep(sleep_time_after_clicking_resource_subcategory)


def click_on_arcana():
    time.sleep(sleep_time_before_clicking_subcategory)
    click_coords(212, 802, 'click_on_arcana', subcategory=True)
    time.sleep(sleep_time_after_clicking_resource_subcategory)


def click_on_item_in_search_box(_item_name):
    focus_on_new_world()
    pyautogui.click(192, 354)
    time.sleep(0.2)
    pyautogui.click(192, 354)
    print("Clicked on %s in search bar (maybe)" % _item_name)
    time.sleep(1)
    debug_save_image("clicked on item in search box")


def click_on_search_box():
    focus_on_new_world()
    pyautogui.click(250, 226)
    time.sleep(0.2)
    pyautogui.click(250, 226)
    print("clicked on Search bar")
    debug_save_image("clicked on search box")


def type_in_search_box(_item_name):
    for letter in _item_name:
        keyboard.press(letter)
        time.sleep(0.05)
    keyboard.press(Key.enter)
    debug_save_image("Presed enter in search box")


if __name__ == '__main__':

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

    if not SKIP_ALL_RESOURCES:
        if not SKIP_RAW_RESOURCES:
            # Get resource prices per subcategory
            click_on_resources()

            click_on_raw_resource()
            category_pages = get_pages()
            while category_pages[-1] == 499:
                click_on_resources()
                click_on_raw_resource()
                category_pages = get_pages()
            for page in category_pages:
                screen_cap_scroll_down_screen_cap(page, 'raw_resources', total_pages=category_pages[-1], current_page=page)

            # anti-AFK
            reset_afk_timer()
            time.sleep(2)
        else:
            print("Skipping Raw Resources")

        if not SKIP_REFINED_RESOURCES:
            # Get resource prices per subcategory
            click_on_resources()

            click_on_refined_resource()
            category_pages = get_pages()
            while category_pages[-1] == 499:
                click_on_resources()
                click_on_refined_resource()
                category_pages = get_pages()
            for page in category_pages:
                screen_cap_scroll_down_screen_cap(page, 'refined_resources', total_pages=category_pages[-1], current_page=page)

            # anti-AFK
            reset_afk_timer()
            time.sleep(2)
        else:
            print("Skipping Refined Resources")

        if not SKIP_COOKING_INGREDIENTS:
            # Get resource prices per subcategory
            click_on_resources()

            click_on_cooking_ingredients()
            category_pages = get_pages()
            while category_pages[-1] == 499:
                click_on_resources()
                click_on_cooking_ingredients()
                category_pages = get_pages()
            for page in category_pages:
                screen_cap_scroll_down_screen_cap(page, 'cooking_ingredients', total_pages=category_pages[-1], current_page=page)

            # anti-AFK
            reset_afk_timer()
            time.sleep(2)
        else:
            print("Skipping Cooking Ingredients")

        if not SKIP_CRAFT_MODS:
            # Get resource prices per subcategory
            click_on_resources()

            click_on_craft_mods()
            category_pages = get_pages()
            while category_pages[-1] == 499:
                click_on_resources()
                click_on_craft_mods()
                category_pages = get_pages()
            for page in category_pages:
                screen_cap_scroll_down_screen_cap(page, 'craft_mods', total_pages=category_pages[-1], current_page=page)

            # anti-AFK
            reset_afk_timer()
            time.sleep(2)
        else:
            print("Skipping Craft Mods")

        if not SKIP_COMPONENTS:
            # Get resource prices per subcategory
            click_on_resources()

            click_on_components()
            category_pages = get_pages()
            while category_pages[-1] == 499:
                click_on_resources()
                click_on_components()
                category_pages = get_pages()
            for page in category_pages:
                screen_cap_scroll_down_screen_cap(page, 'components', total_pages=category_pages[-1], current_page=page)

            # anti-AFK
            reset_afk_timer()
            time.sleep(2)
        else:
            print("Skipping Components")

        if not SKIP_POTION_REAGENTS:
            # Get resource prices per subcategory
            click_on_resources()

            click_on_potion_reagents()
            category_pages = get_pages()
            while category_pages[-1] == 499:
                click_on_resources()
                click_on_potion_reagents()
                category_pages = get_pages()
            for page in category_pages:
                screen_cap_scroll_down_screen_cap(page, 'potion_reagents', total_pages=category_pages[-1], current_page=page)

            # anti-AFK
            reset_afk_timer()
            time.sleep(2)
        else:
            print("Skipping Potion Reagents")

        if not SKIP_DYES:
            # Get resource prices per subcategory
            click_on_resources()

            click_on_dyes()
            category_pages = get_pages()
            while category_pages[-1] == 499:
                click_on_resources()
                click_on_dyes()
                category_pages = get_pages()
            for page in category_pages:
                screen_cap_scroll_down_screen_cap(page, 'dyes', total_pages=category_pages[-1], current_page=page)

            # anti-AFK
            reset_afk_timer()
            time.sleep(2)
        else:
            print("Skipping Dyes")

        if not SKIP_AZOTH:
            # Get resource prices per subcategory
            click_on_resources()

            click_on_azoth()
            category_pages = get_pages()
            while category_pages[-1] == 499:
                click_on_resources()
                click_on_azoth()
                category_pages = get_pages()
            for page in category_pages:
                screen_cap_scroll_down_screen_cap(page, 'azoth', total_pages=category_pages[-1], current_page=page)

            # anti-AFK
            reset_afk_timer()
            time.sleep(2)
        else:
            print("Skipping Azoth")

        if not SKIP_ARCANA:
            # Get resource prices per subcategory
            click_on_resources()

            click_on_arcana()
            category_pages = get_pages()
            while category_pages[-1] == 499:
                click_on_resources()
                click_on_arcana()
                category_pages = get_pages()
            for page in category_pages:
                screen_cap_scroll_down_screen_cap(page, 'arcana', total_pages=category_pages[-1], current_page=page)

            # anti-AFK
            reset_afk_timer()
            time.sleep(2)
        else:
            print("Skipping Arcana")

    if not SKIP_CONSUMABLES:
        # Get consumable prices
        click_on_consumables_category()
        category_pages = get_pages()
        while category_pages[-1] == 499:
            click_on_consumables_category()
            category_pages = get_pages()
        for page in category_pages:
            screen_cap_scroll_down_screen_cap(page, 'consumables', total_pages=category_pages[-1], current_page=page)

        # anti-AFK
        reset_afk_timer()
        time.sleep(2)
    else:
        print("Skipping Consumables")

    if not SKIP_AMMO:
        # Get ammo pages
        click_on_ammo_category()
        category_pages = get_pages()
        while category_pages[-1] == 499:
            click_on_ammo_category()
            category_pages = get_pages()
        for page in category_pages:
            screen_cap_scroll_down_screen_cap(page, 'ammo', total_pages=category_pages[-1], current_page=page)

        # anti-AFK
        reset_afk_timer()
        time.sleep(2)
    else:
        print("Skipping Ammo")

    if not SKIP_FURNITURE:
        # Get furniture
        click_on_furniture_category()
        category_pages = get_pages()
        while category_pages[-1] == 499:
            click_on_furniture_category()
            category_pages = get_pages()
        for page in category_pages:
            screen_cap_scroll_down_screen_cap(page, 'furniture', total_pages=category_pages[-1], current_page=page)

        # anti-AFK
        reset_afk_timer()
        time.sleep(2)
    else:
        print("Skipping Furniture")

    if not SKIP_LIST:
        # # The following code will get straggling items that must be put in a list
        now = datetime.datetime.now()
        next_afk_time = now + datetime.timedelta(minutes=afk_time)
        static_item_list = get_static_list_of_items()
        if DEBUG_LIST:
            first_index = static_item_list.index(DEBUG_LIST_FIRST_ITEM)
            static_item_list = static_item_list[first_index:]
        counter = 0
        for item_name in static_item_list:
            if DEBUG_AFK_RESETTER:
                if counter >= 40:
                    exit(0)
            counter += 1

            now = datetime.datetime.now()
            if now > next_afk_time:
                reset_afk_timer()
                time.sleep(2)
                # reset_afk_timer()
                # time.sleep(2)
                now = datetime.datetime.now()
                next_afk_time = now + datetime.timedelta(minutes=afk_time)

            click_on_search_box()

            type_in_search_box(item_name)

            img = get_screen_shot()
            print("Saving debug screenshot %s..." % item_name)
            img.save("%s/%s.png" % (debug_dir, item_name))
            print("Done saving debug screenshot for %s" % item_name)

            click_on_item_in_search_box(item_name)

            get_screen_shot()

            img = get_screen_shot()
            print("Saving screenshot %s ..." % item_name)
            img.save("%s/%s.png" % (new_dir, item_name))
            print("Done saving screenshot %s" % (item_name))
    else:
        print("Skipping Static List")
