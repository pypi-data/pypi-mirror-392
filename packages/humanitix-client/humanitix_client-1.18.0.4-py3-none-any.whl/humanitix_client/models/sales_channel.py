from enum import Enum


class SalesChannel(str, Enum):
    BOXOFFICE = "boxOffice"
    MANUAL = "manual"
    ONLINE = "online"

    def __str__(self) -> str:
        return str(self.value)
