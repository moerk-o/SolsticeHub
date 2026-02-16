"""Tests for last_start attribute on timestamp sensors (Issue #4).

This module tests the new previous_* fields in SeasonData and the
last_start attribute on timestamp sensors.

Test Categories:
1. Basic functionality tests for get_previous_event_date()
2. Consistency tests: last_start in 2026 == sensor value from 2025
3. Edge cases around event transitions
4. Year boundary tests (January after December solstice)
5. Southern hemisphere tests
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


# =============================================================================
# 1. Basic Functionality Tests
# =============================================================================


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


# =============================================================================
# 2. Consistency Tests: last_start in 2026 == sensor value from 2025
# =============================================================================


class TestConsistencySpringEquinox:
    """Consistency test for spring_equinox sensor."""

    def test_spring_equinox_consistency_northern(self):
        """In 2026, last_start for spring must equal 2025's spring_equinox sensor value."""
        # Get what the spring_equinox sensor would show in 2025 (after the event)
        date_2025 = datetime(2025, 4, 15, 12, 0, 0, tzinfo=timezone.utc)
        data_2025 = calculate_season_data("northern", "astronomical", date_2025)
        spring_2025_sensor_value = data_2025["previous_spring_equinox"].date()

        # Get what last_start shows in 2026 (before the event)
        date_2026 = datetime(2026, 2, 15, 12, 0, 0, tzinfo=timezone.utc)
        data_2026 = calculate_season_data("northern", "astronomical", date_2026)
        last_start_2026 = data_2026["previous_spring_equinox"].date()

        # They must be identical
        assert spring_2025_sensor_value == last_start_2026, (
            f"Inconsistency! 2025 spring_equinox={spring_2025_sensor_value}, "
            f"2026 last_start={last_start_2026}"
        )


class TestConsistencySummerSolstice:
    """Consistency test for summer_solstice sensor."""

    def test_summer_solstice_consistency_northern(self):
        """In 2026, last_start for summer must equal 2025's summer_solstice sensor value."""
        # Get what the summer_solstice sensor would show in 2025 (after the event)
        date_2025 = datetime(2025, 7, 15, 12, 0, 0, tzinfo=timezone.utc)
        data_2025 = calculate_season_data("northern", "astronomical", date_2025)
        summer_2025_sensor_value = data_2025["previous_summer_solstice"].date()

        # Get what last_start shows in 2026 (before the event)
        date_2026 = datetime(2026, 2, 15, 12, 0, 0, tzinfo=timezone.utc)
        data_2026 = calculate_season_data("northern", "astronomical", date_2026)
        last_start_2026 = data_2026["previous_summer_solstice"].date()

        # They must be identical
        assert summer_2025_sensor_value == last_start_2026, (
            f"Inconsistency! 2025 summer_solstice={summer_2025_sensor_value}, "
            f"2026 last_start={last_start_2026}"
        )


class TestConsistencyAutumnEquinox:
    """Consistency test for autumn_equinox sensor."""

    def test_autumn_equinox_consistency_northern(self):
        """In 2026, last_start for autumn must equal 2025's autumn_equinox sensor value."""
        # Get what the autumn_equinox sensor would show in 2025 (after the event)
        date_2025 = datetime(2025, 10, 15, 12, 0, 0, tzinfo=timezone.utc)
        data_2025 = calculate_season_data("northern", "astronomical", date_2025)
        autumn_2025_sensor_value = data_2025["previous_autumn_equinox"].date()

        # Get what last_start shows in 2026 (before the event)
        date_2026 = datetime(2026, 2, 15, 12, 0, 0, tzinfo=timezone.utc)
        data_2026 = calculate_season_data("northern", "astronomical", date_2026)
        last_start_2026 = data_2026["previous_autumn_equinox"].date()

        # They must be identical
        assert autumn_2025_sensor_value == last_start_2026, (
            f"Inconsistency! 2025 autumn_equinox={autumn_2025_sensor_value}, "
            f"2026 last_start={last_start_2026}"
        )


