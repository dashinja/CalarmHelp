import json
import os
import pprint
from typing import Dict
from haystack import Pipeline
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, FewShotChatMessagePromptTemplate

from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain.tools import StructuredTool
from datetime import datetime
from langchain.output_parsers.openai_tools import JsonOutputKeyToolsParser
from langchain.evaluation import JsonSchemaEvaluator

from calarmhelp.services.util.constants import Examples, CalarmHelpPromptTemplate
from calarmhelp.services.util.llmSetup import ChatBotStreamer as llm
from calarmhelp.services.util.util import CalendarAlarmResponse, Category, GoogleCalendarInfoInput

from haystack.core.component import component
from haystack.components.generators import OpenAIGenerator
from haystack.components.builders import PromptBuilder
from jinja2 import Environment, FileSystemLoader

from ..templates.googleCalendarFeeder import google_calendar_feeder

template_dir = os.path.join(os.path.dirname(__file__), '../templates')
env = Environment(loader=FileSystemLoader(template_dir))
template = env.get_template('googleCalendarFeeder.jinja')


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
    """Provides the 'description' field for google calendar

    Args:
        input (dict): The input dictionary containing alarm information.

    Returns:
        str: A string that describes the alarm in a format that Google Calendar can understand.
    """

    input = CalendarAlarmResponse(**input)

    month = input.event_time.strftime('%B')
    day_number = input.event_time.strftime('%d')
    day_of_week = input.event_time.strftime('%A')
    time_of_day = input.event_time.strftime('%I:%M %p')
    locationCondition = f"{(' at ' + input.location) if input.location else ''}"

    # Take care with format. Everything, even spacing - is intentional.
    return f"{input.name} @ {time_of_day}{locationCondition} on {day_of_week} {month} {day_number} #{input.category.name.lower()} [{input.lead_time}m]"

@component
class JSONValidator:
    @component.output_types(properties_to_validate=list[str], json=str)
    def run(self, properties: list[str]):
        if 'DONE' in properties[0]:
            return {"json": properties[0].replace('Done', '')}
        else:
            return {"properties_to_validate": properties[0]}
        
@component
class CalendarAlarmServiceHaystack:

    def __init__(self):
        self.generator = OpenAIGenerator()
        self.pipeline = Pipeline()
        
        
    @component.output_types(output=GoogleCalendarInfoInput)
    def run(self, input: str) -> GoogleCalendarInfoInput:
        modified_input = {
            "user_input": input,
            "current_time": datetime.now().isoformat()
        }
    
        # rendered_template = template.render(input=modified_input)
        # print("rendered_template: ", rendered_template)
        prompt_builder = PromptBuilder(template=google_calendar_feeder)
        generator = OpenAIGenerator()
        json_validator = JSONValidator()
        
        self.pipeline.add_component("prompt_builder", prompt_builder)
        self.pipeline.add_component("generator", generator)
        self.pipeline.add_component("validator", json_validator)

        self.pipeline.connect("prompt_builder.prompt", "generator.prompt")
        self.pipeline.connect("generator.replies", "validator.properties")
        self.pipeline.connect("validator.properties_to_validate", "prompt_builder.properties_to_validate")

        results = self.pipeline.run(data={
            "prompt_builder": {"input": modified_input},
        })

        jsonOutput = results['validator']['json'].replace('DONE', '')

        # print("results: ", results['generator']['validator']['json'])
        print("jsonOutPut: ", jsonOutput)
        
        realJson = json.loads(jsonOutput)
        
        print("realJson: ", realJson)
        return GoogleCalendarInfoInput(
            response = create_alarm_readout(realJson),
            theJson = CalendarAlarmResponse.validate(realJson)
        )
        


class CalendarAlarmService:
    """A service class for creating calendar alarms."""

    def __init__(self):
        super(CalendarAlarmService, self).__init__()
        print("=====Calendar Alarm Service Initialized")

    async def create_alarm_json(self, user_input: str) -> GoogleCalendarInfoInput:
        """Creates a calendar alarm in JSON format.

        Args:
            user_input (str): The user input for creating the alarm.

        Returns:
            GoogleCalendarInfoInput: The response containing the alarm information in JSON format.
        """

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

        agent_executer = AgentExecutor(agent=agent, tools=tools, verbose=True, return_intermediate_steps=True, max_execution_time=30.0, max_iterations=15)  # type: ignore

        async def getResponseAndValidate(input):
            global evaluationCount
            evaluationCount = 0
            response = await agent_executer.ainvoke(input)

            parsedOutput = json.loads(response['output'])
            examenResponse: Dict[str, bool] = evaluator.evaluate_strings(
                prediction=parsedOutput, reference=agent_executer.get_output_schema().schema_json())

            if examenResponse['score'] is False and evaluationCount <= 3:
                evaluationCount += 1
                pprint.pprint(examenResponse)
                return getResponseAndValidate(input)

            elif evaluationCount > 3:
                return GoogleCalendarInfoInput(
                    response="",
                    theJson=CalendarAlarmResponse(
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

                output = json.loads(response['output'])
                responseValue = GoogleCalendarInfoInput(
                    response=output['response'],
                    theJson=output['json']
                )
                return responseValue

        final = await getResponseAndValidate(input)
        return final
