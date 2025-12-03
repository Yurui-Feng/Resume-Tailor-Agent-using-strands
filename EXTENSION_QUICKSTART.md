# Resume Tailor Chrome Extension - Quick Start

🎉 **Your Chrome extension is ready to use!**

This extension solves the bottleneck from GitHub Issue #6 by allowing you to tailor resumes directly from job posting pages without switching tabs.

## What Was Built

✅ Chrome Manifest V3 extension
✅ Browser action popup with brutalist theme
✅ Auto-scraping for LinkedIn and Indeed
✅ Real-time progress tracking
✅ Service worker for API communication
✅ CORS configuration updated

## Installation (2 minutes)

### Step 1: Start Backend
```bash
cd d:\Strands-agent
python -m uvicorn backend.main:app --reload
```

### Step 2: Load Extension
1. Open Chrome → `chrome://extensions/`
2. Enable "Developer mode" (top-right toggle)
3. Click "Load unpacked"
4. Select folder: `d:\Strands-agent\extension`
5. Extension appears in list ✓

### Step 3: Pin to Toolbar (Optional)
1. Click puzzle piece icon in Chrome
2. Pin "Resume Tailor" extension
3. Icon appears in toolbar

## Usage

### On LinkedIn or Indeed:
1. Navigate to any job posting
2. Click Resume Tailor extension icon
3. Job description auto-fills ✨
4. Select resume → Click "Tailor Resume"
5. Watch progress in popup
6. Download PDF when complete

### On Any Other Site:
1. Copy job description
2. Click extension icon
3. Paste description
4. Select resume → Generate
5. Download result

## Files Created

```
extension/
├── manifest.json                  # MV3 configuration
├── popup/
│   ├── popup.html                # UI (brutalist theme)
│   ├── popup.css                 # Adapted styles
│   └── popup.js                  # Logic & polling
├── background/
│   └── service-worker.js         # API communication
├── content/
│   ├── linkedin-scraper.js       # LinkedIn auto-scraping
│   └── indeed-scraper.js         # Indeed auto-scraping
├── icons/
│   ├── icon.svg                  # SVG template
│   └── README.md                 # Icon instructions
├── README.md                     # Full documentation
└── INSTALL.md                    # Installation guide
```

## Backend Changes

Only one file was modified:

**`backend/config.py`** (line 69):
```python
ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://localhost:3000",
    "http://127.0.0.1:8000",
    "chrome-extension://*",  # ← Added for extension
]
```

## Features

### Core Features
- ✅ Popup form with job posting textarea
- ✅ Resume dropdown (loads from backend)
- ✅ Checkboxes: "Update Experience", "Generate PDF"
- ✅ Submit button with validation (min 50 chars)
- ✅ Link to open full web app

### Progress Tracking
- ✅ Smooth progress bar (0-100%)
- ✅ Real-time terminal logs
- ✅ Progress text updates
- ✅ Cancel button
- ✅ 2-second polling (matches web app)

### Results Display
- ✅ Company and position shown
- ✅ Download .tex and .pdf buttons
- ✅ "View Full Results" link to web app
- ✅ "Tailor Another Resume" button

### Auto-Scraping
- ✅ LinkedIn job descriptions
- ✅ Indeed job descriptions
- ✅ Auto-detection on page load
- ✅ Graceful fallback (manual paste)

### Smart Features
- ✅ Saves last-used resume preference
- ✅ Saves checkbox preferences
- ✅ Resumes in-progress jobs on popup reopen
- ✅ Error handling (backend offline, network issues)
- ✅ Character count validation

## Testing Checklist

Before first use:

- [ ] Backend running on `http://localhost:8000`
- [ ] Extension loaded in `chrome://extensions/`
- [ ] No errors in extension list
- [ ] Click icon → popup opens
- [ ] Resumes appear in dropdown

Basic flow test:

- [ ] Paste 50+ character job description
- [ ] Select resume from dropdown
- [ ] Click "Tailor Resume"
- [ ] Progress bar animates
- [ ] Logs appear in terminal
- [ ] Completion shows results
- [ ] Download buttons work

Auto-scraping test:

- [ ] Go to LinkedIn job posting
- [ ] Click extension icon
- [ ] Job description auto-fills
- [ ] Green notification appears

## Troubleshooting

**Extension won't load:**
- Check `manifest.json` is valid JSON
- All required files exist in `extension/` folder
- Chrome version 88+ required

**Cannot connect to backend:**
- Backend must be running on port 8000
- Visit `http://localhost:8000` to verify
- Check CORS settings include `chrome-extension://*`

**Auto-scraping doesn't work:**
- Refresh job posting page after installing extension
- Check browser console for errors (F12)
- Fallback: Manually paste job description

**Downloads fail:**
- Check files created in `data/tailored_resumes/`
- Try "View Full Results" link as alternative
- Check Chrome download permissions

## Documentation

Full documentation available in:
- **`extension/README.md`** - Complete extension documentation
- **`extension/INSTALL.md`** - Detailed installation guide
- **`extension/icons/README.md`** - Icon creation instructions

## Next Steps

### Optional Enhancements
- Add real icons (currently using SVG template)
- Test on real LinkedIn/Indeed job postings
- Configure keyboard shortcuts
- Add browser notifications
- Implement dark mode

### Publishing to Chrome Web Store (Future)
1. Create proper icons (16px, 48px, 128px)
2. Add screenshots for store listing
3. Write store description
4. Submit for review ($5 one-time fee)
5. Update CORS with specific extension ID

## Workflow Improvement

**Before (Issue #6):**
1. Find job posting
2. Copy text
3. Switch to app tab
4. Paste, configure, submit
5. Wait, download

**After (Extension):**
1. Navigate to job posting
2. Click extension icon
3. Auto-filled! Just click submit ✨
4. Download directly from popup

**Estimated Time Saved:** ~50% (as predicted in issue)

## Support

For issues:
1. Check `extension/README.md` troubleshooting section
2. Review backend console logs
3. Check browser DevTools (F12) console
4. Open issue on GitHub

---

**Enjoy your streamlined job application workflow! 🚀**
