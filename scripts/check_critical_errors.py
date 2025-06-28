#!/usr/bin/env python3
"""
Check for critical errors and send alerts
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests


class CriticalErrorChecker:
    """Check for critical errors and send alerts"""

    def __init__(self, log_dir="/opt/litecrewai/logs"):
        self.log_dir = Path(log_dir)
        self.alert_threshold = 5  # Alert if more than 5 critical errors in 1 hour
        self.last_alert_file = self.log_dir / ".last_alert"

    def parse_recent_errors(self, minutes=60):
        """Parse errors from the last N minutes"""
        errors = []
        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
        
        error_log = self.log_dir / "error.log"
        if not error_log.exists():
            return errors
            
        with open(error_log, "r") as f:
            for line in f:
                try:
                    log_entry = json.loads(line.strip())
                    log_time = datetime.fromisoformat(
                        log_entry["timestamp"].replace("Z", "+00:00")
                    )
                    if log_time > cutoff_time and log_entry.get("level") in ["ERROR", "CRITICAL"]:
                        errors.append(log_entry)
                except (json.JSONDecodeError, KeyError, ValueError):
                    continue
                    
        return errors

    def should_send_alert(self):
        """Check if we should send an alert (rate limiting)"""
        if not self.last_alert_file.exists():
            return True
            
        last_alert_time = datetime.fromtimestamp(self.last_alert_file.stat().st_mtime)
        # Only send alerts every 30 minutes to prevent spam
        return datetime.now() - last_alert_time > timedelta(minutes=30)

    def update_last_alert(self):
        """Update last alert timestamp"""
        self.last_alert_file.touch()

    def send_email_alert(self, errors):
        """Send email alert"""
        smtp_host = os.getenv("SMTP_HOST")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        smtp_user = os.getenv("SMTP_USER")
        smtp_pass = os.getenv("SMTP_PASS")
        alert_email = os.getenv("ALERT_EMAIL")
        
        if not all([smtp_host, smtp_user, smtp_pass, alert_email]):
            print("Email configuration not found in environment variables")
            return False
            
        try:
            msg = MIMEMultipart()
            msg["From"] = smtp_user
            msg["To"] = alert_email
            msg["Subject"] = f"LiteCrewAI Critical Error Alert - {len(errors)} errors"
            
            body = f"Critical errors detected in LiteCrewAI:\n\n"
            body += f"Total errors: {len(errors)}\n\n"
            body += "Recent errors:\n"
            
            for error in errors[-10:]:  # Last 10 errors
                timestamp = error.get("timestamp", "")
                level = error.get("level", "")
                message = error.get("message", "")
                module = error.get("module", "")
                body += f"\n[{timestamp}] {level} in {module}:\n{message}\n"
                
            msg.attach(MIMEText(body, "plain"))
            
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_pass)
                server.send_message(msg)
                
            print(f"Email alert sent to {alert_email}")
            return True
            
        except Exception as e:
            print(f"Failed to send email alert: {e}")
            return False

    def send_webhook_alert(self, errors):
        """Send webhook alert (Discord/Slack)"""
        webhook_url = os.getenv("ALERT_WEBHOOK_URL")
        if not webhook_url:
            print("Webhook URL not configured")
            return False
            
        try:
            # Detect webhook type
            if "discord" in webhook_url:
                # Discord webhook format
                payload = {
                    "content": f"🚨 **LiteCrewAI Critical Error Alert**",
                    "embeds": [{
                        "title": f"{len(errors)} Critical Errors Detected",
                        "color": 15158332,  # Red
                        "fields": [
                            {
                                "name": "Time Range",
                                "value": "Last 60 minutes",
                                "inline": True
                            },
                            {
                                "name": "Error Count",
                                "value": str(len(errors)),
                                "inline": True
                            }
                        ],
                        "description": f"Most recent error: {errors[-1].get('message', 'Unknown')[:200]}...",
                        "timestamp": datetime.utcnow().isoformat()
                    }]
                }
            else:
                # Slack webhook format
                payload = {
                    "text": f"🚨 LiteCrewAI Critical Error Alert - {len(errors)} errors",
                    "attachments": [{
                        "color": "danger",
                        "fields": [
                            {
                                "title": "Error Count",
                                "value": str(len(errors)),
                                "short": True
                            },
                            {
                                "title": "Time Range",
                                "value": "Last 60 minutes",
                                "short": True
                            }
                        ],
                        "text": f"Most recent error: {errors[-1].get('message', 'Unknown')[:200]}...",
                        "ts": int(datetime.utcnow().timestamp())
                    }]
                }
                
            response = requests.post(webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            
            print("Webhook alert sent successfully")
            return True
            
        except Exception as e:
            print(f"Failed to send webhook alert: {e}")
            return False

    def check_and_alert(self):
        """Main check and alert logic"""
        errors = self.parse_recent_errors()
        
        if len(errors) < self.alert_threshold:
            print(f"Found {len(errors)} errors - below threshold ({self.alert_threshold})")
            return 0
            
        print(f"CRITICAL: Found {len(errors)} errors - sending alerts!")
        
        if not self.should_send_alert():
            print("Alert rate limit in effect - skipping")
            return 0
            
        # Try to send alerts
        alert_sent = False
        
        # Try email first
        if os.getenv("SMTP_HOST"):
            alert_sent |= self.send_email_alert(errors)
            
        # Try webhook
        if os.getenv("ALERT_WEBHOOK_URL"):
            alert_sent |= self.send_webhook_alert(errors)
            
        if alert_sent:
            self.update_last_alert()
            
        return 1 if len(errors) >= self.alert_threshold else 0


if __name__ == "__main__":
    checker = CriticalErrorChecker()
    sys.exit(checker.check_and_alert())