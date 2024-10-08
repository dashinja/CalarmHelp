from datetime import datetime
from enum import Enum
import json
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
        default=Category.ALWAYS, description="Category of the event", exclude=True
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

    def to_dict(self) -> Dict[str, Union[str, Any]]:
        """Serializes object"""
        return {
            "name": self.name,
            "category": self.category.name.lower(),
            "lead_time": self.lead_time,
            "event_time": self.event_time.isoformat(),
            "event_time_end": self.event_time_end.isoformat(),
            "location": self.location,
            "error": self.error,
            "current_time": self.current_time,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), default=str)


class GoogleCalendarInfoInput(BaseModel):
    """Model for Google Calendar information input."""

    response: str
    jsonResponse: CalendarAlarmResponse = Field(alias="theJson")

    def to_dict(self) -> Dict[str, Union[str, Any]]:
        """Serializes object"""
        return {
            "response": self.response,
            "jsonResponse": self.jsonResponse.to_dict(),
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), default=str)


class GoogleCalendarResponse(BaseModel):
    """Model for Google Calendar response with dynamic keys."""

    success: Optional[str] = None
    error: Optional[str] = None

    __pydantic_extra__: Dict[str, Any] = {}

    class Config:
        extra = "allow"

    def __getitem__(self, item):
        return self.__dict__.get(item)

    def __getattr__(self, item):
        if self.__pydantic_extra__ is None:
            self.__pydantic_extra__ = {}
        if item in self.__pydantic_extra__:
            return self.__pydantic_extra__[item]
        try:
            return self.__dict__[item]
        except KeyError:
            raise AttributeError(
                f"'GoogleCalendarResponse' object has no attribute '{item}'"
            )

    def to_dict(self) -> Dict[str, Any]:
        """Serializes object"""
        return self.model_dump()

    def to_json(self) -> str:
        return self.model_dump_json()
