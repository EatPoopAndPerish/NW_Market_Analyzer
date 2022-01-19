import os
import time
import json
import datetime
from pprint import pprint

from scipy import stats

# We want all of the items in this file to have a price. If we didn't scrape a price, the default will be used.
list_of_mandatory_items_file = './resources/item_lists/item_list_from_g_sheet.txt'
# Setting a super high price for items not found. This is a workaround to avoid having to recreate the Tradesman's Bible spreadsheet.
# Basically, if there's no iron on the market and iron is a component of some craft, then it really costs infinity
# when considering to craft from raw, craft from refined, or buy outright.
default_price_if_not_found = 100000
input_file = './output/file.json'

# These are the data structures we'll be using to keep things organized
items_found_in_market_but_not_in_list = []
items_in_g_sheet_list_not_found_in_market = []
lowest_price_dictionary = {}
found_items = []
g_sheet_result = []
missing_items = []

def get_static_list_of_items():
    with open(list_of_mandatory_items_file) as file:
        print("Reading in list %s" % list_of_mandatory_items_file)
        lines = file.readlines()
        lines = [line.rstrip() for line in lines]
        print("Found %i items in list" % len(lines))
        return lines


if __name__ == '__main__':
    # Setup scaffolding
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d")
    base_dir = 'output/'
    output_folder_name = 'lists_%s' % timestamp
    output_dir = base_dir + '/' + output_folder_name

    dir_exists = os.path.exists(output_dir)
    if not dir_exists:
        os.makedirs(output_dir)

    # This is everything found on the market
    output_all_csv_file = '%s/market_all_%s.csv' % (output_dir , timestamp)
    # The purpose of this file is to copy and paste a static list of items with new prices into g sheets
    output_gsheet_csv_file = '%s/market_gsheet_%s.csv' % (output_dir, timestamp)
    # The purpose of this file is to plug into https://gaming.tools/newworld/ for updated prices
    output_cleaned_up_json_file = '%s/market_%s.json' % (output_dir, timestamp)
    # This file is used for debugging, items in the static list but not found on market go here
    missing_items_file = '%s/missing_items_%s.txt' % (output_dir, timestamp)
    # This list keeps track of all of the items found on the market
    found_items_file = '%s/found_items_%s.txt' % (output_dir, timestamp)
    # This is just a dump of the prices only in order that the g_sheets stuff is  setup
    g_sheets_prices_only = '%s/market_gsheet_prices_only_%s.csv' % (output_dir, timestamp)
    # The json file created by the parser
    in_file = './output/file.json'
    # Initialize the static list
    g_sheet_list = get_static_list_of_items()

    with open(in_file, encoding='utf-8-sig') as f:
        data_from_parser = json.load(f)


    # Cycle through the JSON and create a list of dictionaries that looks like this:
    # itemname price availability itemid
    # itemname price availability itemid
    # itemname price availability itemid
    # ...
    scraped_data_table = []
    for item in data_from_parser:
        ItemId = item['ItemId']
        ItemName = item['ItemName']
        Tier = item['Tier']
        Price = item['Price']
        Availability = item['Availability']
        GearScore = item['GearScore']
        LocationId = item['LocationId']
        Location = item['Location']
        TimeCreatedUtc = item['TimeCreatedUtc']

        # some things come up with hugely inflated values, let's do a sanity check and skip the fucked up ones
        # This is a good place to do some sanity checking
        if Price > default_price_if_not_found:
            continue

        scraped_data_table.append({'ItemName': ItemName, 'Price': Price, 'Availability': Availability, 'ItemId': ItemId})

    # scraped_data_table now has an entry for every json object found
    # We'll sort it for efficiency
    scraped_data_table.sort(key=lambda x: x['ItemName'])



    # First we add all of the items we found, adding entries into the dict of the form item_name: min_price
    for item in scraped_data_table:
        item_name = item['ItemName']
        item_price = item['Price']
        if ',' in item_name:
            print("item %s has a comma, skipping" % item_name)
            continue
        found_items.append(item_name)

        if lowest_price_dictionary.get(item_name) is None:
            lowest_price_dictionary[item_name] = item_price
        else:
            lowest_price_so_far = lowest_price_dictionary.get(item_name)
            lowest_price_now = min(item_price, lowest_price_so_far)
            lowest_price_dictionary[item_name] = lowest_price_now

    print("Items and prices found so far")
    pprint(lowest_price_dictionary)

    # Create the g sheets list
    # Now we ensure there's an entry for every item in the g_sheet_list
    print("################################")
    print("Checking that all required items are in the list")

    for item in g_sheet_list:
        if lowest_price_dictionary.get(item) is None:
            lowest_price_dictionary[item] = default_price_if_not_found
            print("ITEM %s NOT FOUND, ADDING DEFAULT VALUE %i" % (item, default_price_if_not_found))
            missing_items.append(item)
            g_sheet_result.append((item, default_price_if_not_found))
        else:
            item_price = lowest_price_dictionary[item]
            g_sheet_result.append((item, item_price))

    # Somehow duplicates got in, so let's fix that shit
    g_sheet_result_final = []
    [g_sheet_result_final.append(x) for x in g_sheet_result if x not in g_sheet_result_final]
    g_sheet_result_final.sort(key=lambda x: x[0])


    # TODO Let's output all items found in the market not on the g_sheet_list

    # TODO Let's output a json file with some cleaned up values

    table = [(item_name, min_price) for item_name, min_price in lowest_price_dictionary.items()]
    table.sort(key=lambda x: x[0])

    with open(output_all_csv_file, 'w') as out:
        out.write('Item, Price\n')
        for item in table:
            name = item[0]
            min_price = item[1]
            out.write('%s, %s\n' % (name, min_price))

    with open(output_gsheet_csv_file, 'w') as out:
        for item in g_sheet_result_final:
            name = item[0]
            min_price = item[1]
            out.write('%s, %s\n' % (name, min_price))

    with open(g_sheets_prices_only, 'w') as out:
        for item in g_sheet_result_final:
            min_price = item[1]
            out.write('%s\n' % min_price)

    with open(missing_items_file, 'w') as out:
        for item in missing_items:
            out.write('%s\n' % item)

    found_items.sort()
    with open(found_items_file, 'w') as out:
        for item in lowest_price_dictionary.keys():
            out.write('%s\n' % item)