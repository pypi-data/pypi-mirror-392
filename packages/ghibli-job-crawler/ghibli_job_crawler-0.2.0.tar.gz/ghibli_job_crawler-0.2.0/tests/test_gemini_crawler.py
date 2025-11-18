import json
import time
import unittest

from playwright.sync_api import sync_playwright

from job_crawler.gemini_crawler import GeminiCrawler
from job_crawler.utils.logger import logger


class TestGeminiCrawler(unittest.TestCase):
    # @unittest.skip("Skip")
    def test_gemin_crawler(self):
        generator = GeminiCrawler()

        with sync_playwright() as p:
            try:
                logger.info("=" * 80)
                logger.info("  CÔNG CỤ SINH CẤU HÌNH CRAWLER - TÌM PATTERN & CSS SELECTOR")
                logger.info("=" * 80)

                browser = p.chromium.launch(headless=True, args=["--start-maximized"])
                context = browser.new_context(no_viewport=True)
                page = context.new_page()

                # Nhập URL danh sách
                list_url = input("\nNhập URL trang DANH SÁCH việc làm: ").strip()
                if not list_url:
                    logger.info("✗ URL không được để trống!")
                    return

                site_name = list_url.split("//")[1].split("/")[0].replace("www.", "")

                # Kiểm tra config có sẵn không
                existing_config = generator.load_config(site_name)
                if existing_config:
                    logger.info(f"\n⚠ Đã có cấu hình cho {site_name}")
                    if input("Sử dụng lại? (y/n): ").lower() == "y":
                        logger.info(json.dumps(existing_config, indent=2, ensure_ascii=False))
                        return

                # BƯỚC 0: Lấy tất cả links và tìm pattern
                logger.info("\n" + "=" * 80)
                logger.info("  BƯỚC 0: PHÂN TÍCH PATTERN JOB LINKS")
                logger.info("=" * 80)

                all_links = generator.extract_all_links(page, list_url)
                if not all_links:
                    logger.info("\n✗ Không tìm thấy link nào!")
                    return

                job_link_pattern = generator.find_job_link_pattern(all_links, list_url)
                if not job_link_pattern:
                    logger.info("\n✗ Không thể tìm pattern!")
                    return

                # Lọc job links theo pattern
                job_links = generator.filter_job_links_by_pattern(all_links, job_link_pattern, max_jobs=3)
                if not job_links:
                    logger.info("\n✗ Không có job link nào match pattern!")
                    return

                # Chọn 1 job link để phân tích chi tiết
                sample_job_url = job_links[0]
                logger.info(f"\n📌 Chọn job mẫu để phân tích: {sample_job_url}")

                # Truy cập trang job chi tiết
                logger.info(f"\n🌐 Truy cập: {sample_job_url}")
                page.goto(sample_job_url, wait_until="domcontentloaded", timeout=60000)
                time.sleep(2)

                # BƯỚC 1: Lấy text thô theo sections & phân loại dữ liệu
                logger.info("\n" + "=" * 80)
                logger.info("  BƯỚC 1: TRÍCH XUẤT & PHÂN LOẠI DỮ LIỆU")
                logger.info("=" * 80)

                sections = generator.extract_text_sections(page)
                extracted_data = generator.extract_job_data_from_sections(sections, sample_job_url)

                if not extracted_data:
                    logger.info("\n✗ Không thể trích xuất dữ liệu")
                    return
                logger.info("\n📊 Dữ liệu đã trích xuất:")
                logger.info(json.dumps(extracted_data, indent=2, ensure_ascii=False))

                # BƯỚC 2: Tìm CSS selector
                logger.info("\n" + "=" * 80)
                logger.info("  BƯỚC 2: TÌM CSS SELECTOR")
                logger.info("=" * 80)

                selectors_config = generator.find_selectors_from_html(page, extracted_data, sample_job_url)

                if not selectors_config:
                    logger.info("\n✗ Không thể tìm selector")
                    return

                # ✅ THÊM job_link_pattern và list_url vào config
                selectors_config["job_link_pattern"] = job_link_pattern
                selectors_config["list_url"] = list_url  # ✅ THÊM MỚI

                # Hiển thị kết quả cuối cùng
                logger.info("\n" + "=" * 80)
                logger.info("  KẾT QUẢ CUỐI CÙNG")
                logger.info("=" * 80)
                logger.info(json.dumps(selectors_config, indent=2, ensure_ascii=False))

                # Lưu config
                if input("\nLưu config này? (y/n): ").lower() == "y":
                    generator.save_config(selectors_config, site_name)
                    logger.info("\n✅ Hoàn thành! Config đã sẵn sàng để sử dụng với GenericJobCrawler_DB.py")

            except TimeoutError:
                logger.info("\n✗ Hết thời gian chờ")
            except KeyboardInterrupt:
                logger.info("\n⚠ Dừng bởi người dùng")
            except Exception as e:
                logger.info(f"\n✗ Lỗi: {e}")
                import traceback
                traceback.print_exc()
            finally:
                if "browser" in locals() and browser.is_connected():
                    browser.close()
                    logger.info("\n✓ Đã đóng trình duyệt")


if __name__ == "__main__":
    unittest.main()