import unittest

from job_crawler.export import to_csv, to_json


class TestExport(unittest.TestCase):
    def test_export_to_csv(self):
        to_csv("data/test_csv")

    def test_export_to_json(self):
        to_json("data/test_json")


if __name__ == "__main__":
    unittest.main()
