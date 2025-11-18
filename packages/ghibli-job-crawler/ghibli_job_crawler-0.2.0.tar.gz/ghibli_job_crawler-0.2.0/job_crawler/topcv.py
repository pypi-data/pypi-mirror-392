import re
import time
import random
from threading import Event
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from bs4 import BeautifulSoup
from .database.handlers import (
    create_crawl_record, 
    update_crawl_record, 
    save_jobs_to_db,
    get_all_job_names
)
from .utils.logger import logger


class TopCVCrawler:
    def __init__(self, max_workers: int = 5) -> None:
        """
        Args:
            max_workers: Số lượng crawl đồng thời (mặc định 5)
        """

        self.base_url = "https://www.topcv.vn"
        self.source_name = "TopCV"
        self.source_url = "https://www.topcv.vn"
        self.max_workers = max_workers
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'vi-VN,vi;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        
        # Cache existing jobs để giảm query DB
        self._existing_jobs_cache = None
        
        # Stop event để dừng crawler
        self._stop_event = Event()
        
        # CrawlID cho lần crawl hiện tại
        self._current_crawl_id = None

    def stop(self) -> None:
        """Dừng crawler"""
        logger.debug("🛑 Đang dừng crawler...")
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

    def check_job_exists(self, job_name: str, company_name: str):
        """Kiểm tra job tồn tại từ cache (nhanh hơn query DB)"""
        if self._existing_jobs_cache is None:
            self._load_existing_jobs_cache()
        
        key = (job_name.strip().lower(), company_name.strip().lower())
        return key in self._existing_jobs_cache

    def get_job_links_from_page(self, page_num: int) -> list[str]:
        """Crawl danh sách link công việc từ trang listing"""
        if self.is_stopped():
            return []
            
        url = f"https://www.topcv.vn/viec-lam-tot-nhat?page={page_num}"
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            job_links = []

            job_elements = soup.find_all('a', href=re.compile(r'/viec-lam/'))
            for element in job_elements:
                if self.is_stopped():
                    break
                    
                href = element.get('href')
                if href:
                    full_url = urljoin(self.base_url, href)
                    if full_url not in job_links:
                        job_links.append(full_url)

            return job_links
        except Exception as e:
            logger.error(f"Lỗi khi crawl trang {page_num}: {str(e)}")
            return []

    def extract_job_details(self, job_url: str, retry: int = 1) -> dict | None:
        """Crawl chi tiết công việc từ URL (có cơ chế retry khi bị chặn 429)"""
        if self.is_stopped():
            return None
            
        for attempt in range(retry):
            if self.is_stopped():
                return None
                
            try:
                response = self.session.get(job_url, timeout=10)

                # Kiểm tra lỗi 429 Too Many Requests
                if response.status_code == 429:
                    wait = random.uniform(3, 3.5)
                    logger.warn(f"⚠️ Bị chặn 429 ({job_url}), chờ {wait:.1f}s rồi thử lại ({attempt+1}/{retry})...")
                    time.sleep(wait)
                    continue

                # Nếu có lỗi HTTP khác
                response.raise_for_status()

                soup = BeautifulSoup(response.content, 'html.parser')

                company_info = self.extract_company_info(soup)
                job_name = self.clean_text(self.extract_job_name(soup))

                # Kiểm tra trùng lặp từ cache
                if self.check_job_exists(job_name, company_info['name']):
                    return None

                job_data = {
                    'name': job_name,
                    'salary': self.clean_text(self.extract_salary(soup)),
                    'experience': self.clean_text(self.extract_experience(soup)),
                    'education_level': self.clean_text(self.extract_education(soup)),
                    'location': self.clean_text(self.extract_location(soup)),
                    'position_level': self.clean_text(self.extract_position_level(soup)),
                    'job_type': self.clean_text(self.extract_job_type(soup)),
                    'deadline_submission': self.clean_text(self.extract_deadline(soup)),
                    'quantity': self.clean_text(self.extract_quantity(soup)),
                    'description': self.extract_description(soup),
                    'required': self.extract_required(soup),
                    'company_name': company_info['name'],
                    'company_location': company_info['location'],
                    'company_industry': company_info['industry'],
                    'company_scale': company_info['scale'],
                    'job_link': job_url
                }

                return job_data

            except requests.exceptions.RequestException as e:
                # Lỗi mạng hoặc timeout
                wait = random.uniform(3, 6)
                logger.error(f"⚠️ Lỗi khi crawl {job_url}: {str(e)} (lần {attempt+1}/{retry}) – nghỉ {wait:.1f}s rồi thử lại...")
                time.sleep(wait)

            except Exception as e:
                # Lỗi không mong đợi (HTML, parse, ...)
                logger.error(f"❌ Lỗi không mong đợi ở {job_url}: {str(e)}")
                break

        # Nếu sau nhiều lần thử vẫn không thành công
        logger.warn(f"❌ Bỏ qua {job_url} sau {retry} lần thử không thành công.")
        return None
        
    def crawl_job_wrapper(self, job_link: str) -> dict | None:
        """Wrapper để crawl 1 job (dùng cho threading)"""
        if self.is_stopped():
            return None
            
        time.sleep(random.uniform(2, 3))
        return self.extract_job_details(job_link)

    def extract_description(self, soup: BeautifulSoup) -> str:
        """Trích xuất mô tả công việc (phiên bản tối ưu)"""
        description_keywords = [
            'mô tả công việc', 'mo ta cong viec', 'job description',
            'nhiệm vụ', 'trách nhiệm'
        ]
        
        job_desc_div = soup.find('div', class_='job-description')
        if not job_desc_div:
            return ""
        
        items = job_desc_div.find_all('div', class_='job-description__item')
        
        for item in items:
            h3 = item.find('h3')
            if h3:
                h3_text = h3.get_text().strip().lower()
                if any(keyword in h3_text for keyword in description_keywords):
                    content_div = item.find('div', class_='job-description__item--content')
                    if content_div:
                        # Lấy toàn bộ text, giữ lại các dòng xuống hàng
                        return content_div.get_text(separator='\n', strip=True)

        return ""

    def extract_required(self, soup: BeautifulSoup) -> str:
        """Trích xuất yêu cầu ứng viên (phiên bản tối ưu)"""
        required_keywords = [
            'yêu cầu ứng viên', 'yeu cau ung vien', 'job requirements',
            'requirements', 'yêu cầu công việc', 'kỹ năng'
        ]
        
        job_desc_div = soup.find('div', class_='job-description')
        if not job_desc_div:
            return ""
        
        items = job_desc_div.find_all('div', class_='job-description__item')
        
        for item in items:
            h3 = item.find('h3')
            if h3:
                h3_text = h3.get_text().strip().lower()
                if any(keyword in h3_text for keyword in required_keywords):
                    content_div = item.find('div', class_='job-description__item--content')
                    if content_div:
                        # Lấy toàn bộ text, giữ lại các dòng xuống hàng
                        return content_div.get_text(separator='\n', strip=True)

        return ""

    def extract_company_info(self, soup: BeautifulSoup) -> str:
        """Trích xuất thông tin công ty"""
        company = {'name': '', 'location': '', 'industry': '', 'scale': ''}
        box = soup.find('div', class_=re.compile(r'job-detail__box--right.*job-detail__company'))
        if not box:
            return company

        div_name = box.find('div', class_=re.compile(r'company-name-label'))
        if div_name:
            a_tag = div_name.find('a')
            if a_tag:
                company['name'] = self.clean_text(a_tag.get_text())

        scale_elem = box.find('div', class_=re.compile(r'company-scale'))
        if scale_elem:
            val = scale_elem.find('div', class_=re.compile(r'company-value'))
            if val:
                company['scale'] = self.clean_text(val.get_text())

        field_elem = box.find('div', class_=re.compile(r'company-field'))
        if field_elem:
            val = field_elem.find('div', class_=re.compile(r'company-value'))
            if val:
                company['industry'] = self.clean_text(val.get_text())

        address_elem = box.find('div', class_=re.compile(r'company-address'))
        if address_elem:
            val = address_elem.find('div', class_=re.compile(r'company-value'))
            if val:
                company['location'] = self.clean_text(val.get_text())
        return company

    def extract_job_name(self, soup: BeautifulSoup) -> str:
        selectors = ['h1.job-title', 'h1', '.job-detail-title h1', '.title-job', 'h2.job-title']
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text()
        return "N/A"

    def extract_salary(self, soup: BeautifulSoup) -> str:
        sections = soup.find_all('div', class_='job-detail__info--sections')
        for section in sections:
            labels = section.find_all(string=re.compile(r'mức lương|lương|salary', re.IGNORECASE))
            for label in labels:
                label_parent = label.parent
                while label_parent:
                    value_elem = label_parent.find_next('div', class_='job-detail__info--section-content-value')
                    if value_elem:
                        return value_elem.get_text().strip()
                    label_parent = label_parent.parent
        return "Thỏa thuận"

    def extract_experience(self, soup: BeautifulSoup) -> str:
        sections = soup.find_all('div', class_='job-detail__info--sections')
        for section in sections:
            labels = section.find_all(string=re.compile(r'kinh nghiệm|experience', re.IGNORECASE))
            for label in labels:
                label_parent = label.parent
                while label_parent:
                    value_elem = label_parent.find_next('div', class_='job-detail__info--section-content-value')
                    if value_elem:
                        return value_elem.get_text().strip()
                    label_parent = label_parent.parent
        return "Không yêu cầu"

    def extract_education(self, soup: BeautifulSoup) -> str:
        box_general = soup.find('div', class_=re.compile('job-detail__box--right.*job-detail__body-right--item.*job-detail__body-right--box-general'))
        if box_general:
            labels = box_general.find_all(string=re.compile(r'học vấn|education|bằng cấp|trình độ', re.IGNORECASE))
            for label in labels:
                label_parent = label.parent
                while label_parent and label_parent != box_general:
                    value_elem = label_parent.find_next('div', class_='box-general-group-info-value')
                    if value_elem:
                        return value_elem.get_text().strip()
                    label_parent = label_parent.parent
        return "Không yêu cầu"

    def extract_location(self, soup: BeautifulSoup) -> str:
        sections = soup.find_all('div', class_='job-detail__info--sections')
        for section in sections:
            labels = section.find_all(string=re.compile(r'địa điểm|location|nơi làm việc|khu vực', re.IGNORECASE))
            for label in labels:
                label_parent = label.parent
                while label_parent:
                    value_elem = label_parent.find_next('div', class_='job-detail__info--section-content-value')
                    if value_elem:
                        return value_elem.get_text().strip()
                    label_parent = label_parent.parent
        return "Toàn quốc"

    def extract_position_level(self, soup: BeautifulSoup) -> str:
        box_general = soup.find('div', class_=re.compile('job-detail__box--right.*job-detail__body-right--item.*job-detail__body-right--box-general'))
        if box_general:
            labels = box_general.find_all(string=re.compile(r'cấp bậc|level|chức vụ', re.IGNORECASE))
            for label in labels:
                label_parent = label.parent
                while label_parent and label_parent != box_general:
                    value_elem = label_parent.find_next('div', class_='box-general-group-info-value')
                    if value_elem:
                        return value_elem.get_text().strip()
                    label_parent = label_parent.parent
        return "Nhân viên"

    def extract_job_type(self, soup: BeautifulSoup) -> str:
        box_general = soup.find('div', class_=re.compile('job-detail__box--right.*job-detail__body-right--item.*job-detail__body-right--box-general'))
        if box_general:
            labels = box_general.find_all(string=re.compile(r'hình thức|job type|loại công việc|loại hình', re.IGNORECASE))
            for label in labels:
                label_parent = label.parent
                while label_parent and label_parent != box_general:
                    value_elem = label_parent.find_next('div', class_='box-general-group-info-value')
                    if value_elem:
                        return value_elem.get_text().strip()
                    label_parent = label_parent.parent
        return "Full-time"

    def extract_deadline(self, soup: BeautifulSoup) -> str:
        keywords = ['hạn nộp', 'deadline', 'hết hạn', 'ứng tuyển trước']
        for keyword in keywords:
            element = soup.find(string=re.compile(keyword, re.IGNORECASE))
            if element:
                parent = element.parent
                if parent:
                    text = parent.get_text()
                    date_match = re.search(r'\d{1,2}[/-]\d{1,2}[/-]\d{4}', text)
                    if date_match:
                        return date_match.group()
        return "Không giới hạn"

    def extract_quantity(self, soup: BeautifulSoup) -> str:
        box_general = soup.find('div', class_=re.compile('job-detail__box--right.*job-detail__body-right--item.*job-detail__body-right--box-general'))
        if box_general:
            labels = box_general.find_all(string=re.compile(r'số lượng|quantity|tuyển dụng|cần tuyển', re.IGNORECASE))
            for label in labels:
                label_parent = label.parent
                while label_parent and label_parent != box_general:
                    value_elem = label_parent.find_next('div', class_='box-general-group-info-value')
                    if value_elem:
                        text = value_elem.get_text().strip()
                        num_match = re.search(r'(\d+)', text)
                        if num_match:
                            return num_match.group(1) + " người"
                        return text
                    label_parent = label_parent.parent
        return "1 người"

    def clean_text(self, text: str) -> str:
        if not text or text == "N/A":
            return ""
        text = re.sub(r'\s+', ' ', str(text).strip())
        return text.strip()

    def crawl_jobs(self, start_page: int = 1, end_page: int = 3) -> list[dict]:
        """
        Hàm chính - Crawl song song với threading
        
        Args:
            start_page: Trang bắt đầu
            end_page: Trang kết thúc
        """
        logger.info(f"\n{'='*80}")
        logger.info(f"Bắt đầu crawl từ {self.source_name} (song song {self.max_workers} luồng)")
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
        
        crawled_jobs = []
        
        try:
            # Thu thập links
            all_job_links = []
            for page in range(start_page, end_page + 1):
                if self.is_stopped():
                    logger.debug("🛑 Đã dừng việc thu thập links")
                    break
                    
                job_links = self.get_job_links_from_page(page)
                all_job_links.extend(job_links)
                time.sleep(random.uniform(1, 2))

            if self.is_stopped():
                # ✅ CẬP NHẬT STATUS = 'stopped'
                update_crawl_record(
                    self._current_crawl_id, 
                    status='stopped',
                    jobs_count=len(crawled_jobs)
                )
                logger.debug(f"🛑 Crawler đã bị dừng. Đã crawl được {len(crawled_jobs)} jobs")
                return crawled_jobs

            logger.info(f"Tìm thấy {len(all_job_links)} link công việc")
            
            # Crawl song song
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
                        logger.info(f"Crawl thành công: {job_data['name']}")
                    else:
                        skipped += 1
            
            if self.is_stopped():
                # ✅ CẬP NHẬT STATUS = 'stopped'
                update_crawl_record(
                    self._current_crawl_id, 
                    status='stopped',
                    jobs_count=len(crawled_jobs)
                )
                logger.debug(f"🛑 Crawler đã dừng. Đã crawl được {len(crawled_jobs)} jobs trước khi dừng")
                
                # Vẫn lưu jobs đã crawl được vào DB
                if crawled_jobs:
                    logger.info(f"Đang lưu {len(crawled_jobs)} công việc đã crawl được...")
                    save_jobs_to_db(crawled_jobs, self._current_crawl_id)
                
                return crawled_jobs
            
            logger.debug(f"\nBỏ qua {skipped} job trùng lặp")
            
            # Lưu vào database
            if crawled_jobs:
                logger.info(f"Đang lưu {len(crawled_jobs)} công việc vào database...")
                saved_count = save_jobs_to_db(crawled_jobs, self._current_crawl_id)
                
                # ✅ CẬP NHẬT STATUS = 'success'
                update_crawl_record(
                    self._current_crawl_id, 
                    status='success',
                    jobs_count=saved_count
                )
            else:
                logger.info("Không có công việc mới để lưu")
                # ✅ CẬP NHẬT STATUS = 'success' với 0 jobs
                update_crawl_record(
                    self._current_crawl_id, 
                    status='empty',
                    message='Không có job mới để crawl',
                    jobs_count=0
                )

        except Exception as e:
            logger.error(f"\n❌ Lỗi trong quá trình crawl: {str(e)}")
            
            # ✅ CẬP NHẬT STATUS = 'failed'
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
