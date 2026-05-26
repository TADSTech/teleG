"""
Telegram Channel Monitor with ntfy.sh Alerts
Monitors a Telegram channel and sends alerts via ntfy.sh
"""

import asyncio
import os
import requests
from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError
import logging
import dotenv

# Load environment variables
dotenv.load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Configuration
API_ID = int(os.getenv('TELEGRAM_API_ID', ''))
API_HASH = os.getenv('TELEGRAM_API_HASH', '')
PHONE = os.getenv('TELEGRAM_PHONE', '')
SESSION_NAME = 'telegram_monitor'

# Channel to monitor (can be username like 'mychannel' or channel ID)
CHANNEL_TO_MONITOR = os.getenv('MONITOR_CHANNEL', '')

# ntfy.sh configuration
NTFY_TOPIC = os.getenv('NTFY_TOPIC', 'my_telegram_alerts')
NTFY_URL = f'https://ntfy.sh/{NTFY_TOPIC}'

# Keywords to trigger alerts (customize as needed)
TRIGGER_KEYWORDS = [
    'alert',
    'urgent',
    'breaking',
    'important',
]

# Initialize the Telegram client
client = TelegramClient(SESSION_NAME, API_ID, API_HASH)


def send_ntfy_alert(title: str, message: str, tags: str = None, priority: str = 'default'):
    """
    Send an alert to ntfy.sh
    
    Args:
        title: Alert title
        message: Alert message
        tags: Optional tags (comma-separated)
        priority: 'min', 'low', 'default', 'high', 'max'
    """
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
            logger.info(f"✓ Alert sent to ntfy.sh: {title}")
        else:
            logger.error(f"✗ Failed to send alert: {response.status_code}")
            
    except Exception as e:
        logger.error(f"✗ Error sending ntfy alert: {e}")


def should_trigger_alert(message_text: str) -> tuple[bool, str]:
    """
    Determine if a message should trigger an alert
    Returns (should_alert, reason)
    """
    if not message_text:
        return False, ""
    
    lower_text = message_text.lower()
    
    # Check for keywords
    for keyword in TRIGGER_KEYWORDS:
        if keyword in lower_text:
            return True, f"Keyword found: {keyword}"
    
    # Check for specific patterns (customize these)
    if message_text.startswith('$'):  # e.g., price signals
        return True, "Signal message detected"
    
    if any(emoji in message_text for emoji in ['⚠️', '🔴', '🚨']):
        return True, "Alert emoji detected"
    
    return False, ""


@client.on(events.NewMessage(chats=CHANNEL_TO_MONITOR))
async def handle_new_message(event):
    """Handle new messages from monitored channel"""
    try:
        message = event.message
        sender = await message.get_sender()
        
        # Get message text
        text = message.text or ""
        
        logger.info(f"📨 New message from {sender.first_name}: {text[:50]}...")
        
        # Check if message should trigger alert
        should_alert, reason = should_trigger_alert(text)
        
        if should_alert:
            # Prepare alert details
            sender_name = getattr(sender, 'first_name', 'Unknown')
            alert_title = f"📢 {sender_name}: {reason}"
            
            # Truncate message for alert
            alert_message = text[:200]
            if len(text) > 200:
                alert_message += "..."
            
            # Send the alert
            send_ntfy_alert(
                title=alert_title,
                message=alert_message,
                tags='telegram',
                priority='high'
            )
        
    except Exception as e:
        logger.error(f"✗ Error processing message: {e}")


async def main():
    """Main function to start the monitor"""
    try:
        await client.start(phone=PHONE)
        logger.info("✓ Connected to Telegram")
        
        # Verify we can access the channel
        try:
            channel = await client.get_entity(CHANNEL_TO_MONITOR)
            logger.info(f"✓ Monitoring channel: {channel.title}")
        except Exception as e:
            logger.error(f"✗ Could not access channel '{CHANNEL_TO_MONITOR}': {e}")
            logger.error("Make sure you're subscribed to the channel and CHANNEL_TO_MONITOR is correct")
            await client.disconnect()
            return
        
        logger.info("📡 Monitor started. Listening for messages...")
        logger.info(f"Alerts will be sent to: {NTFY_URL}")
        
        # Keep the client running
        await client.run_until_disconnected()
        
    except SessionPasswordNeededError:
        logger.error("✗ Two-factor authentication enabled. Please handle in code.")
    except Exception as e:
        logger.error(f"✗ Error: {e}")
    finally:
        await client.disconnect()


if __name__ == '__main__':
    # Validate configuration
    if not all([API_ID, API_HASH, PHONE, CHANNEL_TO_MONITOR]):
        print("❌ Missing required environment variables:")
        print("   TELEGRAM_API_ID")
        print("   TELEGRAM_API_HASH")
        print("   TELEGRAM_PHONE")
        print("   MONITOR_CHANNEL")
        exit(1)
    
    asyncio.run(main())
