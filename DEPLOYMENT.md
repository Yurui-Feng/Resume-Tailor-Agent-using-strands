# Deployment Guide - Mac Mini Setup

This guide covers deploying the Resume Tailor application on a Mac Mini that runs 24/7 on your local network, accessible from your Windows machine.

---

## Overview

**Architecture:**
- **Mac Mini**: Hosts the Docker container running the Resume Tailor backend and frontend
- **Windows Machine**: Accesses the web UI via local network URL (e.g., `http://192.168.1.100:8000`)
- **Chrome Extension**: Points to Mac Mini's IP address for API calls

---

## Prerequisites

### On Mac Mini

1. **Docker Desktop for Mac**
   ```bash
   # Install via Homebrew
   brew install --cask docker

   # Or download from: https://www.docker.com/products/docker-desktop
   ```

2. **Git** (usually pre-installed)
   ```bash
   git --version
   # If not installed:
   brew install git
   ```

3. **Network Requirements**
   - Static IP address (recommended) or DHCP reservation
   - Firewall allows incoming connections on port 8000
   - Mac Mini set to never sleep (for 24/7 operation)

### On Windows Machine

1. **Git for Windows** (to clone/sync repository)
2. **Chrome Browser** (for extension)
3. **Network access** to Mac Mini

---

## Step 1: Mac Mini Initial Setup

### 1.1 Set Static IP Address (Recommended)

**Option A: Router DHCP Reservation (Recommended)**
- Log into your router admin panel
- Find Mac Mini's MAC address
- Reserve a static IP (e.g., `192.168.1.100`)

**Option B: macOS Static IP**
```bash
# System Preferences → Network → Advanced → TCP/IP
# Configure IPv4: Manually
# IP Address: 192.168.1.100
# Subnet Mask: 255.255.255.0
# Router: 192.168.1.1
```

### 1.2 Prevent Sleep

```bash
# System Preferences → Energy Saver
# - Prevent computer from sleeping automatically when display is off: ON
# - Start up automatically after power failure: ON

# Or via command line:
sudo pmset -a sleep 0
sudo pmset -a hibernatemode 0
sudo pmset -a disablesleep 1
```

### 1.3 Enable Remote Access (Optional)

```bash
# System Preferences → Sharing
# - Remote Login: ON (for SSH access)
# - File Sharing: ON (optional, for easy file transfer)
```

---

## Step 2: Clone Repository on Mac Mini

```bash
# SSH into Mac Mini from Windows (if Remote Login enabled)
ssh yourusername@192.168.1.100

# Or work directly on Mac Mini
cd ~/Documents  # or your preferred location
git clone <your-repo-url> Strands-agent
cd Strands-agent
```

---

## Step 3: Configure Environment Variables

### 3.1 Create `.env` File on Mac Mini

```bash
cd ~/Documents/Strands-agent
nano .env  # or use vim, TextEdit, etc.
```

**Add your credentials:**
```bash
# OpenAI (recommended)
OPENAI_API_KEY=sk-proj-your-actual-key-here

# Or AWS Bedrock (alternative)
AWS_BEARER_TOKEN_BEDROCK=your-bedrock-token-here
AWS_REGION=us-east-1
```

**Save and secure:**
```bash
chmod 600 .env  # Restrict permissions to owner only
```

### 3.2 Verify `.gitignore` Excludes `.env`

The `.env` file is already excluded in [.gitignore](.gitignore) (line 22-24), so it won't be committed to git.

---

## Step 4: Prepare Data Directory

```bash
cd ~/Documents/Strands-agent

# Create necessary directories
mkdir -p data/original
mkdir -p data/tailored_resumes
mkdir -p data/cover_letters
mkdir -p logs

# Copy your resume(s) to data/original/
# Example:
cp ~/Desktop/my_resume.tex data/original/
```

---

## Step 5: Deploy with Docker

### 5.1 Build and Start Container

```bash
cd ~/Documents/Strands-agent

# Build the Docker image
docker-compose build

# Start the container in detached mode
docker-compose up -d

# Verify it's running
docker ps
# Should show: resume-tailor container on port 8000
```

### 5.2 Check Logs

```bash
# Follow logs in real-time
docker logs resume-tailor -f

# Press Ctrl+C to stop following

# View last 50 lines
docker logs resume-tailor --tail 50
```

### 5.3 Test Health Check

```bash
# From Mac Mini
curl http://localhost:8000/api/health

# Expected response:
# {"status": "healthy"}
```

---

## Step 6: Access from Windows Machine

### 6.1 Find Mac Mini's IP Address

```bash
# On Mac Mini
ipconfig getifaddr en0  # Wi-Fi
# or
ipconfig getifaddr en1  # Ethernet

# Example output: 192.168.1.100
```

### 6.2 Test Connection from Windows

**Open browser on Windows:**
```
http://192.168.1.100:8000
```

You should see the Resume Tailor web interface!

**Test API endpoint:**
```powershell
# PowerShell
Invoke-WebRequest -Uri "http://192.168.1.100:8000/api/health"

# Or use browser:
http://192.168.1.100:8000/api/health
```

