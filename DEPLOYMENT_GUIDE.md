# 📡 Telegram Monitor - Complete Setup

## Quick Start

### 1️⃣ **Fill Telegram Credentials on VPS**
```bash
ssh -i ~/.ssh/ssh-key-2026-04-26.key ubuntu@129.151.247.139
nano /home/ubuntu/teleG/.env
```

Fill in your credentials:
```env
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_PHONE=+your_phone
MONITOR_CHANNEL=THEABZBRAND
NTFY_TOPIC=anonyTG_alertz
```

### 2️⃣ **Start the Service**
```bash
sudo systemctl start telegram-monitor
sudo systemctl enable telegram-monitor  # Auto-start on reboot
```

### 3️⃣ **Check Logs & Authentication**
```bash
sudo journalctl -u telegram-monitor -f
```

**First Connection:** When you start the service for the first time, Telegram will send a verification code via SMS or your Telegram app. The monitor will:
1. Display "⏳ Waiting for code from dashboard" in logs
2. Show a modal in your dashboard asking for the code
3. Enter the code in the dashboard and click **Verify**
4. The service will authenticate and start monitoring

---

## 📊 Monitor Health Dashboard

### Local Deployment (Development)
```bash
cd frontend
python3 -m http.server 8000
# Visit: http://localhost:8000
```

### GitHub Pages Deployment (Production)
The dashboard automatically deploys to GitHub Pages on every push to `frontend/` folder.

**Your dashboard:** `https://your-username.github.io/teleG/`

**Features:**
- ✅ Real-time service status monitoring
- ✅ Message count & alert history
- ✅ Clear cache functionality
- ✅ View logs remotely
- ✅ Restart service
- ✅ Responsive design (mobile-friendly)

---

## 🔄 Health Check API

The monitor includes a health check server on `localhost:9999`:

```bash
# Check health
curl http://localhost:9999/health

# Get recent logs
curl http://localhost:9999/logs

# Clear cache
curl -X POST http://localhost:9999/cache/clear

# View settings
curl http://localhost:9999/settings
```

To use from dashboard, update in `frontend/script.js`:
```javascript
const API_BASE = 'http://your-vps-ip:9999';  // For remote access
```

---

## 🚀 CI/CD Pipeline

GitHub Actions automatically:
1. ✅ Tests HTML/CSS/JS validity
2. ✅ Deploys to GitHub Pages on push
3. ✅ Validates frontend structure
4. ✅ Notifies of deployment status

**Trigger:** Push changes to `frontend/` or `.github/workflows/`

**View results:** GitHub repo → Actions tab

---

## 📁 Project Structure

```
teleG/
├── telegram_monitor_advanced.py   # Main monitor
├── health_check_server.py         # Health API
├── requirements.txt               # Python deps
├── .env                          # Credentials (Git ignored)
├── .gitignore                    # Git exclusions
├── processed_messages.json       # Message cache
├── frontend/                     # Dashboard
│   ├── index.html                # Main page
│   ├── styles.css                # Styling
│   └── script.js                 # Frontend logic
├── .github/
│   └── workflows/
│       └── deploy.yml            # CI/CD config
└── SETUP.md                      # This file
```

---

## 🔒 Security Notes

1. **Credentials:** `.env` is Git-ignored and NOT tracked
2. **API Access:** Health check server runs on localhost by default
3. **GitHub Pages:** Frontend is static - no secrets exposed
4. **WXATA:** Completely isolated in `/home/ubuntu/WXATA/`

---

## 🛠️ Troubleshooting

### Service won't start
```bash
# Check status
sudo systemctl status telegram-monitor

# View errors
sudo journalctl -u telegram-monitor -n 50

# Restart
sudo systemctl restart telegram-monitor
```

### Can't connect to API
- Ensure `.env` is filled with correct credentials
- Check internet connectivity on VPS
- Verify Telegram API credentials are valid

### Dashboard shows "Offline"
- Confirm service is running: `sudo systemctl status telegram-monitor`
- Check health API: `curl http://localhost:9999/health`
- Verify network connectivity

### Telegram login keeps failing
```bash
# Reset WhatsApp session (keep TG session)
cd /home/ubuntu/WXATA
./wxata_start.sh --reset-wa

# For TG, delete session file
rm /home/ubuntu/teleG/telegram_monitor.session
# Restart and re-authenticate
```

---

## 📈 Next Steps

1. **Monitor in Production**
   - Access dashboard: `https://your-username.github.io/teleG/`
   - Set browser bookmark for quick access
   - Mobile-friendly dashboard works on phones too

2. **Set Up Alerts**
   - Subscribe to ntfy topic: `https://ntfy.sh/anonyTG_alertz`
   - Get notifications on phone/desktop
   - Download ntfy app for better experience

3. **Automated Alerts**
   - Create Discord webhook integration
   - Send alerts to Slack/Teams
   - Set up email notifications

4. **Enable Remote API**
   - Expose health check server with reverse proxy
   - Add authentication (basic auth)
   - Monitor from anywhere

---

## 📞 Quick Commands

```bash
# SSH into VPS
ssh -i ~/.ssh/ssh-key-2026-04-26.key ubuntu@129.151.247.139

# Check service status
sudo systemctl status telegram-monitor

# View real-time logs
sudo journalctl -u telegram-monitor -f

# Restart service
sudo systemctl restart telegram-monitor

# Clear logs
sudo journalctl --vacuum=7d

# Check disk usage
df -h /home/ubuntu/teleG

# View message cache
wc -l processed_messages.json
```

---

**Version:** 1.0 | **Last Updated:** May 2026
