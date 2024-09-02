import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware

from calarmhelp.services.calendarAlarmService import CalendarAlarmServicePipeline
from calarmhelp.services.googleCalendarService import GoogleCalendarServiceScript
from calarmhelp.services.util.util import CreateAlarmRequest

load_dotenv()

if os.getenv("ENVIRONMENT") in ["production", "docker"]:
    logging.basicConfig(
        format="%(levelname)s - %(name)s: %(message)s", level=logging.DEBUG
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
async def create_alarm(request: CreateAlarmRequest):
    """
    Endpoint to create an alarm.

    Args:
        user_input (CreateAlarmRequest): The input provided by the user.

    Returns:
        StreamingResponse: A streaming response with the alarm information in JSON format.
    """
    loggerGoogleCalendarService.info("Calling Calendar Alarm Service")

    CalendarService = CalendarAlarmServicePipeline(max_loops_allowed=40)
    calendar_service_response = CalendarService.run(input=request.input)

    loggerGoogleCalendarService.info("Passing to Google Calendar Service")
    GoogleCalendarServiceScript(calendar_service_response, loggerGoogleCalendarService)

    loggerGoogleCalendarService.info("Returning from Google Calendar Service")
    return calendar_service_response.to_dict()
