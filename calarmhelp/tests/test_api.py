"""Tests for API endpoints."""

import json
import pytest
from unittest.mock import patch, MagicMock

from fastapi import status

from calarmhelp.services.util.util import (
    CalendarAlarmResponse,
    GoogleCalendarResponse,
    Category,
)


class TestAPIEndpoints:
    """Tests for API endpoints."""

    @patch("calarmhelp.main.CalendarAlarmServicePipeline")
    @patch("calarmhelp.main.GoogleCalendarServiceScript")
    def test_create_alarm_success(
        self,
        mock_google_calendar_service,
        mock_calendar_alarm_service,
        test_client,
        sample_calendar_alarm_response,
    ):
        """Test successful alarm creation."""
        # Configure mocks
        mock_calendar_pipeline_instance = MagicMock()
        mock_calendar_alarm_service.return_value = mock_calendar_pipeline_instance
        mock_calendar_pipeline_instance.run.return_value = (
            sample_calendar_alarm_response
        )

        mock_google_calendar_service.return_value = GoogleCalendarResponse(
            success="Event created successfully",
        )

        # Make request
        response = test_client.post(
            "/create_alarm", json={"input": "Remind me to buy groceries at 5pm"}
        )

        # Check response
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == sample_calendar_alarm_response.name
        assert data["error"] is False

        # Verify mocks called correctly
        mock_calendar_pipeline_instance.run.assert_called_once_with(
            input="Remind me to buy groceries at 5pm"
        )
        # We only check if the mock was called, not the exact arguments since it includes a logger
        assert mock_google_calendar_service.called

    @patch("calarmhelp.main.CalendarAlarmServicePipeline")
    def test_create_alarm_calendar_service_error(
        self, mock_calendar_alarm_service, test_client
    ):
        """Test alarm creation with error in calendar alarm service."""
        # Configure mocks
        mock_calendar_pipeline_instance = MagicMock()
        mock_calendar_alarm_service.return_value = mock_calendar_pipeline_instance

        error_response = GoogleCalendarResponse(error="Failed to parse input")
        mock_calendar_pipeline_instance.run.return_value = error_response

        # Make request
        response = test_client.post("/create_alarm", json={"input": "Invalid input"})

        # Check response
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["error"] == "Failed to parse input"
        # The GoogleCalendarResponse model always includes the success field, though it will be None
        assert data["success"] is None

        # Verify mock called correctly
        mock_calendar_pipeline_instance.run.assert_called_once_with(
            input="Invalid input"
        )

    @patch("calarmhelp.main.CalendarAlarmServicePipeline")
    @patch("calarmhelp.main.GoogleCalendarServiceScript")
    def test_create_alarm_google_calendar_error(
        self,
        mock_google_calendar_service,
        mock_calendar_alarm_service,
        test_client,
        sample_calendar_alarm_response,
    ):
        """Test alarm creation with error in Google Calendar service."""
        # Configure mocks
        mock_calendar_pipeline_instance = MagicMock()
        mock_calendar_alarm_service.return_value = mock_calendar_pipeline_instance
        mock_calendar_pipeline_instance.run.return_value = (
            sample_calendar_alarm_response
        )

        # Use GoogleCalendarResponse instead of a dict to match the implementation
        error_response = GoogleCalendarResponse(
            error="Failed to create calendar event", success=None
        )
        mock_google_calendar_service.return_value = error_response

        # Make request
        response = test_client.post(
            "/create_alarm", json={"input": "Remind me to buy groceries at 5pm"}
        )

        # Check response
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "error" in data
        assert data["error"] == "Failed to create calendar event"

        # Verify mocks called correctly
        mock_calendar_pipeline_instance.run.assert_called_once_with(
            input="Remind me to buy groceries at 5pm"
        )
        # We only check if the mock was called, not the exact arguments since it includes a logger
        assert mock_google_calendar_service.called
