from enum import Enum


class AccountRole(str, Enum):
    USER = "user"
    ADMIN = "admin"


class CrawlRecordStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
    STOPPED = "stopped"
    EMPTY = "empty"