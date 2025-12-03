# Quick Installation Guide

## Prerequisites

1. Resume Tailor backend must be running at `http://localhost:8000`
2. Chrome browser (version 88 or higher)

## Installation Steps

### 1. Start the Backend

```bash
cd d:\Strands-agent
python -m uvicorn backend.main:app --reload
```

Verify it's running by visiting: http://localhost:8000

### 2. Load Extension in Chrome

1. Open Chrome
2. Go to `chrome://extensions/`
3. Enable **Developer mode** (toggle switch in top-right)
4. Click **Load unpacked**
5. Navigate to and select: `d:\Strands-agent\extension`
6. Extension loads successfully ✓

### 3. Pin Extension to Toolbar (Optional)

1. Click the puzzle piece icon in Chrome toolbar
2. Find "Resume Tailor"
3. Click the pin icon next to it
4. Icon now appears in main toolbar

## First Use

1. Click the Resume Tailor icon in Chrome toolbar
2. Popup opens with form
3. If resumes show in dropdown → Backend connected ✓
4. If error appears → Check backend is running

## Testing Auto-Scraping

1. Go to any LinkedIn job posting: `linkedin.com/jobs/view/...`
2. Click Resume Tailor extension icon
3. Job description should auto-fill in textarea
4. "Job posting detected and auto-filled" message appears

## Quick Test

1. Paste any job description (50+ characters)
2. Select a resume from dropdown
3. Click "Tailor Resume"
4. Watch progress bar and logs
5. Download .tex and .pdf when complete

## Troubleshooting

**"Could not connect to backend"**
- Make sure backend is running on port 8000
- Check CORS is configured (should be automatic after setup)

**Auto-scraping not working**
- Refresh the job posting page
- Extension content scripts load when page loads
- Fallback: Manually paste job description

**Extension won't load**
- Check all files exist in `extension/` folder
- Manifest.json must be valid JSON
- Icons are optional (uses default if missing)

## Updating Extension

After making code changes:
1. Go to `chrome://extensions/`
2. Find "Resume Tailor"
3. Click reload icon (circular arrow)
4. Reopen popup to see changes

## Uninstalling

1. Go to `chrome://extensions/`
2. Find "Resume Tailor"
3. Click "Remove"
