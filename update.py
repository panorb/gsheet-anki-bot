import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import datetime
import iso8601
import rfc3339
import pytz

import random
import anki

import telegram

import data
con = data.get_db()

def fill_zeros(array):
    non_zero_indices = [i for i, num in enumerate(array) if num != 0]

    for i in range(len(non_zero_indices) - 1):
        start_index = non_zero_indices[i]
        end_index = non_zero_indices[i + 1]
        num_zeros = end_index - start_index - 1

        if num_zeros > 0:
            if num_zeros == 1:
                array[start_index + 1] = (array[start_index] + array[end_index]) // 2
            else:
                step = (array[end_index] - array[start_index]) / (num_zeros + 1)
                for j in range(1, num_zeros + 1):
                    array[start_index + j] = int(array[start_index] + j * step)
    
    # If there is no non-zero indice we do not need to handle it
    if not non_zero_indices:
        return array

    first_index = non_zero_indices[0]
    if (first_index > 0):
        for i in range(first_index-1, -1, -1):
            array[i] = array[i+1] - random.randint(4480, 4520)

    last_index = non_zero_indices[-1]
    if (last_index < len(array) - 1):
        for i in range(last_index + 1, len(array)):
            array[i] = array[i-1] + random.randint(4480, 4520)

    return array

SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive.metadata.readonly"]
SPREADSHEET_ID = data.spreadsheet_id

def fix_ids(sheet, sheet_name, values):
    ids = []

    for row in values[1:]:
        if len(row) > 0:
            if row[0].isdigit():
                ids.append(int(row[0]))
            else:
                ids.append(0)
    
    zero_indices = [i for i, num in enumerate(ids) if num == 0]

    if zero_indices: 
        print(f"{sheet_name} has zero-indices. Fixing...")
        ids = fill_zeros(ids)
        ids.insert(0, "Id")

        newValues = []

        for y in range(len(ids)):
            newValues.append([ ids[y] ]) # Prepare query to update remote sheet
            values[y][0] = ids[y] # Update in local copy, so that we don't have to query again

        result = (
            sheet.values()
            .update(spreadsheetId=SPREADSHEET_ID,
                    range=f"{sheet_name}!A:A",
                    valueInputOption="RAW",
                    body={'values': newValues})
            .execute()
        )

    return values

def get_values(service, sheet_name):
    # Call the Sheets API
    sheet = service.spreadsheets()

    result = (
            sheet.values()
            .get(spreadsheetId=SPREADSHEET_ID, range=sheet_name)
            .execute()
        )

    values = result.get("values", [])
    values = fix_ids(sheet, sheet_name, values)

    return values

def get_state_hash(deck_id):
    cur = con.cursor()
    cur.execute("SELECT state_sheet_hash FROM decks WHERE id = ?", (deck_id,))
    return cur.fetchone().state_sheet_hash

import hashlib

def get_sheet_hash(values):
    content = ""

    for row in values:
        for cell in row:
            content += str(cell)

    return hashlib.sha256(content.encode("utf-8")).hexdigest()

def main():
  cur = con.cursor()
  cur.execute("CREATE TABLE IF NOT EXISTS meta (`key` TEXT NOT NULL, `value` TEXT NOT NULL, PRIMARY KEY (`key`))")
    
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  try:
    service = build("drive", "v3", credentials=creds) # Please use your authorization script here.
    res = service.files().get(fileId=SPREADSHEET_ID, fields="modifiedTime").execute()
    modified_time = iso8601.parse_date(res['modifiedTime'])

    state_date = pytz.UTC.localize(datetime.datetime.min)
    cur.execute("SELECT value FROM meta WHERE key = ?", ("state_time",))
    state_date_stamp = cur.fetchone()

    if state_date_stamp:
        state_date = iso8601.parse_date(state_date_stamp.value)
    
    if modified_time <= state_date:
        print("Es gab seit der letzten Ausführung keine Änderungen mehr.")
        return

    service = build("sheets", "v4", credentials=creds)
    changed_decks = []

    for deck in data.get_available_decks():
        print(f"Behandle {deck.anki_name}...")
        values = get_values(service, deck.sheet_name)
        state_hash = get_state_hash(deck.id)
        current_hash = get_sheet_hash(values)

        #  id, deck_type, internal_name, sheet_name, anki_name, state_sheet_hash
        if current_hash == state_hash:
            print("Hash hat sich nicht geändert. Überspringe...")
            continue

        if deck.deck_type == "vocab":
            anki.create_vocab_deck(deck.anki_name, values) 
        elif deck.deck_type == "hanzi":
            anki.create_hanzi_deck(deck.anki_name, values)
        
        cur.execute("UPDATE decks SET state_sheet_hash = ? WHERE id = ?", (current_hash, deck.id))
        con.commit()

        changed_decks.append(deck)

    telegram.send_update_message(changed_decks)

    now = datetime.datetime.now(datetime.timezone.utc)
    rfc_time = rfc3339.rfc3339(now)
    cur.execute("INSERT INTO meta (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = ?", ("state_time", rfc_time, rfc_time))
    con.commit()
  except HttpError as err:
    print(err)


if __name__ == "__main__":
  main()
