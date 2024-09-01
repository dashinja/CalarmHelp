import os.path
import os
from typing import Any
from logging import Logger

from google.auth import default
from google.auth.exceptions import MutualTLSChannelError
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request


from calarmhelp.services.util.util import GoogleCalendarInfoInput

# Add the import statement for GoogleCalendarInfoInput

from google.oauth2 import service_account


from dotenv import load_dotenv

load_dotenv()

SCOPES = [
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/calendar",
]


def GoogleCalendarServiceScript(
    whole_user_input: GoogleCalendarInfoInput, logger: Logger
) -> dict[str, Any]:
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
            logger.info("Using Service Account")
            cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

            userServiceCredentials = (
                service_account.Credentials.from_service_account_file(
                    filename=cred_path, scopes=SCOPES
                )
            )

            if not userServiceCredentials.valid:
                logger.info("UserServiceCredentials not valid")
            if not userServiceCredentials or not userServiceCredentials.valid:
                # if userServiceCredentials and userServiceCredentials.expired:
                    logger.info("Credentials Expired")
                    logger.info("Refreshing Credentials")
                    request = Request()
                    
                    userServiceCredentials.refresh(request)
                    if userServiceCredentials.valid:
                        logger.info("Credentials now valid and refreshed")

            service = build(
                "calendar",
                "v3",
                credentials=userServiceCredentials,
                cache_discovery=False,
            )
        else:
            logger.info("Using Default Credentials")
            defaultCreds, _ = default()

            if not defaultCreds:
                logger.exception("defaultCreds not found")
                return {"error": "defaultCreds not found"}

            service = build("calendar", "v3", credentials=defaultCreds)

        if not service:
            logger.exception("google calendar service not created, find a better way")
            return {"error": "google calendar service not created, find a better way"}

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

        calendarIds = service.calendarList().list().execute()
        logger.info(f"Calendar List: {calendarIds}")

        logger.debug(f"Event Object: {myEvent}")
        logger.info("Creating Event")
        created_event = (
            service.events().insert(calendarId="primary", body=myEvent).execute()
        )

        if not created_event:
            logger.exception("Event Creation Failed")
            return {"error": "Event Creation Failed"}
        else:
            logger.info("Event Created")
            logger.debug(f"Event Object: {created_event}")
            return {"success": "Event Created"}
    except (HttpError, MutualTLSChannelError) as error:
        logger.exception(error)
        return {"error": str(error)}
