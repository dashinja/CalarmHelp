import os.path
import os
from typing import Any
from logging import Logger
import logging

from google.auth import default
from google.auth.exceptions import MutualTLSChannelError
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request


from calarmhelp.services.util.util import GoogleCalendarInfoInput


from google.oauth2 import service_account


from dotenv import load_dotenv

load_dotenv()

loggerIsCalendarFoundFunc = logging.getLogger("isCalendarFoundFunc")
calendar_id = os.getenv("CALENDAR_ID")

SCOPES = [
    "https://www.googleapis.com/auth/calendar",
]


def isCalendarFound(calendar_id: str | None, service):
    try:
        calendar = service.calendars().get(calendarId=calendar_id).execute()
        loggerIsCalendarFoundFunc.debug(f"Calendar found: {calendar['summary']}")
        return {"calendar": calendar, "found": True}
    except Exception as e:
        loggerIsCalendarFoundFunc.debug(f"Error accessing calendar: {e}")
        return {"calendar": None, "found": False}


def GoogleCalendarServiceScript(
    whole_user_input: GoogleCalendarInfoInput, logger: Logger
) -> dict[str, Any]:
    """
    Interacts with the Google Calendar API to create a new event on the user's calendar.

    Args:
        whole_user_input (GoogleCalendarInfoInput): The user input containing the event details.
        logger (Logger): The logger instance for logging information and errors.

    Returns:
        dict[str, Any]: A dictionary containing either a success message with the created event details or an error message if event creation failed.
    """
    user_input = whole_user_input.jsonResponse

    try:
        # see https://developers.google.com/calendar/api/v3/reference/events/insert

        if os.getenv("ENVIRONMENT") not in ["production", "docker"]:
            logger.debug("Using Service Account")
            cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

            userServiceCredentials = (
                service_account.Credentials.from_service_account_file(
                    filename=cred_path, scopes=SCOPES
                )
            )

            if not userServiceCredentials or not userServiceCredentials.valid:
                logger.debug("UserServiceCredentials Expired: Refreshing Credentials")
                request = Request()

                userServiceCredentials.refresh(request)

                if userServiceCredentials.valid:
                    logger.debug("Credentials now valid and refreshed")

            # Service created via Google Discovery API for Google Calendar
            service = build(
                "calendar",
                "v3",
                credentials=userServiceCredentials,
                cache_discovery=False,
            )

        else:
            logger.debug("Using Default Credentials")
            defaultCreds, _ = default()

            if not defaultCreds:
                return {"error": "defaultCreds not found"}

            service = build("calendar", "v3", credentials=defaultCreds)

        if not service:
            return {"error": "google calendar service not created, find a better way"}

        calendar_list = service.calendarList().list().execute()
        for calendar in calendar_list["items"]:
            logger.debug(f"Calendar Name: {calendar['summary']}")
            logger.debug(f"Calendar ID: {calendar['id']}\n\n")

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

        calendarIdList = service.calendarList().list().execute()
        logger.debug(f"Calendar List: {calendarIdList}\n")

        logger.debug(f"Event Object: {myEvent}\n")
        logger.debug("Creating Event")

        calendarFound = isCalendarFound(calendar_id=calendar_id, service=service)

        if calendarFound["found"]:
            created_event = (
                service.events().insert(calendarId=calendar_id, body=myEvent).execute()
            )
        else:
            return {"error": "Calendar not found"}

        if not created_event:
            return {"error": "Event Creation Failed"}
        else:
            logger.debug("Event Created")
            logger.debug(f"Created Event: {created_event}")
            return {"success": "Event Created"}
    except (HttpError, MutualTLSChannelError) as error:
        logger.exception(error)
        return {"error": str(error)}
