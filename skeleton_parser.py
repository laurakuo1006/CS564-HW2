
"""
FILE: skeleton_parser.py
------------------
Author: Firas Abuzaid (fabuzaid@stanford.edu)
Author: Perth Charernwattanagul (puch@stanford.edu)
Modified: 04/21/2014

Skeleton parser for CS564 programming project 1. Has useful imports and
functions for parsing, including:

1) Directory handling -- the parser takes a list of eBay json files
and opens each file inside of a loop. You just need to fill in the rest.
2) Dollar value conversions -- the json files store dollar value amounts in
a string like $3,453.23 -- we provide a function to convert it to a string
like XXXXX.xx.
3) Date/time conversions -- the json files store dates/ times in the form
Mon-DD-YY HH:MM:SS -- we wrote a function (transformDttm) that converts to the
for YYYY-MM-DD HH:MM:SS, which will sort chronologically in SQL.

Your job is to implement the parseJson function, which is invoked on each file by
the main function. We create the initial Python dictionary object of items for
you; the rest is up to you!
Happy parsing!
"""

import sys
from json import loads
from re import sub

columnSeparator = "|"

# Dictionary of months used for date transformation
MONTHS = {'Jan':'01','Feb':'02','Mar':'03','Apr':'04','May':'05','Jun':'06',\
        'Jul':'07','Aug':'08','Sep':'09','Oct':'10','Nov':'11','Dec':'12'}

ItemsTable = []
bidsTable = []
UsersTable = []
Item_CategoriesTable = []
UsersDict = {}
items_cat_pairs = {}

"""
Returns true if a file ends in .json
"""
def isJson(f):
    return len(f) > 5 and f[-5:] == '.json'

"""
Converts month to a number, e.g. 'Dec' to '12'
"""
def transformMonth(mon):
    if mon in MONTHS:
        return MONTHS[mon]
    else:
        return mon

"""
Transforms a timestamp from Mon-DD-YY HH:MM:SS to YYYY-MM-DD HH:MM:SS
"""
def transformDttm(dttm):
    dttm = dttm.strip().split(' ')
    dt = dttm[0].split('-')
    date = '20' + dt[2] + '-'
    date += transformMonth(dt[0]) + '-' + dt[1]
    return date + ' ' + dttm[1]

"""
Transform a dollar value amount from a string like $3,453.23 to XXXXX.xx
"""

def transformDollar(money):
    if money == None or len(money) == 0:
        return money
    return sub(r'[^\d.]', '', money)

"""
Parses a single json file. Currently, there's a loop that iterates over each
item in the data set. Your job is to extend this functionality to create all
of the necessary SQL tables for your database.
"""
def parseJson(json_file):
    with open(json_file, 'r') as f:
        items = loads(f.read())['Items'] # creates a Python dictionary of Items for the supplied json file
        global ItemsTable #stores all item info
        global bidsTable #stores all bids for all items
        global UsersDict #stores all users in a dict to get rid of duplicates later
        global Item_CategoriesTable
        global UsersTable
        
        for item in items:
            ItemsTable.append(gettItemString(item))
            bidsTable.extend(getBidsString(item)) #add bids info of this item to the aggregate BidsArray
            getUsers(item, UsersDict)
            Item_CategoriesTable.extend(getItem_CategoriesString(item))
            
"""
Item Schema: Item(ItemID, Name, Currently, First_Bid, Buy_Price, Started, Ends, UserID, Description)
Parses item from json format into a list of strings to be added to the Item load file
"""
def gettItemString(item):
    ItemID = str(item['ItemID'])
    Name = str(item['Name']).replace('"', '')
    Currently = transformDollar(item['Currently'])
    First_Bid = transformDollar(item['First_Bid'])
    Buy_Price = transformDollar(item['Buy_Price']) if 'Buy_Price' in item else 'NULL'
    Started = transformDttm(item['Started'])
    Ends = transformDttm(item['Ends'])
    UserID = str(item['Seller']['UserID']).replace('"', '')
    Description = str(item['Description']).replace('"', '')
    
    itemString = ItemID + "|" + Name + "|" + Currently + "|" + First_Bid + "|" + Buy_Price + "|" + Started + "|" + Ends + "|" + UserID + "|" + Description + "\n"
    
    return itemString

"""
bids Schema: bids(ItemID, UserID, Time, Amount)
Parses item from json format into a list of strings to be added to the bids load file
"""
def getBidsString(item):
    ItemID = str(item['ItemID'])
    bids = []
    if item['Bids'] != None:
        for bid in item['Bids']:
            UserID = bid['Bid']['Bidder']['UserID'].replace('"', '')
            Time = transformDttm(bid['Bid']['Time'])
            Amount = transformDollar(bid['Bid']['Amount'])
            bidString = ItemID + "|" + UserID + "|" + Time + "|" + Amount + "\n"
            bids.append(bidString)
        
    return bids
        
