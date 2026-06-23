"""Tests for coordinator update mechanisms.

This module tests:
1. _calculate_time_until_midnight() - midnight synchronization
2. Event-based updates with async_track_point_in_time
3. async_unload() cleanup of event listeners
"""

from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

from freezegun import freeze_time

# Add parent directory to path for imports
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "custom_components"))

from solsticehub.coordinator import _calculate_time_until_midnight


class TestCalculateTimeUntilMidnight:
    """Tests for _calculate_time_until_midnight() function."""

    @freeze_time("2026-02-15 10:00:00")
    def test_morning_time_until_midnight(self):
        """At 10:00, should be ~14 hours until midnight."""
        with patch("solsticehub.coordinator.dt_util") as mock_dt:
            # Mock local time
            mock_dt.now.return_value = datetime(2026, 2, 15, 10, 0, 0)

            result = _calculate_time_until_midnight()

            # Should be 14 hours until midnight
            assert result == timedelta(hours=14)

    @freeze_time("2026-02-15 18:30:00")
    def test_evening_time_until_midnight(self):
        """At 18:30, should be 5.5 hours until midnight."""
        with patch("solsticehub.coordinator.dt_util") as mock_dt:
            mock_dt.now.return_value = datetime(2026, 2, 15, 18, 30, 0)

            result = _calculate_time_until_midnight()

            assert result == timedelta(hours=5, minutes=30)

    @freeze_time("2026-02-15 23:30:00")
    def test_late_night_time_until_midnight(self):
        """At 23:30, should be 30 minutes until midnight."""
        with patch("solsticehub.coordinator.dt_util") as mock_dt:
            mock_dt.now.return_value = datetime(2026, 2, 15, 23, 30, 0)

            result = _calculate_time_until_midnight()

            assert result == timedelta(minutes=30)

    @freeze_time("2026-02-15 23:59:30")
    def test_very_close_to_midnight_uses_minimum(self):
        """At 23:59:30, less than 1 minute to midnight, should return 24h."""
        with patch("solsticehub.coordinator.dt_util") as mock_dt:
            mock_dt.now.return_value = datetime(2026, 2, 15, 23, 59, 30)

            result = _calculate_time_until_midnight()

            # Should fallback to 24 hours (1 day) as minimum
            assert result == timedelta(days=1)

    @freeze_time("2026-02-15 00:00:30")
    def test_just_after_midnight(self):
        """At 00:00:30, should be almost 24 hours until next midnight."""
        with patch("solsticehub.coordinator.dt_util") as mock_dt:
            mock_dt.now.return_value = datetime(2026, 2, 15, 0, 0, 30)

            result = _calculate_time_until_midnight()

            # Should be 23:59:30 until next midnight
            expected = timedelta(hours=23, minutes=59, seconds=30)
            assert result == expected

    @freeze_time("2026-02-15 12:00:00")
    def test_noon_time_until_midnight(self):
        """At noon, should be exactly 12 hours until midnight."""
        with patch("solsticehub.coordinator.dt_util") as mock_dt:
            mock_dt.now.return_value = datetime(2026, 2, 15, 12, 0, 0)

            result = _calculate_time_until_midnight()

            assert result == timedelta(hours=12)


