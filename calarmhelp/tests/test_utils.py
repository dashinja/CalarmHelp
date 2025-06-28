"""Tests for utility models and functions."""

import json
from datetime import datetime
import pytest

from calarmhelp.services.util.util import (
    CreateAlarmRequest,
    Category,
    CalendarAlarmResponse,
    GoogleCalendarInfoInput,
    GoogleCalendarResponse,
)


class TestCreateAlarmRequest:
    """Tests for the CreateAlarmRequest model."""

    def test_create_alarm_request_model(self):
        """Test the CreateAlarmRequest model with valid input."""
        data = {"input": "Test input"}
        request = CreateAlarmRequest(**data)
        assert request.input == "Test input"


class TestCategory:
    """Tests for the Category enumeration."""

    def test_category_enum_values(self):
        """Test that Category enum has expected values."""
        assert Category.ALWAYS.value == "always"
        assert Category.WORK.value == "work"
        assert Category.HOME.value == "home"


class TestCalendarAlarmResponse:
    """Tests for the CalendarAlarmResponse model."""

    def test_calendar_alarm_response_model(self, sample_calendar_alarm_response):
        """Test CalendarAlarmResponse serialization."""
        model_dict = sample_calendar_alarm_response.to_dict()
        assert model_dict["name"] == "Test Event"
        assert model_dict["error"] is False

        if hasattr(sample_calendar_alarm_response, "to_json"):
            model_json = sample_calendar_alarm_response.to_json()
            parsed_json = json.loads(model_json)
            assert parsed_json["name"] == "Test Event"


class TestGoogleCalendarInfoInput:
    """Tests for the GoogleCalendarInfoInput model."""

    def test_google_calendar_info_input_model(self, sample_google_calendar_info_input):
        """Test GoogleCalendarInfoInput serialization."""
        model_dict = sample_google_calendar_info_input.to_dict()
        assert model_dict["response"] == "Test response"
        assert "jsonResponse" in model_dict

        if hasattr(sample_google_calendar_info_input, "to_json"):
            model_json = sample_google_calendar_info_input.to_json()
            parsed_json = json.loads(model_json)
            assert parsed_json["response"] == "Test response"


class TestGoogleCalendarResponse:
    """Tests for the GoogleCalendarResponse model."""

    def test_google_calendar_response_success(self):
        """Test GoogleCalendarResponse with success."""
        response = GoogleCalendarResponse(success="Event created successfully")
        assert response.success == "Event created successfully"
        assert response["success"] == "Event created successfully"

        model_dict = response.to_dict()
        assert model_dict["success"] == "Event created successfully"
        assert model_dict["error"] is None

    def test_google_calendar_response_error(self):
        """Test GoogleCalendarResponse with error."""
        response = GoogleCalendarResponse(error="Failed to create event")
        assert response.error == "Failed to create event"
        assert response["error"] == "Failed to create event"

        model_dict = response.to_dict()
        assert model_dict["error"] == "Failed to create event"
        assert model_dict["success"] is None
