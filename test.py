import pandas as pd

def google_sheet_to_df(sheet_url):
    # Extract the file ID and gid
    import re
    match = re.search(r'/d/([a-zA-Z0-9-_]+)', sheet_url)
    gid_match = re.search(r'gid=([0-9]+)', sheet_url)
    if not match:
        raise ValueError("Invalid Google Sheet URL")
    file_id = match.group(1)
    gid = gid_match.group(1) if gid_match else '0'
    export_url = f"https://docs.google.com/spreadsheets/d/{file_id}/export?format=csv&gid={gid}"
    return pd.read_csv(export_url)

# Usage
sheet_url = "https://docs.google.com/spreadsheets/d/14phNqQD4Q_5WUY8Eyu3ccWfGHan---nU9tZPzqpkT10/edit?gid=0#gid=0"
df = google_sheet_to_df(sheet_url)
print(df.head())