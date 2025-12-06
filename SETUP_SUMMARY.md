# Setup Summary - Ready for Mac Mini Deployment

## What I've Done

I've prepared your Resume Tailor application for deployment on your Mac Mini (`10.10.10.2`) with access from your Windows machine.

### Files Created/Modified

#### 1. **DEPLOYMENT.md** (Comprehensive Guide)
   - Complete step-by-step deployment instructions
   - Mac Mini network configuration
   - Docker setup and management
   - Troubleshooting guide
   - Security considerations

#### 2. **DEPLOYMENT_QUICKSTART.md** (Quick Reference)
   - Your specific network configuration (IP: 10.10.10.2, User: fengyurui)
   - Fast deployment steps
   - Useful commands cheat sheet
   - Sync strategies

#### 3. **.env.example** (Template)
   - Example environment variables file
   - Shows both OpenAI and AWS Bedrock options
   - You already have `.env` with your credentials

#### 4. **backend/config.py** (Updated CORS)
   - Added `http://10.10.10.2:8000` to ALLOWED_ORIGINS
   - Allows Chrome extension to connect from Windows to Mac Mini

#### 5. **extension/background/service-worker.js** (Updated API URL)
   - Changed API_BASE from `localhost` to `http://10.10.10.2:8000/api`
   - Now points to your Mac Mini

#### 6. **.gitignore** (Already Configured)
   - `.env` file is already excluded from git commits
   - Your API keys are safe

---

## Your Current Configuration

| Component | Value |
|-----------|-------|
| Mac Mini IP | 10.10.10.2 |
| Mac Mini User | fengyurui |
| Windows SSH | Already configured ✅ |
| Backend Port | 8000 |
| Docker | Required on Mac Mini |
| Chrome Extension | Updated to use Mac Mini IP |

---

## Quick Deployment Steps

### 1. Transfer Repository to Mac Mini

**Option A: Git Clone (If pushed to GitHub)**
```bash
ssh fengyurui@10.10.10.2
cd ~/Documents
git clone <your-repo-url> Strands-agent
```

**Option B: SCP from Windows**
```bash
# From Windows (Git Bash or WSL)
scp -r d:/Strands-agent fengyurui@10.10.10.2:~/Documents/
```

### 2. Setup .env on Mac Mini

```bash
ssh fengyurui@10.10.10.2
cd ~/Documents/Strands-agent
nano .env
```

**Copy your credentials:**
```env
OPENAI_API_KEY=sk-proj-your-actual-openai-key-here
AWS_BEARER_TOKEN_BEDROCK=your-actual-bedrock-token-here
```

**Note:** Use the actual API keys from your local `.env` file on Windows.

Save and secure:
```bash
chmod 600 .env
```

### 3. Install Docker on Mac Mini (if needed)

```bash
# Check if installed
docker --version

# If not, install
brew install --cask docker
open /Applications/Docker.app
```

### 4. Deploy Container

```bash
cd ~/Documents/Strands-agent

# Create directories
mkdir -p data/original data/tailored_resumes data/cover_letters logs

# Build and start
docker-compose build
docker-compose up -d

# Check status
docker ps
docker logs resume-tailor -f
```

### 5. Test from Windows

**Browser:**
```
http://10.10.10.2:8000
```

**PowerShell:**
```powershell
Invoke-WebRequest -Uri "http://10.10.10.2:8000/api/health"
```

### 6. Use Chrome Extension on Windows

The extension is already updated to use `http://10.10.10.2:8000/api`

**To reload extension:**
1. Open `chrome://extensions/`
2. Find "Resume Tailor"
3. Click reload icon
4. Test on a LinkedIn job posting

---

## What Still Needs to be Done

### On Mac Mini:
1. ✅ Clone/copy repository
2. ✅ Create `.env` file with API keys
3. ✅ Install Docker Desktop (if not already)
4. ✅ Run `docker-compose up -d`
5. ⏳ (Optional) Setup auto-start on boot

### On Windows:
1. ✅ Commit and push changes (if using Git)
2. ✅ Reload Chrome extension
3. ✅ Test web UI and extension

---

## Files You Need to Sync

