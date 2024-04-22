import json

from fastapi import FastAPI
from pydantic import BaseModel

from services.googleCalendarService import googleCalendarServiceScript
from services.calendarAlarmService import CalendarAlarmService


app = FastAPI()


class CreateAlarmRequest(BaseModel):
    input: str


@app.post("/create_alarm/")
async def create_alarm(user_input: CreateAlarmRequest):
    print("Calling Calendar Alarm Service")
    calendarService = CalendarAlarmService()
    calendarServiceResponse = calendarService.create_alarm_json(user_input.input)

    print("Parsing Calendar Alarm Service Response")
    parsedCalendarServiceResponse = json.loads(calendarServiceResponse)

    print("Passing to Google Calendar Service")
    endgame = googleCalendarServiceScript(parsedCalendarServiceResponse)

    print("Returning from Google Calendar Service")
    return endgame
