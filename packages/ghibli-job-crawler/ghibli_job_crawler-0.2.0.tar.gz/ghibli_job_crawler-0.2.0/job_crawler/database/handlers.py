import re
import sqlite3
from datetime import datetime, timedelta

from .connection import get_db_connection
from .sql import execute_sql
from .models import *
from ..utils.logger import logger


# ========================= HELPER FUNCTIONS =========================

def _convert_str_to_date(date_str: str) -> str | None:
    """Chuyển đổi chuỗi ngày tháng (dd/mm/yyyy) sang chuỗi YYYY-MM-DD cho SQLite."""
    if not date_str or not isinstance(date_str, str):
        return None
    try:
        dt = datetime.strptime(date_str.strip(), '%d/%m/%Y')
        return dt.strftime('%Y-%m-%d')  # Trả chuỗi
    except ValueError:
        return None


def _parse_quantity(quantity_str: str) -> int:
    """Trích xuất số lượng từ chuỗi 'X người'."""

    if not quantity_str or not isinstance(quantity_str, str):
        return 1
    match = re.search(r'\d+', quantity_str)
    return int(match.group(0)) if match else 1


def _parse_scale(scale_str: str) -> int:
    """Trích xuất số lượng từ chuỗi quy mô."""

    if not scale_str or not isinstance(scale_str, str):
        return 0
    numbers = re.findall(r'\d+', scale_str)
    if numbers:
        return max(map(int, numbers))
    return 0

# ========================= ISNEW MANAGEMENT =========================

def reset_all_jobs_to_old() -> int:
    """
    Set all Job.IsNew = 0 in sqlite3.
    Call this function before crawling.
    """

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # UPDATE tất cả job đang có IsNew = 1
        execute_sql(
            cursor,
            "UPDATE job SET IsNew = 0 WHERE IsNew = 1;",
            fetch=None
        )

        conn.commit()

        # Lấy số dòng bị ảnh hưởng
        updated_count = cursor.rowcount

        logger.info(f"✅ Đã reset {updated_count} jobs về IsNew=0")
        return updated_count

    except sqlite3.Error as e:
        conn.rollback()
        logger.error(f"❌ Lỗi khi reset IsNew: {e}")
        return 0

    finally:
        conn.close()


def mark_jobs_as_old_by_source(source_name: str) -> int:
    """
    Chuyển các jobs thuộc 1 source nhất định về IsNew = 0
    """

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Bước 1: Select danh sách JobID -> dùng subquery
        job_ids = execute_sql(
            cursor,
            """
            SELECT job.JobID
            FROM job
            JOIN crawlrecord ON job.CrawlID = crawlrecord.CrawlID
            JOIN source ON crawlrecord.SourceID = source.SourceID
            WHERE source.Name = ? AND job.IsNew = 1;
            """,
            params=(source_name,),
            fetch="all"
        )

        # Nếu không có job nào → không cần update
        if not job_ids:
            logger.debug(f"ℹ️ Không có job nào của source '{source_name}' cần reset.")
            return 0

        # Chuyển list tuple -> list id
        job_ids = [row[0] for row in job_ids]

        # Bước 2: Update bằng mảng IN (...)
        placeholders = ",".join("?" for _ in job_ids)

        execute_sql(
            cursor,
            f"UPDATE job SET IsNew = 0 WHERE JobID IN ({placeholders});",
            params=tuple(job_ids),
            fetch=None
        )

        conn.commit()

        updated = cursor.rowcount 

        logger.info(f"✅ Đã reset {updated} jobs từ source '{source_name}' về IsNew=0")
        return updated

    except sqlite3.Error as e:
        conn.rollback()
        logger.error(f"❌ Lỗi khi reset IsNew cho {source_name}: {e}")
        return 0

    finally:
        conn.close()


