import json
import pprint
from typing import Dict, Optional
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


llm = ChatOpenAI(model='gpt-4-turbo', temperature=0)

parser = JsonOutputKeyToolsParser(key_name="observation")
evaluator = JsonSchemaEvaluator()


class CalendarAlarmFinalResponse(BaseModel):
    displayText: str = Field(description="The final response to be displayed to the user")


class CalendarAlarmResponse(BaseModel):
    name: str = Field(description="Name of the event")
    category: Category = Field(description="Category of the event")
    lead_time: int = Field(description="How long before the event I should be reminded. Defaults to 30 minutes if not provided.")
    event_time: datetime = Field(description="When the event should actually happen. Always following the 'America/New_York' timezone.")
    event_time_end: datetime = Field(description="When the event should actually end. Always following the 'America/New_York' timezone.")
    location: str = Field(description="Location of event, if provided")
    error: bool = Field(default=False, description="If there was an error in the input then True. Otherwise, False.")
    current_time: datetime = Field(description="The current time. Always following the 'America/New_York' timezone.")
    response: Optional[str] = Field(description="The final response to be displayed to the user. This can only be populated after the tool is called. The output of the tool goes here")


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

        systemPrompt_gpt = """You are an Executive Scheduling Assistant, and your task is to transform freeform text descriptions of events, provided as `{user_input}`, into a structured Python dictionary. This transformation must consider `{current_time}`, the current time in 'America/New_York' timezone, to validate the event's timing. Use the tool `create_alarm_readout` to finalize the processing of event details. The expected output is a Python dictionary with the following structure:

1. Ensure that the event described in `{user_input}` is in the future relative to `{current_time}`. If the event is in the past, set 'error' to True.
2. Construct the event details into a dictionary, adhering to the specified schema:
    - name: The name of the event.
    - category: The category of the event, inferred from the input or defaulted to 'General'.
    - lead_time: The reminder lead time in minutes. If unspecified, default to 30 minutes.
    - event_time: The start time of the event, in 'America/New_York' timezone.
    - event_time_end: The end time of the event, also in 'America/New_York' timezone.
    - location: The location of the event, if provided.
    - error: A boolean flag indicating if there was an error in processing.
    - current_time: The current time, provided as `{current_time}`, in 'America/New_York' timezone.
3. Process the initial input or the structured dictionary through the tool `create_alarm_readout`.
4. Output the final response as a Python dictionary in the following format:

```python
{
    "response": <Final processed output from `create_alarm_readout` tool>,
    "event_dict": {
        "name": "<Name of the event>",
        "category": "<Category of the event>",
        "lead_time": <Reminder lead time>,
        "event_time": "<Event start time>",
        "event_time_end": "<Event end time>",
        "location": "<Location>",
        "error": <Error flag>,
        "current_time": "<Current time as provided in `{current_time}`>"
    }
}


"""

        systemPrompt_original = """
        From the user_input you will extract the name (string) of the event, the category of one of the types "always | work | home" for the event (if category is unclear, default to "always"), lead_time (number) which is how long before the event I should be reminded, event_time (datetime) is when the event should actually happen, 'event_time_end' (if not specified, always has the value of half an hour after the event_time), and creation_time of the call to the llm (currentDateTime), and location (as a string, only if clearly provided. Most of the time this should be an empty string. Location callouts are rare.), and an 'error' (boolean, only ever true if llm fails). Your JSON response will only have the fields 'name', 'category', 'lead_time' (always expressed in terms of minutes. So 3 hours = 180 for example - and if lead_time is not specified, defaults to 30), event_time_end, event_time', 'creation_time' (datetime object), 'location', and 'error'. Always use double quotes for keys and values in the JSON object you create.
        Do not create events that are in the past. If a time is given, say 8AM but the current time is 9AM - assume the time given is for the future. Also, look for language that indicates when - and pair that with time to produce the correct date.                 
        name: str = Field(description="Name of the event")
        category: Category = Field(description="Category of the event")
        lead_time: int = Field(description="How long before the event I should be reminded. Defaults to 30 minutes if not provided.")
        event_time: datetime = Field(description="When the event should actually happen. Always following the 'America/New_York' timezone.")
        event_time_end: datetime = Field(description="When the event should actually end. Always following the 'America/New_York' timezone.")
        location: str = Field(description="Location of event, if provided")
        error: bool = Field(default=False, description="If there was an error in the input then True. Otherwise, False.")
        current_time: datetime = Field(description="The current time. Always following the 'America/New_York' timezone.")
        {user_input}
        {current_time}
        Finally, run the output through the tool attached to the agent to get the final response in a field called response. ALWAYS use the tool.
        Return a json object that has a field for the final response, as well as a field for the json."""

        systemPrompt_gpt_2 = """Given the current time provided as `{current_time}` and an event description `{user_input}`, your role is to process this information to generate event details in a structured format. You must ensure the event is scheduled for the future, considering `{current_time}`. Utilize the tool `create_alarm_readout` to finalize the event details. 

Your output should be organized into a Python dictionary named `event_details`, which you will then process with `create_alarm_readout`. The structured dictionary should include fields for the event's name, category, lead time (defaulting to 30 minutes if not provided), start and end times (both in 'America/New_York' timezone), location (if available), and a boolean for errors (set to True if the event does not meet validation criteria).

Follow these steps:

1. Check if `{user_input}` describes a future event relative to `{current_time}`. If not, flag the event as an error.
2. Populate the dictionary with the information extracted from `{user_input}` and `{current_time}`, following the specified schema.
3. Remember to set the timezone for `event_time`, `event_time_end`, and `current_time` to 'America/New_York'.
4. If critical information is missing or if an error is detected during validation (e.g., event date in the past), ensure to flag the event appropriately.

After constructing the `event_details` dictionary, process it through `create_alarm_readout` to obtain the final structured output. 

Please provide the structured dictionary ready for processing, ensuring all provided details are accurate and complete."""

        systemPrompt_gpt_3 = """Given the details of an event described in `{user_input}` and considering the current time `{current_time}`, create a structured dictionary representing the event. Ensure the event is in the future relative to `{current_time}`. After constructing the dictionary, simulate the output of the `create_alarm_readout` tool based on the event details. 

The structured dictionary should follow this schema:
- name: str (Name of the event)
- category: str (Category of the event, inferred from the input)
- lead_time: int (Reminder lead time in minutes, default to 30 if not specified)
- event_time: str (Event start time in 'America/New_York' timezone)
- event_time_end: str (Event end time in 'America/New_York' timezone)
- location: str (Location of the event, if provided)
- error: bool (Set to True if there's an error, like the event being in the past)
- current_time: str (The current time, provided in '{current_time}', in 'America/New_York' timezone)

Then, simulate the output of the `create_alarm_readout` tool using the structured dictionary, adding a field called "response" to the dictionary, which will contain the simulated tool output. The "response" should be a string formatted as follows: "<name> @ <time_of_day> on <day_of_week> <month> <day_number> #<category> [<lead_time>m]".

Output only the final structured dictionary with the added "response" field.
"""

        systemPrompt_gpt_4 = """Given the event details described in `{user_input}` and considering the current time is `{current_time}`, create a structured Python dictionary that represents these details, ensuring the event is scheduled for the future relative to `{current_time}`. The output should be a Python dictionary named `event_details`, which includes the event's name, category, lead time, start and end times (in 'America/New_York' timezone), location (if applicable), and an error flag (set to True if the event is incorrectly specified, such as being scheduled in the past). 

Additionally, simulate the processing of this event through an imaginary tool, `create_alarm_readout`, which generates a descriptive response based on the event details. Include this response in the `event_details` dictionary under the key "response".

Format the output as a Python dictionary without using JSON or Markdown notation, making it immediately usable in a Python codebase. Here is the structure to follow for the `event_details` dictionary:


{
"name": "<name of the event>",
"category": "<category of the event>",
"lead_time": <reminder lead time in minutes>,
"event_time": "<event start time in 'America/New_York' timezone>",
"event_time_end": "<event end time in 'America/New_York' timezone>",
"location": "<location of the event>",
"error": <True if there's an error, otherwise False>,
"current_time": "<current time in 'America/New_York' timezone>",
"response": "<simulated response from create_alarm_readout>"
}



Ensure all details are accurate and complete based on `{user_input}` and `{current_time}`. The dictionary should be ready to use in Python without requiring any conversion from JSON or Markdown formats.
"""

        systemPrompt_gpt_5 = """Given the event description contained in `{user_input}` and the current time `{current_time}`, process this information to generate a Python dictionary detailing the event. This dictionary must represent the event accurately, including its schedule in relation to `{current_time}`. You must use the tool available to you for processing the event information. The dictionary should be structured with keys for the event's name, category, lead time, event start and end times (in 'America/New_York' timezone), location, and an error flag for any issues detected. Additionally, include the current time as provided in the input.

        The following information should be extracted or inferred from the user_input and current_time -
The output dictionary should be formatted as follows, making it directly usable in a Python code base without further modification:


{
"name": "<event name>",
"category": "<event category>",
"lead_time": <reminder lead time in minutes>,
"event_time": "<event start time in 'America/New_York' timezone>",
"event_time_end": "<event end time in 'America/New_York' timezone>",
"location": "<event location>",
"error": <True if an error is detected, else False>,
"current_time": "<current time as provided>",
"response": "<output from the tool processing>"
}



Ensure all provided details are based on `{user_input}` and `{current_time}`, and make sure to actually use the tool to process the event details before including the "response" in the output. The "response" key should contain the processed information from the tool, reflecting a summary or analysis of the event as required.

"""

        systemPrompt_gpt_6 = """Using the current time provided as {current_time} and the event description from {user_input}, generate a Python dictionary that represents the event's details, ensuring the event is future-oriented relative to the current time. The dictionary should include keys for the event's name, category, lead time, start and end times (in 'America/New_York' timezone), location, and an error flag indicating any issues. Additionally, include a simulated process that mimics the output of an external tool, formatted as a string under the key 'response'. Format the entire output so it can be directly used as a Python dictionary in a code base.

        Intended output - after using the tool to process the event details, the final dictionary should be structured as follows:

        class CalendarAlarmResponse(BaseModel):
    name: str = Field(description="Name of the event")
    category: Category = Field(description="Category of the event")
    lead_time: int = Field(description="How long before the event I should be reminded. Defaults to 30 minutes if not provided.")
    event_time: datetime = Field(description="When the event should actually happen. Always following the 'America/New_York' timezone.")
    event_time_end: datetime = Field(description="When the event should actually end. Always following the 'America/New_York' timezone.")
    location: str = Field(description="Location of event, if provided")
    error: bool = Field(default=False, description="If there was an error in the input then True. Otherwise, False.")
    current_time: datetime = Field(description="The current time. Always following the 'America/New_York' timezone.")
    response: Optional[str] = Field(description="The final response to be displayed to the user. This can only be populated after the tool is called. The output of the tool goes here")

    The 'output' field should contain the final python dictionary in a form immediately usable in a Python codebase. It should not contain other code, just the output reading the dictionary. The 'response' field should contain the final response to be displayed to the user. Ensure all details are accurate and complete based on the input and current time provided.
"""
        systemPrompt = [("system", systemPrompt_original),
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
            global evaluationCount
            evaluationCount = 0
            response = agent_executer.invoke(input)
            print("RESPONSE::::::")
            pprint.pprint(response)
            parsedOutput = json.loads(response['output'])

            saved_schema = json.dumps({'json': {'name': 'Tell her I love her', 'category': 'always', 'lead_time': 120, 'event_time': '2024-04-25T08:00:00', 'event_time_end': '2024-04-25T08:30:00', 'creation_time': '2024-04-20T20:22:19.290603', 'location': 'Disney World', 'error': "false"}, 'response': 'Tell her I love her @ 08:00 AM at Disney World on Thursday April 25 #always [120m]'})

            examenResponse: Dict[str, bool] = evaluator.evaluate_strings(
                prediction=parsedOutput, reference=saved_schema)

            if examenResponse['score'] is True:
                return response['output']
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
                    current_time=datetime.now(),
                    response=response['output']

                )

        return getResponseAndValidate(input)
