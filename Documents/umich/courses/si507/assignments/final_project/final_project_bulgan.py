#################################
##### Name: Bulgan Jugderkhuu
##### Uniqname: bulgan
#################################
#this project is to find things to do in Chicago today, this weekend,
#this month (April for the database requirement), and all time

from bs4 import BeautifulSoup
import requests
import json
import time
import sqlite3
import webbrowser

BASE_URL = 'https://www.timeout.com'
STATES_INDEX_PATH = '/index.htm'
CACHE_FILE_NAME = 'chicago_cache.json'
CACHE_DICT = {}


#stating the global constant urls
chi_dict = {
    'today': 'https://www.timeout.com/chicago/things-to-do/things-to-do-in-chicago-today',
    'this week': 'https://www.timeout.com/chicago/things-to-do/best-things-to-do-this-week-in-chicago',
}

#caching functions
def open_cache():
    try:
        cache_file = open(CACHE_FILE_NAME, 'r')
        cache_file_contents = cache_file.read()
        cache = json.loads(cache_file_contents)
        cache_file.close()
    except:
        cache = {}
    return cache


def save_cache(cache):
    cache_file = open(CACHE_FILE_NAME, 'w')
    contents_to_write = json.dumps(cache)
    cache_file.write(contents_to_write)
    cache_file.close()

def make_request(baseurl):
    '''Make a request to the webpage

    Parameters
    ----------
    baseurl: string
        The URL
    Returns
    -------
    dict
        the data returned from making the request in the form of
        a dictionary
    '''

    resp = requests.get(baseurl)
    return resp.text

def make_url_request_using_cache(url, cache):
    '''Make a request to the webpage using the url if
    it is not already in the cache file

    Parameters
    ----------
    url: string
        The URL for the webpage
    cache: cache
        A dictionary of the cache

    Returns
    -------
    dict
        the data returned from making the request in the form of
        a dictionary
    '''
    if (url in cache.keys()): # the url is our unique key
        print("Using cache")
        return cache[url]
    else:
        print("Fetching")
        response = requests.get(url)
        cache[url] = response.text
        save_cache(cache)
        return cache[url]

class Event:
    '''an event for things to do

    Instance Attributes
    -------------------
    name: string
        the name of an event(thing to do)
    category: string
        the category of that event (ex. art)
    date: string
        the date of the location if available
    address: string
        the address of the event if available
    price: string
        the price of the event if available
    url: string
        the url of the event if available
    '''
    def __init__(self, name=None, category=None, date=None, address=None, price=None, url=None):
        self.name = name
        self.category = category
        self.date = date
        self.address = address
        self.price = price
        self.url = url


    def info(self):
        return f"{self.name} ({self.category}): {self.address} {self.date} {self.price}"


def get_event_instance(site_url):
    '''Make an event instance from an event url.

    Parameters
    ----------
    site_url: string
        The URL for an event page on timeout.com

    Returns
    -------
    instance
        an event instance
    '''
    #uses beautifulsoup for the url information to extract

    site_text = make_url_request_using_cache(site_url, CACHE_DICT)
    soup = BeautifulSoup(site_text, 'html.parser')
    try:
        event_name = soup.find(class_='xs-text-2 v4-md-text-1 xs-line-height-2 v4-md-line-height-1 xs-mt4').text.strip()
    except:
        event_name = 'No name'
    try:
        event_category = soup.find('span', class_='flag--primary_category').text.strip()
    except:
        event_category = 'No category'
    try:
        event_date = soup.find('span', class_='flag icon icon_calendar').text.strip()
    except:
        event_date = 'No date'

    try:
        #checks if the bottom of the page is available to extract address
        event_footer = soup.find('table', class_='listing_details tabless__listing_details xs-text-left xs-col-12 xs-mb5 sm-mb0')
        event_tr = event_footer.findChildren('th')
        #loops through the 'th' tags that have the address
        for th in event_tr:
            try:
                if (th.text.strip()) == 'Address:':
                    event_address = th.next_sibling.next_sibling.text.strip().split('\n')[0]
            except:
                event_address = 'No Address'
    #if footer doesn't exist - fill in no address
    except:
        event_address = 'No address'

    event_price = 'No price'
    try:
        #checks if the bottom of the page is available to extract price
        event_footer = soup.find('table', class_='listing_details tabless__listing_details xs-text-left xs-col-12 xs-mb5 sm-mb0')
        event_tr = event_footer.findChildren('th')
        #loops through the 'th' tags that have the price
        for th in event_tr:
            try:
                if (th.text.strip()) == 'Price:':
                    event_price = th.next_sibling.next_sibling.text.strip()
            except:
                continue
    #if footer doesn't exist - fill in no price
    except:
        event_price = 'No price'

    event_instance = Event(name=event_name, category=event_category, date=event_date, address=event_address, price=event_price,url=site_url)
    return event_instance


