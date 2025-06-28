"""Additional tests for Calendar Alarm Service."""

import os
import json
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
    GoogleCalendarInfoInput,
    GoogleCalendarResponse,
)


class TestCalendarAlarmServiceAdditional:
    """Additional tests for Calendar Alarm Service."""

    def test_clean_json_output(self):
        """Test cleanJsonOutput method."""
        # Create service
        service = CalendarAlarmServicePipeline()

        # Test with markdown code block syntax
        json_with_markdown = '```json\n{"name": "Test Event"}\n```'
        cleaned_json = service.cleanJsonOutput(json_with_markdown)
        assert cleaned_json == '\n{"name": "Test Event"}\n'

        # Test with only closing code block
        json_with_closing = '{"name": "Test Event"}\n```'
        cleaned_json = service.cleanJsonOutput(json_with_closing)
        assert cleaned_json == '{"name": "Test Event"}\n'

        # Test with no markdown
        clean_json = '{"name": "Test Event"}'
        cleaned_json = service.cleanJsonOutput(clean_json)
        assert cleaned_json == clean_json

    @patch("calarmhelp.services.calendarAlarmService.OpenAIGenerator")
    @patch("calarmhelp.services.calendarAlarmService.PromptBuilder")
    def test_calendar_alarm_service_pipeline_error_handling(
        self, mock_prompt_builder, mock_openai_generator
    ):
        """Test error handling in CalendarAlarmServicePipeline."""
        # Set up mocks
        mock_pipeline_instance = MagicMock()

        # Setup invalid JSON that will cause an error
        invalid_json = "DONE{invalid_json: this is not valid json}"
        mock_pipeline_instance.run.return_value = {"validator": {"json": invalid_json}}

        # Patch Pipeline
        with patch(
            "calarmhelp.services.calendarAlarmService.Pipeline",
            return_value=mock_pipeline_instance,
        ):
            with patch("calarmhelp.services.calendarAlarmService.JSONValidator"):
                with patch(
                    "calarmhelp.services.calendarAlarmService.LangfuseConnector"
                ):
                    # Create service with init parameters
                    service = CalendarAlarmServicePipeline(max_loops_allowed=10)

                    # Run service with invalid JSON that should trigger error handling
                    result = service.run("Invalid input that causes error")

        # Verify error response
        assert isinstance(result, GoogleCalendarResponse)
        assert result.error is not None
        assert "Error in Google Calendar Service" in result.error

    @patch("calarmhelp.services.calendarAlarmService.OpenAIGenerator")
    @patch("calarmhelp.services.calendarAlarmService.Pipeline")
    def test_pipeline_creation_and_connections(
        self, mock_pipeline, mock_openai_generator
    ):
        """Test pipeline creation and component connections."""
        # Create mock pipeline
        mock_pipeline_instance = MagicMock()
        mock_pipeline.return_value = mock_pipeline_instance

        # Create service
        with patch("calarmhelp.services.calendarAlarmService.PromptBuilder"):
            with patch("calarmhelp.services.calendarAlarmService.JSONValidator"):
                with patch(
                    "calarmhelp.services.calendarAlarmService.LangfuseConnector"
                ):
                    service = CalendarAlarmServicePipeline(max_loops_allowed=15)

                    # Call run to trigger pipeline setup
                    mock_pipeline_instance.run.return_value = {
                        "validator": {"json": "DONE{}"}
                    }
                    service.run("Test input")

        # Verify pipeline components were added and connected
        assert (
            mock_pipeline_instance.add_component.call_count == 4
        )  # prompt_builder, generator, validator, tracer
        assert (
            mock_pipeline_instance.connect.call_count == 3
        )  # Three connections in the pipeline

    @patch("calarmhelp.services.calendarAlarmService.OpenAIGenerator")
    @patch("calarmhelp.services.calendarAlarmService.PromptBuilder")
    def test_calendar_alarm_service_pipeline_full_run(
        self, mock_prompt_builder, mock_openai_generator
    ):
        """Test complete run flow of CalendarAlarmServicePipeline."""
        # Set up mocks

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
        json_response = json.dumps(expected_response)

        # Mock pipeline execution
        mock_pipeline_instance = MagicMock()
        mock_pipeline_instance.run.return_value = {
            "validator": {"json": f"DONE{json_response}"},
            "tracer": {"trace_url": "https://example.com/trace/123"},
        }

        # Set up the pipeline's instance attributes
        mock_openai_instance = MagicMock()
        mock_prompt_builder_instance = MagicMock()
        mock_openai_generator.return_value = mock_openai_instance
        mock_prompt_builder.return_value = mock_prompt_builder_instance

        # Patch Pipeline
        with patch(
            "calarmhelp.services.calendarAlarmService.Pipeline",
            return_value=mock_pipeline_instance,
        ):
            with patch("calarmhelp.services.calendarAlarmService.JSONValidator"):
                with patch(
                    "calarmhelp.services.calendarAlarmService.LangfuseConnector"
                ):
                    # Create service
                    service = CalendarAlarmServicePipeline(max_loops_allowed=10)

                    # Run service
                    result = service.run("Remind me to buy groceries at 5pm")

        # Verify result
        assert isinstance(result, GoogleCalendarInfoInput)
        # The response is formatted to lowercase the name
        assert "Test event" in result.response
        assert result.jsonResponse.name == "Test Event"
        assert result.jsonResponse.category == Category.HOME