def get_new_jobs_count(crawl_id: int = None) -> int:
    """Đếm số lượng jobs có IsNew = 1 trong sqlite3"""

    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if not crawl_id:
            sql = "SELECT COUNT(*) FROM job WHERE IsNew = 1;"
        else:
            sql = "SELECT COUNT(*) FROM job WHERE IsNew = 1 and CrawlID = ?;"

        result = execute_sql(
            cursor,
            sql,
            fetch="one",
            params=(crawl_id,) if crawl_id else None
        )
        
        # result = (count,) → lấy result[0]
        return result[0] if result else 0

    finally:
        conn.close()

# ========================= USER MANAGEMENT =========================

def get_all_user_emails() -> list[str]:
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        emails = execute_sql(
            cursor,
            """
            SELECT Email FROM account
            WHERE Role = "user" and IsNotification = true
            """
        )

        return emails
    finally:
        conn.close()

# ========================= CRAWL RECORD MANAGEMENT =========================

def create_crawl_record(source_name: str, source_url: str, reset_old_jobs: bool = True) -> int:
    """
    Tạo CrawlRecord mới trong sqlite3 khi bắt đầu crawl.
    
    Returns:
        crawl_id (int)
    """

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # -----------------------------------------------
        # 1️⃣ Reset job cũ của source này (tuỳ chọn)
        # -----------------------------------------------
        if reset_old_jobs:
            mark_jobs_as_old_by_source(source_name)

        # -----------------------------------------------
        # 2️⃣ Kiểm tra xem source đã tồn tại chưa
        # -----------------------------------------------
        source_row = execute_sql(
            cursor,
            "SELECT SourceID FROM source WHERE Name = ?;",
            params=(source_name,),
            fetch="one"
        )

        if source_row:
            source_id = source_row[0]
        else:
            # Insert source mới
            execute_sql(
                cursor,
                "INSERT INTO source (Name, URL, Required_Login) VALUES (?, ?, 0);",
                params=(source_name, source_url),
                fetch=None
            )
            source_id = cursor.lastrowid

        # -----------------------------------------------
        # 3️⃣ Tạo CrawlRecord mới
        # -----------------------------------------------
        now = datetime.now().isoformat()

        execute_sql(
            cursor,
            """
            INSERT INTO crawlrecord (SourceID, CrawlDate, Status, Message)
            VALUES (?, ?, ?, ?);
            """,
            params=(source_id, now, "success", "Crawling in progress..."),
            fetch=None
        )

        crawl_id = cursor.lastrowid

        conn.commit()

        logger.info(f"✅ Đã tạo CrawlRecord ID: {crawl_id}")
        return crawl_id

    except sqlite3.Error as e:
        conn.rollback()
        logger.error(f"❌ Lỗi khi tạo CrawlRecord: {e}")
        raise

    finally:
        conn.close()


