"""
Advanced Telegram Monitor with Persistence & Custom Filters
Includes message persistence, deduplication, and advanced filtering
"""

import asyncio
import os
import json
import requests
from pathlib import Path
from datetime import datetime, timedelta
from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError
import logging
from typing import Callable
import dotenv

dotenv.load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
API_ID = int(os.getenv('TELEGRAM_API_ID', ''))
API_HASH = os.getenv('TELEGRAM_API_HASH', '')
PHONE = os.getenv('TELEGRAM_PHONE', '')
CHANNEL_TO_MONITOR = os.getenv('MONITOR_CHANNEL', '')
NTFY_TOPIC = os.getenv('NTFY_TOPIC', 'telegram_alerts')
NTFY_URL = f'https://ntfy.sh/{NTFY_TOPIC}'

# Persistence
MESSAGE_LOG_FILE = 'processed_messages.json'
MAX_SAVED_MESSAGES = 1000  # Keep last N messages to prevent duplicates


class MessageFilter:
    """Define custom message filters"""
    
    @staticmethod
    def contains_keywords(keywords: list[str]) -> Callable:
        """Filter messages containing any keyword (case-insensitive)"""
        def filter_func(text: str) -> bool:
            lower = text.lower()
            return any(kw in lower for kw in keywords)
        return filter_func
    
    @staticmethod
    def matches_pattern(pattern: str) -> Callable:
        """Filter messages matching regex pattern"""
        import re
        regex = re.compile(pattern)
        def filter_func(text: str) -> bool:
            return bool(regex.search(text))
        return filter_func
    
    @staticmethod
    def starts_with(prefix: str) -> Callable:
        """Filter messages starting with prefix"""
        def filter_func(text: str) -> bool:
            return text.startswith(prefix)
        return filter_func
    
    @staticmethod
    def contains_emoji(emojis: list[str]) -> Callable:
        """Filter messages containing specific emojis"""
        def filter_func(text: str) -> bool:
            return any(emoji in text for emoji in emojis)
        return filter_func


