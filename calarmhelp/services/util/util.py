from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional, Union

from pydantic import BaseModel, Field


class CreateAlarmRequest(BaseModel):
    input: str


class Category(str, Enum):
    """Enumeration for event categories."""

    ALWAYS = "always"
    WORK = "work"
    HOME = "home"


class CalendarAlarmResponse(BaseModel):
    """Model for the calendar alarm response."""

    name: str = Field(description="Name of the event")
    category: Category = Field(
        default=Category.ALWAYS, description="Category of the event"
    )
    lead_time: int = Field(
        description="How long before the event I should be reminded. Defaults to 30 minutes if not provided."
    )
    event_time: datetime = Field(
        description="When the event should actually happen. Always following the 'America/New_York' timezone."
    )
    event_time_end: datetime = Field(
        description="When the event should actually end. Always following the 'America/New_York' timezone.If this value isn't pulled from the text, assume it is thirty minutes after the event_time"
    )
    location: Optional[str] = Field(
        default=None, description="Location of event, if provided"
    )
    error: bool = Field(
        default=False,
        description="If there was an error in the input then True. Otherwise, False.",
    )
    current_time: datetime = Field(
        description="The current time. Always following the 'America/New_York' timezone."
    )


class GoogleCalendarInfoInput(BaseModel):
    """Model for Google Calendar information input."""

    response: str
    jsonResponse: CalendarAlarmResponse = Field(alias="theJson")

    def to_dict(self) -> Dict[str, Union[str, Any]]:
        """Serializes object"""
        return {
            "response": self.response,
            "jsonResponse": self.jsonResponse.model_dump(),
        }
