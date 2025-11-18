import re
import os
import time
import json
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Event, Lock

from playwright.sync_api import sync_playwright, Page

from .database.handlers import (
    create_crawl_record, 
    update_crawl_record, 
    save_jobs_to_db,
    get_all_job_names
)
from .utils.logger import logger


class GenericJobCrawler:
    def __init__(self, config_path: str, max_workers: int = 3) -> None:
        """
        Khởi tạo crawler với file config
        
        Args:
            config_path: Đường dẫn đến file config JSON
            max_workers: Số lượng crawl đồng thời (mặc định 3)
        """
        self.config: dict = self.load_config(config_path)
        self.site_name: str = self.config.get("site_name", "unknown")
        self.source_url: str = self.config.get("base_url", "")
        self.selectors: dict = self.config.get("selectors", {})
        self.job_link_pattern: str = self.config.get("job_link_pattern", "")
        self.list_url: str = self.config.get("list_url", "")
        self.max_workers = max_workers
        
        # Stop event để dừng crawler
        self._stop_event = Event()
        
        # CrawlID cho lần crawl hiện tại
        self._current_crawl_id: int | None = None
        
        # Cache existing jobs
        self._existing_jobs_cache: set | None = None
        
        # Lock để in ra console an toàn
        self._print_lock = Lock()
        
    def load_config(self, config_path: str) -> dict:
        """Load file config JSON"""
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                logger.info(f"✓ Đã load config: {config.get('site_name', 'Unknown')}")
                return config
        except FileNotFoundError:
            logger.info(f"✗ Không tìm thấy file: {config_path}")
            exit(1)
        except json.JSONDecodeError:
            logger.info(f"✗ File config không đúng định dạng JSON")
            exit(1)
    
    def stop(self) -> None:
        """Dừng crawler"""
        logger.info("🛑 Đang dừng crawler...")
        self._stop_event.set()

    def is_stopped(self) -> bool:
        """Kiểm tra xem crawler đã dừng chưa"""
        return self._stop_event.is_set()

    def _load_existing_jobs_cache(self):
        """Load tất cả existing jobs vào memory"""
        if self._existing_jobs_cache is not None:
            return

        try:
            jobs = get_all_job_names()
            
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

    def check_job_exists(self, job_name: str, company_name: str) -> bool:
        """Kiểm tra job tồn tại từ cache"""
        if self._existing_jobs_cache is None:
            self._load_existing_jobs_cache()
        
        key = (job_name.strip().lower(), company_name.strip().lower())
        return key in self._existing_jobs_cache
    
    def get_job_links_from_page(self, page_num: int) -> list[str]:
        """
        Crawl danh sách link công việc từ 1 trang listing
        Mỗi lần gọi tạo playwright instance riêng
        """
        if self.is_stopped():
            return []
        
        # Xây dựng URL với page number
        if "?" in self.list_url:
            page_url = f"{self.list_url}&page={page_num}"
        else:
            page_url = f"{self.list_url}?page={page_num}"
        
        with self._print_lock:
            logger.info(f"\n{'='*80}")
            logger.info(f"  ĐANG CRAWL TRANG {page_num}")
            logger.info(f"{'='*80}")
            logger.info(f"URL: {page_url}")
        
        # Tạo Playwright instance riêng cho việc lấy links
        with sync_playwright() as p:
            try:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    viewport={"width": 1920, "height": 1080},
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                )
                page = context.new_page()
                
                page.goto(page_url, wait_until="domcontentloaded", timeout=60000)
                time.sleep(2)
                
                # Lấy domain gốc
                parsed_url = urlparse(self.list_url)
                base_domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
                
                # Lấy tất cả links
                all_links = page.locator("a[href]").all()
                
                job_links = []
                seen_urls = set()
                
                # Compile regex pattern
                try:
                    pattern_regex = re.compile(self.job_link_pattern)
                except re.error as e:
                    with self._print_lock:
                        logger.error(f"✗ Pattern regex không hợp lệ: {e}")
                    pattern_regex = None
                
                for link in all_links:
                    if self.is_stopped():
                        break
                        
                    try:
                        href = link.get_attribute("href")
                        if not href:
                            continue
                        
                        # Build full URL
                        if href.startswith("/"):
                            full_url = urljoin(base_domain, href)
                        elif href.startswith("http"):
                            full_url = href
                        else:
                            continue
                        
                        # Lọc chỉ lấy link thuộc domain hiện tại
                        if base_domain not in full_url:
                            continue
                        
                        # Loại bỏ các link không liên quan
                        exclude_keywords = [
                            "facebook.com", "twitter.com", "linkedin.com",
                            ".pdf", ".doc", ".zip", ".jpg", ".png"
                        ]
                        
                        if any(keyword in full_url.lower() for keyword in exclude_keywords):
                            continue
                        
                        # Tránh trùng lặp
                        if full_url in seen_urls:
                            continue
                        
                        # Kiểm tra với pattern
                        if pattern_regex and pattern_regex.search(full_url):
                            job_links.append(full_url)
                            seen_urls.add(full_url)
                                
                    except Exception:
                        continue
                
                browser.close()
                
                with self._print_lock:
                    logger.info(f"✓ Tìm thấy {len(job_links)} job links từ trang {page_num}")
                
                return job_links
                
            except Exception as e:
                with self._print_lock:
                    logger.error(f"✗ Lỗi khi crawl trang {page_num}: {e}")
                return []
    
    def extract_field(self, page: Page, field_name: str, selector: str) -> str | None:
        """Trích xuất dữ liệu từ 1 field dựa vào selector"""
        if not selector or selector == "null":
            return None
        
        try:
            element = page.locator(selector).first
            if element.count() > 0:
                text = element.inner_text().strip()
                return text if text else None
            return None
        except Exception:
            return None
    
    def crawl_job_detail(self, job_url: str) -> dict | None:
        """
        Crawl chi tiết 1 công việc
        Mỗi thread tạo Playwright instance riêng (FIX thread-safety)
        """
        if self.is_stopped():
            return None
        
        with sync_playwright() as p:
            try:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    viewport={"width": 1920, "height": 1080},
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                )
                page = context.new_page()
                
                page.goto(job_url, wait_until="domcontentloaded", timeout=60000)
                time.sleep(2)
                
                # Trích xuất dữ liệu
                company_name = self.extract_field(page, "company_name", self.selectors.get("company_name"))
                job_name = self.extract_field(page, "name", self.selectors.get("name"))
                
                # Kiểm tra trùng lặp
                if job_name and company_name:
                    if self.check_job_exists(job_name, company_name):
                        with self._print_lock:
                            logger.info(f"   ⚠️  Bỏ qua (trùng): {job_name}")
                        browser.close()
                        return None
                
                job_data = {
                    "job_link": job_url,
                    "name": "",
                    "salary": "",
                    "experience": "",
                    "education_level": "",
                    "location": "",
                    "position_level": "",
                    "job_type": "",
                    "quantity": "",
                    "deadline_submission": "",
                    "description": "",
                    "required": "",
                    "company_name": "",
                    "company_location": "",
                    "company_industry": "",
                    "company_scale": ""
                }
                
                # Trích xuất từng field theo config
                fields = [
                    "name", "salary", "experience", "education_level", "location",
                    "position_level", "job_type", "quantity", "deadline_submission",
                    "description", "required",
                    "company_name", "company_location", "company_industry", "company_scale"
                ]
                
                for field_name in fields:
                    selector = self.selectors.get(field_name)
                    value = self.extract_field(page, field_name, selector)
                    job_data[field_name] = value if value else ""
                
                browser.close()
                
                with self._print_lock:
                    logger.info(f"   ✓ Đã crawl xong: {job_data.get('name', 'N/A')}")
                
                return job_data
                
            except Exception as e:
                with self._print_lock:
                    logger.info(f"   ✗ Lỗi khi crawl {job_url}: {e}")
                return None
    
    def crawl_job_wrapper(self, job_url: str) -> dict | None:
        """Wrapper để crawl 1 job (dùng cho threading)"""
        if self.is_stopped():
            return None
        time.sleep(1)  # Tránh spam requests
        return self.crawl_job_detail(job_url)
    
    def crawl_jobs(self, start_page: int = 1, end_page: int = 3):
        """
        HÀM CHÍNH - Crawl song song với threading
        
        Args:
            start_page: Trang bắt đầu
            end_page: Trang kết thúc
        """
        logger.info(f"\n{'='*80}")
        logger.info(f"Bắt đầu crawl từ {self.site_name} (song song {self.max_workers} luồng)")
        logger.info(f"{'='*80}")
        
        # Reset stop event
        self._stop_event.clear()
        
        # ✅ TẠO CRAWL RECORD NGAY KHI BẮT ĐẦU
        try:
            self._current_crawl_id = create_crawl_record(
                self.site_name, 
                self.source_url
            )
        except Exception as e:
            logger.error(f"✗ Không thể tạo CrawlRecord: {e}")
            return []
        
        # Load cache trước
        self._load_existing_jobs_cache()
        
        crawled_jobs = []
        
        try:
            # BƯỚC 1: Thu thập links từ nhiều trang
            all_job_links = []
            for page_num in range(start_page, end_page + 1):
                if self.is_stopped():
                    logger.debug("🛑 Đã dừng việc thu thập links")
                    break
                    
                job_links = self.get_job_links_from_page(page_num)
                all_job_links.extend(job_links)
                time.sleep(1)
            
            if self.is_stopped():
                update_crawl_record(
                    self._current_crawl_id,
                    status='stopped',
                    jobs_count=len(crawled_jobs)
                )
                logger.debug(f"🛑 Crawler đã bị dừng. Đã crawl được {len(crawled_jobs)} jobs")
                return crawled_jobs
            
            logger.info(f"\n{'='*80}")
            logger.info(f"Tìm thấy tổng cộng {len(all_job_links)} link công việc")
            logger.info(f"{'='*80}")
            
            # BƯỚC 2: Crawl song song với ThreadPoolExecutor
            skipped = 0
            
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                future_to_url = {
                    executor.submit(self.crawl_job_wrapper, link): link
                    for link in all_job_links
                }
                
                for future in as_completed(future_to_url):
                    if self.is_stopped():
                        logger.debug("🛑 Đang hủy các task đang chạy...")
                        executor.shutdown(wait=False, cancel_futures=True)
                        break
                    
                    job_data = future.result()
                    if job_data:
                        crawled_jobs.append(job_data)
                        with self._print_lock:
                            logger.info(f"Crawl thành công: {job_data['name']}")
                    else:
                        skipped += 1
            
            if self.is_stopped():
                update_crawl_record(
                    self._current_crawl_id,
                    status='stopped',
                    jobs_count=len(crawled_jobs)
                )
                logger.debug(f"🛑 Crawler đã dừng. Đã crawl được {len(crawled_jobs)} jobs trước khi dừng")
                
                # Vẫn lưu jobs đã crawl được vào DB
                if crawled_jobs:
                    logger.debug(f"Đang lưu {len(crawled_jobs)} công việc đã crawl được...")
                    save_jobs_to_db(crawled_jobs, self._current_crawl_id)
                
                return crawled_jobs
            
            logger.info(f"\nBỏ qua {skipped} job trùng lặp")
            
            # Lưu vào database
            if crawled_jobs:
                logger.debug(f"\nĐang lưu {len(crawled_jobs)} công việc vào database...")
                saved_count = save_jobs_to_db(crawled_jobs, self._current_crawl_id)
                
                update_crawl_record(
                    self._current_crawl_id,
                    status='success',
                    jobs_count=saved_count
                )
                
                logger.info(f"\n{'='*80}")
                logger.info(f"  HOÀN THÀNH!")
                logger.info(f"{'='*80}")
                logger.info(f"✓ Đã crawl: {len(crawled_jobs)} công việc")
                logger.info(f"✓ Đã lưu vào database: {saved_count} công việc")
            else:
                logger.info("Không có công việc mới để lưu")
                update_crawl_record(
                    self._current_crawl_id,
                    status='empty',
                    message='Không có job mới để crawl',
                    jobs_count=0
                )
        
        except Exception as e:
            logger.error(f"\n✗ Lỗi trong quá trình crawl: {str(e)}")
            
            update_crawl_record(
                self._current_crawl_id,
                status='failed',
                message=f'Lỗi: {str(e)}',
                jobs_count=len(crawled_jobs)
            )
            
            # Vẫn cố lưu jobs đã crawl được
            if crawled_jobs:
                logger.debug(f"Đang lưu {len(crawled_jobs)} jobs đã crawl được trước khi lỗi...")
                save_jobs_to_db(crawled_jobs, self._current_crawl_id)
        
        return crawled_jobs
