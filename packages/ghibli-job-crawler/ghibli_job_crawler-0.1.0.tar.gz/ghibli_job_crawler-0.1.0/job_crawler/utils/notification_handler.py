from typing import List

from .email_service import EmailService
from .logger import logger
from ..database.handlers import (
    get_all_user_emails,
    get_new_jobs_count,
)


class NotificationHandler:
    def __init__(self):
        """Khởi tạo Notification Handler"""
        self.email_service = EmailService()
    
    def get_notification_enabled_users(self) -> List[str]:
        """
        Lấy danh sách email của users có bật thông báo
        
        Returns:
            Danh sách email
        """

        try:
            email_list = get_all_user_emails()
            
            logger.info(f"📋 Tìm thấy {len(email_list)} users bật thông báo")
            return email_list
            
        except Exception as e:
            logger.error(f"❌ Lỗi khi lấy danh sách users: {str(e)}")
            return []
    
    def count_new_jobs(self, crawl_id: int = None) -> int:
        """
        Đếm số lượng job mới (IsNew = 1)
        
        Args:
            crawl_id: ID của lần crawl (nếu muốn đếm theo lần crawl cụ thể)
        
        Returns:
            Số lượng job mới
        """

        count = get_new_jobs_count(crawl_id)

        logger.info(f"📊 Số lượng job mới: {count}")
 
        return count
    
    def send_notifications_after_crawl(self, crawl_id: int, source_name: str):
        """
        Gửi thông báo cho users sau khi crawl xong
        
        Args:
            crawl_id: ID của lần crawl
            source_name: Tên nguồn crawl (TopCV, VietnamWorks, etc.)
        """

        logger.info(f"\n{'='*80}")
        logger.info(f"🔔 BẮT ĐẦU QUÁ TRÌNH GỬI THÔNG BÁO")
        logger.info(f"{'='*80}")
        
        # Đếm số job mới từ lần crawl này
        new_job_count = self.count_new_jobs(crawl_id)
        
        if new_job_count == 0:
            logger.debug("⚠️ Không có job mới, không gửi thông báo")
            return
        
        # Lấy danh sách users cần gửi thông báo
        recipient_emails = self.get_notification_enabled_users()
        
        if not recipient_emails:
            logger.info("⚠️ Không có user nào bật thông báo")
            return
        
        # Gửi email hàng loạt
        success_count = self.email_service.send_bulk_notifications(
            recipient_emails=recipient_emails,
            job_count=new_job_count,
            source_name=source_name
        )
        
        logger.info(f"✅ Hoàn thành! Đã gửi {success_count}/{len(recipient_emails)} email thành công")


# Test function
if __name__ == "__main__":
    logger.info("🧪 Test Notification Handler...")
    
    handler = NotificationHandler()
    
    # Test đếm job mới
    count = handler.count_new_jobs()
    print(f"Tổng số job mới: {count}")
    
    # Test lấy users
    users = handler.get_notification_enabled_users()
    print(f"Danh sách email: {users}")
    
    # Test gửi thông báo (uncomment để test thật)
    # handler.send_notifications_after_crawl(crawl_id=1, source_name="TopCV")