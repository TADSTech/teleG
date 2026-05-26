# Telegram Channel Monitor with ntfy.sh Alerts

Monitor messages from a Telegram channel and send real-time alerts via [ntfy.sh](https://ntfy.sh).

## ✨ Features

- 📡 **Real-time monitoring** of Telegram channels
- 🔔 **Push notifications** via ntfy.sh (desktop, mobile, web)
- 🎯 **Smart filtering** - keyword detection, emoji matching, pattern recognition
- 💾 **Message persistence** - track processed messages, prevent duplicates
- ⏱️ **Rate limiting** - avoid alert spam for repeated triggers
- 🔧 **Easy customization** - add custom filters and logic
- 🚀 **Production ready** - error handling, logging, systemd support

## 🚀 Quick Start

### 1. Clone/Download Files

Save these files to a directory:
- `telegram_monitor.py` - Basic version
- `telegram_monitor_advanced.py` - Advanced version with filters
- `requirements.txt` - Python dependencies
- `.env.example` - Configuration template

### 2. Get Telegram API Credentials

1. Go to https://my.telegram.org/apps
2. Log in with your Telegram account
3. Create a new application
4. Copy your **API ID** and **API Hash**
5. Note your **phone number** (with country code, e.g., +1234567890)

### 3. Set Up Configuration

```bash
# Copy template
cp .env.example .env

# Edit with your details
nano .env  # or your favorite editor
```

Fill in:
```
TELEGRAM_API_ID=your_api_id_here
TELEGRAM_API_HASH=your_api_hash_here
TELEGRAM_PHONE=+1234567890
MONITOR_CHANNEL=@channel_username
NTFY_TOPIC=choose_random_topic_name
```

### 4. Choose Your ntfy Topic

- Go to https://ntfy.sh
- Enter a topic name (random, hard to guess): `https://ntfy.sh/my_custom_topic_12345`
- Subscribe to get notifications:
  - **Desktop**: Bookmark or use browser notifications
  - **Mobile**: Install ntfy app, subscribe to topic
  - **CLI**: `curl -s https://ntfy.sh/my_custom_topic | tail -f`

### 5. Install & Run

```bash
# Install dependencies
pip install -r requirements.txt

# Run basic monitor
python3 telegram_monitor.py

# OR run advanced monitor
python3 telegram_monitor_advanced.py
```

**On first run**: You'll be asked for a Telegram verification code (sent to your phone).

## 📖 Usage Examples

### Basic Version - Customize Triggers

Edit `telegram_monitor.py` to change what triggers alerts:

```python
# What keywords to look for
TRIGGER_KEYWORDS = [
    'alert',
    'urgent',
    'breaking',
    'signal',
]
```

Modify the `should_trigger_alert()` function:

```python
def should_trigger_alert(message_text: str) -> tuple[bool, str]:
    lower_text = message_text.lower()
    
    # Price alerts example
    if 'btc' in lower_text and any(c.isdigit() for c in lower_text):
        return True, "Bitcoin signal"
    
    # Keyword matching
    for keyword in TRIGGER_KEYWORDS:
        if keyword in lower_text:
            return True, f"Keyword: {keyword}"
    
    return False, ""
```

### Advanced Version - Multiple Filters

The advanced version makes it easy to add complex filters:

```python
monitor = TelegramMonitor()

# Add keyword filter
monitor.add_filter(
    MessageFilter.contains_keywords(['urgent', 'breaking']),
    priority=10
)

# Add emoji filter
monitor.add_filter(
    MessageFilter.contains_emoji(['⚠️', '🔴']),
    priority=5
)

# Add regex pattern filter
monitor.add_filter(
    MessageFilter.matches_pattern(r'\$\d+\.?\d*'),  # Match prices like $123.45
    priority=8
)

# Run monitor
await monitor.start()
```

### Alert Priority Levels

```python
send_ntfy_alert(
    title="Alert Title",
    message="Alert message",
    priority='max'   # 'max', 'high', 'default', 'low', 'min'
)
```

### Monitor Multiple Channels

```python
@client.on(events.NewMessage(chats=['@channel1', '@channel2', '@channel3']))
async def handle_new_message(event):
    # Will trigger for all three channels
    pass
```

## 🔧 Configuration Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `TELEGRAM_API_ID` | From my.telegram.org | `123456789` |
| `TELEGRAM_API_HASH` | From my.telegram.org | `abcdef1234567890...` |
| `TELEGRAM_PHONE` | Your Telegram number | `+1234567890` |
| `MONITOR_CHANNEL` | Channel to monitor | `@mychannel` or `123456789` |
| `NTFY_TOPIC` | ntfy.sh topic | `my_alerts_xyz123` |

## 🔐 Security Tips

- 🔒 Keep `.env` file secret (add to `.gitignore`)
- 🚫 Don't commit credentials to git
- 🔑 Use unique, random ntfy topics
- 📱 Enable 2FA on your Telegram account
- 🗑️ Periodically clean up old session files

## 📋 Running as a Service

### Linux Systemd

Create `/etc/systemd/system/telegram-monitor.service`:

```ini
[Unit]
Description=Telegram Channel Monitor
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/project
EnvironmentFile=/path/to/.env
ExecStart=/usr/bin/python3 /path/to/telegram_monitor.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl enable telegram-monitor
sudo systemctl start telegram-monitor
sudo journalctl -u telegram-monitor -f  # View logs
```

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY telegram_monitor.py .
CMD ["python3", "telegram_monitor.py"]
```

```bash
docker build -t telegram-monitor .
docker run --env-file .env telegram-monitor
```

## 🆘 Troubleshooting

### "Could not access channel"
- Make sure you're **subscribed** to the channel
- Use channel username (e.g., `@mychannel`) not full name
- For private channels, use the numeric ID

### No alerts appearing
- Check ntfy.sh topic in browser: `https://ntfy.sh/your_topic`
- Verify keywords/filters match your messages
- Check logs for errors

### "Two-factor authentication enabled"
- Enter password when prompted
- Or disable 2FA temporarily during setup

### Connection keeps dropping
- Normal behavior, script auto-reconnects
- Use systemd/Docker for persistent monitoring

## 📚 API Reference

### Basic Monitor Functions

```python
send_ntfy_alert(title, message, tags=None, priority='default')
should_trigger_alert(message_text) -> (bool, reason)
```

### Advanced Monitor Class

```python
monitor = TelegramMonitor()
monitor.add_filter(filter_func, priority=0)
monitor.should_alert(message_text, message_id) -> (bool, reason)
monitor.send_alert(title, message, priority='high', tags=None)
await monitor.start()
```

### MessageFilter Helpers

```python
MessageFilter.contains_keywords(keywords_list)
MessageFilter.matches_pattern(regex_pattern)
MessageFilter.starts_with(prefix)
MessageFilter.contains_emoji(emoji_list)
```

## 📞 Support

- **ntfy.sh docs**: https://docs.ntfy.sh
- **Telethon docs**: https://docs.telethon.dev
- **Telegram API**: https://core.telegram.org

## 📝 License

MIT - Feel free to modify and use!

---

**Need help?** Check the detailed [SETUP.md](SETUP.md) guide for in-depth instructions.
