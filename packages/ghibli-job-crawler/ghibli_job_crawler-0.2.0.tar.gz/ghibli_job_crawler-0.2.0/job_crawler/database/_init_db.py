from .connection import get_db_connection
from ..utils.logger import logger


def init_database() -> None:
    conn = get_db_connection()
    cursor = conn.cursor()


    # Bảng Account
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS account (
        AccountID INTEGER PRIMARY KEY AUTOINCREMENT,
        Email TEXT NOT NULL UNIQUE,
        PasswordHash TEXT NOT NULL,
        Created_At TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        IsNotification BOOLEAN NOT NULL DEFAULT 1,
        Role TEXT NOT NULL DEFAULT 'user'
    );
    """)

    # Bảng Company
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS company (
        CompanyID INTEGER PRIMARY KEY AUTOINCREMENT,
        Name TEXT NOT NULL,
        Location TEXT,
        Company_Industry TEXT,
        Scale TEXT
    );
    """)

    # Bảng Source
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS source (
        SourceID INTEGER PRIMARY KEY AUTOINCREMENT,
        Name TEXT NOT NULL,
        URL TEXT NOT NULL,
        Required_Login BOOLEAN DEFAULT 0
    );
    """)

    # Bảng CrawlRecord
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS crawlrecord (
        CrawlID INTEGER PRIMARY KEY AUTOINCREMENT,
        SourceID INTEGER,
        CrawlDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        Status TEXT DEFAULT 'success',  -- success, failed, stopped, empty
        Message TEXT,
        FOREIGN KEY (SourceID) REFERENCES source(SourceID) ON UPDATE CASCADE ON DELETE SET NULL
    );
    """)

    # Bảng Job
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS job (
        JobID INTEGER PRIMARY KEY AUTOINCREMENT,
        CompanyID INTEGER,
        CrawlID INTEGER,
        Name TEXT NOT NULL,
        Salary TEXT,
        Experience INTEGER,
        Education_Level INTEGER,
        Location TEXT,
        Position_Level TEXT,
        Job_Type TEXT,
        Deadline_Submission DATE,
        Quantity INTEGER DEFAULT 1,
        Job_Link TEXT,
        Description TEXT,
        Required TEXT,
        IsNew INTEGER,
        FOREIGN KEY (CompanyID) REFERENCES company(CompanyID) ON UPDATE CASCADE ON DELETE CASCADE,
        FOREIGN KEY (CrawlID) REFERENCES crawlrecord(CrawlID) ON UPDATE CASCADE ON DELETE SET NULL
    );
    """)

    # Bảng SavedJob
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS saved_job (
        SaveID INTEGER PRIMARY KEY AUTOINCREMENT,
        AccountID INTEGER,
        JobID INTEGER,
        Date_Saved TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (AccountID) REFERENCES account(AccountID) ON DELETE CASCADE,
        FOREIGN KEY (JobID) REFERENCES job(JobID) ON DELETE CASCADE,
        UNIQUE(AccountID, JobID)
    );
    """)


    conn.commit()
    conn.close()
    logger.info("✅ Database và các bảng đã được tạo thành công!")