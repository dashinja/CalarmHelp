from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from dotenv import load_dotenv
from pydantic.v1 import BaseModel, Field

from datetime import date
from enum import Enum
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain.tools import StructuredTool
from datetime import datetime


load_dotenv()


class Category(Enum):
    ALWAYS = "always"
    WORK = "work"
    HOME = "home"


llm = ChatOpenAI(model='gpt-4-turbo', model_kwargs={
    "response_format": {"type": "json_object"}}, temperature=0)


class CalendarAlarmResponse(BaseModel):
    name: str = Field(description="Name of the event")
    category: Category = Field(description="Category of the event")
    lead_time: int = Field(description="How long before the event I should be reminded")
    event_time: datetime = Field(description="When the event should actually happen")
    error: bool = Field(default=False, description="If there was an error in the input")


def create_alarm_readout(alarm_json: CalendarAlarmResponse):
    """Provides the 'description' field for google calendar"""
    print("I am first!!!!!!")
    print("alarm_json.name: ", alarm_json.name)

    month = alarm_json.event_time.strftime('%B')
    day_number = alarm_json.event_time.strftime('%d')
    day_of_week = alarm_json.event_time.strftime('%A')
    time_of_day = alarm_json.event_time.strftime('%I:%M %p')

    print("Test Enum: ", Category.ALWAYS)
    return f"{alarm_json.name} @ {time_of_day} on {day_of_week} {month} {day_number} #{alarm_json.category.name.lower()} [{alarm_json.lead_time}m]"


class CalendarAlarmService:
    """docstring for ClassName."""

    def __init__(self):
        super(CalendarAlarmService, self).__init__()
        print("INITIALIZED")

    def create_alarm_json(self, user_input: str):

        systemPrompt = ("system", """You respond with JSON only. From the user_input you will extract the name (string) of the event, the category of one of the types "always | work | home" for the event (if category is unclear, default to "always"), lead_time (number) which is how long before the event I should be reminded, event_time (datetime) is when the event should actually happen, and creation_time of the call to the llm (currentDateTime) Your JSON response will only have the fields 'name', 'category', 'lead_time' (always expressed in terms of minutes. So 3 hours = 180 for example), 'event_time', and 'creation_time'.
                        {user_input}
                        {current_time}
                        {agent_scratchpad}
                        
                        Finally, run the output through the tool attached to the agent to get the final response.""")

        prompt = ChatPromptTemplate.from_messages([systemPrompt])
        print("Created Prompt")

        createCalendarReadout = StructuredTool.from_function(
            create_alarm_readout
            # func=create_alarm_readout,
            # args_schema=CalendarAlarmResponse,
            # name="CalendarReadout",
            # return_direct=True,
        )
        print("Created createCalendarReadout")

        tools = [createCalendarReadout]
        print("Created Tools")

        agent = create_openai_tools_agent(llm, tools, prompt)
        print("Created AGENT")

        print("INVOKED agent to get agentResponse2")

        agent_executer = AgentExecutor(agent=agent, tools=tools, verbose=True, return_intermediate_steps=True)  # type: ignore
        print("Agent executer created")

        print("BEFORE BEFORE response variable populated")

        response = agent_executer.invoke({
            "user_input": user_input,
            "current_time": datetime.now().isoformat()
        })

        print("AFTER AFTER response variable populated")

        return response
