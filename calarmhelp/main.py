import os
import logging
from dotenv import load_dotenv
from fastapi import FastAPI, status
from pydantic import BaseModel

from calarmhelp.services.calendarAlarmService import CalendarAlarmServicePipeline
from calarmhelp.services.googleCalendarService import GoogleCalendarServiceScript
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()


logging.basicConfig(
    format="%(levelname)s - %(name)s -  %(message)s", level=logging.WARNING
)
logging.getLogger("haystack").setLevel(logging.DEBUG)

app = FastAPI(docs_url="/")

origins = [os.environ["ORIGINS"]]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


class CreateAlarmRequest(BaseModel):
    input: str


@app.post("/create_alarm", status_code=status.HTTP_201_CREATED)
async def create_alarm(request: CreateAlarmRequest):
    """
    Endpoint to create an alarm.

    Args:
        user_input (CreateAlarmRequest): The input provided by the user.

    Returns:
        StreamingResponse: A streaming response with the alarm information in JSON format.
    """
    print("=====Calling Calendar Alarm Service\n")
    CalendarService = CalendarAlarmServicePipeline()
    calendar_service_response = CalendarService.run(input=request.input)

    print("=====Passing to Google Calendar Service\n")
    GoogleCalendarServiceScript(calendar_service_response)

    print("=====Returning from Google Calendar Service\n")
    return calendar_service_response.to_dict()
