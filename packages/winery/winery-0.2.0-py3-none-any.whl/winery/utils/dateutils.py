from datetime import datetime, timezone
from typing import Union
from zoneinfo import ZoneInfo


class DateHelper:
    """
    A helper class to handle timezone-aware date and time operations.
    """

    def __init__(self, timezone: Union[ZoneInfo, str] = "Europe/London"):
        """
        Initialises the DateHelper with a specific timezone.

        :param ZoneInfo | str timezone: The timezone context for the winery,
                                        can be a string or ZoneInfo object.
                                        Defaults to "Europe/London".
        """
        if isinstance(timezone, str):
            self.timezone = ZoneInfo(timezone)
        else:
            self.timezone = timezone

    def now(self):
        """
        Returns the current date and time within the configured timezone.

        :return datetime: The current timezone-aware datetime object.
        """
        return datetime.now(self.timezone)

    def to_local_time(self, timestamp: Union[int, float]) -> datetime:
        """
        Converts a Unix timestamp to a datetime object in the configured timezone.

        :param int | float timestamp: The Unix timestamp (seconds since epoch).
        :return datetime: A timezone-aware datetime object corresponding to the timestamp.
        """
        return datetime.fromtimestamp(timestamp, tz=self.timezone)

    def ensure_timezone(self, dt: datetime) -> datetime:
        """
        Ensures a given datetime object is in the winery's timezone.

        If the datetime is naive (no timezone), it localises it.
        If it is aware (has timezone), it converts it.

        :param datetime dt: The datetime object to check or convert.
        :return datetime: The datetime object adjusted to the winery's timezone.
        """
        if dt.tzinfo is None:
            return dt.replace(tzinfo=self.timezone)
        return dt.astimezone(self.timezone)