"""
User Schema: User(UserID, Country, Rating, Location)
Put seller and bidder information in a dictionary to handle duplicate users
"""
def getUsers(item, UsersDict):
    #get user info of seller
    sellerID = str(item['Seller']['UserID']).replace('"', '')
    sellerCountry = str(item['Country']).replace('"', '') if 'Country' in item.keys() and item['Country'] != None else 'NULL'
    sellerRating = item['Seller']['Rating'] if 'Rating' in item['Seller'].keys() and item['Seller']['Rating'] != None else 'NULL'
    sellerLocation = "\"" + str(item['Location']).replace('"', '') + "\"" if 'Location' in item.keys() and item['Location'] != None else 'NULL'
    
    #avoid duplicates
    if sellerID in UsersDict:
        UsersDict[sellerID]['Country'] = sellerCountry
        UsersDict[sellerID]['Rating'] = sellerRating
        UsersDict[sellerID]['Location'] = sellerLocation
    else:
        UsersDict[sellerID] = {'Country': sellerCountry, 'Rating': sellerRating, 'Location': sellerLocation}
        
    #get user info for bidders
    if item['Bids'] != None:
        for bid in item['Bids']:
            bidderID = str(bid['Bid']['Bidder']['UserID']).replace('"', '') 
            bidderCountry = str(bid['Bid']['Bidder']['Country']).replace('"', '') if 'Country' in bid['Bid']['Bidder'].keys() and bid['Bid']['Bidder']['Country'] != None else 'NULL'
            bidderRating = bid['Bid']['Bidder']['Rating'] if 'Rating' in bid['Bid']['Bidder'].keys() and bid['Bid']['Bidder']['Rating'] != None else 'NULL'
            bidderLocation = "\"" + str(bid['Bid']['Bidder']['Location']).replace('"', '') + "\"" if 'Location' in bid['Bid']['Bidder'].keys() and bid['Bid']['Bidder']['Location'] != None else 'NULL'
            
            if bidderID in UsersDict:
                UsersDict[bidderID]['Country'] = bidderCountry
                UsersDict[bidderID]['Rating'] = bidderRating
                UsersDict[bidderID]['Location'] = bidderLocation
            else:
                UsersDict[bidderID] = {'Country': bidderCountry, 'Rating': bidderRating, 'Location': bidderLocation}
                
"""
Given dictionary of unique, updated user info, convert to list of strings for load file
"""
def getUsersString(UsersDict):
    global UsersTable
    
    for UserID, info in UsersDict.items():
        userString = UserID + "|" + info['Country'] + "|" + info['Rating'] + "|" + info['Location'] +"\n"
        UsersTable.append(userString)
        
    return UsersTable

"""
Item_Categories Schema: Item_Categories(ItemID, Category)
Parses item from json format into list of strings to be added to the Item_Categories load file
"""
def getItem_CategoriesString(item):
    global items_cat_pairs
    ItemID = str(item['ItemID'])
    item_cat = []
    if ItemID not in items_cat_pairs.keys():
        items_cat_pairs[ItemID] = []
        for cat in item['Category']:
            if cat not in items_cat_pairs[ItemID]:
                catString = ItemID + "|" + str(cat).replace('"', '') + "\n"
                item_cat.append(catString)
                items_cat_pairs[ItemID].append(cat)
            
    return item_cat
    
"""
Loops through each json files provided on the command line and passes each file
to the parser
"""
def main(argv):
    if len(argv) < 2:
        print >> sys.stderr, 'Usage: python skeleton_json_parser.py <path to json files>'
        sys.exit(1)
        
    global ItemsTable
    global bidsTable
    global UsersTable
    global Item_CategoriesTable 
    global UsersDict
    
    # loops over all .json files in the argument
    # NOTE: items-*.json doesn't work on my laptop yet, according to instructor's piazza post 
    # it should work on a CSL Linux machine (?) 
    # waiting for a response under this post: https://piazza.com/class/m66rboeq3bk6po/post/81
    for f in argv[1:]:
        if isJson(f):
            parseJson(f)
            print ("Success parsing " + f)
            
    UsersTable = getUsersString(UsersDict)
            
    with open('Item.dat', 'w') as f:
        f.writelines(ItemsTable)
        
    with open('bids.dat', 'w') as f:
        f.writelines(bidsTable)
        
    with open('User.dat', 'w') as f:
        f.writelines(UsersTable)
        
    with open('Item_Categories.dat', 'w') as f:
        f.writelines(Item_CategoriesTable)

if __name__ == '__main__':
    main(sys.argv)