---

## Step 7: Configure Chrome Extension (Windows)

### 7.1 Update Extension Backend URL

**Edit `extension/background/service-worker.js`:**

```javascript
// Change this line (around line 3-4):
const BACKEND_URL = 'http://192.168.1.100:8000';  // Use Mac Mini's IP
```

### 7.2 Load Extension in Chrome

1. Open Chrome on Windows
2. Navigate to `chrome://extensions/`
3. Enable **Developer mode** (top-right toggle)
4. Click **Load unpacked**
5. Select folder: `d:\Strands-agent\extension`

### 7.3 Test Extension

1. Navigate to a LinkedIn or Indeed job posting
2. Click Resume Tailor extension icon
3. Job description should auto-fill
4. Check console (F12) for connection errors

**Troubleshooting:**
- If connection fails, verify Mac Mini's IP address
- Ensure port 8000 is accessible (check macOS firewall)
- Verify Docker container is running on Mac Mini

---

## Step 8: Firewall Configuration (macOS)

If you can't connect from Windows:

```bash
# On Mac Mini - Allow port 8000
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /usr/bin/python3
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --unblockapp /usr/bin/python3

# Or disable firewall entirely (less secure)
# System Preferences → Security & Privacy → Firewall → Turn Off Firewall
```

**Docker Desktop:**
- Docker Desktop typically handles firewall rules automatically
- Ensure Docker Desktop is allowed in: System Preferences → Security & Privacy → Firewall → Firewall Options

---

## Step 9: Auto-Start on Boot (Optional)

### 9.1 Create Launch Agent (macOS)

```bash
# Create LaunchAgent plist file
nano ~/Library/LaunchAgents/com.resume-tailor.plist
```

**Add this content:**
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
        <string>/Users/yourusername/Documents/Strands-agent/docker-compose.yml</string>
        <string>up</string>
        <string>-d</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/Users/yourusername/Documents/Strands-agent</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <false/>
    <key>StandardOutPath</key>
    <string>/Users/yourusername/Documents/Strands-agent/logs/launchd.out</string>
    <key>StandardErrorPath</key>
    <string>/Users/yourusername/Documents/Strands-agent/logs/launchd.err</string>
</dict>
</plist>
```

**Update paths:**
- Replace `yourusername` with your actual macOS username
- Adjust `/Users/yourusername/Documents/Strands-agent` to your actual path

**Load the agent:**
```bash
launchctl load ~/Library/LaunchAgents/com.resume-tailor.plist

# Verify it's loaded
launchctl list | grep resume-tailor
```

### 9.2 Alternative: Docker Desktop Auto-Start

**Simpler option:**
1. Open Docker Desktop on Mac Mini
2. Preferences → General → **Start Docker Desktop when you log in**: ON
3. In terminal:
   ```bash
   cd ~/Documents/Strands-agent
   docker-compose up -d

   # Docker will remember and auto-restart containers on boot if:
   docker-compose.yml has: restart: unless-stopped
   ```

---

## Step 10: Sync Code Changes (Windows → Mac Mini)

### Option A: Git Push/Pull (Recommended)

**On Windows:**
```bash
cd d:\Strands-agent
git add .
git commit -m "Update extension backend URL"
git push
```

**On Mac Mini:**
```bash
cd ~/Documents/Strands-agent
git pull

# Rebuild and restart if code changed
docker-compose down
docker-compose up --build -d
```

### Option B: File Sharing (Quick Updates)

**Setup SMB sharing on Mac Mini:**
1. System Preferences → Sharing → File Sharing: ON
2. Add Strands-agent folder to Shared Folders

**From Windows:**
```powershell
# Map network drive
net use Z: \\192.168.1.100\Strands-agent

# Copy files
copy d:\Strands-agent\extension\background\service-worker.js Z:\extension\background\
```

### Option C: SSH/SCP (For Single Files)

```bash
# From Windows (using WSL or Git Bash)
scp d:/Strands-agent/.env yourusername@192.168.1.100:~/Documents/Strands-agent/.env

# Or use tools like WinSCP, FileZilla, etc.
```

---

## Maintenance Commands

### Check Container Status

```bash
# SSH into Mac Mini
ssh yourusername@192.168.1.100

cd ~/Documents/Strands-agent

# View running containers
docker ps

# Check logs
docker logs resume-tailor -f

# Check resource usage
docker stats resume-tailor
```

### Restart Container

```bash
cd ~/Documents/Strands-agent

# Graceful restart
docker-compose restart

# Full rebuild (after code changes)
docker-compose down
docker-compose up --build -d
```

### Update Application

```bash
cd ~/Documents/Strands-agent

# Pull latest code
git pull

# Rebuild and restart
docker-compose down
docker-compose up --build -d
```

### Backup Data

```bash
# Backup generated resumes and cover letters
cd ~/Documents/Strands-agent
tar -czf backup-$(date +%Y%m%d).tar.gz data/ logs/

