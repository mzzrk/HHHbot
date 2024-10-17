#pulls data from map sheet, creates shortlist of reach maps and saves to json

import os
import requests
import simplejson as json
from dotenv import load_dotenv

load_dotenv()
spreadsheet_id = os.getenv('sheetID')
sheet_name = os.getenv('SheetName')
KEY = os.getenv('KEY')

def get_google_sheet_data(spreadsheet_id,sheet_name, api_key):
    # Construct the URL for the Google Sheets API
    url = f'https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/{sheet_name}!A1:Z?alt=json&key={api_key}'

    try:
        # Make a GET request to retrieve data from the Google Sheets API
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Parse the JSON response
        data = response.json()
        return data

    except requests.exceptions.RequestException as e:
        # Handle any errors that occur during the request
        print(f"An error occurred: {e}")
        return None

#sheet_data = get_google_sheet_data(spreadsheet_id,sheet_name,KEY)

#if sheet_data:
#    print("\nObtained sheet data")
#else:
#    print("\nFailed to fetch data from Google Sheets API.")

#shortlist filtering out non reach maps
#maps = list(sheet_data.values())[2]

#create shortlist
def make_reach(original):
    reach_maps = []
    for i in original:
    # print(i)
        if i[3] == "REACH" and "*" not in i[8]:
            reach_maps.append(i)
    return reach_maps

def update_maps(map_list):
  #reads reach_maps.json, edits content, rewrites back to file
  with open("reach_maps.json", "w") as f:
    json.dump(map_list, f)

#for i in sheet_data, if i[3] = REACH, add i to reach_maps
#store reach_maps locally in json
#pull maps from json in bot.py
#select random number from 0 - len(reach_maps)
#chosen = reach_maps[rand]
#send message in chat: chosen[1] by chosen[0] (chosen[2])

#reach_maps = make_reach(maps)
#update_maps(reach_maps)

#input("Press any key to continue...")
