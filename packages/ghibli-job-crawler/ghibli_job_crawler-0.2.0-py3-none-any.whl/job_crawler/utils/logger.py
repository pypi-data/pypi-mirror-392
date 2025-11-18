from datetime import datetime


class logger:
    _printer = print

    @classmethod
    def now(cls) -> str:
        return datetime.now().isoformat()

    @classmethod
    def info(cls, msg: str):
        cls._printer(f"{cls.now()} [INFO] {msg}")

    @classmethod
    def debug(cls, msg: str):
        cls._printer(f"{cls.now()} [DEBUG] {msg}")

    @classmethod
    def warn(cls, msg: str):
        cls._printer(f"{cls.now()} [WARN] {msg}")

    @classmethod
    def error(cls, msg: str):
        cls._printer(f"{cls.now()} [ERROR] {msg}")

    @classmethod
    def fatal(cls, msg: str):
        cls._printer(f"{cls.now()} [FATAL] {msg}")    