import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from typing import Dict, Any

async def send_email(options: Dict[str, Any]):
    """
    Send email using SMTP
    """
    try:
        # Get environment variables with defaults
        smtp_user = os.getenv("SMTP_USER", "")
        smtp_pass = os.getenv("SMTP_PASS", "")
        smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        
        if not smtp_user or not smtp_pass:
            raise ValueError("SMTP_USER and SMTP_PASS environment variables are required")
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = smtp_user
        msg['To'] = options['email']
        msg['Subject'] = options['subject']
        
        # Add body to email
        msg.attach(MIMEText(options['message'], 'plain'))
        
        # Create SMTP session
        server = smtplib.SMTP(host=smtp_host, port=smtp_port)
        
        # Start TLS for security
        server.starttls()
        
        # Login to the server
        server.login(smtp_user, smtp_pass)
        
        # Send email
        text = msg.as_string()
        server.sendmail(smtp_user, options['email'], text)
        
        # Close the connection
        server.quit()
        
        return True
        
    except Exception as e:
        print(f"Error sending email: {e}")
        raise e 