from datetime import datetime, timedelta
import os.path

from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from calarmhelp.services.util.util import GoogleCalendarInfoInput


# If modifying these scopes, delete the file token.json.
SCOPES = [
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/calendar",
]


def GoogleCalendarServiceScript(whole_user_input: GoogleCalendarInfoInput):
    """
    This function interacts with the Google Calendar API to create a new event on the user's calendar.

    Args:
        whole_user_input (GoogleCalendarInfoInput): The user input containing the event details.

    Returns:
        str: The summary of the created event, or None if event creation failed.
    """
    user_input = whole_user_input.jsonResponse

    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except RefreshError:
                creds = None
        if not creds:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open("token.json", "w") as token:
                token.write(creds.to_json())

    try:
        # see https://developers.google.com/calendar/api/v3/reference/events/insert
        service = build("calendar", "v3", credentials=creds)

        myEvent = {
            "summary": whole_user_input.response,
            "location": user_input.location,
            "start": {
                "dateTime": user_input.event_time.isoformat(),
                "timeZone": "America/New_York",
            },
            "end": {
                "dateTime": user_input.event_time_end.isoformat(),
                "timeZone": "America/New_York",
            },
        }

        created_event = (
            service.events().insert(calendarId="primary", body=myEvent).execute()
        )
        if not created_event:
            print("====Event Creation Failed")
            return
        else:
            return created_event["summary"]
    except HttpError as error:
        print(f"====An error occurred: {error}")
