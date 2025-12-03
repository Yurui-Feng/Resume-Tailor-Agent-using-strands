# Resume Tailor Chrome Extension

Chrome extension for AI-powered resume tailoring. Streamlines your job application workflow by allowing you to tailor resumes directly from job posting pages.

## Features

- **Browser Action Popup**: Quick access to resume tailoring from any page
- **Auto-Scraping**: Automatically extracts job descriptions from LinkedIn and Indeed
- **Real-Time Progress**: Watch your resume being generated with live progress updates
- **In-Popup Results**: Download tailored resumes without leaving the job posting page
- **Persistent Preferences**: Remembers your last-used resume and settings

## Installation

### Development Mode (Local Testing)

1. **Ensure Backend is Running**
   ```bash
   cd d:\Strands-agent
   # Start the backend server
   python -m uvicorn backend.main:app --reload
   ```
   The backend should be accessible at `http://localhost:8000`

2. **Add Extension Icons** (Optional but recommended)
   - Navigate to `extension/icons/`
   - Add three PNG files: `icon16.png`, `icon48.png`, `icon128.png`
   - See `icons/README.md` for icon creation instructions
   - You can use the provided `icon.svg` as a template

3. **Load Extension in Chrome**
   - Open Chrome and navigate to `chrome://extensions/`
   - Enable "Developer mode" (toggle in top-right corner)
   - Click "Load unpacked"
   - Select the `extension` folder: `d:\Strands-agent\extension`
   - The extension should now appear in your extensions list

4. **Pin the Extension** (Recommended)
   - Click the puzzle piece icon in Chrome toolbar
   - Find "Resume Tailor" and click the pin icon
   - Extension icon will now appear in toolbar for quick access

## Usage

### Basic Workflow

1. **Navigate to a job posting** (or any page)
2. **Click the Resume Tailor extension icon** in Chrome toolbar
3. **Paste or auto-fill job description**:
   - On LinkedIn/Indeed: Job description auto-fills automatically
   - On other sites: Paste job description manually
4. **Select your resume** from the dropdown
5. **Configure options**:
   - ☐ Update Experience Section (optional)
   - ☑ Generate PDF (recommended)
6. **Click "Tailor Resume"**
7. **Watch progress** in real-time with progress bar and terminal logs
8. **Download results** when complete (.tex and .pdf files)

### Auto-Scraping Support

The extension automatically detects and extracts job descriptions from:

- **LinkedIn Jobs**: `*.linkedin.com/jobs/*`
- **Indeed**: `*.indeed.com/viewjob*`

When you open the extension popup on these sites, the job description will be automatically filled in.

### Keyboard Shortcuts

Currently no keyboard shortcuts are configured. You can add them via Chrome's extension settings if desired.

## Troubleshooting

### Extension Not Loading

**Problem**: Extension shows errors when loading

**Solutions**:
- Check that all required files exist in the `extension` folder
- Ensure `manifest.json` is valid JSON (no syntax errors)
- Check Chrome DevTools console for error messages
- Try removing and re-adding the extension

### Cannot Connect to Backend

**Problem**: "Could not connect to backend" error

**Solutions**:
- Verify backend server is running: Visit `http://localhost:8000` in browser
- Check CORS settings in `backend/config.py` include `"chrome-extension://*"`
- Restart the backend server after CORS changes
- Check backend console for CORS-related errors

### Auto-Scraping Not Working

**Problem**: Job description doesn't auto-fill on LinkedIn/Indeed

**Solutions**:
- Refresh the job posting page after installing extension
- Check if LinkedIn/Indeed updated their page structure
- Open extension popup, then check browser console for errors
- Manually paste job description as fallback

### Progress Stuck or Not Updating

**Problem**: Progress bar stuck at certain percentage

**Solutions**:
- Check backend console logs for errors
- Ensure backend process hasn't crashed
- Wait longer (some jobs take 2-3 minutes)
- Click "Cancel" and try again

### Downloads Not Working

**Problem**: Download buttons don't work

**Solutions**:
- Check that job completed successfully
- Verify files exist in `data/tailored_resumes/` on backend
- Check Chrome's download settings allow downloads
- Try "View Full Results & History" link to download from web app

## Development

### File Structure

```
extension/
├── manifest.json              # Extension configuration
├── popup/
│   ├── popup.html            # Popup UI
│   ├── popup.css             # Brutalist theme styles
│   └── popup.js              # Popup logic
├── background/
│   └── service-worker.js     # API communication
├── content/
│   ├── linkedin-scraper.js   # LinkedIn job extraction
│   └── indeed-scraper.js     # Indeed job extraction
└── icons/
    ├── icon.svg              # SVG source for icons
    ├── icon16.png            # 16x16 toolbar icon
    ├── icon48.png            # 48x48 management icon
    └── icon128.png           # 128x128 store icon
```

### Debugging

**Popup Debugging**:
1. Right-click extension icon → "Inspect popup"
2. Chrome DevTools opens for popup page
3. Check Console tab for JavaScript errors
4. Use debugger statements or breakpoints

**Background Service Worker Debugging**:
1. Go to `chrome://extensions/`
2. Find "Resume Tailor" extension
3. Click "service worker" link under "Inspect views"
4. DevTools opens for background script

**Content Script Debugging**:
1. Open a LinkedIn or Indeed job page
2. Open DevTools (F12)
3. Check Console for content script logs
4. Content scripts run in page context

### Making Changes

After modifying extension files:

1. **For popup changes** (HTML/CSS/JS):
   - Close and reopen popup to see changes
   - Or click "Reload" on extension in `chrome://extensions/`

2. **For background service worker changes**:
   - Must click "Reload" on extension in `chrome://extensions/`

3. **For content script changes**:
   - Must click "Reload" on extension
   - Then refresh any job posting pages

### Testing Checklist

- [ ] Extension loads without errors
- [ ] Popup opens and shows form
- [ ] Resumes load from backend
- [ ] Character count updates
- [ ] Submit button enables when valid
- [ ] Job submission works
- [ ] Progress bar animates smoothly
- [ ] Terminal logs appear
- [ ] Completion shows results view
- [ ] Download buttons work
- [ ] Auto-scraping works on LinkedIn
- [ ] Auto-scraping works on Indeed
- [ ] Preferences are saved and restored
- [ ] Cancel button works
- [ ] Error handling works (backend offline)

## API Endpoints Used

The extension communicates with these backend endpoints:

- `GET /api/resumes` - List available resumes
- `POST /api/tailor` - Submit resume tailoring job
- `GET /api/jobs/{job_id}/status` - Poll job status
- `GET /api/results/{id}/tex` - Download .tex file
- `GET /api/results/{id}/pdf` - Download .pdf file

## Browser Compatibility

- **Chrome**: 88+ (Manifest V3 support)
- **Edge**: 88+ (Chromium-based)
- **Brave**: Latest (Chromium-based)
- **Firefox**: Not compatible (uses different extension API)

## Future Enhancements

Planned features for future versions:

- [ ] Cover letter generation from extension
- [ ] History view in popup
- [ ] Metadata override fields (company name, job title)
- [ ] Support for more job boards (Glassdoor, Dice)
- [ ] Dark mode theme
- [ ] Browser notifications on completion
- [ ] Keyboard shortcuts
- [ ] Export to multiple formats

## License

Same license as parent Resume Tailor project.

## Support

For issues or questions:
1. Check this README's Troubleshooting section
2. Review backend console logs
3. Check browser DevTools console
4. Open an issue on the project repository
