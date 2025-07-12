# Add your utilities or helper functions to this file.

import os
import pandas as pd
import re
from dotenv import load_dotenv, find_dotenv

# these expect to find a .env file at the directory above the lesson.                                                                                                                     # the format for that file is (without the comment)                                                                                                                                       #API_KEYNAME=AStringThatIsTheLongAPIKeyFromSomeService                                                                                                                                     
def load_env():
    _ = load_dotenv(find_dotenv())

def get_openai_api_key():
    load_env()
    openai_api_key = os.getenv("OPENAI_API_KEY")
    return openai_api_key


def google_sheet_to_df(sheet_url):
    # Extract the file ID and gid
    
    match = re.search(r'/d/([a-zA-Z0-9-_]+)', sheet_url)
    gid_match = re.search(r'gid=([0-9]+)', sheet_url)
    if not match:
        raise ValueError("Invalid Google Sheet URL")
    file_id = match.group(1)
    gid = gid_match.group(1) if gid_match else '0'
    export_url = f"https://docs.google.com/spreadsheets/d/{file_id}/export?format=csv&gid={gid}"
    df = pd.read_csv(export_url)
    df.to_csv('./sheet_dump/temp.csv', index=False)
    
# Usage
sheet_url = "https://docs.google.com/spreadsheets/d/14phNqQD4Q_5WUY8Eyu3ccWfGHan---nU9tZPzqpkT10/edit?gid=0#gid=0"