def update_crawl_record(crawl_id: int, status: str, message: str = None, jobs_count: int = 0) -> bool:
    """
    Cập nhật trạng thái của CrawlRecord trong sqlite3.

    Args:
        crawl_id (int): ID của crawl record cần cập nhật.
        status (str): 'success', 'failed', hoặc 'stopped'.
        message (str, optional): Thông báo chi tiết. Nếu None thì tự sinh.
        jobs_count (int): Số lượng jobs đã thu thập được.

    Returns:
        bool: True nếu cập nhật thành công, False nếu thất bại hoặc không tìm thấy record.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # 1️⃣ Kiểm tra CrawlRecord tồn tại
        row = execute_sql(
            cursor,
            "SELECT CrawlID FROM crawlrecord WHERE CrawlID = ?;",
            params=(crawl_id,),
            fetch="one"
        )

        if not row:
            logger.warn(f"⚠️ Không tìm thấy CrawlRecord ID {crawl_id}")
            return False

        # 2️⃣ Sinh message nếu cần
        if not message:
            if status == "success":
                message = f"Crawl thành công {jobs_count} jobs mới"
            elif status == "failed":
                message = f"Crawl thất bại sau khi thu thập {jobs_count} jobs"
            elif status == "stopped":
                message = f"Crawl bị dừng bởi người dùng. Đã thu thập {jobs_count} jobs"
            else:
                message = "Trạng thái không xác định"

        # 3️⃣ Update CrawlRecord
        execute_sql(
            cursor,
            "UPDATE crawlrecord SET Status = ?, Message = ? WHERE CrawlID = ?;",
            params=(status, message, crawl_id),
            fetch=None
        )

        conn.commit()
        logger.info(f"✅ Đã cập nhật CrawlRecord ID {crawl_id} với trạng thái '{status}'")
        return True

    except sqlite3.Error as e:
        conn.rollback()
        logger.error(f"❌ Lỗi khi update CrawlRecord ID {crawl_id}: {e}")
        return False

    finally:
        conn.close()


def get_or_create_source(source_name: str, source_url: str) -> Source:
    """
    Lấy hoặc tạo mới một Source trong sqlite3.

    Returns:
        int: SourceID
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Kiểm tra xem source đã tồn tại chưa
        row = execute_sql(
            cursor,
            "SELECT SourceID FROM source WHERE Name = ?;",
            params=(source_name,),
            fetch="one"
        )

        if not row:
            # Tạo mới source
            execute_sql(
                cursor,
                "INSERT INTO source (Name, URL, Required_Login) VALUES (?, ?, 0);",
                params=(source_name, source_url),
                fetch=None
            )
            source = Source(
                SourceID=cursor.lastrowid,
                Name=source_name,
                URL=source_url
            )
            conn.commit()
        else: 
            source = Source(
                SourceID=row[0],
                Name=row[1],
                URL=row[2],
                Required_Login=row[3],
            )

        return source

    except sqlite3.Error as e:
        conn.rollback()
        logger.error(f"❌ Lỗi khi get_or_create_source: {e}")
        raise

    finally:
        conn.close()


def get_or_create_company(job_data: dict) -> Company | None:
    """
    Lấy hoặc tạo mới một Company trong sqlite3.

    Returns:
        int: CompanyID nếu tồn tại hoặc được tạo mới, None nếu không có company_name.
    """
    company_name = job_data.get("company_name")
    if not company_name:
        return None

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Kiểm tra xem công ty đã tồn tại chưa
        row = execute_sql(
            cursor,
            "SELECT CompanyID FROM company WHERE Name = ?;",
            params=(company_name,),
            fetch="one"
        )

        if row:
            company = Company(
                CompanyID=row[0],
                Name=row[1],
                Location=row[2],
                Company_Industry=row[3],
                Scale=row[4],
            )
        else:
            # Tạo mới công ty
            execute_sql(
                cursor,
                """
                INSERT INTO company (Name, Location, Company_Industry, Scale)
                VALUES (?, ?, ?, ?);
                """,
                params=(
                    company_name,
                    job_data.get("company_location"),
                    job_data.get("company_industry"),
                    _parse_scale(job_data.get("company_scale"))
                ),
                fetch=None
            )

            company = Company(
                CompanyID=cursor.lastrowid,
                Name=company_name,
                Location=job_data.get('company_location'),
                Company_Industry=job_data.get("company_industry"),
            )

            conn.commit()

        return company

    except sqlite3.Error as e:
        conn.rollback()
        logger.error(f"❌ Lỗi khi get_or_create_company: {e}")
        raise

    finally:
        conn.close()


