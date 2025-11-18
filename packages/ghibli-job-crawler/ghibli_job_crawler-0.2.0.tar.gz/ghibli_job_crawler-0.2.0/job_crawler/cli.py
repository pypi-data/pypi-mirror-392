import time
import json
import argparse

from playwright.sync_api import sync_playwright

from .generic_job import GenericJobCrawler
from .gemini_crawler import GeminiCrawler
from .topcv import TopCVCrawler
from .vietnamworks import VietnamWorksCrawler
from .export import to_csv, to_json
from .utils.logger import logger


def crawl_topcv(num_workers: int = 3, start_page: int = 0, end_page: int = 0) -> None:
    logger.info("TopCV Job Crawler (Optimized)")
    crawler = TopCVCrawler(max_workers=num_workers)
    try:
        crawler.crawl_jobs(start_page=start_page, end_page=end_page)
        logger.info("\nHoàn thành crawl từ TopCV!")
    except KeyboardInterrupt:
        crawler.stop()
        logger.error("\nĐã dừng crawler theo yêu cầu người dùng.")
    except Exception as e:
        logger.error(f"\nLỗi trong quá trình crawl: {str(e)}")


def crawl_vietnamworks(num_workers: int = 3, start_page: int = 0, end_page: int = 0) -> None:
    logger.info("VietnamWorks Job Crawler (Optimized)")
    crawler = VietnamWorksCrawler(max_workers=num_workers)
    try:
        crawler.crawl_jobs(start_page=start_page, end_page=end_page)
        logger.info("\nHoàn thành crawl từ TopCV!")
    except KeyboardInterrupt:
        crawler.stop()
        logger.error("\nĐã dừng crawler theo yêu cầu người dùng.")
    except Exception as e:
        logger.error(f"\nLỗi trong quá trình crawl: {str(e)}")


def crawl_generic_job(config_path: str, num_workers: int = 3, start_page: int = 0, end_page: int = 0) -> None:
    logger.info("Generic Job Crawler (Optimized)")
    crawler = GenericJobCrawler(config_path, max_workers=num_workers)
    try:
        crawler.crawl_jobs(start_page=start_page, end_page=end_page)
        logger.info("\nHoàn thành crawl!")
    except KeyboardInterrupt:
        crawler.stop()
        logger.info("\nĐã dừng crawler theo yêu cầu người dùng.")


def crawl_gemini() -> None:
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


def cli():
    parser = argparse.ArgumentParser(prog="job-crawler", description="Job Crawler CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    export_parser = subparsers.add_parser("export", help="Export crawled data")

    # ---- Subcommand crawl ----
    crawl_parser = subparsers.add_parser("crawl", help="Crawl job data")
    crawl_parser.add_argument("--type", choices=["topcv", "vietnamworks", "generic_job", "gemini"], required=True, help="Source to crawl")
    crawl_parser.add_argument("--max-workers", type=int, default=3, help="Number of threads")
    crawl_parser.add_argument("--start-page", type=int, default=0, help="Start page index")
    crawl_parser.add_argument("--end-page", type=int, default=1, help="End page index")
    crawl_parser.add_argument("--config", type=str, default="", help="Config path for generic job crawler")

    # ---- Subcommand export ----
    export_parser = subparsers.add_parser("export", help="Export crawled data")
    export_parser.add_argument("--type", choices=["csv", "json"], default="csv", help="Export format")
    export_parser.add_argument("--save-path", type=str, required=True, help="Directory or file path to save exported data")
    export_parser.add_argument("--table-name", type=str, nargs="*", default=None, help="Optional table names to export (default all tables)")

    args = parser.parse_args()

    if args.command == "crawl":
        if args.type == "topcv":
            crawl_topcv(
                args.max_workers,
                args.start_page,
                args.end_page
            )
        elif args.type == "vietnamworks":
            crawl_vietnamworks(
                args.max_workers,
                args.start_page,
                args.end_page
            )
        elif args.type == "generic_job":
            crawl_generic_job(
                args.config,
                args.max_workers,
                args.start_page,
                args.end_page
            )
        elif args.type == "gemini":
            crawl_gemini()
    elif args.command == "export":
        if args.type == "csv":
            to_csv(args.save_path, args.table_name)
        elif args.type == "json":
            to_json(args.save_path, args.table_name)

    
