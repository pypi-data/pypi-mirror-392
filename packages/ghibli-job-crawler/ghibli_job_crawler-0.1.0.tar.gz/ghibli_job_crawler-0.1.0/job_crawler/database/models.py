from dataclasses import dataclass, field
from datetime import datetime, date
from typing import List, Optional


# --------------------------
# Account
# --------------------------
@dataclass
class Account:
    AccountID: int
    Email: str
    PasswordHash: str
    Created_At: datetime = field(default_factory=datetime.now)
    IsNotification: bool = True
    Role: str = "user"  # 'user' hoặc 'admin'

    # Relationships
    saved_job_links: List["SavedJob"] = field(default_factory=list)

    def get_id(self):
        return str(self.AccountID)

    def __repr__(self):
        return f"<Account(Email='{self.Email}')>"

# --------------------------
# Company
# --------------------------
@dataclass
class Company:
    CompanyID: int
    Name: str
    Location: Optional[str] = None
    Company_Industry: Optional[str] = None
    Scale: Optional[str] = None

    # Relationship
    jobs: List["Job"] = field(default_factory=list)

    def __repr__(self):
        return f"<Company(Name='{self.Name}')>"

# --------------------------
# Source
# --------------------------
@dataclass
class Source:
    SourceID: int
    Name: str
    URL: str
    Required_Login: bool = False

    # Relationship
    crawl_records: List["CrawlRecord"] = field(default_factory=list)

    def __repr__(self):
        return f"<Source(Name='{self.Name}')>"

# --------------------------
# CrawlRecord
# --------------------------
@dataclass
class CrawlRecord:
    CrawlID: int
    SourceID: int
    CrawlDate: datetime = field(default_factory=datetime.now)
    Status: str = "success"  # 'success', 'failed', 'stopped', 'empty'
    Message: Optional[str] = None

    # Relationships
    source: Optional[Source] = None
    jobs: List["Job"] = field(default_factory=list)

    def __repr__(self):
        return f"<CrawlRecord(SourceID={self.SourceID}, Status='{self.Status}')>"

# --------------------------
# Job
# --------------------------
@dataclass
class Job:
    JobID: int
    CompanyID: int
    CrawlID: int
    Name: str
    Salary: Optional[str] = None
    Experience: Optional[int] = None
    Education_Level: Optional[int] = None
    Location: Optional[str] = None
    Position_Level: Optional[str] = None
    Job_Type: Optional[str] = None
    Deadline_Submission: Optional[date] = None
    Quantity: int = 1
    Job_Link: Optional[str] = None
    Description: Optional[str] = None
    Required: Optional[str] = None
    IsNew: int = 1

    # Relationships
    company: Optional[Company] = None
    crawl_record: Optional[CrawlRecord] = None
    saved_by_links: List["SavedJob"] = field(default_factory=list)

    def __repr__(self):
        return f"<Job(Name='{self.Name}', CompanyID={self.CompanyID})>"

# --------------------------
# SavedJob
# --------------------------
@dataclass
class SavedJob:
    SaveID: int
    AccountID: int
    JobID: int
    Date_Saved: datetime = field(default_factory=datetime.now)

    # Relationships
    account: Optional[Account] = None
    job: Optional[Job] = None

    def __repr__(self):
        return f"<SavedJob(AccountID={self.AccountID}, JobID={self.JobID}, SavedAt={self.Date_Saved})>"
