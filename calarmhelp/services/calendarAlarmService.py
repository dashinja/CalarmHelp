import json
import pprint
from typing import Dict, Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, FewShotChatMessagePromptTemplate


from dotenv import load_dotenv
from pydantic.v1 import BaseModel, Field

from enum import Enum
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain.tools import StructuredTool
from datetime import datetime
from langchain.output_parsers.openai_tools import JsonOutputKeyToolsParser
from langchain.evaluation import JsonSchemaEvaluator

from calarmhelp.services.util.constants import Examples, CalarmHelpPromptTemplate
from calarmhelp.services.util.llmSetup import ChatBotStreamer as llm
from calarmhelp.services.util.util import CalendarAlarmResponse, Category, GoogleCalendarInfoInput

parser = JsonOutputKeyToolsParser(key_name="observation")
evaluator = JsonSchemaEvaluator()

calendar_alarm_service_system_prompt = [("system", CalarmHelpPromptTemplate),
                MessagesPlaceholder("agent_scratchpad")
                ]

calendar_alarm_service_example_prompt = ChatPromptTemplate.from_messages(
    [
        ("human", "{input}"),
        ("ai", "{output}")
    ]
)

calendar_alarm_service_few_shot_prompt = FewShotChatMessagePromptTemplate(
    example_prompt=calendar_alarm_service_example_prompt,
    examples=Examples 
)

calendar_alarm_service_final_prompt = ChatPromptTemplate.from_messages([
    *calendar_alarm_service_system_prompt,
    calendar_alarm_service_few_shot_prompt,
])

def create_alarm_readout(input):
    """Provides the 'description' field for google calendar"""

    input = CalendarAlarmResponse(**input)
    
    month = input.event_time.strftime('%B')
    day_number = input.event_time.strftime('%d')
    day_of_week = input.event_time.strftime('%A')
    time_of_day = input.event_time.strftime('%I:%M %p')
    locationCondition = f"{(' at ' + input.location) if input.location else ''}"

    # Take care with format. Everything, even spacing - is intentional.
    return f"{input.name} @ {time_of_day}{locationCondition} on {day_of_week} {month} {day_number} #{input.category.name.lower()} [{input.lead_time}m]"


class CalendarAlarmService:
    """docstring for ClassName."""

    def __init__(self):
        super(CalendarAlarmService, self).__init__()
        print("INITIALIZED")

    async def create_alarm_json(self, user_input: str) -> GoogleCalendarInfoInput:
        input = {
            "user_input": user_input,
            "current_time": datetime.now().isoformat()
        }



        create_calendar_readout_structured_tool = StructuredTool.from_function(
            func=create_alarm_readout,
            name="CreateCalendarReadoutTool",
            description="This tool should be called with the JSON object that contains the alarm information. It will return a string that describes the alarm in a format that Google Calendar can understand.",
        )

        tools = [create_calendar_readout_structured_tool]

        agent = create_openai_tools_agent(llm, tools, calendar_alarm_service_final_prompt)

        agent_executer = AgentExecutor(agent=agent, tools=tools, verbose=True, return_intermediate_steps=True, max_execution_time=15.0, max_iterations=5)  # type: ignore

        async def getResponseAndValidate(input):
            global evaluationCount
            evaluationCount = 0
            response = await agent_executer.ainvoke(input)
            
            print("RESPONSE::::::")
            pprint.pprint(response['output'])
            
            parsedOutput = json.loads(response['output'])
            # print("PARSED OUTPUT::::::")
            # pprint.pprint(parsedOutput)

            saved_schema = {'theJson': {'name': 'string', 'category': 'string', 'lead_time': 'integer', 'event_time': 'string', 'event_time_end': 'string', 'creation_time': 'string', 'location': 'string', 'error': "string"}, 'response': 'string'}
            
            saved_schema_double_quote = {"theJson": {"name": "string", "category": "string", "lead_time": "integer", "event_time": "string", "event_time_end": "string", "creation_time": "string", "location": "string", "error": "string"}, "response": "string"}

            # print("SAVED SCHEMA::::::")
            # pprint.pprint(json.loads(saved_schema))
            # pprint.pprint(saved_schema)

            # examenResponse: Dict[str, bool] = evaluator.evaluate_strings(
            #     prediction=parsedOutput, reference=json.dumps(saved_schema_double_quote))
            
            examenResponse: Dict[str, bool] = evaluator.evaluate_strings(
                prediction=parsedOutput, reference=agent_executer.get_output_schema().schema_json())

            # print("examenResponse: ")
            # pprint.pprint(examenResponse)
            
            if examenResponse['score'] is False and evaluationCount <= 3:
                evaluationCount += 1
                print("examenResponse after it was false: ")
                pprint.pprint(examenResponse)
                return getResponseAndValidate(input)
            


            elif evaluationCount > 3:
                return GoogleCalendarInfoInput(
                    response = "",
                    theJson = CalendarAlarmResponse(
                    error=True,
                    # create empty responses for the remaining fields
                    name="",
                    category=Category.ALWAYS,
                    lead_time=0,
                    event_time=datetime.now(),
                    event_time_end=datetime.now(),
                    location="",
                    current_time=datetime.now(),
                    response=response['output']
                ))
            else:
                # print("before attempt to coerse into GoogleCalendarInfoInput")
                # pprint.pprint(response)

                output = json.loads(json.dumps(response['output']))
                # output = json.dumps(response['output'])

                # **
                # print("the output is:")
                # pprint.pprint(output)

                # print("parse output['json']")
                # pprint.pprint(json.dumps(output['json']))

                # testOutput = json.loads(output['json'])

                # testOutput = json.loads(output)
                # print("testOutput")
                # print("typeof testOutput: ", type(testOutput))
                # pprint.pprint(testOutput)

                theJson = json.loads(output)
                # **
                # print("theJson")
                # pprint.pprint(theJson)


                parsedOutputResponseValue = json.loads(output)
                responseValue = GoogleCalendarInfoInput(
                    response = parsedOutputResponseValue['response'],
                    theJson = parsedOutputResponseValue['json']
                )
                return responseValue

        # print("input")
        # pprint.pprint(input)

        final = await getResponseAndValidate(input)
        return final
