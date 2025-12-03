# How to Load Resume Tailor Extension in Chrome

## Visual Step-by-Step Guide

### Step 1: Open Chrome Extensions Page

**Method A - Type in Address Bar:**
```
chrome://extensions/
```
Just type this and press Enter

**Method B - Use Menu:**
1. Click the three dots ⋮ in top-right corner of Chrome
2. Hover over "Extensions"
3. Click "Manage Extensions"

---

### Step 2: Enable Developer Mode

Once on the extensions page (`chrome://extensions/`):

1. Look at the **TOP-RIGHT corner** of the page
2. Find the toggle switch labeled **"Developer mode"**
3. Click it to turn it **ON** (it will turn blue/highlighted)

```
Before:  Developer mode [  OFF  ]
After:   Developer mode [  ON   ] ← Should be blue/active
```

After enabling, you'll see new buttons appear:
- "Load unpacked"
- "Pack extension"
- "Update"

---

### Step 3: Click "Load unpacked"

1. Click the **"Load unpacked"** button (appears after Step 2)
2. A file picker window will open

---

### Step 4: Navigate to Extension Folder

In the file picker window:

1. Navigate to: **`d:\Strands-agent\extension`**

   Your path should look like:
   ```
   This PC > D: > Strands-agent > extension
   ```

2. You should see these files/folders:
   ```
   extension/
   ├── manifest.json          ← Must be present!
   ├── popup/
   ├── background/
   ├── content/
   ├── icons/
   └── README.md
   ```

3. **Important:** Select the `extension` folder itself, not a file inside it

4. Click **"Select Folder"** button at bottom-right

---

### Step 5: Verify Extension Loaded

Back on `chrome://extensions/`, you should now see:

```
┌─────────────────────────────────────────────┐
│  Resume Tailor                       v1.0.0 │
│  AI-powered resume tailoring from job...    │
│                                             │
│  [  ] Service worker                        │
│  [  ] Errors  [  ] Details  [  ] Remove     │
│                                             │
│  ID: abcdefghijklmnopqrstuvwxyz...         │
└─────────────────────────────────────────────┘
```

**✅ Success indicators:**
- Extension card appears
- No red error messages
- Toggle is ON (blue)

**❌ If you see errors:**
- Red text with error messages → Check troubleshooting below

---

### Step 6: Pin to Toolbar (Optional but Recommended)

1. Look for the **puzzle piece icon** 🧩 in Chrome toolbar (top-right, near profile icon)
2. Click it to open extensions menu
3. Find "Resume Tailor" in the list
4. Click the **pin icon** 📌 next to it

Now the extension icon will appear directly in your toolbar!

---

## Quick Path Reference

**Exact folder to select:**
```
d:\Strands-agent\extension
```

**What Chrome is looking for:**
Chrome needs to see `manifest.json` in the folder you select.

---

## Testing It Works

### After loading:

1. **Click the extension icon** in Chrome toolbar
   - If you pinned it: Click the icon directly
   - If not pinned: Click puzzle piece 🧩 → Click "Resume Tailor"

2. **Popup should open** showing:
   ```
   Resume Tailor
   AI-powered resume tailoring

   Job Posting
   [                                    ]
   [                                    ]

   Resume
   [Select resume ▼]

   ☐ Update Experience Section
   ☑ Generate PDF

   [    Tailor Resume    ]

   Open Full App →
   ```

3. **Check resumes load:**
   - The "Resume" dropdown should show your available resumes
   - If it shows "Loading resumes..." forever → Backend might not be running
   - If it shows "Failed to load resumes" → Connection issue

---

## Troubleshooting

### Error: "Manifest file is missing or unreadable"

**Problem:** Chrome can't find `manifest.json`

**Fix:**
- Make sure you selected the `extension` folder, not a subfolder
- Check that `d:\Strands-agent\extension\manifest.json` exists
- Don't select individual files, select the whole folder

---

### Error: "Could not load manifest"

**Problem:** `manifest.json` has syntax errors

**Fix:**
- Check if `manifest.json` is valid JSON
- Look at the specific error message for line number
- File should have been created correctly, but verify it exists

---

### Extension loads but shows "Could not connect to backend"

**Problem:** Extension can't reach the backend API

**Fix:**
1. ✅ Backend should already be running (you started it)
2. Test in browser: Open `http://localhost:8000` - should show the web app
3. If browser shows connection refused → Backend isn't running
4. Restart backend: `python -m uvicorn backend.main:app --reload --port 8000`

---

### Extension loads but dropdown shows "Loading resumes..." forever

**Problem:** API call is hanging or CORS issue

**Fix:**
1. Open Chrome DevTools (F12)
2. Click extension icon to open popup
3. Right-click popup → "Inspect"
4. Check Console tab for errors
5. Look for CORS errors (red text)
6. Verify `backend/config.py` has `chrome-extension://*` in ALLOWED_ORIGINS

---

### "Manifest version 2 is deprecated"

**Don't worry!** This is just a warning. Our extension uses Manifest V3 (the new version).

If you see this warning, Chrome is just reminding you about old extensions. Ours is already using V3.

---

## Video/Screenshot Guide

Since I can't create screenshots, here's what to look for:

**Extensions page looks like:**
- Top bar: "Extensions" title
- Top-right: Blue toggle "Developer mode"
- Left side: List of installed extensions
- Top-left (after enabling dev mode): Three blue buttons

**File picker looks like:**
- Standard Windows file explorer
- Shows folders and files
- Bottom-right: "Select Folder" button
- Make sure you see `manifest.json` in the right panel

---

## Still Having Issues?

1. **Verify backend is running:**
   ```bash
   # Should already be running, but if not:
   python -m uvicorn backend.main:app --reload --port 8000
   ```

2. **Check browser console:**
   - F12 → Console tab
   - Look for red errors

3. **Try reloading extension:**
   - Go to `chrome://extensions/`
   - Find "Resume Tailor"
   - Click the reload icon (circular arrow)

4. **Try removing and re-adding:**
   - Click "Remove"
   - Repeat Steps 1-4 above

---

## Success!

Once loaded, you can:
- ✅ Click extension icon anywhere in Chrome
- ✅ Popup opens with form
- ✅ Resumes show in dropdown
- ✅ Submit job descriptions
- ✅ Watch real-time progress
- ✅ Download tailored resumes

Try it on a LinkedIn or Indeed job posting to see auto-scraping in action! 🚀
