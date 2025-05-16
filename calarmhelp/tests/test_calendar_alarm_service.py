"""Tests for Calendar Alarm Service."""

import os
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

from calarmhelp.services.calendarAlarmService import (
    create_alarm_readout,
    CalendarAlarmServicePipeline,
)
from calarmhelp.services.util.util import (
    CalendarAlarmResponse,
    Category,
)


class TestCalendarAlarmService:
    """Tests for Calendar Alarm Service."""

    def test_create_alarm_readout(self, sample_calendar_alarm_response):
        """Test create_alarm_readout function."""
        readout = create_alarm_readout(sample_calendar_alarm_response)

        # Check that the readout contains expected elements
        assert sample_calendar_alarm_response.name.capitalize() in readout
        assert sample_calendar_alarm_response.location in readout
        assert f"#{sample_calendar_alarm_response.category.name.lower()}" in readout
        assert f"[{sample_calendar_alarm_response.lead_time}m]" in readout

        # Test format has key elements
        assert "@" in readout  # Time indicator
        assert "on" in readout  # Date indicator
        assert "#" in readout  # Category marker
        assert "[" in readout and "]" in readout  # Lead time markers

    @patch("calarmhelp.services.calendarAlarmService.OpenAIGenerator")
    @patch("calarmhelp.services.calendarAlarmService.PromptBuilder")
    def test_calendar_alarm_service_pipeline_successful_run(
        self, mock_prompt_builder, mock_openai_generator
    ):
        """Test successful run of CalendarAlarmServicePipeline."""
        # Set up mocks
        mock_pipeline = MagicMock()

        # Configure OpenAI response
        sample_date = datetime.now()
        expected_response = {
            "name": "Test Event",
            "category": "home",
            "lead_time": 10,
            "event_time": sample_date.isoformat(),
            "event_time_end": (
                sample_date.replace(hour=sample_date.hour + 1)
            ).isoformat(),
            "location": "Test Location",
            "error": False,
            "current_time": sample_date.isoformat(),
        }

        with patch.object(CalendarAlarmServicePipeline, "__init__", return_value=None):
            with patch.object(CalendarAlarmServicePipeline, "run") as mock_run:
                # Configure mock to return expected response
                mock_run.return_value = CalendarAlarmResponse(
                    name="Test Event",
                    category=Category.HOME,
                    lead_time=10,
                    event_time=sample_date,
                    event_time_end=sample_date.replace(hour=sample_date.hour + 1),
                    location="Test Location",
                    error=False,
                    current_time=sample_date,
                )

                # Create instance
                service = CalendarAlarmServicePipeline()

                # Test run
                result = service.run("Remind me to buy groceries at 5pm")

                # Verify result
                assert isinstance(result, CalendarAlarmResponse)
                assert result.name == "Test Event"
                assert result.category == Category.HOME
                assert result.lead_time == 10

                # Verify mock was called
                mock_run.assert_called_once_with("Remind me to buy groceries at 5pm")
