import json
import pprint
from typing import Dict

from fastapi import FastAPI
from pydantic import BaseModel

from calarmhelp.services.calendarAlarmService import CalendarAlarmService
from calarmhelp.services.googleCalendarService import googleCalendarServiceScript
from calarmhelp.services.util.util import GoogleCalendarInfoInput

app = FastAPI()


class CreateAlarmRequest(BaseModel):
    input: str

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/")
async def post_root(user_input):
    return {user_input}

@app.post("/create_alarm/")
async def create_alarm(user_input: CreateAlarmRequest):
    print("Calling Calendar Alarm Service")
    calendarService = CalendarAlarmService()
    calendarServiceResponse = calendarService.create_alarm_json(user_input.input)

    print("Parsing Calendar Alarm Service Response")
    # parsedCalendarServiceResponse = json.loads(calendarServiceResponse)  # type: ignore

    print("CalendarServiceResponse Shown:::::::")
    pprint.pprint(calendarServiceResponse)

    print("Passing to Google Calendar Service")

    # googleCalendarInput = GoogleCalendarInfoInput(
    #     response=calendarServiceResponse.response,
    #     json=calendarServiceResponse.json
    # )

    # endgame = googleCalendarServiceScript(googleCalendarInput)
    # intermediate = GoogleCalendarInfoInput(calendarServiceResponse)
    endgame = googleCalendarServiceScript(calendarServiceResponse)

    response = calendarServiceResponse

    print("Returning from Google Calendar Service")
    return response
