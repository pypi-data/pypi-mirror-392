import unittest

from job_crawler.topcv import TopCVCrawler


class TestTopCV(unittest.TestCase):
    # @unittest.skip("Skip")
    def test_topcv_crawler(self):
        print("TopCV Job Crawler (Optimized)")
        crawler = TopCVCrawler(max_workers=3)
        try:
            crawler.crawl_jobs(start_page=1, end_page=1)
            print("\nHoàn thành crawl từ TopCV!")
        except KeyboardInterrupt:
            crawler.stop()
            print("\nĐã dừng crawler theo yêu cầu người dùng.")
        except Exception as e:
            print(f"\nLỗi trong quá trình crawl: {str(e)}")


if __name__ == "__main__":
    unittest.main()