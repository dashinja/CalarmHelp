import os
from calarmhelp.services.calendarAlarmService import CalendarAlarmService
from fastapi import FastAPI
from pydantic import BaseModel

cwd = os.getcwd()
print(cwd)

app = FastAPI()


class CreateAlarmRequest(BaseModel):
    input: str


@app.post("/create_alarm/")
async def create_alarm(user_input: CreateAlarmRequest):
    service = CalendarAlarmService()
    return service.create_alarm_json(user_input)
