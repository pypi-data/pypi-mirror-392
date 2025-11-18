import json
import os
import time
import re
from urllib.parse import urljoin, urlparse

from google import genai
from playwright.sync_api import sync_playwright, TimeoutError, Page
from bs4 import BeautifulSoup
from dotenv import load_dotenv

from .utils.logger import logger


CONFIG_DIR = "configs"


class GeminiCrawler:
    def __init__(self, api_key: str | None = None):
        """Khởi tạo generator với API key"""

        if api_key is None:
            load_dotenv()
            api_key = os.getenv("GOOGLE_API_KEY", None)

            assert api_key is not None, "GOOLE_API_KEY is not set in you environment variables."

        self.api_key = api_key            
        self.client = genai.Client(api_key=api_key)

        os.makedirs(CONFIG_DIR, exist_ok=True)

    # ========================================================================
    # BƯỚC 0: PHÂN TÍCH PATTERN CỦA JOB LINKS
    # ========================================================================

    def extract_all_links(self, page: Page, list_url: str) -> list[str]:
        """
        Lấy TẤT CẢ links từ trang danh sách việc làm
        """
        logger.info(f"\n{'='*80}")
        logger.info(f"  BƯỚC 0: LẤY TẤT CẢ LINKS TỪ TRANG DANH SÁCH")
        logger.info(f"{'='*80}")
        logger.info(f"Đang truy cập: {list_url}")
        
        try:
            page.goto(list_url, wait_until="domcontentloaded", timeout=60000)
            for _ in range(10):
                page.mouse.wheel(0, 1000)
                time.sleep(1)
            
            parsed_url = urlparse(list_url)
            base_domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
            
            all_links = page.locator("a[href]").all()
            
            links = []
            seen_urls = set()
            
            for link in all_links:
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
                    
                    # Chỉ lấy link thuộc domain hiện tại
                    if base_domain not in full_url:
                        continue
                    
                    # Loại bỏ các link rõ ràng không phải job
                    exclude_keywords = [
                        "facebook.com", "twitter.com", "linkedin.com",
                        ".pdf", ".doc", ".zip", ".jpg", ".png"
                    ]
                    
                    if any(keyword in full_url.lower() for keyword in exclude_keywords):
                        continue
                    
                    # Tránh trùng lặp
                    if full_url in seen_urls:
                        continue
                    
                    links.append(full_url)
                    seen_urls.add(full_url)
                    
                except Exception:
                    continue
            
            logger.info(f"✓ Tìm thấy {len(links)} links từ trang")
            return links
            
        except Exception as e:
            logger.error(f"✗ Lỗi khi lấy links: {e}")
            return []

    def find_job_link_pattern(self, links: list[str], base_url: str) -> str:
        """
        Dùng LLM để phân tích và tìm pattern chung của job links
        """
        logger.info(f"\n   [Step 0.1] Phân tích pattern của {len(links)} links...")
        
        # Giới hạn số links gửi cho LLM
        sample_links = links[:50] if len(links) > 50 else links
        
        links_text = "\n".join(sample_links)
        
        prompt = f"""
Bạn là chuyên gia phân tích URL patterns.

Dưới đây là danh sách các links từ một trang tuyển dụng việc làm tại Việt Nam.
Nguồn: {base_url}

**NHIỆM VỤ:** Tìm REGEX PATTERN chung nhất của các links chi tiết công việc.

**HƯỚNG DẪN:**
1. Phân tích tất cả links để tìm pattern lặp lại nhiều nhất
2. Links chi tiết công việc thường có:
   - Đường dẫn đặc trưng: /viec-lam/, /job/, /tuyen-dung/, /cong-viec/, /detail/
   - ID số hoặc slug
   - Cấu trúc URL nhất quán
3. Tạo regex pattern có thể match CHÍNH XÁC các job links
4. Pattern phải tối ưu: không quá rộng (match nhầm), không quá hẹp (miss job links)

**VÍ DỤ OUTPUT:**
- Nếu links dạng: /viec-lam/title-12345, /viec-lam/another-67890
  → Pattern: "/viec-lam/.*-\\d+$"
  
- Nếu links dạng: /job/detail/12345, /job/detail/67890
  → Pattern: "/job/detail/\\d+$"

**DANH SÁCH LINKS:**
{links_text}

**ĐẦU RA YÊU CẦU - JSON:**
{{
  "pattern": "regex pattern ở đây",
  "explanation": "Giải thích ngắn gọn tại sao chọn pattern này",
  "sample_matches": ["ví dụ URL match 1", "ví dụ URL match 2", "ví dụ URL match 3"]
}}

Chỉ trả về JSON, không giải thích gì thêm.
"""

        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                content=[prompt],
                config=genai.types.GenerationConfig(
                    response_mime_type="application/json",
                    temperature=0.1
                )
            )
            result = json.loads(response.text)
            pattern = result.get("pattern", "")
            explanation = result.get("explanation", "")
            samples = result.get("sample_matches", [])
            
            logger.info(f"   [Step 0.1] ✓ Tìm thấy pattern: {pattern}")
            logger.info(f"   [Step 0.1] 💡 Giải thích: {explanation}")
            logger.info(f"   [Step 0.1] 📋 Ví dụ match:")
            for sample in samples[:3]:
                logger.info(f"      - {sample}")
            
            return pattern
        except Exception as e:
            logger.error(f"   Lỗi khi tìm pattern: {e}")
            return ""

    def filter_job_links_by_pattern(self, links: list[str], pattern: str, max_jobs: int = 3) -> list[str]:
        """
        Lọc job links dựa vào pattern regex
        """
        logger.info(f"\n   [Step 0.2] Lọc job links theo pattern...")
        
        if not pattern:
            logger.warn("   Không có pattern, trả về links gốc")
            return links[:max_jobs]
        try:
            regex = re.compile(pattern)
            job_links = []
            
            for link in links:
                if regex.search(link):
                    job_links.append(link)
                    if len(job_links) >= max_jobs:
                        break
            
            logger.info(f"   [Step 0.2] ✓ Lọc được {len(job_links)} job links")
            for i, link in enumerate(job_links[:5], 1):
                logger.info(f"      {i}. {link}")
            
            return job_links
        except Exception as e:
            logger.error(f"   Lỗi regex: {e}")
            return links[:max_jobs]

    # ========================================================================
    # BƯỚC 1: LẤY TEXT THÔNG MINH (THEO SECTION)
    # ========================================================================

    def extract_text_sections(self, page: Page) -> list[dict]:
        """
        Tìm các container lớn trong HTML và lấy text từng section riêng lẻ
        """
        logger.info("   [Step 1.1] Đang phân tích HTML structure...")
        
        html_content = page.content()
        soup = BeautifulSoup(html_content, 'html.parser')

        # Xóa script, style, không cần thiết
        for tag in soup(['script', 'style', 'noscript', 'iframe', 'svg']):
            tag.decompose()

        # Tìm các container chính (div, section, article)
        containers = soup.find_all(['div', 'section', 'article'])
        
        sections = []
        
        for idx, container in enumerate(containers):
            text = container.get_text(strip=True)
            
            # Chỉ lấy container có nội dung >= 100 ký tự
            if len(text) >= 100:
                text = re.sub(r'\s+', ' ', text).strip()
                
                container_id = container.get('id', '')
                container_class = ' '.join(container.get('class', []))
                
                sections.append({
                    "index": idx,
                    "id": container_id,
                    "class": container_class,
                    "text": text,
                    "length": len(text)
                })
        
        logger.info(f"   [Step 1.1] ✓ Tìm được {len(sections)} sections chính")
        return sections

    def extract_job_data_from_sections(self, sections: list[dict], job_url: str) -> dict:
        """
        Gửi các sections cho Gemini để phân loại dữ liệu (✅ ĐÃ BỎ BENEFITS)
        """
        logger.info("   [Step 1.2] Gửi sections đến Gemini để phân loại dữ liệu...")

        sections_text = "\n\n".join([f"[SECTION {s['index']}]\n{s['text']}" for s in sections])

        prompt = f"""
Bạn là chuyên gia phân tích tin tuyển dụng tại Việt Nam.

Dưới đây là các sections (phần) của một trang chi tiết công việc (nguồn: {job_url}).
Mỗi section được trích xuất từ HTML structure, không bị cắt hay thay đổi.

**NHIỆM VỤ:** Phân tích toàn bộ sections này và trích xuất các thông tin công việc thành JSON.

**CÁC TRƯỜNG CẦN TRÍCH XUẤT:**
- name: Tiêu đề công việc / Chức danh
- salary: Mức lương (format: "X - Y triệu VND" hoặc "null")
- experience: Yêu cầu kinh nghiệm (text ngắn hoặc "null")
- education_level: Trình độ học vấn (text ngắn hoặc "null")
- location: Địa điểm làm việc chỉ cần tên thành phố hoặc tỉnh(text ngắn hoặc "null")
- position_level: Cấp bậc / chức vụ (text ngắn hoặc "null")
- job_type: Loại hình công việc (toàn thời gian / bán thời gian / thực tập, hoặc "null")
- deadline_submission: Hạn nộp hồ sơ thường như 29/11/2025(format: "DD/MM/YYYY" hoặc "null")
- quantity: Số lượng tuyển (số hoặc "null")
- description: Mô tả công việc (text 150-300 từ, hoặc "null")
- required: Yêu cầu ứng viên (text 150-300 từ, hoặc "null")
- company_name: Tên công ty / Nhà tuyển dụng (text, hoặc "null")
- company_location: Địa chỉ công ty (text, hoặc "null")
- company_industry: Ngành nghề công ty (text, hoặc "null")
- company_scale: Quy mô công ty (text như "25-99 nhân viên", hoặc "null")

**HƯỚNG DẪN:**
1. Đọc kỹ toàn bộ sections để tìm thông tin
2. Nếu không tìm thấy thông tin, ghi "null"
3. Đảm bảo đầu ra là **JSON hợp lệ**
4. Không thêm giải thích, chỉ trả về JSON

SECTIONS CẦN PHÂN TÍCH:
{sections_text}
"""
        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                content=[prompt],
                config=genai.types.GenerationConfig(
                    response_mime_type="application/json",
                    temperature=0.1
                )
            )
            extracted_data = json.loads(response.text)
            logger.info("   [Step 1.2] ✓ Phân loại dữ liệu thành công")
            return extracted_data
        except json.JSONDecodeError as e:
            logger.error(f"   JSON không hợp lệ: {e}")
            return {}
        except Exception as e:
            logger.error(f"   Lỗi API: {e}")
            return {}

    # ========================================================================
    # BƯỚC 2: PHÂN TÍCH HTML ĐỂ TÌM CSS SELECTOR
    # ========================================================================

    def prepare_html_for_selector_search(self, page: Page) -> str:
        """Chuẩn bị HTML cho việc tìm selector"""
        logger.info("   [Step 2.1] Làm sạch HTML...")
        
        html_content = page.content()
        soup = BeautifulSoup(html_content, 'html.parser')
        
        for tag in soup(['script', 'style', 'noscript', 'iframe', 'svg']):
            tag.decompose()
        
        cleaned_html = str(soup)[:50000]
        logger.info(f"   [Step 2.1] ✓ HTML đã làm sạch")
        
        return cleaned_html

    def find_selectors_from_html(self, page: Page, extracted_data: dict, job_url: str) -> dict:
        """
        Gửi HTML + dữ liệu đã phân loại cho Gemini để tìm CSS selector
        """
        logger.info("   [Step 2.2] Gửi HTML + dữ liệu đến Gemini để tìm selector...")

        cleaned_html = self.prepare_html_for_selector_search(page)
        data_summary = json.dumps(extracted_data, ensure_ascii=False, indent=2)

        prompt = f"""
Bạn là chuyên gia CSS selector và web scraping.

Dưới đây là:
1. **Dữ liệu đã trích xuất** từ trang (dạng JSON)
2. **HTML gốc** của trang

**NHIỆM VỤ:** Tìm các CSS selector chính xác ứng với từng trường dữ liệu.

**HƯỚNG DẪN TÌM SELECTOR:**
1. Ưu tiên: id > class > data-* > tag name
2. Tránh `:nth-child()` hoặc `:nth-of-type()` (selector không ổn định)
3. Chọn selector duy nhất, không phụ thuộc vào vị trí
4. Nếu không tìm thấy, ghi "null"
5. Selector phải có thể định vị được phần tử chứa giá trị tương ứng

**DỮ LIỆU ĐÃ TRÍCH XUẤT:**
{data_summary}

**HTML GỐC:**
{cleaned_html}

**ĐẦU RA YÊU CẦU - JSON:**
{{
  "site_name": "Tên website",
  "base_url": "{job_url}",
  "selectors": {{
    "name": "Selector cho tên công việc",
    "salary": "Selector cho lương",
    "experience": "Selector cho kinh nghiệm",
    "education_level": "Selector cho trình độ học vấn",
    "location": "Selector cho địa điểm",
    "position_level": "Selector cho cấp bậc",
    "job_type": "Selector cho loại hình công việc",
    "deadline_submission": "Selector cho hạn nộp",
    "quantity": "Selector cho số lượng tuyển",
    "description": "Selector cho mô tả công việc",
    "required": "Selector cho yêu cầu",
    "company_name": "Selector cho tên công ty",
    "company_location": "Selector cho địa chỉ công ty",
    "company_industry": "Selector cho ngành nghề",
    "company_scale": "Selector cho quy mô"
  }}
}}

Chỉ trả về JSON, không giải thích gì thêm.
"""

        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                content=[prompt],
                config=genai.types.GenerationConfig(
                    response_mime_type="application/json",
                    temperature=0.1
                )
            )
            selectors_config = json.loads(response.text)
            logger.info("   [Step 2.2] ✓ Tìm selector thành công")
            return selectors_config
        except json.JSONDecodeError as e:
            logger.info(f"   [ERROR] JSON không hợp lệ: {e}")
            return {}
        except Exception as e:
            logger.info(f"   [ERROR] Lỗi API: {e}")
            return {}

    def save_config(self, config: dict, site_name: str):
        """Lưu config vào file JSON"""
        filename = f"{CONFIG_DIR}/{site_name.lower().replace(' ', '_')}_config.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        logger.info(f"\n✓ Đã lưu config vào: {filename}")

    def load_config(self, site_name: str) -> dict | None:
        """Tải config đã lưu"""
        filename = f"{CONFIG_DIR}/{site_name.lower().replace(' ', '_')}_config.json"
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                return json.load(f)
        return None