class TestConsistencyWinterSolstice:
    """Consistency test for winter_solstice sensor."""

    def test_winter_solstice_consistency_northern(self):
        """In 2026, last_start for winter must equal 2025's winter_solstice sensor value."""
        # Get what the winter_solstice sensor would show in 2025 (after the event)
        date_2025 = datetime(2025, 12, 25, 12, 0, 0, tzinfo=timezone.utc)
        data_2025 = calculate_season_data("northern", "astronomical", date_2025)
        winter_2025_sensor_value = data_2025["previous_winter_solstice"].date()

        # Get what last_start shows in 2026 (before the event, after year change)
        date_2026 = datetime(2026, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
        data_2026 = calculate_season_data("northern", "astronomical", date_2026)
        last_start_2026 = data_2026["previous_winter_solstice"].date()

        # They must be identical
        assert winter_2025_sensor_value == last_start_2026, (
            f"Inconsistency! 2025 winter_solstice={winter_2025_sensor_value}, "
            f"2026 last_start={last_start_2026}"
        )


# =============================================================================
# 3. Edge Cases: Before and After Event Transitions
# =============================================================================


class TestEdgeCasesAroundEvents:
    """Tests for edge cases around event transitions."""

    def test_day_before_spring_equinox(self):
        """Day before spring equinox: last_start should be previous year."""
        # Get 2026 spring equinox date
        events_2026 = get_astronomical_events(2026)
        spring_2026 = events_2026["march_equinox"]

        # One day before
        day_before = datetime(
            spring_2026.year, spring_2026.month, spring_2026.day - 1,
            12, 0, 0, tzinfo=timezone.utc
        )
        data = calculate_season_data("northern", "astronomical", day_before)

        # last_start should be 2025
        assert data["previous_spring_equinox"].year == 2025

    def test_day_after_spring_equinox(self):
        """Day after spring equinox: last_start should be current year."""
        # Get 2026 spring equinox date
        events_2026 = get_astronomical_events(2026)
        spring_2026 = events_2026["march_equinox"]

        # One day after
        day_after = datetime(
            spring_2026.year, spring_2026.month, spring_2026.day + 1,
            12, 0, 0, tzinfo=timezone.utc
        )
        data = calculate_season_data("northern", "astronomical", day_after)

        # last_start should be 2026
        assert data["previous_spring_equinox"].year == 2026

    def test_exact_moment_of_equinox(self):
        """At exact moment of equinox: last_start should be current year."""
        events_2026 = get_astronomical_events(2026)
        spring_2026 = events_2026["march_equinox"]

        data = calculate_season_data("northern", "astronomical", spring_2026)

        # At the exact moment, the event has occurred, so last_start = this year
        assert data["previous_spring_equinox"].year == 2026
        assert data["previous_spring_equinox"].date() == spring_2026.date()


# =============================================================================
# 4. Year Boundary Tests
# =============================================================================


class TestYearBoundaryAstronomical:
    """Tests for year boundary with astronomical calculation."""

    @freeze_time("2026-01-01 12:00:00", tz_offset=0)
    def test_january_first_winter_solstice_northern(self):
        """On Jan 1, winter_solstice last_start must be Dec 2025 (northern)."""
        now = datetime.now(timezone.utc)
        data = calculate_season_data("northern", "astronomical", now)

        # Winter started in December 2025
        assert data["previous_winter_solstice"].year == 2025
        assert data["previous_winter_solstice"].month == 12

    @freeze_time("2026-01-01 12:00:00", tz_offset=0)
    def test_january_first_current_season_is_winter(self):
        """On Jan 1 northern hemisphere, current season must be winter."""
        now = datetime.now(timezone.utc)
        data = calculate_season_data("northern", "astronomical", now)

        assert data["current_season"] == "winter"

    @freeze_time("2026-01-15 12:00:00", tz_offset=0)
    def test_mid_january_all_previous_events_correct(self):
        """In mid-January, all previous events should be from 2025."""
        now = datetime.now(timezone.utc)
        data = calculate_season_data("northern", "astronomical", now)

        # All events from 2025 (none have occurred in 2026 yet)
        assert data["previous_spring_equinox"].year == 2025
        assert data["previous_summer_solstice"].year == 2025
        assert data["previous_autumn_equinox"].year == 2025
        assert data["previous_winter_solstice"].year == 2025


class TestYearBoundaryMeteorological:
    """Tests for year boundary with meteorological calculation."""

    @freeze_time("2026-01-01 12:00:00", tz_offset=0)
    def test_january_first_winter_start_meteorological_northern(self):
        """On Jan 1 meteorological, winter_solstice last_start must be Dec 1, 2025."""
        now = datetime.now(timezone.utc)
        data = calculate_season_data("northern", "meteorological", now)

        # Meteorological winter starts Dec 1
        assert data["previous_winter_solstice"].year == 2025
        assert data["previous_winter_solstice"].month == 12
        assert data["previous_winter_solstice"].day == 1

    @freeze_time("2026-01-01 12:00:00", tz_offset=0)
    def test_january_first_current_season_meteorological(self):
        """On Jan 1 meteorological northern, current season must be winter."""
        now = datetime.now(timezone.utc)
        data = calculate_season_data("northern", "meteorological", now)

        assert data["current_season"] == "winter"


# =============================================================================
# 5. Southern Hemisphere Tests
# =============================================================================


class TestSouthernHemisphereConsistency:
    """Consistency tests for southern hemisphere."""

    @freeze_time("2026-02-15 12:00:00", tz_offset=0)
    def test_southern_spring_is_september(self):
        """Southern hemisphere spring_equinox should map to September equinox."""
        now = datetime.now(timezone.utc)
        data = calculate_season_data("southern", "astronomical", now)

        # Spring in southern hemisphere = September equinox
        # In February 2026, the last spring was September 2025
        assert data["previous_spring_equinox"].year == 2025
        assert data["previous_spring_equinox"].month == 9

    @freeze_time("2026-02-15 12:00:00", tz_offset=0)
    def test_southern_summer_is_december(self):
        """Southern hemisphere summer_solstice should map to December solstice."""
        now = datetime.now(timezone.utc)
        data = calculate_season_data("southern", "astronomical", now)

        # Summer in southern hemisphere = December solstice
        # In February 2026, the last summer was December 2025
        assert data["previous_summer_solstice"].year == 2025
        assert data["previous_summer_solstice"].month == 12

    @freeze_time("2026-02-15 12:00:00", tz_offset=0)
    def test_southern_current_season_is_summer(self):
        """In February, southern hemisphere should be in summer."""
        now = datetime.now(timezone.utc)
        data = calculate_season_data("southern", "astronomical", now)

        assert data["current_season"] == "summer"

    def test_southern_spring_equinox_consistency(self):
        """Southern spring consistency: 2026 last_start == 2025 sensor value."""
        # Get 2025 southern spring (September equinox) after it occurred
        date_2025 = datetime(2025, 10, 15, 12, 0, 0, tzinfo=timezone.utc)
        data_2025 = calculate_season_data("southern", "astronomical", date_2025)
        spring_2025_value = data_2025["previous_spring_equinox"].date()

        # Get 2026 last_start (before the 2026 September equinox)
        date_2026 = datetime(2026, 2, 15, 12, 0, 0, tzinfo=timezone.utc)
        data_2026 = calculate_season_data("southern", "astronomical", date_2026)
        last_start_2026 = data_2026["previous_spring_equinox"].date()

        assert spring_2025_value == last_start_2026, (
            f"Southern spring inconsistency! 2025={spring_2025_value}, "
            f"2026 last_start={last_start_2026}"
        )

    def test_southern_winter_solstice_consistency(self):
        """Southern winter consistency: 2026 last_start == 2025 sensor value."""
        # Southern winter = June solstice
        # Get 2025 southern winter after it occurred
        date_2025 = datetime(2025, 7, 15, 12, 0, 0, tzinfo=timezone.utc)
        data_2025 = calculate_season_data("southern", "astronomical", date_2025)
        winter_2025_value = data_2025["previous_winter_solstice"].date()

        # Get 2026 last_start (before the 2026 June solstice)
        date_2026 = datetime(2026, 2, 15, 12, 0, 0, tzinfo=timezone.utc)
        data_2026 = calculate_season_data("southern", "astronomical", date_2026)
        last_start_2026 = data_2026["previous_winter_solstice"].date()

        assert winter_2025_value == last_start_2026, (
            f"Southern winter inconsistency! 2025={winter_2025_value}, "
            f"2026 last_start={last_start_2026}"
        )


# =============================================================================
# 6. Format Tests
# =============================================================================


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
