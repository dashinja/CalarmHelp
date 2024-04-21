import json
import os
from calarmhelp.services.calendarAlarmService import CalendarAlarmService
from fastapi import FastAPI
from pydantic import BaseModel

from calarmhelp.services.googleCalendarService import googleCalendarServiceScript

cwd = os.getcwd()
print(cwd)

app = FastAPI()


class CreateAlarmRequest(BaseModel):
    input: str


@app.post("/create_alarm/")
async def create_alarm(user_input: CreateAlarmRequest):
    calendarService = CalendarAlarmService()
    calendarServiceResponse = calendarService.create_alarm_json(user_input.input)

    print("Passing to Google Calendar Service")
    googleCalendarService = googleCalendarServiceScript(calendarServiceResponse)

    return googleCalendarService