class TestEventScheduling:
    """Tests for event-based update scheduling."""

    def test_schedule_event_in_future(self):
        """Event listener should be registered for future events."""
        with patch("solsticehub.coordinator.async_track_point_in_time") as mock_track:
            with patch("solsticehub.coordinator.dt_util") as mock_dt:
                # Setup: current time is before event
                now = datetime(2026, 3, 20, 10, 0, 0, tzinfo=timezone.utc)
                event_time = datetime(2026, 3, 20, 15, 30, 0, tzinfo=timezone.utc)
                mock_dt.utcnow.return_value = now

                # Create mock coordinator
                mock_hass = MagicMock()
                mock_config_entry = MagicMock()
                mock_config_entry.title = "Test Entry"

                # Import and test
                from solsticehub.coordinator import SolsticeHubCoordinator

                # We need to patch the parent class init
                with patch.object(SolsticeHubCoordinator, "__init__", lambda self, h, c: None):
                    coordinator = SolsticeHubCoordinator.__new__(SolsticeHubCoordinator)
                    coordinator.hass = mock_hass
                    coordinator.config_entry = mock_config_entry
                    coordinator._unsub_event = None

                    coordinator._schedule_event_update(event_time)

                    # Verify async_track_point_in_time was called
                    mock_track.assert_called_once()
                    call_args = mock_track.call_args
                    assert call_args[0][0] == mock_hass  # hass
                    assert call_args[0][2] == event_time  # event time

    def test_no_schedule_for_past_event(self):
        """Event listener should NOT be registered for past events."""
        with patch("solsticehub.coordinator.async_track_point_in_time") as mock_track:
            with patch("solsticehub.coordinator.dt_util") as mock_dt:
                # Setup: current time is AFTER event
                now = datetime(2026, 3, 20, 18, 0, 0, tzinfo=timezone.utc)
                event_time = datetime(2026, 3, 20, 15, 30, 0, tzinfo=timezone.utc)
                mock_dt.utcnow.return_value = now

                mock_hass = MagicMock()
                mock_config_entry = MagicMock()
                mock_config_entry.title = "Test Entry"

                from solsticehub.coordinator import SolsticeHubCoordinator

                with patch.object(SolsticeHubCoordinator, "__init__", lambda self, h, c: None):
                    coordinator = SolsticeHubCoordinator.__new__(SolsticeHubCoordinator)
                    coordinator.hass = mock_hass
                    coordinator.config_entry = mock_config_entry
                    coordinator._unsub_event = None

                    coordinator._schedule_event_update(event_time)

                    # Should NOT register listener for past event
                    mock_track.assert_not_called()

    def test_cancel_previous_event_before_scheduling_new(self):
        """Previous event listener should be cancelled before scheduling new one."""
        with patch("solsticehub.coordinator.async_track_point_in_time") as mock_track:
            with patch("solsticehub.coordinator.dt_util") as mock_dt:
                now = datetime(2026, 3, 20, 10, 0, 0, tzinfo=timezone.utc)
                event_time = datetime(2026, 3, 20, 15, 30, 0, tzinfo=timezone.utc)
                mock_dt.utcnow.return_value = now

                mock_hass = MagicMock()
                mock_config_entry = MagicMock()
                mock_config_entry.title = "Test Entry"

                # Create mock unsubscribe function
                mock_unsub = MagicMock()

                from solsticehub.coordinator import SolsticeHubCoordinator

                with patch.object(SolsticeHubCoordinator, "__init__", lambda self, h, c: None):
                    coordinator = SolsticeHubCoordinator.__new__(SolsticeHubCoordinator)
                    coordinator.hass = mock_hass
                    coordinator.config_entry = mock_config_entry
                    coordinator._unsub_event = mock_unsub  # Existing listener

                    coordinator._schedule_event_update(event_time)

                    # Previous listener should be cancelled, new one scheduled
                    mock_unsub.assert_called_once()
                    mock_track.assert_called_once()


class TestAsyncUnload:
    """Tests for async_unload() cleanup."""

    def test_unload_cancels_event_listener(self):
        """async_unload() should cancel registered event listener."""
        mock_unsub = MagicMock()

        from solsticehub.coordinator import SolsticeHubCoordinator

        with patch.object(SolsticeHubCoordinator, "__init__", lambda self, h, c: None):
            coordinator = SolsticeHubCoordinator.__new__(SolsticeHubCoordinator)
            coordinator._unsub_event = mock_unsub

            coordinator.async_unload()

            # Listener should be cancelled
            mock_unsub.assert_called_once()
            # Reference should be cleared
            assert coordinator._unsub_event is None

    def test_unload_without_listener_is_safe(self):
        """async_unload() should not fail when no listener exists."""
        from solsticehub.coordinator import SolsticeHubCoordinator

        with patch.object(SolsticeHubCoordinator, "__init__", lambda self, h, c: None):
            coordinator = SolsticeHubCoordinator.__new__(SolsticeHubCoordinator)
            coordinator._unsub_event = None

            # Should not raise any exception
            coordinator.async_unload()

            assert coordinator._unsub_event is None


class TestAllCoordinatorsHaveSamePattern:
    """Verify all coordinators implement the same update pattern."""

    def test_cross_quarter_coordinator_has_event_scheduling(self):
        """CrossQuarterCoordinator should have _schedule_event_update method."""
        from solsticehub.cross_quarter_coordinator import CrossQuarterCoordinator

        assert hasattr(CrossQuarterCoordinator, "_schedule_event_update")
        assert hasattr(CrossQuarterCoordinator, "async_unload")
        assert hasattr(CrossQuarterCoordinator, "_handle_event_update")

    def test_chinese_coordinator_has_event_scheduling(self):
        """ChineseSolarTermsCoordinator should have _schedule_event_update method."""
        from solsticehub.chinese_coordinator import ChineseSolarTermsCoordinator

        assert hasattr(ChineseSolarTermsCoordinator, "_schedule_event_update")
        assert hasattr(ChineseSolarTermsCoordinator, "async_unload")
        assert hasattr(ChineseSolarTermsCoordinator, "_handle_event_update")

    def test_four_seasons_coordinator_has_event_scheduling(self):
        """SolsticeHubCoordinator should have _schedule_event_update method."""
        from solsticehub.coordinator import SolsticeHubCoordinator

        assert hasattr(SolsticeHubCoordinator, "_schedule_event_update")
        assert hasattr(SolsticeHubCoordinator, "async_unload")
        assert hasattr(SolsticeHubCoordinator, "_handle_event_update")
