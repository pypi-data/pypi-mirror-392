import os
import csv
import json
import sqlite3
from typing import Union, List

from .database.connection import get_db_connection
from .utils.logger import logger


def to_csv(save_path: str, table_name: Union[List[str], str, None] = None):
    """
    Xuất dữ liệu từ database ra CSV (dùng csv chuẩn Python).

    Args:
        save_path (str): Thư mục lưu file CSV.
        table_name (list[str] | str | None): Tên bảng hoặc danh sách bảng cần export.
                                             Nếu None, export tất cả bảng.
        conn: Kết nối database (sqlite3, pymysql, psycopg2).
    """

    os.makedirs(save_path, exist_ok=True)

    conn = get_db_connection()
    cursor = conn.cursor()

    # Lấy danh sách bảng nếu table_name=None
    if table_name is None:
        if isinstance(conn, sqlite3.Connection):
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
        else:
            cursor.execute("SHOW TABLES;")
            tables = [row[0] for row in cursor.fetchall()]
    elif isinstance(table_name, str):
        tables = [table_name]
    else:
        tables = table_name

    for table in tables:
        cursor.execute(f"SELECT * FROM {table}")
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()

        csv_file = os.path.join(save_path, f"{table}.csv")
        with open(csv_file, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(columns)  # header
            writer.writerows(rows)    # dữ liệu

        logger.info(f"Exported table {table} to {csv_file}")


def to_json(save_path: str, table_name: Union[List[str], str, None] = None):
    """
    Xuất dữ liệu từ database ra JSON (dùng json chuẩn Python).

    Args:
        save_path (str): Thư mục lưu file JSON.
        table_name (list[str] | str | None): Tên bảng hoặc danh sách bảng cần export.
                                             Nếu None, export tất cả bảng.
        conn: Kết nối database (sqlite3, pymysql, psycopg2).
    """

    os.makedirs(save_path, exist_ok=True)

    conn = get_db_connection()
    cursor = conn.cursor()

    # Lấy danh sách bảng nếu table_name=None
    if table_name is None:
        if isinstance(conn, sqlite3.Connection):
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
        else:
            cursor.execute("SHOW TABLES;")
            tables = [row[0] for row in cursor.fetchall()]
    elif isinstance(table_name, str):
        tables = [table_name]
    else:
        tables = table_name

    for table in tables:
        cursor.execute(f"SELECT * FROM {table}")
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()

        data = [dict(zip(columns, row)) for row in rows]

        json_file = os.path.join(save_path, f"{table}.json")
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        logger.info(f"Exported table {table} to {json_file}")
