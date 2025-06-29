"""
Alert system for LiteCrewAI
"""

from typing import Dict, List, Optional, Callable
from datetime import datetime, timedelta
import asyncio
import logging

from app.core.metrics_storage import MetricsStorage


logger = logging.getLogger(__name__)


class AlertRule:
    """Define an alert rule"""
    
    def __init__(
        self,
        name: str,
        metric_name: str,
        condition: Callable[[float], bool],
        duration_seconds: int = 60,
        severity: str = "warning",
        message_template: str = "Alert: {metric_name} triggered",
    ):
        self.name = name
        self.metric_name = metric_name
        self.condition = condition
        self.duration_seconds = duration_seconds
        self.severity = severity
        self.message_template = message_template
        self.last_triggered = None


class AlertManager:
    """Manage alerts and rules"""
    
    def __init__(self, storage: MetricsStorage):
        self.storage = storage
        self.rules: List[AlertRule] = []
        self.initialize_default_rules()
        
    def initialize_default_rules(self):
        """Set up default alert rules"""
        
        # High CPU usage
        self.add_rule(AlertRule(
            name="high_cpu_usage",
            metric_name="system.cpu.usage_percent",
            condition=lambda x: x > 80,
            duration_seconds=300,  # 5 minutes
            severity="warning",
            message_template="CPU usage above 80% for 5 minutes: {value:.1f}%"
        ))
        
        # High memory usage
        self.add_rule(AlertRule(
            name="high_memory_usage",
            metric_name="system.memory.percent",
            condition=lambda x: x > 85,
            duration_seconds=300,
            severity="warning",
            message_template="Memory usage above 85% for 5 minutes: {value:.1f}%"
        ))
        
        # Disk space critical
        self.add_rule(AlertRule(
            name="disk_space_critical",
            metric_name="system.disk.usage_percent",
            condition=lambda x: x > 90,
            duration_seconds=60,
            severity="critical",
            message_template="Disk usage critical: {value:.1f}%"
        ))
        
        # High error rate
        self.add_rule(AlertRule(
            name="high_error_rate",
            metric_name="http.request.error_rate",
            condition=lambda x: x > 0.05,  # 5% error rate
            duration_seconds=120,
            severity="warning",
            message_template="High error rate detected: {value:.1%}"
        ))
        
        # Slow response time
        self.add_rule(AlertRule(
            name="slow_response_time",
            metric_name="http.request.duration_seconds",
            condition=lambda x: x > 2.0,  # 2 seconds
            duration_seconds=180,
            severity="warning",
            message_template="Slow response time: {value:.2f}s average"
        ))
        
        # High LLM costs
        self.add_rule(AlertRule(
            name="high_llm_costs",
            metric_name="llm.cost.hourly_usd",
            condition=lambda x: x > 1.0,  # $1/hour
            duration_seconds=3600,
            severity="warning",
            message_template="High LLM costs: ${value:.2f}/hour"
        ))
        
    def add_rule(self, rule: AlertRule):
        """Add a new alert rule"""
        self.rules.append(rule)
        
    def check_rule(self, rule: AlertRule) -> Optional[Dict]:
        """Check if a rule should trigger an alert"""
        try:
            # Get recent metrics
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(seconds=rule.duration_seconds)
            
            metrics = self.storage.get_metrics(
                rule.metric_name,
                start_time=start_time,
                end_time=end_time
            )
            
            if not metrics:
                return None
                
            # Check if condition is met for all recent values
            values = [m["metric_value"] for m in metrics]
            if not values:
                return None
                
            avg_value = sum(values) / len(values)
            
            if rule.condition(avg_value):
                # Check if we should trigger (rate limiting)
                if rule.last_triggered:
                    time_since_last = datetime.utcnow() - rule.last_triggered
                    if time_since_last < timedelta(minutes=30):
                        return None  # Rate limit alerts
                        
                rule.last_triggered = datetime.utcnow()
                
                return {
                    "rule_name": rule.name,
                    "metric_name": rule.metric_name,
                    "value": avg_value,
                    "severity": rule.severity,
                    "message": rule.message_template.format(
                        metric_name=rule.metric_name,
                        value=avg_value
                    )
                }
                
        except Exception as e:
            logger.error(f"Error checking rule {rule.name}: {e}")
            
        return None
        
    async def check_all_rules(self):
        """Check all alert rules"""
        alerts_triggered = []
        
        for rule in self.rules:
            alert = self.check_rule(rule)
            if alert:
                alerts_triggered.append(alert)
                
                # Record alert in storage
                self.storage.record_alert(
                    alert_name=alert["rule_name"],
                    severity=alert["severity"],
                    message=alert["message"],
                    metric_name=alert["metric_name"],
                    metric_value=alert["value"]
                )
                
                logger.warning(f"Alert triggered: {alert['message']}")
                
        return alerts_triggered
        
    async def start_monitoring(self, interval_seconds: int = 60):
        """Start continuous alert monitoring"""
        logger.info(f"Starting alert monitoring with {interval_seconds}s interval")
        
        while True:
            try:
                await self.check_all_rules()
            except Exception as e:
                logger.error(f"Error in alert monitoring: {e}")
                
            await asyncio.sleep(interval_seconds)


# Import Telegram sender if available
try:
    from scripts.telegram_alerts import send_telegram_notification
except ImportError:
    send_telegram_notification = None

# Webhook notifier
async def send_webhook_notification(webhook_url: str, alerts: List[Dict]):
    """Send alert notifications to webhook"""
    import aiohttp
    
    if not alerts:
        return
    
    # Check if we should use Telegram instead
    if webhook_url == "telegram" and send_telegram_notification:
        await send_telegram_notification(alerts)
        return
        
    # Format for Discord/Slack
    if "discord" in webhook_url:
        payload = {
            "content": f"🚨 **LiteCrewAI Alerts** - {len(alerts)} active",
            "embeds": [
                {
                    "title": alert["message"],
                    "color": 15158332 if alert["severity"] == "critical" else 16776960,
                    "fields": [
                        {"name": "Severity", "value": alert["severity"], "inline": True},
                        {"name": "Metric", "value": alert["metric_name"], "inline": True},
                        {"name": "Value", "value": f"{alert['value']:.2f}", "inline": True}
                    ],
                    "timestamp": datetime.utcnow().isoformat()
                }
                for alert in alerts[:5]  # Limit to 5 alerts
            ]
        }
    else:  # Slack format
        payload = {
            "text": f"🚨 LiteCrewAI Alerts - {len(alerts)} active",
            "attachments": [
                {
                    "color": "danger" if alert["severity"] == "critical" else "warning",
                    "title": alert["message"],
                    "fields": [
                        {"title": "Severity", "value": alert["severity"], "short": True},
                        {"title": "Value", "value": f"{alert['value']:.2f}", "short": True}
                    ],
                    "ts": int(datetime.utcnow().timestamp())
                }
                for alert in alerts[:5]
            ]
        }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(webhook_url, json=payload) as response:
                if response.status != 200:
                    logger.error(f"Failed to send webhook: {response.status}")
    except Exception as e:
        logger.error(f"Error sending webhook notification: {e}")