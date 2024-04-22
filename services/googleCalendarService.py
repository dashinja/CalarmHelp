import json
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from services.calendarAlarmService import CalendarAlarmResponse
from pydantic.v1 import BaseModel
from pydantic import Field


class GoogleCalendarInfoInput(BaseModel):
    response: str
    jsonResponse: CalendarAlarmResponse = Field(alias="json")


# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly", "https://www.googleapis.com/auth/calendar"]


def googleCalendarServiceScript(user_input):
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

        myEvent = {
            'summary': user_input['response'],
            'location': user_input['json']['location'],
            'start': {
                'dateTime': user_input['json']['event_time'],
                'timeZone': 'America/New_York'
            },
            'end': {
                'dateTime': user_input['json']['event_time_end'],
                'timeZone': 'America/New_York'
            },

        }

        created_event = service.events().insert(calendarId='primary', body=myEvent).execute()

        if not created_event:
            print("Event Creation Failed")
            return
        else:
            return {"new_event_created": created_event['summary']}

    except HttpError as error:
        print(f"An error occurred: {error}")
