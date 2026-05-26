## Telegram Channel Monitor Setup Guide

### 1. Get Telegram API Credentials

1. Go to https://my.telegram.org/apps
2. Log in with your Telegram account
3. Create a new application:
   - Fill in app details (name, short name, etc.)
   - Accept terms and create
4. Copy your **API ID** and **API Hash**
5. Get your phone number (the one registered with Telegram)

### 2. Set Environment Variables

Create a `.env` file in your project directory:

```bash
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_PHONE=+1234567890
MONITOR_CHANNEL=@channel_username
NTFY_TOPIC=my_custom_topic
```

**Or set them in your shell:**

```bash
export TELEGRAM_API_ID=123456
export TELEGRAM_API_HASH=abc123def456
export TELEGRAM_PHONE=+1234567890
export MONITOR_CHANNEL=@mychannel
export NTFY_TOPIC=telegram_alerts
```

### 3. Get ntfy.sh Topic

1. Go to https://ntfy.sh
2. Choose a topic name (something random/hard to guess)
3. Subscribe to get notifications:
   - **Desktop**: Install app or bookmark https://ntfy.sh/your_topic
   - **Mobile**: Download ntfy app and subscribe
   - **Webhook**: Post to https://ntfy.sh/your_topic for notifications

### 4. Customize Alert Triggers

Edit the `TRIGGER_KEYWORDS` and `should_trigger_alert()` function in the script to match your needs:

```python
TRIGGER_KEYWORDS = [
    'alert',
    'urgent',
    'custom_keyword',
]
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

### 6. Run the Monitor

```bash
python telegram_monitor.py
```

**First run:** The script will ask for a verification code sent to your Telegram account.

### Advanced Usage

#### Monitor Multiple Channels

```python
@client.on(events.NewMessage(chats=['@channel1', '@channel2']))
async def handle_new_message(event):
    # Will trigger for both channels
    pass
```

#### Custom Alert Logic

Modify `should_trigger_alert()` for more complex conditions:

```python
def should_trigger_alert(message_text: str) -> tuple[bool, str]:
    # Check price levels
    if 'BTC' in message_text and '$' in message_text:
        return True, "Bitcoin signal"
    
    # Check for mentions
    if '@username' in message_text:
        return True, "User mentioned"
    
    return False, ""
```

#### Different Alert Priorities

```python
send_ntfy_alert(
    title="Critical Alert",
    message="Something urgent happened",
    priority='max'  # or 'high', 'default', 'low', 'min'
)
```

#### Add Tags to Alerts

```python
send_ntfy_alert(
    title="Alert",
    message="Message content",
    tags='telegram,important,crypto'
)
```

### Troubleshooting

**"Could not access channel"**
- Make sure you're subscribed to the channel
- Use channel username (e.g., `@mychannel`) not channel name
- For private channels, use the channel ID number

**"Two-factor authentication enabled"**
- The script will ask for your password - enter it when prompted
- Or disable 2FA temporarily during setup

**No notifications showing up**
- Check the ntfy.sh topic URL in your browser
- Make sure ntfy app is installed/subscribed
- Verify keywords/triggers are being matched

**Connection keeps dropping**
- Run with a process manager like supervisor, systemd, or PM2
- The script will auto-reconnect on failure

### Running as a Service (Linux)

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

### Security Notes

- Keep your `.env` file secret (add to `.gitignore`)
- Don't commit API credentials to git
- Use a random/hard-to-guess ntfy topic
- For private channels, only you can access them with your credentials
