import json
from typing import Dict
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from dotenv import load_dotenv
from pydantic.v1 import BaseModel, Field

from enum import Enum
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain.tools import StructuredTool
from datetime import datetime
from langchain.output_parsers.openai_tools import JsonOutputKeyToolsParser
from langchain.evaluation import JsonSchemaEvaluator


load_dotenv()


class Category(Enum):
    ALWAYS = "always"
    WORK = "work"
    HOME = "home"


llm = ChatOpenAI(model='gpt-4-turbo', model_kwargs={
    "response_format": {"type": "json_object"}}, temperature=0)

parser = JsonOutputKeyToolsParser(key_name="observation")
evaluator = JsonSchemaEvaluator()


class CalendarAlarmFinalResponse(BaseModel):
    displayText: str = Field(description="The final response to be displayed to the user")


class CalendarAlarmResponse(BaseModel):
    name: str = Field(description="Name of the event")
    category: Category = Field(description="Category of the event")
    lead_time: int = Field(description="How long before the event I should be reminded")
    event_time: datetime = Field(description="When the event should actually happen")
    event_time_end: datetime = Field(description="When the event should actually end")
    location: str = Field(description="Location of event, if provided")
    error: bool = Field(default=False, description="If there was an error in the input")


def create_alarm_readout(alarm_json: CalendarAlarmResponse):
    """Provides the 'description' field for google calendar"""

    month = alarm_json.event_time.strftime('%B')
    day_number = alarm_json.event_time.strftime('%d')
    day_of_week = alarm_json.event_time.strftime('%A')
    time_of_day = alarm_json.event_time.strftime('%I:%M %p')
    locationCondition = f"{(' at ' + alarm_json.location) if alarm_json.location else ''}"

    # Take care with format. Everything, even spacing - is intentional.
    return f"{alarm_json.name} @ {time_of_day}{locationCondition} on {day_of_week} {month} {day_number} #{alarm_json.category.name.lower()} [{alarm_json.lead_time}m]"


class CalendarAlarmService:
    """docstring for ClassName."""

    def __init__(self):
        super(CalendarAlarmService, self).__init__()
        print("INITIALIZED")

    def create_alarm_json(self, user_input: str):

        input = {
            "user_input": user_input,
            "current_time": datetime.now().isoformat()
        }

        systemPrompt = [("system", """From the user_input you will extract the name (string) of the event, the category of one of the types "always | work | home" for the event (if category is unclear, default to "always"), lead_time (number) which is how long before the event I should be reminded, event_time (datetime) is when the event should actually happen, 'event_time_end' (if not specified, always has the value of half an hour after the event_time), and creation_time of the call to the llm (currentDateTime), and location (as a string, only if clearly provided. Most of the time this should be an empty string. Location callouts are rare.), and an 'error' (boolean, only ever true if llm fails). Your JSON response will only have the fields 'name', 'category', 'lead_time' (always expressed in terms of minutes. So 3 hours = 180 for example), event_time_end, event_time', 'creation_time' (datetime object), 'location', and 'error'. Always use double quotes for keys and values in the JSON object you create.
                        {user_input}
                        {current_time}
                        Finally, run the output through the tool attached to the agent to get the final response in a field called response. ALWAYS use the tool.
                        Return a json object that has a field for the final response, as well as a field for the json."""),
                        MessagesPlaceholder("agent_scratchpad")
                        ]

        prompt = ChatPromptTemplate.from_messages(systemPrompt)

        createCalendarReadout = StructuredTool.from_function(
            create_alarm_readout
        )

        tools = [createCalendarReadout]

        agent = create_openai_tools_agent(llm, tools, prompt)

        agent_executer = AgentExecutor(agent=agent, tools=tools, verbose=True, return_intermediate_steps=False, )  # type: ignore

        def getResponseAndValidate(input):
            global evaluationCount; evaluationCount = 0
            response = agent_executer.invoke(input)

            parsedOutput = json.loads(response['output'])

            saved_schema = json.dumps({'json': {'name': 'Tell her I love her', 'category': 'always', 'lead_time': 120, 'event_time': '2024-04-25T08:00:00', 'event_time_end': '2024-04-25T08:30:00', 'creation_time': '2024-04-20T20:22:19.290603', 'location': 'Disney World', 'error': "false"}, 'response': 'Tell her I love her @ 08:00 AM at Disney World on Thursday April 25 #always [120m]'})
                  
            examenResponse: Dict[str, bool] = evaluator.evaluate_strings(
                prediction=parsedOutput, reference=saved_schema)

            if examenResponse['score'] is True:
                return response
            elif evaluationCount < 3:
                evaluationCount += 1
                return getResponseAndValidate(input)
            else:
                return CalendarAlarmResponse(
                    error=True,
                    # create empty responses for the remaining fields
                    name="",
                    category=Category.ALWAYS,
                    lead_time=0,
                    event_time=datetime.now(),
                    event_time_end=datetime.now(),
                    location="",
                )

        return getResponseAndValidate(input)
