from pathlib import Path

from typing import Optional, Union
from zoneinfo import ZoneInfo
from .utils.dateutils import DateHelper
from .templates import WineryTemplateBackend
from .contracts import PersistenceContract


class Winery:
    def __init__(
        self,
        template_path: Union[Path, str],
        local_time: Union[ZoneInfo, str],
        persistant_backend: PersistenceContract | None = None,
        database_user: Optional[str] = "winery",
        database_password: Optional[str] = None,
        database_host: Optional[str] = None,
        database_name: Optional[str] = "winery",
        database_port: Optional[int] = 3306,
    ):
        self.template_path = self._template_path_exists(template_path)
        self.local_time = self._check_local_time(local_time)
        self.date_helper = DateHelper(self.local_time)
        self.database_user = database_user
        self.database_password = database_password
        self.database_host = database_host
        self.database_name = database_name
        self.database_port = database_port
        self.persistant_backend = (
            persistant_backend(self) if persistant_backend else None
        )

        self.winery_template_backend = WineryTemplateBackend(self, self.template_path)

    def _template_path_exists(self, template_path: str | Path):
        """_template_path_exists Checks and returns whether a template_path is valid or not.

        :param str | Path template_path: Given Winery Template Path.
        :raises ValueError: Template Path does not exist
        :return Path: Template Path as Path object.
        """
        if isinstance(template_path, str):
            template_path = Path(template_path)
        if not template_path.exists():
            raise ValueError("Template path not found.")
        return template_path

    def _check_local_time(self, local_time):
        """_check_local_time Checks if the specified local_time is correct.

        :param str | ZoneInfo local_time: local time as TimeZone.
        :return ZoneInfo: A valid ZoneInfo object.
        :raises ZoneInfoNotFoundError: If the specified local_time is faulty.
        """
        if isinstance(local_time, str):
            local_time = ZoneInfo(local_time)
        return local_time

    @property
    def templates(self):
        return self.winery_template_backend
