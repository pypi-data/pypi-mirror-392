import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List

from dotenv import load_dotenv

from .logger import logger


load_dotenv()

class EmailService:
    def __init__(self):
        """Khởi tạo Email Service với Gmail SMTP"""
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = os.getenv("GMAIL_EMAIL")
        self.sender_password = os.getenv("GMAIL_APP_PASSWORD")
        
        if not self.sender_email or not self.sender_password:
            raise ValueError("⚠️ Chưa cấu hình GMAIL_EMAIL và GMAIL_APP_PASSWORD trong file .env")
    
    def send_job_notification(self, recipient_email: str, job_count: int, source_name: str = "JobCrawler"):
        """
        Gửi email thông báo số lượng công việc mới
        
        Args:
            recipient_email: Email người nhận
            job_count: Số lượng công việc mới
            source_name: Tên nguồn crawl
        """
        
        try:
            # Tạo nội dung email
            subject = f"🎯 Chúc bạn sớm thành công! Hôm nay có {job_count} công việc mới"
            
            body = f"""
Xin chào,

Chúng tôi vừa cập nhật thêm {job_count} công việc mới từ {source_name}.

Đừng bỏ lỡ cơ hội! Hãy truy cập ngay để xem các công việc phù hợp với bạn.

Chúc bạn sớm tìm được công việc mơ ước!

---
Trân trọng,
Đội ngũ JobCrawler
            """
            
            # Tạo message
            message = MIMEMultipart()
            message["From"] = self.sender_email
            message["To"] = recipient_email
            message["Subject"] = subject
            message.attach(MIMEText(body, "plain", "utf-8"))
            
            # Kết nối và gửi email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(message)
            
            logger.info(f"✅ Đã gửi email đến {recipient_email}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Lỗi khi gửi email đến {recipient_email}: {str(e)}")
            return False
    
    def send_bulk_notifications(self, recipient_emails: List[str], job_count: int, source_name: str = "JobCrawler"):
        """
        Gửi email hàng loạt cho nhiều người dùng
        
        Args:
            recipient_emails: Danh sách email người nhận
            job_count: Số lượng công việc mới
            source_name: Tên nguồn crawl
        
        Returns:
            Số lượng email gửi thành công
        """
        success_count = 0
        failed_count = 0
        
        logger.info(f"\n{'='*80}")
        logger.info(f"📧 BẮT ĐẦU GỬI EMAIL THÔNG BÁO CHO {len(recipient_emails)} NGƯỜI DÙNG")
        logger.info(f"{'='*80}")
        
        for email in recipient_emails:
            if self.send_job_notification(email, job_count, source_name):
                success_count += 1
            else:
                failed_count += 1
        
        logger.info(f"\n{'='*80}")
        logger.info(f"📊 KẾT QUẢ GỬI EMAIL:")
        logger.info(f"   ✅ Thành công: {success_count}")
        logger.info(f"   ❌ Thất bại: {failed_count}")
        logger.info(f"{'='*80}\n")
        
        return success_count


# Test function
if __name__ == "__main__":
    logger.info("🧪 Test Email Service...")
    
    # Test gửi 1 email
    email_service = EmailService()
    email_service.send_job_notification(
        recipient_email="test@example.com",
        job_count=25,
        source_name="TopCV"
    )