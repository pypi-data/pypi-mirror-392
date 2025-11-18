import sqlite3
from typing import Literal, Union, Any, Optional

from ..utils.logger import logger


def execute_sql(
    cursor: any,
    sql: str,
    fetch: Union[Literal["all", "one", "many"], int] = "all",
    params: Optional[tuple] = None,
) -> Any:
    """
    Execute SQL query using sqlite3 with flexible fetch options.

    Args:
        cursor (sqlite3.Cursor): Cursor của kết nối sqlite3.
        sql (str): Câu SQL cần thực thi.
        fetch (Literal["all", "one", "many"] or int): Kiểu trả kết quả:
            - "all": fetchall()
            - "one": fetchone()
            - "many": fetchmany()
            - int: fetch N rows
        params (tuple): Tham số truyền vào câu SQL (nếu có).

    Returns:
        Any: Kết quả truy vấn (list, tuple hoặc None).
    """

    if params is None:
        params = ()

    try:
        cursor.execute(sql, params)

        # Không fetch nếu là câu lệnh không trả dữ liệu (INSERT, UPDATE...)
        if cursor.description is None:
            return None

        if fetch == "all":
            return cursor.fetchall()

        elif fetch == "one":
            return cursor.fetchone()

        elif fetch == "many":
            return cursor.fetchmany(10)

        elif isinstance(fetch, int):
            return cursor.fetchmany(fetch)

        else:
            raise ValueError(f"Invalid fetch type: {fetch}")

    except sqlite3.Error as e:
        logger.error(str(e))
        raise
