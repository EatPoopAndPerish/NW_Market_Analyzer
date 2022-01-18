import time
import json
from scipy import stats

item_list_file = './resources/item_lists/item_list.txt'
# Setting a super high price for items not found. This is a workaround to avoid having to recreate the Tradesman's Bible spreadsheet.
default_price_if_not_found = 100000


def unique(list1):
    # initialize a null list
    unique_list = []

    # traverse for all elements
    for x in list1:
        # check if exists in unique_list or not
        if x not in unique_list:
            unique_list.append(x)


def get_static_list_of_items():
    with open(item_list_file) as file:
        lines = file.readlines()
        lines = [line.rstrip() for line in lines]
        return lines


if __name__ == '__main__':
    timestamp = time.time()
    base_dir = 'output/'
    out_file = '%s/market_%s.csv' % (base_dir, timestamp)
    in_file = './output/file.json'
    static_item_name_list = get_static_list_of_items()

    with open(in_file, encoding='utf-8-sig') as f:
        data = json.load(f)


    # Cycle through the JSON and create a table that looks like this:
    # itemname price availability itemid
    # itemname price availability itemid
    # itemname price availability itemid
    # ...
    tmp_table = []
    for item in data:
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
        if Price > 50000:
            continue

        # ids.add(ItemId)

        tmp_table.append({'ItemName': ItemName, 'Price': Price, 'Availability': Availability, 'ItemId': ItemId})

    # tmp_table now has an entry for every json object found
    # We'll sort it for efficiency
    tmp_table.sort(key=lambda x: x['ItemName'])

    # ids is a static list of items found in item_list.txt
    table = []
    items_found_in_market_but_not_in_list = []
    for item_name in static_item_name_list:
        count = 0
        # assume all items start at 100k, go down from there if prices are found
        min_price = default_price_if_not_found
        # inefficient, but fuck it...
        for item in tmp_table:
            if item['ItemName'] != item_name:
                continue
            count += 1
            min_price = min(min_price, item['Price'])
        if count == 0:
            items_found_in_market_but_not_in_list.append(item_name)


        entry = (item_name, min_price)
        table.append(entry)
        print(entry)

    print("Items found in market, but not in static list:")
    for item in items_found_in_market_but_not_in_list:
        print(item)
        table.append((item, default_price_if_not_found))

    table.sort()
    table.sort(key=lambda x: x[0])

    with open(out_file, 'w') as out:
        out.write('Item, Price\n')
        for item in table:
            name = item[0]
            min_price = item[1]

            out.write('%s, %s\n' % (name, min_price))