import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from calarmhelp.services.calendarAlarmService import CalendarAlarmService
from calarmhelp.services.googleCalendarService import GoogleCalendarServiceScript
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI()
origins = [os.environ['ORIGINS']]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


class CreateAlarmRequest(BaseModel):
    input: str


@app.get("/")
async def root():
    """
    Root endpoint of the API.

    Returns:
        dict: A dictionary with a welcome message.
    """
    return {"message": "Welcome to CalarmHelp"}


@app.post("/")
async def post_root(user_input):
    """
    Endpoint to echo the user input.

    Args:
        user_input: The input provided by the user.

    Returns:
        dict: A dictionary with the echoed input.
    """
    return {"echo": user_input}


@app.post("/create_alarm")
async def create_alarm(user_input: CreateAlarmRequest):
    """
    Endpoint to create an alarm.

    Args:
        user_input (CreateAlarmRequest): The input provided by the user.

    Returns:
        StreamingResponse: A streaming response with the alarm information in JSON format.
    """
    print("=====Calling Calendar Alarm Service\n")
    CalendarService = CalendarAlarmService()
    calendar_service_response = await CalendarService.create_alarm_json(user_input.input)

    print("=====Passing to Google Calendar Service\n")
    GoogleCalendarServiceScript(calendar_service_response)

    print("=====Returning from Google Calendar Service\n")
    return StreamingResponse(
        content=calendar_service_response.to_dict(),
        status_code=201,
        media_type="application/json",
    )