# Copy to external drive or cloud storage
cp backup-*.tar.gz /Volumes/Backup/
```

---

## Troubleshooting

### Container Won't Start

```bash
# Check Docker is running
docker ps

# View error logs
docker logs resume-tailor

# Common issues:
# 1. .env file missing or invalid
cat .env

# 2. Port 8000 already in use
lsof -i :8000

# 3. Rebuild from scratch
docker-compose down -v
docker-compose up --build
```

### Can't Connect from Windows

**Test network connectivity:**
```powershell
# From Windows PowerShell
Test-NetConnection -ComputerName 192.168.1.100 -Port 8000
```

**If connection fails:**
1. Check Mac Mini's IP: `ipconfig getifaddr en0`
2. Check firewall: System Preferences → Security → Firewall
3. Verify container is running: `docker ps`
4. Check Docker port binding: `docker port resume-tailor`

### Extension Can't Connect

**Update backend URL:**
1. Edit `extension/background/service-worker.js`
2. Set `BACKEND_URL = 'http://192.168.1.100:8000'`
3. Reload extension: chrome://extensions/ → Reload
4. Test: http://192.168.1.100:8000/api/health

**Check CORS:**
1. Open `backend/config.py` on Mac Mini
2. Verify `ALLOWED_ORIGINS` includes:
   ```python
   ALLOWED_ORIGINS = [
       "http://localhost:8000",
       "http://192.168.1.100:8000",
       "chrome-extension://*"
   ]
   ```
3. Restart container if changed

### Slow Performance

**Check Docker resources:**
```bash
# View resource usage
docker stats resume-tailor

# Increase Docker memory (Docker Desktop → Preferences → Resources)
# Recommended: 4GB RAM, 2 CPUs
```

**LaTeX compilation slow:**
- This is normal for first run (package installation)
- Subsequent runs should be faster

---

## Security Considerations

### 1. Network Isolation

**If only accessing from Windows on same network:**
```yaml
# Edit docker-compose.yml
ports:
  - "127.0.0.1:8000:8000"  # Only localhost (more secure)
  # OR
  - "192.168.1.100:8000:8000"  # Only Mac Mini's IP
```

### 2. API Key Protection

**Never commit `.env` to git:**
```bash
# Already in .gitignore, but verify:
git status
# .env should NOT appear in untracked files
```

**Restrict .env permissions:**
```bash
chmod 600 .env  # Owner read/write only
```

### 3. Firewall Rules

**Only allow Windows machine:**
```bash
# macOS Application Firewall (basic)
# System Preferences → Security → Firewall → Firewall Options → Add Docker

# For advanced control, use pf (packet filter)
# Create /etc/pf.conf rule to allow only 192.168.1.x subnet
```

### 4. HTTPS (Optional)

For encrypted communication, set up reverse proxy with SSL:

```bash
# Install nginx
brew install nginx

# Configure as reverse proxy with self-signed cert
# nginx.conf:
# server {
#     listen 443 ssl;
#     ssl_certificate /path/to/cert.pem;
#     ssl_certificate_key /path/to/key.pem;
#     location / {
#         proxy_pass http://localhost:8000;
#     }
# }
```

---

## Network Configuration Summary

| Component | Location | URL/IP | Port |
|-----------|----------|--------|------|
| Docker Container | Mac Mini | localhost:8000 | 8000 |
| Web UI Access | Windows | http://192.168.1.100:8000 | 8000 |
| Chrome Extension API | Windows → Mac Mini | http://192.168.1.100:8000 | 8000 |
| SSH Access | Windows → Mac Mini | ssh://192.168.1.100 | 22 |

---

## Quick Reference Commands

### Mac Mini

```bash
# Start service
cd ~/Documents/Strands-agent && docker-compose up -d

# Stop service
docker-compose down

# View logs
docker logs resume-tailor -f

# Restart service
docker-compose restart

# Update code and rebuild
git pull && docker-compose up --build -d

# Check health
curl http://localhost:8000/api/health
```

### Windows

```powershell
# Test connection
Invoke-WebRequest -Uri "http://192.168.1.100:8000/api/health"

# Open web UI
start http://192.168.1.100:8000

# SSH into Mac Mini
ssh yourusername@192.168.1.100

# Sync code
cd d:\Strands-agent
git pull origin main  # Get updates
git push origin main  # Push changes
```

---

## Next Steps

1. ✅ **Deploy on Mac Mini** - Follow steps 1-5
2. ✅ **Test from Windows** - Follow step 6
3. ✅ **Configure Extension** - Follow step 7
4. ✅ **Setup Auto-Start** - Follow step 9 (optional)
5. 📝 **Add your resumes** to `data/original/`
6. 🚀 **Start tailoring resumes!**

---

## Support

For issues or questions:
- Check [README.md](README.md) for general usage
- Check [extension/README.md](extension/README.md) for extension details
- Review Docker logs: `docker logs resume-tailor -f`
- Verify network connectivity between Windows and Mac Mini

---

**Built for 24/7 operation on Mac Mini with Windows client access**
