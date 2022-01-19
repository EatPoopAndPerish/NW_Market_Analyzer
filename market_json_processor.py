import time
import json
from pprint import pprint

from scipy import stats

# We want all of the items in this file to have a price. If we didn't scrape a price, the default will be used.
list_of_mandatory_items_file = './resources/item_lists/item_list_from_g_sheet.txt'
# Setting a super high price for items not found. This is a workaround to avoid having to recreate the Tradesman's Bible spreadsheet.
# Basically, if there's no iron on the market and iron is a component of some craft, then it really costs infinity
# when considering to craft from raw, craft from refined, or buy outright.
default_price_if_not_found = 100000
input_file = './output/file.json'


def unique(_list):
    # initialize a null list
    unique_list = []

    # traverse for all elements
    for x in _list:
        # check if exists in unique_list or not
        if x not in unique_list:
            unique_list.append(x)


def get_static_list_of_items():
    with open(list_of_mandatory_items_file) as file:
        lines = file.readlines()
        lines = [line.rstrip() for line in lines]
        return lines


if __name__ == '__main__':

    # Setup scaffolding
    timestamp = time.time()
    base_dir = 'output/'
    output_csv_file = '%s/market_%s.csv' % (base_dir, timestamp)
    output_cleaned_up_json_file = '%s/market_%s.json' % (base_dir, timestamp)
    missing_items_file = '%s/missing_items_%s.txt' % (base_dir, timestamp)
    found_items_file = '%s/found_items_%s.txt' % (base_dir, timestamp)
    in_file = './output/file.json'
    g_sheet_list = get_static_list_of_items()

    with open(in_file, encoding='utf-8-sig') as f:
        data_from_parser = json.load(f)


    # Cycle through the JSON and create a table that looks like this:
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
        if Price > 90000:
            continue

        scraped_data_table.append({'ItemName': ItemName, 'Price': Price, 'Availability': Availability, 'ItemId': ItemId})

    # scraped_data_table now has an entry for every json object found
    # We'll sort it for efficiency
    scraped_data_table.sort(key=lambda x: x['ItemName'])

    # ids is a static list of items found in item_list.txt
    items_found_in_market_but_not_in_list = []
    items_in_g_sheet_list_not_found_in_market = []

    lowest_price_dictionary = {}
    found_items = []

    # First we add all of the items we found, adding entries into the dict of the form item_name: min_price
    for item in scraped_data_table:
        item_name = item['ItemName']
        item_price = item['Price']
        found_items.append(item_name)

        if lowest_price_dictionary.get(item_name) is None:
            lowest_price_dictionary[item_name] = item_price
        else:
            lowest_price_so_far = lowest_price_dictionary.get(item_name)
            lowest_price_now = min(item_price, lowest_price_so_far)
            lowest_price_dictionary[item_name] = lowest_price_now

    print("Items and prices found so far")
    pprint(lowest_price_dictionary)

    # Now we ensure there's an entry for every item in the g_sheet_list
    print("################################")
    print("Checking that all required items are in the list")
    missing_items = []
    for item in g_sheet_list:
        if lowest_price_dictionary.get(item) is None:
            lowest_price_dictionary[item] = default_price_if_not_found
            print("ITEM %s NOT FOUND, ADDING DEFAULT VALUE %i" % (item, default_price_if_not_found))
            missing_items.append(item)

    # TODO Let's output all items found in the market not on the g_sheet_list

    # TODO Let's output a json file with some cleaned up values

    table = [(item_name, min_price) for item_name, min_price in lowest_price_dictionary.items()]
    table.sort(key=lambda x: x[0])

    with open(output_csv_file, 'w') as out:
        out.write('Item, Price\n')
        for item in table:
            name = item[0]
            min_price = item[1]
            out.write('%s, %s\n' % (name, min_price))

    with open(missing_items_file, 'w') as out:
        for item in missing_items:
            out.write('%s\n' % item)

    found_items.sort()
    with open(found_items_file, 'w') as out:
        for item in lowest_price_dictionary.keys():
            out.write('%s\n' % item)