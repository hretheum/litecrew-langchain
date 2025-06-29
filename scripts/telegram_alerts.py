#!/usr/bin/env python3
"""
Telegram alert system for LiteCrewAI
"""

import os
import sys
import json
import asyncio
from datetime import datetime
from typing import Dict, List, Optional
import aiohttp


class TelegramAlertSender:
    """Send alerts via Telegram Bot API"""
    
    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.base_url = "https://api.telegram.org/bot{token}"
        
    def is_configured(self) -> bool:
        """Check if Telegram is configured"""
        return bool(self.bot_token and self.chat_id)
    
    async def send_message(self, text: str, parse_mode: str = "Markdown") -> bool:
        """Send message to Telegram"""
        if not self.is_configured():
            print("Telegram not configured. Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env")
            return False
            
        url = self.base_url.format(token=self.bot_token) + "/sendMessage"
        
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": True
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        return True
                    else:
                        error = await response.text()
                        print(f"Telegram API error: {error}")
                        return False
        except Exception as e:
            print(f"Failed to send Telegram message: {e}")
            return False
    
    def format_alert(self, alert: Dict) -> str:
        """Format alert for Telegram"""
        severity_emoji = {
            "critical": "🚨",
            "warning": "⚠️",
            "info": "ℹ️"
        }.get(alert.get("severity", "info").lower(), "📢")
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        text = f"{severity_emoji} *LiteCrewAI Alert*\n\n"
        text += f"*Severity:* {alert.get('severity', 'Unknown').upper()}\n"
        text += f"*Time:* {timestamp}\n"
        text += f"*Alert:* {alert.get('alert_name', 'Unknown')}\n\n"
        text += f"*Message:*\n{alert.get('message', 'No message')}\n"
        
        if alert.get("metric_name"):
            text += f"\n*Metric:* `{alert['metric_name']}`\n"
            text += f"*Value:* `{alert.get('value', 'N/A')}`\n"
            
        # Add server info
        text += f"\n_Server: {os.getenv('DROPLET_IP', 'Unknown')}_"
        
        return text
    
    async def send_alert(self, alert: Dict) -> bool:
        """Send formatted alert"""
        message = self.format_alert(alert)
        return await self.send_message(message)
    
    async def send_batch_alerts(self, alerts: List[Dict]) -> bool:
        """Send multiple alerts in one message"""
        if not alerts:
            return True
            
        severity_order = {"critical": 0, "warning": 1, "info": 2}
        sorted_alerts = sorted(
            alerts, 
            key=lambda x: severity_order.get(x.get("severity", "info").lower(), 3)
        )
        
        # Group by severity
        grouped = {}
        for alert in sorted_alerts:
            severity = alert.get("severity", "info").lower()
            if severity not in grouped:
                grouped[severity] = []
            grouped[severity].append(alert)
        
        # Format message
        text = "🔔 *LiteCrewAI Alert Summary*\n\n"
        text += f"*Total Alerts:* {len(alerts)}\n\n"
        
        for severity, severity_alerts in grouped.items():
            emoji = {"critical": "🚨", "warning": "⚠️", "info": "ℹ️"}.get(severity, "📢")
            text += f"{emoji} *{severity.upper()}* ({len(severity_alerts)})\n"
            
            for alert in severity_alerts[:3]:  # Show max 3 per severity
                text += f"  • {alert.get('message', 'No message')[:50]}...\n"
            
            if len(severity_alerts) > 3:
                text += f"  • _...and {len(severity_alerts) - 3} more_\n"
            text += "\n"
        
        text += f"\n_Server: {os.getenv('DROPLET_IP', 'Unknown')}_"
        text += f"\n_Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_"
        
        return await self.send_message(text)
    
    async def test_connection(self) -> bool:
        """Test Telegram connection"""
        test_message = (
            "✅ *LiteCrewAI Telegram Alerts Configured*\n\n"
            "This is a test message to confirm alerts are working.\n"
            f"_Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_"
        )
        return await self.send_message(test_message)


# Integration with existing alert system
async def send_telegram_notification(alerts: List[Dict]):
    """Send alerts to Telegram (drop-in replacement for webhook)"""
    sender = TelegramAlertSender()
    
    if not sender.is_configured():
        print("Telegram alerts not configured")
        return
    
    if len(alerts) == 1:
        await sender.send_alert(alerts[0])
    else:
        await sender.send_batch_alerts(alerts)


if __name__ == "__main__":
    # Test script
    async def test():
        sender = TelegramAlertSender()
        
        if not sender.is_configured():
            print("❌ Telegram not configured!")
            print("\nAdd to your .env file:")
            print("TELEGRAM_BOT_TOKEN=your_bot_token_here")
            print("TELEGRAM_CHAT_ID=your_chat_id_here")
            print("\nTo get bot token:")
            print("1. Message @BotFather on Telegram")
            print("2. Create new bot with /newbot")
            print("3. Copy the token")
            print("\nTo get chat ID:")
            print("1. Message your bot")
            print("2. Visit: https://api.telegram.org/bot<TOKEN>/getUpdates")
            print("3. Look for 'chat':{'id':YOUR_CHAT_ID}")
            return
        
        print("Testing Telegram connection...")
        if await sender.test_connection():
            print("✅ Test message sent successfully!")
            
            # Test alert
            test_alert = {
                "severity": "warning",
                "alert_name": "test_alert",
                "message": "This is a test alert from LiteCrewAI",
                "metric_name": "system.test",
                "value": 42
            }
            
            print("\nSending test alert...")
            if await sender.send_alert(test_alert):
                print("✅ Test alert sent successfully!")
        else:
            print("❌ Failed to send test message")
    
    asyncio.run(test())