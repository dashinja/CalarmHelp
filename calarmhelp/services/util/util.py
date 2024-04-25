from pydantic.v1 import Field, BaseModel
from typing import Optional
from enum import Enum
from datetime import datetime

class Category(Enum):
    ALWAYS = "always"
    WORK = "work"
    HOME = "home"

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

class GoogleCalendarInfoInput(BaseModel):
    response: str
    jsonResponse: CalendarAlarmResponse = Field(alias="theJson")