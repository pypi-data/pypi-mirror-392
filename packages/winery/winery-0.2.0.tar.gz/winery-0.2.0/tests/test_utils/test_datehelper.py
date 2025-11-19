import pytest
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from freezegun import freeze_time
from winery.utils.dateutils import DateHelper


def test_date_helper_init_default():
    """Tests DateHelper initialization with default timezone."""
    dh = DateHelper()
    assert dh.timezone == ZoneInfo("Europe/London")


def test_date_helper_init_with_string():
    """Tests DateHelper initialization with a timezone string."""
    dh = DateHelper("America/New_York")
    assert dh.timezone == ZoneInfo("America/New_York")


def test_date_helper_init_with_zoneinfo():
    """Tests DateHelper initialization with a ZoneInfo object."""
    tz = ZoneInfo("Asia/Tokyo")
    dh = DateHelper(tz)
    assert dh.timezone == tz


@freeze_time("2025-01-01 12:00:00+01:00")
def test_now():
    """Tests the now() method returns current time in the configured timezone."""
    dh = DateHelper("Europe/Paris")
    result = dh.now()
    expected_dt = datetime(2025, 1, 1, 12, 0, 0, tzinfo=ZoneInfo("Europe/Paris"))
    assert result == expected_dt


def test_to_local_time():
    """Tests converting a Unix timestamp to a local datetime object."""
    dh = DateHelper("Europe/Paris")
    timestamp = 1672531200  # 2023-01-01 00:00:00 UTC
    expected_dt = datetime(2023, 1, 1, 1, 0, 0, tzinfo=ZoneInfo("Europe/Paris"))
    assert dh.to_local_time(timestamp) == expected_dt


def test_to_local_time_float():
    """Tests converting a float Unix timestamp to a local datetime object."""
    dh = DateHelper("Europe/Paris")
    timestamp = 1672531200.5
    expected_dt = datetime(2023, 1, 1, 1, 0, 0, 500000, tzinfo=ZoneInfo("Europe/Paris"))
    assert dh.to_local_time(timestamp) == expected_dt


def test_ensure_timezone_naive():
    """Tests ensuring a timezone on a naive datetime object."""
    dh = DateHelper("America/Los_Angeles")
    naive_dt = datetime(2025, 10, 26, 10, 0, 0)
    aware_dt = dh.ensure_timezone(naive_dt)
    assert aware_dt.tzinfo == dh.timezone
    assert aware_dt.year == 2025 and aware_dt.hour == 10


def test_ensure_timezone_aware():
    """Tests ensuring a timezone on an aware datetime object."""
    dh = DateHelper("America/Los_Angeles")
    utc_dt = datetime(2025, 10, 26, 17, 0, 0, tzinfo=timezone.utc)
    local_dt = dh.ensure_timezone(utc_dt)
    assert local_dt.tzinfo == dh.timezone
    # 17:00 UTC should be 10:00 in LA (PDT is UTC-7)
    assert local_dt.hour == 10
    assert local_dt.year == 2025 and local_dt.day == 26
