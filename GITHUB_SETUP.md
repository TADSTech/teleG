# ⚡ GitHub Setup Instructions

## 1️⃣ Create GitHub Repository

Visit https://github.com/new and create a repository:
- **Name:** `teleG` (or your preferred name)
- **Description:** "Telegram Channel Monitor with Real-time Dashboard"
- **Visibility:** Public (for GitHub Pages)
- **Don't initialize** (we have local repo already)

## 2️⃣ Connect Local Repo to GitHub

```bash
cd c:\Users\TADS\WORK\TADSFX\teleG

# Add remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/teleG.git

# Rename branch to main if needed
git branch -M main

# Push to GitHub
git push -u origin main
```

## 3️⃣ Enable GitHub Pages

1. Go to your repository on GitHub
2. **Settings** → **Pages** 
3. **Source:** Select `Deploy from a branch`
4. **Branch:** Choose `main` and `/root` (or `/frontend` folder)
5. **Save**

Wait 30-60 seconds for deployment to complete.

## 4️⃣ Access Your Dashboard

Your dashboard will be available at:
```
https://YOUR_USERNAME.github.io/teleG/
```

Example: `https://myusername.github.io/teleG/`

## 🔄 Auto-Deployment

After setting up GitHub Pages:
- Any push to `main` branch → **automatic redeploy**
- Changes to `frontend/` folder → **dashboard updates**
- GitHub Actions runs tests → **ensures quality**

---

## 📋 What You Get

✅ **Live monitoring dashboard** - Real-time service status
✅ **Mobile responsive** - Works on phones
✅ **Cache management** - Clear message history
✅ **Log viewer** - See recent alerts
✅ **Service control** - Restart/manage service
✅ **Auto CI/CD** - Tests and deploys automatically

---

## 🎯 Next: Make a Change & Deploy

Try this to test the pipeline:

```bash
# Edit dashboard
# For example, change title in frontend/index.html
# Then commit and push:

git add frontend/
git commit -m "Update dashboard title"
git push
```

Check GitHub Actions tab → see it deploy automatically!

---

## 📍 Your Links

| Service | URL |
|---------|-----|
| **Dashboard** | https://YOUR_USERNAME.github.io/teleG/ |
| **Repository** | https://github.com/YOUR_USERNAME/teleG |
| **Actions** | https://github.com/YOUR_USERNAME/teleG/actions |
| **Telegram Alerts** | https://ntfy.sh/anonyTG_alertz |

---

## ❓ Troubleshooting GitHub Pages

**"404 Not Found" on dashboard:**
- Check Settings → Pages shows "✓ Your site is live"
- Wait 1-2 minutes after push
- Clear browser cache (Ctrl+Shift+R)

**Nothing changed after push:**
- Check GitHub Actions → Deployments tab
- Ensure files are in `frontend/` folder
- Verify `.github/workflows/deploy.yml` exists

**Want to use custom domain:**
- Settings → Pages → Custom domain
- Add DNS record (CNAME)
- [Detailed guide](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site)

---

## 🔐 Security Reminder

✅ Your `.env` file is in `.gitignore` - secrets NOT pushed
✅ Dashboard is static HTML - no backend needed
✅ Health API stays internal on VPS
✅ Perfect separation of concerns

---

**You're all set!** 🚀
