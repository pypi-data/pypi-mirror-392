import re
import time
import random
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock, Event

import requests

from .database.handlers import (
    create_crawl_record, 
    update_crawl_record, 
    save_jobs_to_db,
    get_all_job_names
)
from .utils.notification_handler import NotificationHandler
from .utils.logger import logger


class VietnamWorksCrawler:
    def __init__(self, max_workers: int = 5) -> None:
        """
        Args:
            max_workers: Số lượng crawl đồng thời (mặc định 5)
        """
        self.api_url = "https://ms.vietnamworks.com/job-search/v1.0/search"
        self.source_name = "VietnamWorks"
        self.source_url = "https://www.vietnamworks.com"
        self.max_workers = max_workers
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
            'Content-Type': 'application/json',
            'Origin': 'https://www.vietnamworks.com',
            'Referer': 'https://www.vietnamworks.com/'
        })
        
        # Cache existing jobs để giảm query DB
        self._existing_jobs_cache = None
        self._cache_lock = Lock()  # Lock để thread-safe khi thêm vào cache
        
        # Stop event để dừng crawler
        self._stop_event = Event()
        
        # CrawlID cho lần crawl hiện tại
        self._current_crawl_id = None
        
        # ✅ THÊM NOTIFICATION HANDLER
        self.notification_handler = NotificationHandler()

    def stop(self) -> None:
        """Dừng crawler"""
        logger.info("🛑 Đang dừng crawler...")
        self._stop_event.set()

    def is_stopped(self) -> bool:
        """Kiểm tra xem crawler đã dừng chưa"""
        return self._stop_event.is_set()
        
    def _load_existing_jobs_cache(self) -> None:
        """Load tất cả existing jobs vào memory 1 lần duy nhất"""
        if self._existing_jobs_cache is not None:
            return

        try:
            jobs = get_all_job_names()
            
            # Tạo set để tra cứu nhanh O(1)
            self._existing_jobs_cache = {
                (
                    job_name.strip().lower() if job_name else "", 
                    company_name.strip().lower() if company_name else ""
                )
                for job_name, company_name in jobs
            }
            logger.info(f"Đã load {len(self._existing_jobs_cache)} jobs vào cache")
        except Exception as e:
            logger.error(f"Lỗi khi load cache: {str(e)}")
            self._existing_jobs_cache = set()

    def check_and_add_to_cache(self, job_name: str, company_name: str) -> bool:
        """
        Kiểm tra và thêm job vào cache trong 1 thao tác atomic (thread-safe)
        Returns: True nếu job đã tồn tại, False nếu là job mới
        """

        if self._existing_jobs_cache is None:
            self._load_existing_jobs_cache()
        
        key = (job_name.strip().lower(), company_name.strip().lower())
        
        # CRITICAL: Kiểm tra và thêm phải trong cùng 1 lock
        with self._cache_lock:
            if key in self._existing_jobs_cache:
                return True  # Job đã tồn tại
            else:
                self._existing_jobs_cache.add(key)  # Thêm ngay
                return False  # Job mới

    def get_jobs_from_page(self, page_num: int) -> list[dict]:
        """Lấy danh sách công việc từ API theo page"""
        if self.is_stopped():
            return []
            
        payload = {
            "userId": 0,
            "query": "",
            "filter": [],
            "ranges": [],
            "order": [],
            "hitsPerPage": 50,
            "page": page_num,
            "retrieveFields": [
                "address", "benefits", "jobTitle", "salaryMax", 
                "salaryMin", "salaryCurrency", "prettySalary",
                "isSalaryVisible", "jobLevelVI", "isShowLogo",
                "workingLocations", "companyLogo", "companyName",
                "approvedOn", "jobUrl", "alias", "expiredOn",
                "industries", "industriesV3",
                "jobId", "companyId",
                "jobDescription", "jobRequirement"
            ],
            "summaryVersion": "",
        }
        
        try:
            response = self.session.post(self.api_url, json=payload, timeout=15)
            response.raise_for_status()
            data: dict = response.json()
            
            if data.get('meta', {}).get('code') == 200:
                jobs = data.get('data', [])
                return jobs
            else:
                logger.error(f"❌ API trả về lỗi page {page_num}: {data.get('meta', {}).get('message')}")
                return []
        except Exception as e:
            logger.error(f"❌ Lỗi khi gọi API trang {page_num}: {str(e)}")
            return []

    def extract_job_details(self, job_data: dict) -> dict | None:
        """Parse thông tin chi tiết từ JSON response"""
        if self.is_stopped():
            return None
            
        try:
            name = job_data.get('jobTitle', 'N/A')
            company_name = job_data.get('companyName', 'N/A')
            
            # Kiểm tra trùng lặp và thêm vào cache trong 1 thao tác atomic
            if self.check_and_add_to_cache(name, company_name):
                return None  # Job đã tồn tại, bỏ qua
            
            # Location từ cityNameVI trong workingLocations
            locations = []
            working_locations = job_data.get('workingLocations', [])
            if working_locations and isinstance(working_locations, list):
                for loc in working_locations:
                    if isinstance(loc, dict):
                        city_name = loc.get('cityNameVI', '')
                        if city_name:
                            locations.append(city_name)
            location = ', '.join(locations) if locations else 'Toàn quốc'
            
            # Job type
            type_working_id = job_data.get('typeWorkingId', 1)
            job_type = 'Toàn thời gian' if type_working_id == "1" else 'Bán thời gian'
            
            # Experience
            experience = self.extract_experience_from_requirement(job_data.get('jobRequirement', ''))
            
            # Salary
            salary = job_data.get('prettySalary', 'Thương lượng')
            
            # Position level
            position_level = job_data.get('jobLevelVI', 'N/A')
            
            # Education level
            education_level = 'Cử nhân'
            
            # Quantity
            quantity = f"{random.randint(1, 3)} người"
            
            # Deadline
            expired_on = job_data.get('expiredOn', '')
            deadline = self.parse_deadline(expired_on)
            
            # Company location
            company_location = job_data.get('address', 'N/A')
            
            # Industry
            industries_list = []
            industries = job_data.get('industriesV3', [])
            if industries and isinstance(industries, list):
                for industry in industries:
                    if isinstance(industry, dict):
                        industry_name = industry.get('industryV3NameVI', '')
                        if industry_name:
                            industries_list.append(industry_name)
            company_industry = ', '.join(industries_list) if industries_list else 'N/A'
            
            # Company scale
            company_scale = 'Không hiển thị'

            # Description và Required
            description = self.clean_html(job_data.get('jobDescription', ''))
            required = self.clean_html(job_data.get('jobRequirement', ''))
            
            # Job link
            job_link = job_data.get('jobUrl', '')

            job_info = {
                'name': name,
                'salary': salary,
                'experience': experience,
                'education_level': education_level,
                'location': location,
                'position_level': position_level,
                'job_type': job_type,
                'deadline_submission': deadline,
                'quantity': quantity,
                'description': description,
                'required': required,
                'company_name': company_name,
                'company_location': company_location,
                'company_industry': company_industry,
                'company_scale': company_scale,
                'job_link': job_link
            }
            
            return job_info
        except Exception as e:
            logger.error(f"❌ Lỗi khi parse job data: {str(e)}")
            return None

    def extract_experience_from_requirement(self, job_requirement: str) -> str:
        """Extract số năm kinh nghiệm từ jobRequirement"""
        if not job_requirement:
            return 'Không yêu cầu'
        
        text = self.clean_html(job_requirement)
        
        # Pattern 1: "X years" hoặc "X year"
        match = re.search(r'(\d+)\s*(?:years?|Years?|YEARS?)', text)
        if match:
            years = match.group(1)
            return f'{years} năm'
        
        # Pattern 2: "X năm"
        match = re.search(r'(\d+)\s*(?:năm|Năm)', text)
        if match:
            years = match.group(1)
            return f'{years} năm'
        
        # Kiểm tra các keyword không yêu cầu kinh nghiệm
        no_exp_keywords = ['no experience', 'không yêu cầu', 'không cần', 'fresher', 'entry level']
        text_lower = text.lower()
        for keyword in no_exp_keywords:
            if keyword in text_lower:
                return 'Không yêu cầu'
        
        return 'Không yêu cầu'

    def parse_deadline(self, expired_on_str: str) -> str:
        """Parse deadline từ ISO format"""
        if not expired_on_str:
            return 'Không giới hạn'
        try:
            dt = datetime.fromisoformat(expired_on_str.replace('+07:00', ''))
            return dt.strftime('%d/%m/%Y')
        except:
            return 'Không giới hạn'

    def clean_html(self, html_text: any) -> str:
        """Remove HTML tags và clean text"""
        if html_text is None or not html_text:
            return ''
    
        if not isinstance(html_text, str):
          html_text = str(html_text)
    
        # Thay thế </p> bằng newline
        text = html_text.replace('</p>', '\n')
    
        # Thay thế <br>, <br/> bằng newline
        text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
    
        # Remove tất cả HTML tags
        text = re.sub(r'<[^>]+>', '', text)
    
        # Decode HTML entities
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&amp;', '&')
        text = text.replace('&quot;', '"')
        
        # Clean whitespace
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            line = re.sub(r'\s+', ' ', line).strip()
            if line:
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
        
    def crawl_page_wrapper(self, page_num: int) -> tuple[int, list[dict]]:
        """Wrapper để crawl 1 page (dùng cho threading)"""
        if self.is_stopped():
            return page_num, []
            
        time.sleep(random.uniform(0.3, 0.8))  # Random delay nhẹ
        
        jobs_data = self.get_jobs_from_page(page_num)
        crawled_jobs = []
        
        for job_data in jobs_data:
            if self.is_stopped():
                break
                
            job_info = self.extract_job_details(job_data)
            if job_info:
                crawled_jobs.append(job_info)
        
        return page_num, crawled_jobs

    def crawl_jobs(self, start_page: int = 0, end_page: int = 2):
        """
        Hàm chính để crawl công việc từ VietnamWorks với threading
        
        Args:
            start_page: Trang bắt đầu (0-indexed)
            end_page: Trang kết thúc
        
        Returns:
            Danh sách các công việc đã crawl thành công
        """
        logger.info(f"\n{'='*80}")
        logger.info(f"🚀 Bắt đầu crawl từ {self.source_name} (song song {self.max_workers} luồng)")
        logger.info(f"{'='*80}")
        
        # Reset stop event
        self._stop_event.clear()
        
        # ✅ TẠO CRAWL RECORD NGAY KHI BẮT ĐẦU
        try:
            self._current_crawl_id = create_crawl_record(self.source_name, self.source_url)
        except Exception as e:
            logger.error(f"❌ Không thể tạo CrawlRecord: {e}")
            return []
        
        # Load cache trước
        self._load_existing_jobs_cache()
        
        # Crawl song song theo page
        all_crawled_jobs = []
        
        try:
            skipped = 0
            pages = list(range(start_page, end_page + 1))
            
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                future_to_page = {
                    executor.submit(self.crawl_page_wrapper, page): page 
                    for page in pages
                }
                
                for future in as_completed(future_to_page):
                    if self.is_stopped():
                        logger.debug("🛑 Đang hủy các task đang chạy...")
                        executor.shutdown(wait=False, cancel_futures=True)
                        break
                        
                    page_num, page_jobs = future.result()
                    
                    if page_jobs:
                        for job in page_jobs:
                            all_crawled_jobs.append(job)
                            logger.info(f"✅ [Page {page_num}] {job['name']}")
                        
                        skipped += (len(page_jobs) - len([j for j in page_jobs if j in all_crawled_jobs]))
                    else:
                        logger.debug(f"⚠️  [Page {page_num}] Không có job mới")
            
            if self.is_stopped():
                update_crawl_record(
                    self._current_crawl_id, 
                    status='stopped',
                    jobs_count=len(all_crawled_jobs)
                )
                logger.info(f"🛑 Crawler đã dừng. Đã crawl được {len(all_crawled_jobs)} jobs trước khi dừng")
                
                if all_crawled_jobs:
                    logger.info(f"Đang lưu {len(all_crawled_jobs)} công việc đã crawl được...")
                    save_jobs_to_db(all_crawled_jobs, self._current_crawl_id)
                
                return all_crawled_jobs
            
            logger.info(f"\n📊 Tổng kết: Crawl được {len(all_crawled_jobs)} jobs, bỏ qua {skipped} jobs trùng lặp")

            # Lưu vào database
            if all_crawled_jobs:
                logger.info(f"\n💾 Đang lưu {len(all_crawled_jobs)} công việc vào database...")
                saved_count = save_jobs_to_db(all_crawled_jobs, self._current_crawl_id)
                
                update_crawl_record(
                    self._current_crawl_id, 
                    status='success',
                    jobs_count=saved_count
                )
                
                # ✅ GỬI EMAIL THÔNG BÁO SAU KHI CRAWL XONG
                logger.info("\n" + "="*80)
                logger.info("📧 ĐANG GỬI THÔNG BÁO EMAIL...")
                logger.info("="*80)
                try:
                    self.notification_handler.send_notifications_after_crawl(
                        crawl_id=self._current_crawl_id,
                        source_name=self.source_name
                    )
                except Exception as e:
                    logger.debug(f"⚠️ Lỗi khi gửi email (không ảnh hưởng crawl): {str(e)}")
                
                # CRITICAL: Reset cache để đồng bộ với database
                logger.info("🔄 Reset cache để đồng bộ với database...")
                self._existing_jobs_cache = None
            else:
                logger.debug("⚠️  Không có công việc mới để lưu")
                update_crawl_record(
                    self._current_crawl_id, 
                    status='empty',
                    message='Không có job mới để crawl',
                    jobs_count=0
                )

        except Exception as e:
            logger.error(f"\n❌ Lỗi trong quá trình crawl: {str(e)}")
            
            update_crawl_record(
                self._current_crawl_id, 
                status='failed',
                message=f'Lỗi: {str(e)}',
                jobs_count=len(all_crawled_jobs)
            )
            
            if all_crawled_jobs:
                logger.debug(f"Đang lưu {len(all_crawled_jobs)} jobs đã crawl được trước khi lỗi...")
                save_jobs_to_db(all_crawled_jobs, self._current_crawl_id)

        return all_crawled_jobs
