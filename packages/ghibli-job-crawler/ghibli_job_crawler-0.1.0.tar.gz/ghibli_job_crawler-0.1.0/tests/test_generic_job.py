import os
import unittest

from job_crawler.generic_job import GenericJobCrawler
from job_crawler.utils.logger import logger


class TestVietnamWorks(unittest.TestCase):
    # @unittest.skip("Skip")
    def test_topcv_crawler(self):
        logger.info("""
    ╔═══════════════════════════════════════════════════════════╗
    ║          GENERIC JOB CRAWLER - CRAWL DỰA VÀO CONFIG       ║
    ╚═══════════════════════════════════════════════════════════╝
        """)
        
        # 1. Chọn file config
        config_dir = "configs"
        
        if not os.path.exists(config_dir):
            logger.info(f"✗ Không tìm thấy thư mục config: {config_dir}")
            return
        
        config_files = [f for f in os.listdir(config_dir) if f.endswith(".json")]
        
        if not config_files:
            logger.info(f"✗ Không có file config nào trong {config_dir}")
            return
        
        logger.info("Danh sách config có sẵn:")
        for idx, filename in enumerate(config_files, 1):
            logger.info(f"  {idx}. {filename}")
        
        choice = input("\nChọn config (nhập số hoặc tên file): ").strip()
        
        # Xác định file config
        if choice.isdigit() and 1 <= int(choice) <= len(config_files):
            config_file = config_files[int(choice) - 1]
        elif choice in config_files:
            config_file = choice
        elif choice.endswith(".json"):
            config_file = choice
        else:
            config_file = config_files[0]
        
        config_path = os.path.join(config_dir, config_file)
        
        # 2. Nhập start_page và end_page
        start_page_input = input("Trang bắt đầu (mặc định 1): ").strip()
        start_page = int(start_page_input) if start_page_input.isdigit() else 1
        
        end_page_input = input("Trang kết thúc (mặc định 3): ").strip()
        end_page = int(end_page_input) if end_page_input.isdigit() else 3
        
        # 3. Số luồng crawl song song
        max_workers_input = input("Số luồng crawl song song (mặc định 3): ").strip()
        max_workers = int(max_workers_input) if max_workers_input.isdigit() else 3
        
        # 4. Bắt đầu crawl
        crawler = GenericJobCrawler(config_path, max_workers=max_workers)
        try:
            crawler.crawl_jobs(start_page=start_page, end_page=end_page)
            logger.info("\nHoàn thành crawl!")
        except KeyboardInterrupt:
            crawler.stop()
            logger.info("\nĐã dừng crawler theo yêu cầu người dùng.")


if __name__ == "__main__":
    unittest.main()