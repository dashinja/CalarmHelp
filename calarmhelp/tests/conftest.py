"""Test configuration and shared fixtures for CalarmHelp."""

import os
from datetime import datetime, timedelta
from typing import Dict, Any, Generator
import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient

from calarmhelp.services.util.util import (
    Category,
    CalendarAlarmResponse,
    GoogleCalendarInfoInput,
    GoogleCalendarResponse,
)
from calarmhelp.main import app


@pytest.fixture
def test_client() -> TestClient:
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def mock_env_vars() -> Generator:
    """Mock environment variables required for testing."""
    with patch.dict(
        os.environ,
        {
            "OPENAI_API_KEY": "mock-api-key",
            "ORIGINS": "http://localhost:3000",
            "CALENDAR_ID": "test-calendar-id",
            "GOOGLE_APPLICATION_CREDENTIALS": "/path/to/credentials.json",
        },
    ):
        yield


@pytest.fixture
def sample_calendar_alarm_response() -> CalendarAlarmResponse:
    """Create a sample CalendarAlarmResponse object."""
    now = datetime.now()
    event_time = now + timedelta(hours=1)
    event_time_end = event_time + timedelta(minutes=30)

    return CalendarAlarmResponse(
        name="Test Event",
        category=Category.HOME,
        lead_time=10,
        event_time=event_time,
        event_time_end=event_time_end,
        location="Test Location",
        error=False,
        current_time=now,
    )


@pytest.fixture
def sample_google_calendar_info_input(
    sample_calendar_alarm_response,
) -> GoogleCalendarInfoInput:
    """Create a sample GoogleCalendarInfoInput object."""
    return GoogleCalendarInfoInput(
        response="Test response", theJson=sample_calendar_alarm_response
    )


@pytest.fixture
def mock_google_calendar_service():
    """Mock the Google Calendar API service."""
    mock_service = MagicMock()
    mock_calendar = MagicMock()
    mock_events = MagicMock()

    mock_service.calendars.return_value.get.return_value.execute.return_value = {
        "summary": "Test Calendar"
    }
    mock_service.events.return_value.insert.return_value.execute.return_value = {
        "id": "test-event-id",
        "htmlLink": "https://calendar.google.com/event/test-event-id",
    }

    return mock_service
