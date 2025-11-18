# tests/test_cli_sys.py
import sys
from pathlib import Path
from job_crawler.cli import cli

def test_crawl_topcv():
    sys.argv = [
        "job-crawler",
        "crawl",
        "--type", "topcv",
        "--max-workers", "1",
        "--start-page", "0",
        "--end-page", "1"
    ]
    cli()  # Chạy CLI trực tiếp

def test_crawl_vietnamworks():
    sys.argv = [
        "job-crawler",
        "crawl",
        "--type", "vietnamworks",
        "--max-workers", "1",
        "--start-page", "0",
        "--end-page", "1"
    ]
    cli()

def test_export_csv(tmp_path):
    save_path = tmp_path / "output.csv"
    sys.argv = [
        "job-crawler",
        "export",
        "--type", "csv",
        "--save-path", str(save_path)
    ]
    cli()

def test_export_json(tmp_path):
    save_path = tmp_path / "output.json"
    sys.argv = [
        "job-crawler",
        "export",
        "--type", "json",
        "--save-path", str(save_path)
    ]
    cli()