#get links for the monthly event for a city
def get_events_for_city(city_url):
    '''Make a list of national site instances from a state URL.

    Parameters
    ----------
    state_url: string
        The URL for a state page in nps.gov

    Returns
    -------
    list
        a list of national site instances
    '''
    list_of_events = []
    #city_month_url = 'https://www.timeout.com/chicago/events-calendar/april-events-calendar'
    city_text = make_request(city_url)
    soup = BeautifulSoup(city_text, 'html.parser')
    events = soup.find_all('h3', class_='card-title xs-text-charcoal title--compressed xs-text-2 xs-line-height-2 xs-mb2')
    for event in events:
        event_link_tag = event.find('a')
        event_path = event_link_tag['href']
        event_url = BASE_URL + event_path
        event_obj = get_event_instance(event_url)
        list_of_events.append(event_obj)
    return list_of_events

#monthly events for april in chicago for database
# chi_month_url = 'https://www.timeout.com/chicago/events-calendar/april-events-calendar'
# chi_month_events = get_events_for_city(chi_month_url)



# # best things to do for database
# chi_best_things_url = 'https://www.timeout.com/chicago/things-to-do/best-things-to-do-in-chicago'
# chi_best_things = get_events_for_city(chi_best_things_url)



#commenting out the database for it to not re-insert information
# conn = sqlite3.connect("Chicago_Database.sqlite")
# cur = conn.cursor()

# #database for the april events in chicago (static for now)
# create_chicago_april = '''
#     CREATE TABLE IF NOT EXISTS "Chicago_April" (
#         "Id" INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
#         "Name" TEXT,
#         "Category" TEXT,
#         "Address" TEXT,
#         "Date" TEXT,
#         "Price" TEXT
#     );
# '''
# cur.execute(create_chicago_april)

# insert_data = '''
#     INSERT INTO Chicago_April
#     VALUES (NULL,?,?,?,?,?)
# '''
# for event in chi_month_events:
#     cur.execute(insert_data, [event.name, event.category, event.address, event.date, event.price])

# #database for the "best" events in chicago (static)
# create_chicago_best = '''
#     CREATE TABLE IF NOT EXISTS "Chicago_Best" (
#         "Id" INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
#         "Name" TEXT,
#         "Category" TEXT,
#         "Address" TEXT,
#         "Date" TEXT,
#         "Price" TEXT
#     );
# '''

# cur.execute(create_chicago_best)
# insert_data = '''
#     INSERT INTO Chicago_Best
#     VALUES (NULL,?,?,?,?,?)
# '''
# for event in chi_best_things:
#     cur.execute(insert_data, [event.name, event.category, event.address, event.date, event.price])

# conn.commit()

def print_choice_events(day, events_list):
    '''
    prints the day choice and the events
    ordered by their index in the list with
    relevant info

    Parameters
    ----------
    state: str
        the state name
    sites_list: list
        the list of sites

    Returns
    -------
    prints each site and it's index (starting at 1 not 0)

    '''
    print('-' * 50)
    print(f"List of things to do in Chicago {day}")
    print('-' * 50)
    for x in events_list:
        # print(sites_list.index(x)+1, x.info())
        print(f"[{events_list.index(x)+1}]", x.info())


if __name__ == "__main__":
    print("Welcome to Chicago! I will recommend you things to do during your stay")
    while True:
        user_input = input("Enter 'today', 'this week', 'this month', or 'all time' for things to do, or 'exit' to quit: ").lower().strip()
        if user_input == 'exit':
            break
        elif user_input in chi_dict.keys():
            # states_dict = build_state_url_dict()
            user_input_day_url = chi_dict[user_input]
            event_sites = get_events_for_city(user_input_day_url)
            print_choice_events(user_input, event_sites)

            while True:
                try:
                    user_input = input("Choose the number for detail search or 'exit' or 'back': ")
                    if user_input == 'exit':
                        break
                    elif user_input == 'back':
                        break
                    if user_input.isnumeric():
                        if int(user_input) <= int(len(event_sites)):
                            print(f"Launching {event_sites[int(user_input)-1].url} in web browser...")
                            webbrowser.open(event_sites[int(user_input)-1].url)
                        else:
                            print("Index out of range. Please enter a new number")
                    else:
                        break
                except:
                    print("Error - please try again.")
        # elif user_input in ['this month', 'all time']:
        #     #print_database_choice(user_input)
        elif user_input == 'this month':
            connection = sqlite3.connect("Chicago_Database.sqlite")
            cursor = connection.cursor()
            query = "SELECT * FROM Chicago_April"
            result = cursor.execute(query).fetchall()
            connection.close()
            print("This month's things to do:")
            print('-' * 50)
            for event in result:
                print(event[0],event[1],event[2],event[3], event[4])

        elif user_input == 'all time':
            connection = sqlite3.connect("Chicago_Database.sqlite")
            cursor = connection.cursor()
            query = "SELECT * FROM Chicago_Best"
            result = cursor.execute(query).fetchall()
            connection.close()
            print("All time best things to do:")
            print('-' * 50)
            for event in result:
                print(event[0],event[1],event[2],event[3], event[4])
        else:
            quit()
    print("Enjoy!")