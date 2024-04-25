import json
import os.path
import pprint

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from pydantic.v1 import BaseModel
from pydantic import Field

from calarmhelp.services.calendarAlarmService import CalendarAlarmResponse
from calarmhelp.services.util.util import GoogleCalendarInfoInput


# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly", "https://www.googleapis.com/auth/calendar"]


def googleCalendarServiceScript(whole_user_input: GoogleCalendarInfoInput):
    user_input = whole_user_input.jsonResponse
    # For google credentials - this is the ONLY thing that worked: https://developers.google.com/calendar/api/quickstart/python
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
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
        # see https://developers.google.com/calendar/api/v3/reference/events/insert
        service = build("calendar", "v3", credentials=creds)

        print("user_input.json")
        pprint.pprint(user_input)

        myEvent = {
            'summary': whole_user_input.response,
            'location': user_input.location,
            'start': {
                'dateTime': user_input.event_time.isoformat(),
                'timeZone': 'America/New_York'
            },
            'end': {
                'dateTime': user_input.event_time_end.isoformat(),
                'timeZone': 'America/New_York'
            },

        }

        print("The value you want to see user_input")
        pprint.pprint(user_input)

        # quick_created_event = service.events().quickadd(calendarid='primary', text=whole_user_input.response).execute()
        # if not quick_created_event:
        #     print("event creation failed")
        #     return
        # else:
        #     return quick_created_event['summary']
        
        print("myEvent: ")
        pprint.pprint(myEvent)

        created_event = service.events().insert(calendarId='primary', body=myEvent).execute()
        if not created_event:
            print("Event Creation Failed")
            return
        else:
            return created_event['summary']
        #
    except HttpError as error:
        print(f"An error occurred: {error}")
