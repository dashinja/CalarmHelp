"""Tests for Google Calendar Service."""

import os
import logging
import pytest
from unittest.mock import patch, MagicMock

from calarmhelp.services.googleCalendarService import (
    isCalendarFound,
    getService,
    GoogleCalendarServiceScript,
)


class TestGoogleCalendarService:
    """Tests for the Google Calendar Service."""

    def test_is_calendar_found_success(self):
        """Test calendar found function when calendar exists."""
        mock_service = MagicMock()
        mock_service.calendars().get().execute.return_value = {
            "summary": "Test Calendar"
        }

        result = isCalendarFound("test-calendar-id", mock_service)
        assert result["found"] is True
        assert result["calendar"]["summary"] == "Test Calendar"

    def test_is_calendar_found_failure(self):
        """Test calendar found function when calendar does not exist."""
        mock_service = MagicMock()
        mock_service.calendars().get.side_effect = Exception("Calendar not found")

        result = isCalendarFound("non-existent-id", mock_service)
        assert result["found"] is False
        assert result["calendar"] is None

    @pytest.mark.parametrize("environment", [None, "production", "docker"])
    @patch("calarmhelp.services.googleCalendarService.os.getenv")
    @patch(
        "calarmhelp.services.googleCalendarService.service_account.Credentials.from_service_account_file"
    )
    @patch("calarmhelp.services.googleCalendarService.default")
    @patch("calarmhelp.services.googleCalendarService.build")
    def test_get_service(
        self, mock_build, mock_default, mock_from_file, mock_getenv, environment
    ):
        """Test getting Google Calendar service."""
        # Configure mocks
        mock_getenv.return_value = environment
        mock_logger = MagicMock()

        if environment not in ["production", "docker"]:
            mock_creds = MagicMock()
            mock_from_file.return_value = mock_creds
            mock_creds.valid = True
        else:
            mock_default.return_value = (MagicMock(), None)

        mock_service = MagicMock()
        mock_build.return_value = mock_service

        # Call function
        result = getService(mock_logger)

        # Check result
        assert result == mock_service
        mock_build.assert_called_once()

    @patch("calarmhelp.services.googleCalendarService.getService")
    @patch("calarmhelp.services.googleCalendarService.isCalendarFound")
    def test_google_calendar_service_script_success(
        self,
        mock_is_calendar_found,
        mock_get_service,
        sample_google_calendar_info_input,
    ):
        """Test GoogleCalendarServiceScript with successful event creation."""
        # Configure mocks
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service

        mock_is_calendar_found.return_value = {
            "found": True,
            "calendar": {"summary": "Test Calendar"},
        }

        mock_event_result = {
            "id": "test-event-id",
            "htmlLink": "https://calendar.google.com/event/test-event-id",
        }
        mock_service.events().insert().execute.return_value = mock_event_result

        mock_logger = MagicMock()

        # Call function
        with patch(
            "calarmhelp.services.googleCalendarService.calendar_id", "test-calendar-id"
        ):
            result = GoogleCalendarServiceScript(
                sample_google_calendar_info_input, mock_logger
            )

        # Check response has event info
        assert result.success is not None
        # The implementation returns "Event Created" as success message, not the htmlLink
        assert "Event Created" in result.success
