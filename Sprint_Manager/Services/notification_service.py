# Sprint_Manager/Services/notification_service.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

class NotificationService:
    def __init__(self, sender_email, sender_password, recipient_email):
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.recipient_email = recipient_email

    def format_report_html(self, reports):
        """Formats the collected agent reports into a nice HTML email."""
        report_html = "<h1>JIRA AutoPilot - Daily Sprint Report</h1>"
        report_html += f"<p>Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>"
        report_html += "<hr>"

        for agent_name, content in reports.items():
            report_html += f"<h2>- {agent_name} Summary -</h2>"
            # Replace newlines with <br> for HTML formatting
            report_html += f"<p>{content.replace('\n', '<br>')}</p>"

        return report_html

    def send_report(self, reports):
        """Sends the compiled report via email."""
        if not all([self.sender_email, self.sender_password, self.recipient_email]):
            print("  [Email] Email credentials not fully configured. Skipping report.")
            return

        message = MIMEMultipart("alternative")
        message["Subject"] = f"JIRA AutoPilot Daily Report - {datetime.now().strftime('%Y-%m-%d')}"
        message["From"] = self.sender_email
        message["To"] = self.recipient_email

        html_body = self.format_report_html(reports)
        message.attach(MIMEText(html_body, "html"))

        try:
            # Using Gmail's SMTP server as an example
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            server.sendmail(self.sender_email, self.recipient_email, message.as_string())
            server.quit()
            print(f"  [Email] Report successfully sent to {self.recipient_email}")
        except Exception as e:
            print(f"  [Email] Failed to send report: {e}")