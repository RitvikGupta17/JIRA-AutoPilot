# Sprint_Manager/Services/notification_service.py
import smtplib
import markdown # <-- NEW IMPORT
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

class NotificationService:
    def __init__(self, sender_email, sender_password, recipient_email):
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.recipient_email = recipient_email

    def format_report_html(self, reports):
        """Formats the collected agent reports into a nice HTML email using Markdown."""
        
        # CSS styling to make it look professional (Gmail-compatible)
        css_style = """
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
            h1 { color: #0052cc; border-bottom: 2px solid #eee; padding-bottom: 10px; }
            h2 { color: #2c3e50; margin-top: 30px; background-color: #f4f5f7; padding: 10px; border-left: 5px solid #0052cc; }
            ul { margin-bottom: 15px; }
            li { margin-bottom: 5px; }
            strong { color: #d04437; } /* Highlights alerts/blockers */
            .footer { margin-top: 40px; font-size: 12px; color: #777; border-top: 1px solid #eee; padding-top: 10px; }
        </style>
        """

        report_html = f"<html><head>{css_style}</head><body>"
        report_html += "<h1>✈️ JIRA AutoPilot - Daily Sprint Report</h1>"
        report_html += f"<p><strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>"
        
        for agent_name, content in reports.items():
            # Convert the Agent's Markdown content to HTML
            # 'fenced_code' and 'nl2br' help with code blocks and newlines
            html_content = markdown.markdown(content, extensions=['fenced_code', 'nl2br'])
            
            report_html += f"<h2>{agent_name}</h2>"
            report_html += f"<div>{html_content}</div>"

        report_html += '<div class="footer">Generated autonomously by JIRA AutoPilot Agents 🤖</div>'
        report_html += "</body></html>"

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