def save_jobs_to_db(crawled_jobs: list[dict], crawl_id: int) -> int:
    """
    Lưu jobs vào SQLite với CrawlID đã có sẵn.
    ✅ TẤT CẢ JOBS MỚI SẼ CÓ IsNew=1
    """
    if not crawled_jobs:
        return 0

    conn = get_db_connection()
    cursor = conn.cursor()
    saved_count = 0

    try:
        # 1️⃣ Kiểm tra CrawlRecord tồn tại
        cursor.execute("SELECT CrawlID FROM crawlrecord WHERE CrawlID = ?", (crawl_id,))
        crawl_row = cursor.fetchone()
        if not crawl_row:
            logger.debug(f"❌ Không tìm thấy CrawlRecord với ID {crawl_id}")
            return 0

        # 2️⃣ Lặp từng job
        for job_data in crawled_jobs:
            job_link = job_data.get("job_link")
            if not job_link:
                continue

            # Kiểm tra job đã tồn tại
            cursor.execute("SELECT JobID FROM job WHERE Job_Link = ?", (job_link,))
            if cursor.fetchone():
                continue

            # 3️⃣ Lấy hoặc tạo company
            company_name = job_data.get("company_name")
            company_location = job_data.get("company_location")
            company_industry = job_data.get("company_industry")
            company_scale = _parse_scale(job_data.get("company_scale"))

            # Lấy CompanyID nếu đã có
            cursor.execute("SELECT CompanyID FROM company WHERE Name = ?", (company_name,))
            row = cursor.fetchone()
            if row:
                company_id = row[0]
            else:
                cursor.execute(
                    "INSERT INTO company (Name, Location, Company_Industry, Scale) VALUES (?, ?, ?, ?)",
                    (company_name, company_location, company_industry, company_scale)
                )
                company_id = cursor.lastrowid

            # 4️⃣ Chèn job mới
            cursor.execute(
                """
                INSERT INTO job (
                    Name, Salary, Experience, Education_Level, Location,
                    Position_Level, Job_Type, Deadline_Submission, Quantity,
                    Job_Link, Description, Required, IsNew, CompanyID, CrawlID
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    job_data.get("name"),
                    job_data.get("salary"),
                    job_data.get("experience"),
                    job_data.get("education_level"),
                    job_data.get("location"),
                    job_data.get("position_level"),
                    job_data.get("job_type"),
                    _convert_str_to_date(job_data.get("deadline_submission")),
                    _parse_quantity(job_data.get("quantity")),
                    job_link,
                    job_data.get("description"),
                    job_data.get("required"),
                    1,  # IsNew=1
                    company_id,
                    crawl_id
                )
            )

            saved_count += 1

        conn.commit()
        logger.info(f"✅ Đã lưu {saved_count} jobs MỚI vào database")
        return saved_count

    except Exception as e:
        conn.rollback()
        logger.error(f"❌ Lỗi khi lưu jobs. Rollback...")
        logger.error(f"Chi tiết: {e}")
        return 0

    finally:
        conn.close()


# ========================= APP DATABASE OPERATIONS =========================

def get_all_job_names(only_new: bool = False) -> list[tuple[str, str]]:
    """
    Lấy tất cả tên jobs cùng thông tin company.
    """

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        sql = """
        SELECT 
            j.Name,
            c.Name
        FROM job j 
        LEFT JOIN company c 
            ON j.CompanyID = c.CompanyID
        """

        params = None
        if only_new:
            sql += " WHERE j.IsNew = ?"
            params = (1,)

        rows = execute_sql(cursor, sql, params=params, fetch="all")
    
        return rows
    finally:
        conn.close()


def get_all_jobs(only_new: bool = False) -> list[tuple[Job, Company]]:
    """
    Lấy tất cả jobs cùng thông tin company.

    Args:
        only_new: Nếu True, chỉ lấy jobs có IsNew=1

    Returns:
        list[dict]: Danh sách jobs với thông tin company
    """

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        sql = """
        SELECT 
            j.*, 
            c.Name AS CompanyName, 
            c.Location AS CompanyLocation, 
            c.Company_Industry, 
            c.Scale 
        FROM job j 
        LEFT JOIN company c 
        ON j.CompanyID = c.CompanyID
        """

        params = ()
        if only_new:
            sql += " WHERE j.IsNew = ?"
            params = (1,)

        rows = execute_sql(cursor, sql, params=params, fetch="all")

        # Chuyển thành dict
        jobs = []
        for r in rows:
            job = Job(
                JobID=r[0],
                CompanyID=r[1],
                CrawlID=r[2],
                Name=r[3],
                Salary=r[4],
                Experience=r[5],
                Education_Level=r[6],
                Location=r[7],
                Position_Level=r[8],
                Job_Type=r[9],
                Deadline_Submission=r[9],
                Quantity=r[10],
                Job_Link=r[11],
                Description=r[12],
                Required=r[13],
                IsNew=r[14],
            )
            company_job = Company(
                CompanyID=r[1],
                Name=r[15],
                Location=r[16],
                Company_Industry=r[17],
                Scale=r[18]
            )
            jobs.append((job, company_job))

        return jobs
    finally:
        conn.close()


def search_jobs(keyword: str = None, company_filter: str = None, location_filter: str = None, only_new: bool = False) -> list[dict]:
    """
    Tìm kiếm jobs theo nhiều tiêu chí.

    Args:
        keyword: Từ khóa tìm kiếm trong Name, Description, Required
        company_filter: Lọc theo tên công ty
        location_filter: Lọc theo location
        only_new: Nếu True, chỉ tìm trong jobs mới

    Returns:
        list[dict]: Danh sách jobs khớp
    """

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        sql = """
        SELECT 
            j.*, 
            c.Name AS CompanyName, 
            c.Location AS CompanyLocation, 
            c.Company_Industry, 
            c.Scale 
        FROM job j 
        LEFT JOIN company c 
        ON j.CompanyID = c.CompanyID
        WHERE 1=1
        """
        params = []

        if only_new:
            sql += " AND j.IsNew = ?"
            params.append(1)

        if keyword:
            sql += " AND (j.Name LIKE ? OR j.Description LIKE ? OR j.Required LIKE ?)"
            kw = f"%{keyword}%"
            params.extend([kw, kw, kw])

        if company_filter:
            sql += " AND c.Name LIKE ?"
            params.append(f"%{company_filter}%")

        if location_filter:
            sql += " AND j.Location LIKE ?"
            params.append(f"%{location_filter}%")

        rows = execute_sql(cursor, sql, params=tuple(params), fetch="all")

        jobs = []
        for r in rows:
            job = Job(
                JobID=r[0],
                CompanyID=r[1],
                CrawlID=r[2],
                Name=r[3],
                Salary=r[4],
                Experience=r[5],
                Education_Level=r[6],
                Location=r[7],
                Position_Level=r[8],
                Job_Type=r[9],
                Deadline_Submission=r[9],
                Quantity=r[10],
                Job_Link=r[11],
                Description=r[12],
                Required=r[13],
                IsNew=r[14],
            )
            company_job = Company(
                CompanyID=r[1],
                Name=r[15],
                Location=r[16],
                Company_Industry=r[17],
                Scale=r[18]
            )
            jobs.append((job, company_job))

        return jobs
    finally:
        conn.close()


def update_job(job_id: int, update_data: dict) -> bool:
    """
    Cập nhật thông tin job.

    Args:
        job_id: ID của job cần cập nhật
        update_data: dict chứa key=value của các field cần update

    Returns:
        bool: True nếu cập nhật thành công, False nếu không tìm thấy hoặc lỗi
    """

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Kiểm tra job tồn tại
        row = execute_sql(
            cursor,
            "SELECT JobID FROM job WHERE JobID = ?;",
            params=(job_id,),
            fetch="one"
        )
        if not row:
            return False

        # Xây dựng câu lệnh UPDATE động
        fields = []
        params = []
        for key, value in update_data.items():
            if key in [
                "Name", "Salary", "Experience", "Education_Level", 
                "Location", "Position_Level", "Job_Type", "Deadline_Submission",
                "Quantity", "Job_Link", "Description", "Required", 
                "IsNew", "CompanyID", "CrawlID"
            ]:
                fields.append(f"{key} = ?")
                params.append(value)

        if not fields:
            return False

        sql = f"UPDATE job SET {', '.join(fields)} WHERE JobID = ?"
        params.append(job_id)

        execute_sql(cursor, sql, params=tuple(params), fetch=None)

        conn.commit()
        return True

    except Exception as e:
        conn.rollback()
        logger.error(f"❌ Lỗi khi update job: {e}")
        return False

    finally:
        conn.close()


def delete_job(job_id: int) -> bool:
    """
    Xóa job khỏi database.

    Args:
        job_id (int): ID của job cần xóa

    Returns:
        bool: True nếu xóa thành công, False nếu không tìm thấy hoặc lỗi
    """

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Kiểm tra job tồn tại
        row = execute_sql(
            cursor,
            "SELECT JobID FROM job WHERE JobID = ?;",
            params=(job_id,),
            fetch="one"
        )
        if not row:
            return False

        # Xóa job
        execute_sql(
            cursor,
            "DELETE FROM job WHERE JobID = ?;",
            params=(job_id,),
            fetch=None
        )
        conn.commit()
        return True

    except Exception as e:
        conn.rollback()
        logger.error(f"❌ Lỗi khi xóa job: {e}")
        return False

    finally:
        conn.close()


def get_all_companies() -> list[Company]:
    """
    Lấy tất cả companies.

    Returns:
        list[dict]: Danh sách companies
    """

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        rows = execute_sql(
            cursor,
            "SELECT * FROM company;",
            fetch="all"
        )

        companies = [
            Company(
                CompanyID=r[0],
                Name=r[1],
                Location=r[2],
                Company_Industry=r[3],
                Scale=r[4]
            )
            for r in rows
        ]
        
        return companies

    finally:
        conn.close()


def search_companies(keyword: str = None, industry_filter: str = None) -> list[Company]:
    """
    Tìm kiếm companies theo tên và ngành.

    Args:
        keyword: từ khóa tìm kiếm trong tên công ty
        industry_filter: lọc theo ngành (Company_Industry)

    Returns:
        list[dict]: Danh sách companies khớp
    """

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        sql = "SELECT * FROM company WHERE 1=1"
        params = []

        if keyword:
            sql += " AND Name LIKE ?"
            params.append(f"%{keyword}%")
        if industry_filter:
            sql += " AND Company_Industry LIKE ?"
            params.append(f"%{industry_filter}%")

        rows = execute_sql(cursor, sql, params=tuple(params), fetch="all")

        companies = [
            Company(
                CompanyID=r[0],
                Name=r[1],
                Location=r[2],
                Company_Industry=r[3],
                Scale=r[4]
            ) 
            for r in rows
        ]
        
        return companies

    finally:
        conn.close()


def update_company(company_id: int, update_data: dict) -> bool:
    """
    Cập nhật thông tin company.

    Args:
        company_id: ID của company cần cập nhật
        update_data: dict chứa key=value của các field cần update

    Returns:
        bool: True nếu cập nhật thành công, False nếu không tìm thấy hoặc lỗi
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Kiểm tra company tồn tại
        row = execute_sql(
            cursor,
            "SELECT CompanyID FROM company WHERE CompanyID = ?;",
            params=(company_id,),
            fetch="one"
        )
        if not row:
            return False

        # Xây dựng câu lệnh UPDATE động
        fields = []
        params = []
        for key, value in update_data.items():
            if key in ["Name", "Location", "Company_Industry", "Scale"]:
                fields.append(f"{key} = ?")
                params.append(value)

        if not fields:
            return False

        sql = f"UPDATE company SET {', '.join(fields)} WHERE CompanyID = ?"
        params.append(company_id)

        execute_sql(cursor, sql, params=tuple(params), fetch=None)
        conn.commit()
        return True

    except Exception as e:
        conn.rollback()
        logger.error(f"❌ Lỗi khi update company: {e}")
        return False

    finally:
        conn.close()


def delete_company(company_id: int) -> tuple[bool, str]:
    """
    Xóa company khỏi database, chỉ xóa nếu không còn job nào liên quan.

    Args:
        company_id: ID của company cần xóa

    Returns:
        tuple[bool, str]: (Thành công hay không, Thông báo)
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Kiểm tra company tồn tại
        row = execute_sql(
            cursor,
            "SELECT CompanyID FROM company WHERE CompanyID = ?;",
            params=(company_id,),
            fetch="one"
        )
        if not row:
            return False, "Company không tồn tại"

        # Kiểm tra xem còn job liên quan không
        job_row = execute_sql(
            cursor,
            "SELECT COUNT(*) FROM job WHERE CompanyID = ?;",
            params=(company_id,),
            fetch="one"
        )
        if job_row[0] > 0:
            return False, "Không thể xóa company đang có jobs"

        # Xóa company
        execute_sql(
            cursor,
            "DELETE FROM company WHERE CompanyID = ?;",
            params=(company_id,),
            fetch=None
        )
        conn.commit()
        return True, "Xóa thành công"

    except Exception as e:
        conn.rollback()
        logger.error(f"❌ Lỗi khi xóa company: {e}")
        return False, f"Lỗi: {str(e)}"

    finally:
        conn.close()


def get_crawl_statistics() -> list[dict]:
    """
    Thống kê crawl records theo source.

    Returns:
        list[dict]: Mỗi dict chứa SourceName, total_crawls, total_jobs, new_jobs
    """

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        sql = """
        SELECT 
            s.Name AS SourceName,
            COUNT(DISTINCT cr.CrawlID) AS total_crawls,
            COUNT(j.JobID) AS total_jobs,
            SUM(CASE WHEN j.IsNew = 1 THEN 1 ELSE 0 END) AS new_jobs
        FROM source s
        LEFT JOIN crawlrecord cr ON s.SourceID = cr.SourceID
        LEFT JOIN job j ON cr.CrawlID = j.CrawlID
        GROUP BY s.Name
        """
        rows = execute_sql(cursor, sql, fetch="all")

        stats = []
        for r in rows:
            stats.append({
                "SourceName": r[0],
                "total_crawls": r[1],
                "total_jobs": r[2],
                "new_jobs": r[3] if r[3] is not None else 0
            })
        return stats

    finally:
        conn.close()


def get_recent_crawl_activity(days: int = 7) -> list[dict]:
    """
    Hoạt động crawl gần đây.

    Args:
        days: Số ngày gần đây để thống kê

    Returns:
        list[dict]: Mỗi dict chứa CrawlDate, SourceName, Status, jobs_crawled, new_jobs
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        since_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")

        sql = """
        SELECT 
            cr.CrawlDate,
            s.Name AS SourceName,
            cr.Status,
            COUNT(j.JobID) AS jobs_crawled,
            SUM(CASE WHEN j.IsNew = 1 THEN 1 ELSE 0 END) AS new_jobs
        FROM crawlrecord cr
        LEFT JOIN source s ON cr.SourceID = s.SourceID
        LEFT JOIN job j ON cr.CrawlID = j.CrawlID
        WHERE cr.CrawlDate >= ?
        GROUP BY cr.CrawlID, s.Name, cr.Status
        ORDER BY cr.CrawlDate DESC
        """
        rows = execute_sql(cursor, sql, params=(since_date,), fetch="all")

        activity = []
        for r in rows:
            activity.append({
                "CrawlDate": r[0],
                "SourceName": r[1],
                "Status": r[2],
                "jobs_crawled": r[3],
                "new_jobs": r[4] if r[4] is not None else 0
            })
        return activity

    finally:
        conn.close()


def get_jobs_by_source() -> list[dict]:
    """
    Lấy số lượng jobs theo source, bao gồm tổng jobs và jobs mới (IsNew=1).

    Returns:
        list[dict]: Mỗi dict chứa SourceName, job_count, new_jobs
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        sql = """
        SELECT 
            s.Name AS SourceName,
            COUNT(j.JobID) AS job_count,
            SUM(CASE WHEN j.IsNew = 1 THEN 1 ELSE 0 END) AS new_jobs
        FROM source s
        JOIN crawlrecord cr ON s.SourceID = cr.SourceID
        JOIN job j ON cr.CrawlID = j.CrawlID
        GROUP BY s.Name
        """
        rows = execute_sql(cursor, sql, fetch="all")

        result = []
        for r in rows:
            result.append({
                "SourceName": r[0],
                "job_count": r[1],
                "new_jobs": r[2] if r[2] is not None else 0
            })
        return result

    finally:
        conn.close()


def get_jobs_paginated(
    page: int = 1,
    per_page: int = 50,
    keyword: str = None,
    company_filter: str = None,
    location_filter: str = None,
    only_new: bool = False
) -> tuple[list[dict], int]:
    """
    Lấy jobs với phân trang, có thể filter theo keyword, company, location, và IsNew.

    Returns:
        tuple[list[dict], int]: (danh sách jobs, tổng số jobs khớp điều kiện)
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        sql_base = """
        FROM job j
        LEFT JOIN company c ON j.CompanyID = c.CompanyID
        WHERE 1=1
        """
        params = []

        # Lọc theo IsNew
        if only_new:
            sql_base += " AND j.IsNew = ?"
            params.append(1)

        # Lọc theo keyword
        if keyword:
            sql_base += " AND (j.Name LIKE ? OR j.Description LIKE ? OR j.Required LIKE ?)"
            kw = f"%{keyword}%"
            params.extend([kw, kw, kw])

        # Lọc theo company
        if company_filter:
            sql_base += " AND c.Name LIKE ?"
            params.append(f"%{company_filter}%")

        # Lọc theo location
        if location_filter:
            sql_base += " AND j.Location LIKE ?"
            params.append(f"%{location_filter}%")

        # Tổng số jobs
        count_sql = f"SELECT COUNT(*) {sql_base};"
        total_row = execute_sql(cursor, count_sql, params=tuple(params), fetch="one")
        total = total_row[0] if total_row else 0

        # Phân trang
        offset = (page - 1) * per_page
        data_sql = f"""
        SELECT 
            j.*, 
            c.Name AS CompanyName, 
            c.Location AS CompanyLocation, 
            c.Company_Industry, 
            c.Scale 
        {sql_base}
        ORDER BY j.JobID DESC
        LIMIT ? OFFSET ?;
        """
        params.extend([per_page, offset])

        rows = execute_sql(cursor, data_sql, params=tuple(params), fetch="all")

        jobs = []
        for r in rows:
            job = Job(
                JobID=r[0],
                CompanyID=r[1],
                CrawlID=r[2],
                Name=r[3],
                Salary=r[4],
                Experience=r[5],
                Education_Level=r[6],
                Location=r[7],
                Position_Level=r[8],
                Job_Type=r[9],
                Deadline_Submission=r[9],
                Quantity=r[10],
                Job_Link=r[11],
                Description=r[12],
                Required=r[13],
                IsNew=r[14],
            )
            company_job = Company(
                CompanyID=r[1],
                Name=r[15],
                Location=r[16],
                Company_Industry=r[17],
                Scale=r[18]
            )
            jobs.append((job, company_job))

        return jobs, total

    finally:
        conn.close()


def get_companies_paginated(
    page: int = 1,
    per_page: int = 50,
    keyword: str = None,
    industry_filter: str = None
) -> tuple[list[Company], int]:
    """
    Lấy companies với phân trang và filter theo tên hoặc ngành.

    Args:
        page: Trang hiện tại (bắt đầu từ 1)
        per_page: Số bản ghi mỗi trang
        keyword: Từ khóa tìm kiếm trong tên company
        industry_filter: Lọc theo ngành (Company_Industry)

    Returns:
        tuple[list[dict], int]: (Danh sách companies, tổng số companies khớp điều kiện)
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        sql_base = "FROM company WHERE 1=1"
        params = []

        if keyword:
            sql_base += " AND Name LIKE ?"
            params.append(f"%{keyword}%")

        if industry_filter:
            sql_base += " AND Company_Industry LIKE ?"
            params.append(f"%{industry_filter}%")

        # Tổng số companies
        count_sql = f"SELECT COUNT(*) {sql_base};"
        total_row = execute_sql(cursor, count_sql, params=tuple(params), fetch="one")
        total = total_row[0] if total_row else 0

        # Phân trang
        offset = (page - 1) * per_page
        data_sql = f"""
        SELECT *
        {sql_base}
        ORDER BY CompanyID DESC
        LIMIT ? OFFSET ?;
        """
        params.extend([per_page, offset])

        rows = execute_sql(cursor, data_sql, params=tuple(params), fetch="all")

        companies = [
            Company(
                CompanyID=r[0],
                Name=r[1],
                Location=r[2],
                Company_Industry=r[3],
                Scale=r[4]
            )
            for r in rows
        ]
        
        return companies, total

    finally:
        conn.close()




