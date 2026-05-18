import logging
from typing import List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class EmailConfig:
    """Email configuration"""
    enabled: bool = False
    smtp_server: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    from_email: str = ""
    to_emails: List[str] = None
    
    def __post_init__(self):
        if self.to_emails is None:
            self.to_emails = []


class EmailService:
    """Service for sending email alerts about new opportunities"""
    
    _config: EmailConfig = EmailConfig()
    
    @classmethod
    def configure(cls, config: EmailConfig) -> None:
        """Configure email service"""
        cls._config = config
        logger.info(f"Email service configured (enabled: {config.enabled})")
    
    @classmethod
    def send_alert(cls, subject: str, body: str) -> bool:
        """Send an email alert"""
        if not cls._config.enabled:
            logger.info("Email service disabled, skipping alert")
            return False
        
        try:
            # Import smtplib only when needed to avoid import errors if not configured
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            msg = MIMEMultipart()
            msg['From'] = cls._config.from_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'html'))
            
            server = smtplib.SMTP(cls._config.smtp_server, cls._config.smtp_port)
            server.starttls()
            server.login(cls._config.smtp_username, cls._config.smtp_password)
            
            for to_email in cls._config.to_emails:
                msg['To'] = to_email
                server.send_message(msg)
            
            server.quit()
            logger.info(f"Email alert sent: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
            return False
    
    @classmethod
    def send_new_opportunities_alert(cls, count: int, sources: List[str]) -> bool:
        """Send alert about new opportunities"""
        subject = f"New Startup Opportunities: {count} Added"
        
        body = f"""
        <html>
        <body>
            <h2>New Opportunities Available</h2>
            <p><strong>{count}</strong> new opportunities have been added to the aggregator.</p>
            
            <h3>Sources:</h3>
            <ul>
                {''.join(f'<li>{source}</li>' for source in sources)}
            </ul>
            
            <p>View them at: <a href="http://127.0.0.1:5000/">Dashboard</a></p>
        </body>
        </html>
        """
        
        return cls.send_alert(subject, body)
    
    @classmethod
    def send_scraper_failure_alert(cls, source: str, error: str) -> bool:
        """Send alert about scraper failure"""
        subject = f"Scraper Failure: {source}"
        
        body = f"""
        <html>
        <body>
            <h2>Scraper Failure Alert</h2>
            <p>The scraper for <strong>{source}</strong> has failed.</p>
            
            <h3>Error:</h3>
            <pre>{error}</pre>
            
            <p>Please check the monitoring dashboard for details.</p>
        </body>
        </html>
        """
        
        return cls.send_alert(subject, body)
