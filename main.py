import json

from fastapi import FastAPI
from pydantic import BaseModel

from calarmhelp.services.calendarAlarmService import CalendarAlarmService
from calarmhelp.services.googleCalendarService import googleCalendarServiceScript

app = FastAPI()


class CreateAlarmRequest(BaseModel):
    input: str


@app.post("/create_alarm/")
async def create_alarm(user_input: CreateAlarmRequest):
    print("Calling Calendar Alarm Service")
    calendarService = CalendarAlarmService()
    calendarServiceResponse = calendarService.create_alarm_json(user_input.input)

    print("Parsing Calendar Alarm Service Response")
    parsedCalendarServiceResponse = json.loads(calendarServiceResponse) # type: ignore

    print("Passing to Google Calendar Service")
    endgame = googleCalendarServiceScript(parsedCalendarServiceResponse)

    response = calendarServiceResponse

    print("Returning from Google Calendar Service")
    return response