import os.path
import os

from google.auth.exceptions import MutualTLSChannelError
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials

from calarmhelp.services.util.util import GoogleCalendarInfoInput

from google.oauth2 import service_account

from dotenv import load_dotenv

load_dotenv()

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

    try:
        # see https://developers.google.com/calendar/api/v3/reference/events/insert

        if os.getenv("ENVIRONMENT") not in ["production", "docker"]:
            cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

            streetCred = service_account.Credentials.from_service_account_file(
                cred_path, scopes=SCOPES
            )

            service = build("calendar", "v3", credentials=streetCred)
        # service = build("calendar", "v3", credentials=defaultCreds)

        else:
            defaultCreds, project = default()
            service = build("calendar", "v3", credentials=) 
        if not service:
            raise Exception("google service not created")

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
    except (HttpError, MutualTLSChannelError) as error:
        if MutualTLSChannelError:
            raise Exception(error)
        if HttpError:
            raise Exception(error)
