import json
import pprint
from typing import Dict, Literal
import typing

from fastapi import FastAPI
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.concurrency import run_until_first_complete
from pydantic import BaseModel

from calarmhelp.services.calendarAlarmService import CalendarAlarmService
from calarmhelp.services.googleCalendarService import googleCalendarServiceScript
from calarmhelp.services.util.llmSetup import ChatBot, ChatBotStreamer
from calarmhelp.services.util.util import GoogleCalendarInfoInput
from fastapi.middleware.cors import CORSMiddleware

from langchain.schema import SystemMessage, ChatMessage, BaseMessage, AIMessage

import asyncio
from typing import Callable, Generator


app = FastAPI()
origins = ["*"]
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
    return {"message": "Hello World"}


@app.post("/")
async def post_root(user_input):
    return {user_input}


@app.post("/create_alarm")
async def create_alarm(user_input: CreateAlarmRequest):
    print("=====Calling Calendar Alarm Service=====\n\n")
    
    # stream = await ChatBotStreamer.ainvoke(input="AI Saying: Calling Calendar Alarm Service")
    # print("stream")
    # pprint.pprint(stream)
    
    # stream2 = ChatBotStreamer.astream(input="You are an AI Announcer - simply return the following announcement: 'Calling Calendar Alarm Service'")
    # print("stream2")
    # pprint.pprint(stream2)
    
    calendarService = CalendarAlarmService()
    calendarServiceResponse = await calendarService.create_alarm_json(user_input.input)

    # print("Parsing Calendar Alarm Service Response")
    # parsedCalendarServiceResponse = json.loads(calendarServiceResponse)  # type: ignore

    # **
    # print("=====CalendarServiceResponse Shown:::::::=====\n\n")
    # pprint.pprint(calendarServiceResponse)

    print("=====Passing to Google Calendar Service=====\n\n")

    # googleCalendarInput = GoogleCalendarInfoInput(
    #     response=calendarServiceResponse.response,
    #     json=calendarServiceResponse.json
    # )

    # endgame = googleCalendarServiceScript(googleCalendarInput)
    # intermediate = GoogleCalendarInfoInput(calendarServiceResponse)
    endgame = googleCalendarServiceScript(calendarServiceResponse)

    response = calendarServiceResponse
    
    print("=====Returning from Google Calendar Service=====\n\n")
    
    # print("response before done")
    # pprint.pprint(response)
    
    response = json.dumps(response.json())
    
    return StreamingResponse(
        content = response,  # Use the appropriate content from the GoogleCalendarInfoInput object
        status_code=200,
        media_type="application/json",
        
    )
    # return response