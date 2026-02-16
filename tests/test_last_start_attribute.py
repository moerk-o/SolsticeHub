"""Tests for last_start attribute on timestamp sensors (Issue #4).

This module tests the new previous_* fields in SeasonData and the
last_start attribute on timestamp sensors.
"""

from datetime import datetime, timezone

import pytest
from freezegun import freeze_time

# Add parent directory to path for imports
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "custom_components"))

from solstice_season.calculations import (
    calculate_season_data,
    get_previous_event_date,
    get_astronomical_events,
)


class TestGetPreviousEventDate:
    """Tests for get_previous_event_date() helper function."""

    def test_event_already_occurred_this_year(self):
        """If event already happened this year, return this year's event."""
        # March 25, 2026 - after March equinox
        now = datetime(2026, 3, 25, 12, 0, 0, tzinfo=timezone.utc)
        current_events = get_astronomical_events(2026)
        previous_events = get_astronomical_events(2025)

        result = get_previous_event_date(
            "march_equinox", current_events, previous_events, now
        )

        # Should return 2026 March equinox (already passed)
        assert result.year == 2026
        assert result.month == 3

    def test_event_not_yet_occurred_this_year(self):
        """If event hasn't happened yet this year, return last year's event."""
        # March 15, 2026 - before March equinox
        now = datetime(2026, 3, 15, 12, 0, 0, tzinfo=timezone.utc)
        current_events = get_astronomical_events(2026)
        previous_events = get_astronomical_events(2025)

        result = get_previous_event_date(
            "march_equinox", current_events, previous_events, now
        )

        # Should return 2025 March equinox (last year)
        assert result.year == 2025
        assert result.month == 3

    def test_event_on_exact_day_returns_current(self):
        """If we're on the exact day of the event, return current year's event."""
        current_events = get_astronomical_events(2026)
        # Use the exact event time
        march_equinox = current_events["march_equinox"]

        previous_events = get_astronomical_events(2025)

        result = get_previous_event_date(
            "march_equinox", current_events, previous_events, march_equinox
        )

        # Should return 2026 event (we're at or past the moment)
        assert result.year == 2026


class TestPreviousFieldsInSeasonData:
    """Tests for previous_* fields in calculate_season_data()."""

    @freeze_time("2026-02-15 12:00:00", tz_offset=0)
    def test_february_previous_fields_northern(self):
        """In February, test previous_* fields for northern hemisphere."""
        now = datetime.now(timezone.utc)
        data = calculate_season_data("northern", "astronomical", now)

        # In February 2026:
        # - previous_spring_equinox should be 2025-03-20 (last spring)
        # - previous_summer_solstice should be 2025-06-21 (last summer)
        # - previous_autumn_equinox should be 2025-09-22 (last autumn)
        # - previous_winter_solstice should be 2025-12-21 (last winter, recent)

        assert data["previous_spring_equinox"].year == 2025
        assert data["previous_spring_equinox"].month == 3

        assert data["previous_summer_solstice"].year == 2025
        assert data["previous_summer_solstice"].month == 6

        assert data["previous_autumn_equinox"].year == 2025
        assert data["previous_autumn_equinox"].month == 9

        assert data["previous_winter_solstice"].year == 2025
        assert data["previous_winter_solstice"].month == 12

    @freeze_time("2026-07-15 12:00:00", tz_offset=0)
    def test_july_previous_fields_northern(self):
        """In July, test previous_* fields for northern hemisphere."""
        now = datetime.now(timezone.utc)
        data = calculate_season_data("northern", "astronomical", now)

        # In July 2026:
        # - previous_spring_equinox should be 2026-03-20 (this year, already passed)
        # - previous_summer_solstice should be 2026-06-21 (this year, just passed)
        # - previous_autumn_equinox should be 2025-09-22 (last year, not yet 2026)
        # - previous_winter_solstice should be 2025-12-21 (last year)

        assert data["previous_spring_equinox"].year == 2026
        assert data["previous_spring_equinox"].month == 3

        assert data["previous_summer_solstice"].year == 2026
        assert data["previous_summer_solstice"].month == 6

        assert data["previous_autumn_equinox"].year == 2025
        assert data["previous_autumn_equinox"].month == 9

        assert data["previous_winter_solstice"].year == 2025
        assert data["previous_winter_solstice"].month == 12

    @freeze_time("2026-02-15 12:00:00", tz_offset=0)
    def test_february_previous_fields_southern(self):
        """In February, test previous_* fields for southern hemisphere."""
        now = datetime.now(timezone.utc)
        data = calculate_season_data("southern", "astronomical", now)

        # For southern hemisphere, seasons are mapped differently:
        # - spring_equinox = september_equinox (2025-09)
        # - summer_solstice = december_solstice (2025-12)
        # - autumn_equinox = march_equinox (2025-03)
        # - winter_solstice = june_solstice (2025-06)

        assert data["previous_spring_equinox"].year == 2025
        assert data["previous_spring_equinox"].month == 9

        assert data["previous_summer_solstice"].year == 2025
        assert data["previous_summer_solstice"].month == 12

        assert data["previous_autumn_equinox"].year == 2025
        assert data["previous_autumn_equinox"].month == 3

        assert data["previous_winter_solstice"].year == 2025
        assert data["previous_winter_solstice"].month == 6


class TestLastStartAttributeFormat:
    """Tests that last_start attribute is correctly formatted."""

    @freeze_time("2026-02-15 12:00:00", tz_offset=0)
    def test_previous_fields_are_datetime_objects(self):
        """previous_* fields should be datetime objects."""
        now = datetime.now(timezone.utc)
        data = calculate_season_data("northern", "astronomical", now)

        assert isinstance(data["previous_spring_equinox"], datetime)
        assert isinstance(data["previous_summer_solstice"], datetime)
        assert isinstance(data["previous_autumn_equinox"], datetime)
        assert isinstance(data["previous_winter_solstice"], datetime)

    @freeze_time("2026-02-15 12:00:00", tz_offset=0)
    def test_previous_fields_can_be_formatted_as_iso_date(self):
        """previous_* fields should be convertible to ISO date strings."""
        now = datetime.now(timezone.utc)
        data = calculate_season_data("northern", "astronomical", now)

        # This is how sensor.py formats them for last_start attribute
        last_start_spring = data["previous_spring_equinox"].date().isoformat()
        last_start_summer = data["previous_summer_solstice"].date().isoformat()
        last_start_autumn = data["previous_autumn_equinox"].date().isoformat()
        last_start_winter = data["previous_winter_solstice"].date().isoformat()

        # Should be valid ISO date strings like "2025-03-20"
        assert last_start_spring == "2025-03-20"
        assert last_start_summer == "2025-06-21"
        assert last_start_autumn == "2025-09-22"
        # Winter solstice date varies slightly, just check format
        assert last_start_winter.startswith("2025-12-2")
