# SI 507 Final Project: Things to do in Chicago
## This project is an interactive interface for users to find things to do in Chicago from the command line 
The user is prompted to select a "date" to find things to do on with the options of: today, this week, this month, or all time
The options for today and this week are extracted from the website directly, but the options for this month and all time are stored in a database so this month is only retriving things to do in Chicago April 2021. 
The database creating and inserting codes are between lines 225-268 so they will need to be uncommented to run for the first time and enter the data. They have been commented out to not insert the data every time the code is run. 
Packages needed are bs4 BeautifulSoup, requests, json, time, sqlite3 and webbrowser.