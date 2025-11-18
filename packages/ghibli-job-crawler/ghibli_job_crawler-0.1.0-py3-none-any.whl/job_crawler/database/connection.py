import os
import sqlite3
from typing import Callable

import mysql.connector
import psycopg2
from dotenv import load_dotenv

from ..utils.logger import logger


load_dotenv()

DB_TYPE = os.getenv("DB_TYPE")
assert DB_TYPE is not None, "Database type 'DB_TYPE' is not set in your environments variables."
assert DB_TYPE in ["sqlite", "postgres", "mysql"], "Database type is not support."

if DB_TYPE == "sqlite":
    DB_PATH = os.getenv("DB_PATH")
    assert DB_PATH is not None, "Database path 'DB_PATH' is not set for sqlite."
else:
    HOST = os.getenv("DB_HOST")
    assert HOST is not None, "Database Host 'DB_HOST' is not set in your environment variables."
    USER = os.getenv("DB_USERNAME")
    assert USER is not None, "Username 'DB_USERNAME' is not set in your environment variables."
    PASSWORD = os.getenv("DB_PASSWORD")
    assert PASSWORD is not None, "Password 'DB_PASSWORD' is not set in your environment variables."
    DATABASE = os.getenv("DB_NAME")
    assert DATABASE is not None, "Database name 'DB_NAME' is not set in your environment variables."
    PORT = os.getenv("DB_PORT")

connect: Callable[dict, any]
kwargs: dict
if DB_TYPE == "sqlite":
    connect = sqlite3.connect
    kwargs = {
        'database': DB_PATH,
        'timeout': 10
    }
elif DB_TYPE == "mysql":
    connect = mysql.connector.connect
    kwargs = {
        'host': HOST,
        'user': USER,
        'password': PASSWORD,
        'database': DATABASE    
    }
    if PORT is not None:
        kwargs.update({"port": PORT})
elif DB_TYPE == "postgres":
    connect = psycopg2.connect
    dns = ""
    kwargs = {
        'database': DATABASE, 
        'user': USER, 
        'password': PASSWORD,
        'host': HOST,
    }
    if PORT is not None:
        kwargs.update({"port": PORT})


def get_db_connection() -> any:
    try:
        conn = connect(**kwargs)

        logger.info("Connect to database successfully.")

        return conn
    except Exception as e:
        logger.error("Cann not connect to database.")
        raise e