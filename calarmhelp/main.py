import logging
import os
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware

from calarmhelp.services.calendarAlarmService import CalendarAlarmServicePipeline
from calarmhelp.services.googleCalendarService import GoogleCalendarServiceScript
from calarmhelp.services.util.util import CreateAlarmRequest, GoogleCalendarInfoInput, GoogleCalendarResponse

load_dotenv()

if os.getenv("ENVIRONMENT") in ["production", "docker"]:
    logging.basicConfig(
        format="%(levelname)s - %(name)s: %(message)s", level=logging.INFO
    )

loggerGoogleCalendarService = logging.getLogger("Google Calendar Service")

app = FastAPI(docs_url="/")

origins = [os.environ["ORIGINS"]]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.post("/create_alarm", status_code=status.HTTP_201_CREATED)
async def create_alarm(request: CreateAlarmRequest) -> dict[str, Any]:
    """
    Endpoint to create an alarm.

    Args:
        user_input (CreateAlarmRequest): The input provided by the user.

    Returns:
        StreamingResponse: A streaming response with the alarm information in JSON format.
    """
    loggerGoogleCalendarService.info("Calling Calendar Alarm Service")

    CalendarService = CalendarAlarmServicePipeline(max_loops_allowed=10)
    calendar_service_response = CalendarService.run(input=request.input)

    if isinstance(calendar_service_response, GoogleCalendarResponse):
        loggerGoogleCalendarService.info("Error in Calendar Alarm Service response")
        return calendar_service_response.to_dict()
    
    loggerGoogleCalendarService.info("Passing to Google Calendar Service")
    google_calender_service_response = GoogleCalendarServiceScript(calendar_service_response, loggerGoogleCalendarService)

    if google_calender_service_response["error"]:
        loggerGoogleCalendarService.info("Error in Google Calendar Service response")
        return google_calender_service_response.to_dict()
    
    loggerGoogleCalendarService.info("Pipeline Complete")
    return calendar_service_response.to_dict()