class MessagePersistence:
    """Track processed messages to prevent duplicates"""
    
    def __init__(self, filepath: str = MESSAGE_LOG_FILE):
        self.filepath = filepath
        self.messages = self._load()
    
    def _load(self) -> dict:
        """Load message history from disk"""
        if Path(self.filepath).exists():
            try:
                with open(self.filepath, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not load message history: {e}")
        return {}
    
    def _save(self):
        """Save message history to disk"""
        try:
            with open(self.filepath, 'w') as f:
                json.dump(self.messages, f)
        except Exception as e:
            logger.error(f"Could not save message history: {e}")
    
    def add(self, message_id: int, text: str, timestamp: datetime = None):
        """Add message to history"""
        if timestamp is None:
            timestamp = datetime.now()
        
        self.messages[str(message_id)] = {
            'text': text[:100],  # Store first 100 chars
            'timestamp': timestamp.isoformat()
        }
        
        # Keep only recent messages
        if len(self.messages) > MAX_SAVED_MESSAGES:
            oldest_key = min(self.messages.keys(), 
                           key=lambda k: self.messages[k]['timestamp'])
            del self.messages[oldest_key]
        
        self._save()
    
    def is_duplicate(self, message_id: int) -> bool:
        """Check if message was already processed"""
        return str(message_id) in self.messages
    
    def cleanup_old(self, days: int = 7):
        """Remove messages older than X days"""
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        keys_to_delete = [
            k for k, v in self.messages.items()
            if v['timestamp'] < cutoff
        ]
        for k in keys_to_delete:
            del self.messages[k]
        self._save()


class TelegramMonitor:
    """Main monitor class with advanced features"""
    
    def __init__(self):
        self.client = TelegramClient('session', API_ID, API_HASH)
        self.persistence = MessagePersistence()
        self.filters = []  # List of filter functions
        self.alert_history = {}  # Track alerts to prevent spam
    
    def add_filter(self, filter_func: Callable, priority: int = 0):
        """
        Add a filter function
        
        Args:
            filter_func: Function that takes text and returns bool
            priority: Higher = checked first (0 = default)
        """
        self.filters.append((filter_func, priority))
        self.filters.sort(key=lambda x: x[1], reverse=True)
    
    def should_alert(self, message_text: str, message_id: int) -> tuple[bool, str]:
        """Check if message should trigger alert"""
        
        # Duplicate check
        if self.persistence.is_duplicate(message_id):
            return False, "Duplicate"
        
        # No filters - alert on all messages
        return True, "New message"
    
    def send_alert(self, title: str, message: str, priority: str = 'high', tags: str = None):
        """Send alert to ntfy.sh"""
        
        # Rate limiting: don't send same alert twice in 5 mins
        alert_key = f"{title}:{message[:50]}"
        now = datetime.now()
        
        if alert_key in self.alert_history:
            last_sent = self.alert_history[alert_key]
            if (now - last_sent).total_seconds() < 300:  # 5 minutes
                logger.debug(f"Rate limited: {title}")
                return
        
        headers = {
            'Title': title,
            'Priority': priority,
        }
        
        if tags:
            headers['Tags'] = tags
        
        try:
            response = requests.post(
                NTFY_URL,
                data=message.encode('utf-8'),
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"✓ Alert sent: {title}")
                self.alert_history[alert_key] = now
            else:
                logger.error(f"✗ Alert failed: {response.status_code}")
                
        except Exception as e:
            logger.error(f"✗ Error sending alert: {e}")
    
    async def start(self):
        """Start the monitor"""
        try:
            await self.client.start(phone=PHONE)
            logger.info("✓ Connected to Telegram")
            
            # Get channel
            try:
                channel = await self.client.get_entity(CHANNEL_TO_MONITOR)
                logger.info(f"✓ Monitoring: {channel.title}")
            except Exception as e:
                logger.error(f"✗ Could not access channel: {e}")
                await self.client.disconnect()
                return
            
            # Register message handler
            @self.client.on(events.NewMessage(chats=CHANNEL_TO_MONITOR))
            async def handler(event):
                await self._handle_message(event)
            
            logger.info(f"📡 Monitor started. Alerts → {NTFY_URL}")
            await self.client.run_until_disconnected()
            
        except SessionPasswordNeededError:
            logger.error("✗ 2FA enabled. Please handle authentication.")
        except Exception as e:
            logger.error(f"✗ Error: {e}")
        finally:
            await self.client.disconnect()
    
    async def _handle_message(self, event):
        """Process incoming message"""
        try:
            message = event.message
            text = message.text or ""
            sender = await message.get_sender()
            sender_name = getattr(sender, 'first_name', 'Unknown')
            
            logger.debug(f"Message from {sender_name}: {text[:50]}")
            
            # Check if should alert
            should_alert, reason = self.should_alert(text, message.id)
            
            if should_alert:
                alert_text = text[:150] + ("..." if len(text) > 150 else "")
                self.send_alert(
                    title=f"📢 {sender_name}",
                    message=alert_text,
                    priority='high',
                    tags='telegram'
                )
                self.persistence.add(message.id, text, message.date)
            
        except Exception as e:
            logger.error(f"✗ Error handling message: {e}")


async def main():
    """Main entry point"""
    
    # Validate config
    if not all([API_ID, API_HASH, PHONE, CHANNEL_TO_MONITOR]):
        logger.error("Missing environment variables. Check .env file.")
        return
    
    # Create monitor (no filters - alerts on ALL messages)
    monitor = TelegramMonitor()
    
    # Cleanup old messages monthly
    monitor.persistence.cleanup_old(days=30)
    
    # Start monitoring
    await monitor.start()


if __name__ == '__main__':
    asyncio.run(main())
