# Quick Deployment Guide - Your Mac Mini Setup

**Your Network Configuration:**
- Mac Mini IP: `10.10.10.2`
- Mac Mini User: `fengyurui`
- Windows Machine: SSH access already configured

---

## Step-by-Step Deployment

### 1. Transfer Repository to Mac Mini

**From your Windows machine:**

```bash
# Option A: Git clone on Mac Mini (if repo is on GitHub)
ssh fengyurui@10.10.10.2
cd ~/Documents
git clone <your-repo-url> Strands-agent
exit

# Option B: Copy from Windows via SCP (if you want to sync current state)
scp -r d:/Strands-agent fengyurui@10.10.10.2:~/Documents/
```

### 2. Setup .env File on Mac Mini

```bash
# SSH into Mac Mini
ssh fengyurui@10.10.10.2

# Navigate to project
cd ~/Documents/Strands-agent

# Create .env file (copy from Windows or create new)
nano .env
```

**Paste your credentials:**
```env
OPENAI_API_KEY=sk-proj-your-actual-openai-key-here
AWS_BEARER_TOKEN_BEDROCK=your-actual-bedrock-token-here
```

**Note:** Use the actual API keys from your local `.env` file on Windows.

Save (Ctrl+O, Enter, Ctrl+X)

```bash
# Secure the file
chmod 600 .env
```

### 3. Install Docker on Mac Mini (if not already installed)

```bash
# Check if Docker is installed
docker --version

# If not installed, install via Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install --cask docker

# Start Docker Desktop (or use command line)
open /Applications/Docker.app
```

### 4. Deploy Container

```bash
# Still SSH'd into Mac Mini
cd ~/Documents/Strands-agent

# Create data directories
mkdir -p data/original data/tailored_resumes data/cover_letters logs

# Build and start the container
docker-compose build
docker-compose up -d

# Check it's running
docker ps
# Should show: resume-tailor container on port 8000

# Check logs
docker logs resume-tailor -f
# Press Ctrl+C when you see "Application startup complete"
```

### 5. Test from Mac Mini

```bash
# Test health endpoint
curl http://localhost:8000/api/health
# Should return: {"status":"healthy"}

# Test web UI
curl http://localhost:8000
# Should return HTML
```

### 6. Test from Windows

**Open browser on Windows:**
```
http://10.10.10.2:8000
```

You should see the Resume Tailor interface!

**Test API from PowerShell:**
```powershell
Invoke-WebRequest -Uri "http://10.10.10.2:8000/api/health"
```

### 7. Configure Chrome Extension on Windows

**Edit the extension backend URL:**

File: `d:\Strands-agent\extension\background\service-worker.js`

Change line 6:
```javascript
const API_BASE = 'http://10.10.10.2:8000/api';  // Changed from localhost
```

**Reload extension:**
1. Open Chrome → `chrome://extensions/`
2. Find "Resume Tailor"
3. Click the reload icon (circular arrow)

**Test extension:**
1. Go to a LinkedIn job posting
2. Click the Resume Tailor extension icon
3. Should auto-fill job description
4. Check console (F12) for any connection errors

---

## Auto-Start Container on Mac Mini Boot

### Option 1: Docker Desktop (Simplest)

```bash
# On Mac Mini
# Open Docker Desktop → Preferences → General
# Check: "Start Docker Desktop when you log in"

# Container will auto-restart because docker-compose.yml has:
# restart: unless-stopped
```

### Option 2: LaunchAgent (More Control)

```bash
# Create LaunchAgent
nano ~/Library/LaunchAgents/com.resume-tailor.plist
```

Paste:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.resume-tailor</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/docker-compose</string>
        <string>-f</string>
        <string>/Users/fengyurui/Documents/Strands-agent/docker-compose.yml</string>
        <string>up</string>
        <string>-d</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/Users/fengyurui/Documents/Strands-agent</string>
    <key>RunAtLoad</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/Users/fengyurui/Documents/Strands-agent/logs/launchd.out</string>
    <key>StandardErrorPath</key>
    <string>/Users/fengyurui/Documents/Strands-agent/logs/launchd.err</string>
</dict>
</plist>
```

Load it:
```bash
launchctl load ~/Library/LaunchAgents/com.resume-tailor.plist
launchctl list | grep resume-tailor
```

---

## Syncing Code Changes

### Push from Windows, Pull on Mac Mini

**On Windows (after making changes):**
```bash
cd d:\Strands-agent
git add .
git commit -m "Update extension config for Mac Mini"
git push
```

**On Mac Mini:**
```bash
ssh fengyurui@10.10.10.2
cd ~/Documents/Strands-agent
git pull
docker-compose down
docker-compose up --build -d
```

### Direct SCP for Quick Updates

**Single file:**
```bash
# From Windows (Git Bash or WSL)
scp d:/Strands-agent/extension/background/service-worker.js fengyurui@10.10.10.2:~/Documents/Strands-agent/extension/background/

# No need to restart container for extension changes (only reload in Chrome)
```

---

## Useful Commands

### Mac Mini (via SSH)

```bash
# SSH into Mac Mini
ssh fengyurui@10.10.10.2

# Check container status
docker ps

# View logs
docker logs resume-tailor -f

# Restart container
cd ~/Documents/Strands-agent
docker-compose restart

# Stop container
docker-compose down

# Rebuild and restart
docker-compose up --build -d

# Check disk usage
docker system df

# Clean up old images
docker system prune -a
```

### Windows

```powershell
# Test connection
Test-NetConnection -ComputerName 10.10.10.2 -Port 8000

# Test API
Invoke-WebRequest -Uri "http://10.10.10.2:8000/api/health"

# Open web UI
start http://10.10.10.2:8000

# SSH into Mac Mini
ssh fengyurui@10.10.10.2
```

---

## Troubleshooting

### Can't connect from Windows

```bash
# On Mac Mini, check if container is running
docker ps

# Check if port is listening
netstat -an | grep 8000

# Check macOS firewall
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate

# Allow Docker through firewall
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /Applications/Docker.app/Contents/MacOS/Docker
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --unblockapp /Applications/Docker.app/Contents/MacOS/Docker
```

### Container won't start

```bash
# Check logs
docker logs resume-tailor

# Common issue: .env file missing
ls -la .env
cat .env  # Verify contents

# Rebuild from scratch
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

### Extension can't connect

1. Verify `service-worker.js` has correct IP: `http://10.10.10.2:8000/api`
2. Reload extension in Chrome
3. Check browser console (F12) for errors
4. Test API endpoint directly: http://10.10.10.2:8000/api/health

---

## Files Modified for Your Setup

1. ✅ `backend/config.py` - Added `http://10.10.10.2:8000` to ALLOWED_ORIGINS
2. ⏳ `extension/background/service-worker.js` - Need to change API_BASE to `http://10.10.10.2:8000/api`
3. ✅ `.env.example` - Created template
4. ✅ `.gitignore` - Already excludes .env
5. ✅ `DEPLOYMENT.md` - Complete deployment guide
6. ✅ `DEPLOYMENT_QUICKSTART.md` - This quick reference

---

## Next Steps

1. **Transfer repo to Mac Mini** (via git clone or scp)
2. **Create .env file** on Mac Mini with your API keys
3. **Run `docker-compose up -d`** on Mac Mini
4. **Test from Windows browser**: http://10.10.10.2:8000
5. **Update Chrome extension** backend URL
6. **Setup auto-start** (optional)

You're all set! 🚀
