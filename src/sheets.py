from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import os.path

# If modifying these scopes, delete the file token.json.
GOOGLE_API_SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

SPREADSHEET_ID = os.environ['SPREADSHEET_ID']
SPREADSHEET_RANGE = os.environ['SPREADSHEET_RANGE']

GOOGLE_API_CLIENT_SECRET_FILE = os.environ['GOOGLE_API_CLIENT_SECRET_FILE']
GOOGLE_API_CLIENT_TOKEN_FILE = os.environ['GOOGLE_API_CLIENT_TOKEN_FILE']


def read_sheet():
    """ Returns values from a spreadsheet.

    :return: result, http_error
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(GOOGLE_API_CLIENT_TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(GOOGLE_API_CLIENT_TOKEN_FILE, GOOGLE_API_SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(GOOGLE_API_CLIENT_SECRET_FILE, GOOGLE_API_SCOPES)
            creds = flow.run_local_server(port=8080)
        # Save the credentials for the next run
        with open(GOOGLE_API_CLIENT_TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                    range=SPREADSHEET_RANGE).execute()
        values = result.get('values', [])

        if not values:
            return {}, None

        res = {}
        # [1:] because we don't need Google Sheets header
        for row in values[1:]:
            # if row is empty, don't worry
            try:
                res[int(row[1])] = tuple(row)
            except IndexError:
                pass
    except HttpError as err:
        print(err)
        return {}, err

    return res, None
