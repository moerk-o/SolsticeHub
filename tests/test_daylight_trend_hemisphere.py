"""Test for daylight trend hemisphere correction (Issue #8).

This test validates that the daylight_trend is correctly inverted
for the southern hemisphere.
"""

from datetime import datetime, timezone

import pytest
from freezegun import freeze_time

# Add parent directory to path for imports
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "custom_components"))

from solsticehub.calculations import calculate_season_data


class TestDaylightTrendHemisphere:
    """Tests for daylight trend hemisphere correction."""

    @freeze_time("2026-01-15 12:00:00", tz_offset=0)
    def test_january_northern_days_getting_longer(self):
        """In January, northern hemisphere days should be getting longer.

        After the December solstice (winter), days get longer.
        """
        now = datetime.now(timezone.utc)
        data = calculate_season_data("northern", "astronomical", now)
        assert data["daylight_trend"] == "days_getting_longer"

    @freeze_time("2026-01-15 12:00:00", tz_offset=0)
    def test_january_southern_days_getting_shorter(self):
        """In January, southern hemisphere days should be getting shorter.

        After the December solstice (summer in south), days get shorter.
        This is the bug fix for Issue #8.
        """
        now = datetime.now(timezone.utc)
        data = calculate_season_data("southern", "astronomical", now)
        assert data["daylight_trend"] == "days_getting_shorter"

    @freeze_time("2026-07-15 12:00:00", tz_offset=0)
    def test_july_northern_days_getting_shorter(self):
        """In July, northern hemisphere days should be getting shorter.

        After the June solstice (summer), days get shorter.
        """
        now = datetime.now(timezone.utc)
        data = calculate_season_data("northern", "astronomical", now)
        assert data["daylight_trend"] == "days_getting_shorter"

    @freeze_time("2026-07-15 12:00:00", tz_offset=0)
    def test_july_southern_days_getting_longer(self):
        """In July, southern hemisphere days should be getting longer.

        After the June solstice (winter in south), days get longer.
        """
        now = datetime.now(timezone.utc)
        data = calculate_season_data("southern", "astronomical", now)
        assert data["daylight_trend"] == "days_getting_longer"

    @freeze_time("2026-02-15 12:00:00", tz_offset=0)
    def test_february_southern_days_getting_shorter(self):
        """In February (Australian summer), days should be getting shorter.

        This matches the exact scenario from Issue #8.
        """
        now = datetime.now(timezone.utc)
        data = calculate_season_data("southern", "astronomical", now)
        assert data["daylight_trend"] == "days_getting_shorter"
        # Also verify it's summer in Australia
        assert data["current_season"] == "summer"