Before deploying on Mac Mini, make sure these updated files are transferred:

1. `backend/config.py` - CORS updated ✅
2. `extension/background/service-worker.js` - API URL updated ✅
3. `.env.example` - Template created ✅
4. `DEPLOYMENT.md` - Guide created ✅
5. `DEPLOYMENT_QUICKSTART.md` - Quick reference ✅

**Recommended: Commit and push to git, then pull on Mac Mini**

```bash
# On Windows
cd d:\Strands-agent
git add .
git commit -m "Configure for Mac Mini deployment at 10.10.10.2"
git push

# On Mac Mini
ssh fengyurui@10.10.10.2
cd ~/Documents/Strands-agent
git pull
```

---

## Testing Checklist

### After Deployment:

- [ ] Mac Mini: `curl http://localhost:8000/api/health` returns `{"status":"healthy"}`
- [ ] Mac Mini: `docker ps` shows `resume-tailor` container running
- [ ] Windows: `http://10.10.10.2:8000` loads web UI
- [ ] Windows: Chrome extension connects successfully
- [ ] Windows: Extension auto-scrapes LinkedIn job postings
- [ ] Windows: Can tailor resume and download results

---

## Troubleshooting Quick Fixes

### Can't connect from Windows
```bash
# On Mac Mini
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /Applications/Docker.app/Contents/MacOS/Docker
```

### Container won't start
```bash
# On Mac Mini
docker logs resume-tailor
ls -la .env  # Verify .env exists
```

### Extension can't connect
1. Verify `service-worker.js` has `http://10.10.10.2:8000/api`
2. Reload extension in Chrome
3. Test: http://10.10.10.2:8000/api/health in browser

---

## Useful Commands Reference

### Mac Mini (via SSH)
```bash
ssh fengyurui@10.10.10.2

# Container management
docker ps                          # List running containers
docker logs resume-tailor -f       # View logs
docker-compose restart             # Restart
docker-compose down                # Stop
docker-compose up --build -d       # Rebuild and start

# Updates
cd ~/Documents/Strands-agent
git pull
docker-compose up --build -d
```

### Windows
```powershell
# Test connection
Test-NetConnection -ComputerName 10.10.10.2 -Port 8000

# Open web UI
start http://10.10.10.2:8000

# Push updates
cd d:\Strands-agent
git add .
git commit -m "Update"
git push
```

---

## Auto-Start on Mac Mini Boot (Optional)

**Simplest method: Docker Desktop**

1. Open Docker Desktop on Mac Mini
2. Preferences → General → "Start Docker Desktop when you log in" ✅
3. Container auto-restarts due to `restart: unless-stopped` in docker-compose.yml

**Mac Mini will automatically start Resume Tailor on boot!**

---

## Security Notes

✅ `.env` file is excluded from git commits (.gitignore line 22)
✅ CORS configured to allow only your Mac Mini IP
✅ `.env` should have restricted permissions: `chmod 600 .env`
⚠️ API keys are in plain text - keep `.env` secure
⚠️ HTTP (not HTTPS) - fine for local network, don't expose to internet

---

## Next Steps

1. **Now**: Commit and push these changes
   ```bash
   cd d:\Strands-agent
   git add .
   git commit -m "Configure for Mac Mini deployment"
   git push
   ```

2. **Then**: Follow [DEPLOYMENT_QUICKSTART.md](DEPLOYMENT_QUICKSTART.md) steps 1-5

3. **Finally**: Test everything works from Windows!

---

## Documentation Files

- **[README.md](README.md)** - Main project documentation
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Complete deployment guide
- **[DEPLOYMENT_QUICKSTART.md](DEPLOYMENT_QUICKSTART.md)** - Quick reference for your setup
- **[extension/README.md](extension/README.md)** - Chrome extension docs
- **[.env.example](.env.example)** - Environment variables template

---

## Questions?

If you encounter issues:
1. Check the Troubleshooting sections in DEPLOYMENT.md
2. Review Docker logs: `docker logs resume-tailor -f`
3. Verify network connectivity: `Test-NetConnection -ComputerName 10.10.10.2 -Port 8000`

**You're all set for deployment!** 🚀
