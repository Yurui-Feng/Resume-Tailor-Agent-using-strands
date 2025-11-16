# TODO: Resume Tailor Agent - Next Steps

## Current Issues to Fix

### 🔴 Priority 1: Fix Incomplete LaTeX Generation

**Problem:** Generated `.tex` files are incomplete/broken

**Solution:** Modify agent to update specific sections only
- ✅ Update Professional Summary
- ✅ Update Experience bullets (first 2-3 roles)
- ✅ Update Skills section
- ✅ Update subtitle (`\def \subtitle {Job Title from Posting}`)
- ❌ Keep everything else from original (header, education, certifications, footer)

**Implementation:**
- Create a "section-only update" mode
- Agent generates only the sections that need changing
- Manual merge OR create merge tool to combine with original

**Estimated effort:** 1-2 hours

---

## Feature Roadmap (Prioritized)

### 🟢 Phase 1: Core Functionality (Must Have)

#### 1.1 Direct LaTeX Rendering Pipeline
**Goal:** One command to generate PDF from tailored `.tex`

**Features:**
- Button/command to compile `.tex` → PDF automatically
- Uses `pdflatex` or `xelatex` (based on template requirements)
- Error handling and validation
- Output: `resume_company_role.pdf`

**Implementation options:**
```python
# Option A: Python subprocess
import subprocess
subprocess.run(['pdflatex', 'resume.tex'])

# Option B: Use latexmk (better error handling)
subprocess.run(['latexmk', '-pdf', 'resume.tex'])

# Option C: Overleaf API integration
```

**Estimated effort:** 2-3 hours

**Priority:** ⭐⭐⭐⭐⭐

---

#### 1.2 Simplified Job Input (No Parsing)
**Goal:** Copy-paste job posting, agent handles analysis internally

**Current flow:**
```
User → Save to file → Agent reads file → Analyzes
```

**New flow:**
```
User → Paste into notebook/UI → Agent processes directly
```

**Implementation:**
```python
# Simple function
def tailor_resume(job_text: str, focus_areas: list = None):
    """
    Args:
        job_text: Raw job posting text (copy-pasted)
        focus_areas: Optional list like ['Skills', 'Experience', 'Summary']
    """
    # Agent analyzes internally
    # Returns tailored sections
```

**Estimated effort:** 1 hour

**Priority:** ⭐⭐⭐⭐⭐

---

#### 1.3 Length Matching
**Goal:** Match length/style of AI_engineer.tex and Data_engineer.tex

**Requirements:**
- Summary: ~150 words
- Experience: 2-3 roles, 4-5 bullets each
- Skills: Same sections as original
- Overall: 1 page

**Implementation:**
- Add length constraints to system prompt
- Agent checks word count before outputting
- Provides "trim suggestions" if too long

**Estimated effort:** 30 minutes (prompt update)

**Priority:** ⭐⭐⭐⭐

---

### 🟡 Phase 2: Enhanced Workflow (Should Have)

#### 2.1 Section-Only Updates
**Goal:** Update only specific sections, keep rest intact

**Features:**
```python
# Specify which sections to update
tailor_sections(
    job_text="...",
    sections=['Summary', 'Skills', 'Subtitle'],
    keep_rest=True  # Don't touch Experience, Education, etc.
)
```

**Output:** Only generates LaTeX for requested sections

**Estimated effort:** 2 hours

**Priority:** ⭐⭐⭐⭐

---

#### 2.2 Smart Merge Tool
**Goal:** Merge updated sections into original resume

**Features:**
```python
merge_resume(
    original="data/original/AI_engineer.tex",
    updates={
        'summary': new_summary_latex,
        'skills': new_skills_latex,
        'subtitle': "Senior ML Engineer"
    },
    output="data/tailored_versions/resume_output.tex"
)
```

**Implementation:**
- Parse original `.tex` structure
- Replace specific sections
- Validate final output
- Write complete `.tex` file

**Estimated effort:** 3-4 hours

**Priority:** ⭐⭐⭐⭐

---

#### 2.3 Preview & Edit Interface
**Goal:** See changes before finalizing

**Option A: Jupyter Widgets**
```python
# Show side-by-side comparison
display_comparison(
    original=original_text,
    tailored=tailored_text,
    section="Professional Summary"
)

# Allow inline edits
edit_box = widgets.Textarea(value=tailored_text)
# Apply edits → regenerate
```

**Option B: Simple HTML output**
```python
# Generate HTML preview
preview_html = generate_preview(original, tailored)
IPython.display.HTML(preview_html)
```

**Estimated effort:** 4-5 hours

**Priority:** ⭐⭐⭐

---

### 🔵 Phase 3: GUI Application (Nice to Have)

#### 3.1 Streamlit/Gradio GUI
**Goal:** Full web interface for resume tailoring

**Features:**
- **Input Panel:**
  - Upload resume `.tex`
  - Paste job posting
  - Select sections to update

- **Processing:**
  - "Analyze Job" button
  - Shows requirements extraction
  - "Generate Tailored Resume" button

- **Preview Panel:**
  - Side-by-side: Original vs. Tailored
  - Highlight changes
  - Inline editing

- **Output:**
  - "Download .tex" button
  - "Generate PDF" button (direct render)
  - "Save to Project" button

**Tech stack:**
- **Streamlit** (easier, Python-only)
- **Gradio** (simpler for ML workflows)
- **Flask + React** (more control, more work)

**Estimated effort:** 8-12 hours

**Priority:** ⭐⭐

---

#### 3.2 PDF Direct Render in GUI
**Goal:** Click button → See PDF preview immediately

**Features:**
- Compile `.tex` → PDF in background
- Display PDF in iframe/viewer
- Download button
- Error messages if compilation fails

**Implementation:**
```python
# Backend: Compile LaTeX
def render_pdf(tex_path):
    subprocess.run(['pdflatex', '-output-directory=temp/', tex_path])
    return 'temp/resume.pdf'

# Frontend: Display PDF
st.download_button("Download PDF", pdf_data)
```

**Estimated effort:** 3-4 hours (after GUI built)

**Priority:** ⭐⭐

---

## Implementation Order (Recommended)

### Week 1: Fix Core Issues
1. ✅ **Fix incomplete LaTeX** (Priority 1)
   - Section-only updates
   - Length matching

2. ✅ **Simplify job input** (Priority 1)
   - Direct paste workflow
   - Remove file-based parsing

3. ✅ **Add PDF rendering** (Priority 1)
   - Simple subprocess call
   - Validate output

**Deliverable:** Working end-to-end pipeline in notebook

---

### Week 2: Enhanced Workflow
4. ✅ **Smart merge tool** (Priority 2)
   - Combine sections programmatically
   - Validate complete `.tex`

5. ✅ **Preview interface** (Priority 2)
   - Jupyter widgets OR HTML output
   - Show before/after

**Deliverable:** Polished notebook experience with previews

---

### Week 3+: GUI (Optional)
6. ⚠️ **Streamlit/Gradio app** (Priority 3)
   - Basic UI first
   - Add features incrementally

7. ⚠️ **PDF rendering in GUI** (Priority 3)
   - Integrate compilation
   - Display in browser

**Deliverable:** Standalone GUI application

---

## Quick Wins (Do First)

### 🎯 Immediate Actions (< 1 hour each)

1. **Update system prompt for length constraints**
   ```
   - Summary: max 150 words
   - Experience: 2-3 roles, 4-5 bullets each
   - Skills: match original structure
   - Total: 1 page
   ```

2. **Create simple paste-and-tailor function**
   ```python
   def quick_tailor(job_text: str):
       # No file saving needed
       # Direct processing
   ```

3. **Add PDF compile helper**
   ```python
   def compile_pdf(tex_file):
       subprocess.run(['pdflatex', tex_file])
   ```

4. **Create section-only update function**
   ```python
   def update_sections(job_text, sections=['Summary', 'Skills']):
       # Returns only requested sections
   ```

---

## File Structure After Implementation

```
resume-tailor-agent/
├── data/
│   ├── original/
│   │   ├── AI_engineer.tex
│   │   └── Data_engineer.tex
│   ├── job_postings/          # Optional now
│   ├── tailored_versions/
│   │   ├── resume_company.tex
│   │   └── resume_company.pdf  ← New!
│   └── temp/                   ← New! (build artifacts)
├── tools/
│   ├── resume_tools.py
│   ├── latex_compiler.py       ← New!
│   └── merge_sections.py       ← New!
├── resume_tailor.ipynb
├── resume_tailor_gui.py        ← New! (Phase 3)
└── compile_pdf.sh              ← New! (helper script)
```

---

## Testing Plan

### Test Case 1: Section Updates
- Input: Job posting (ML Engineer)
- Output: Only Summary + Skills sections
- Validate: Can merge into original successfully

### Test Case 2: Complete Resume
- Input: Job posting
- Output: Full `.tex` matching length of AI_engineer.tex
- Validate: Compiles to PDF without errors

### Test Case 3: PDF Rendering
- Input: Tailored `.tex` file
- Output: `.pdf` file
- Validate: PDF looks correct, no LaTeX errors

### Test Case 4: Multiple Jobs
- Input: 3 different job postings
- Output: 3 tailored resumes
- Validate: Each emphasizes different skills correctly

---

## Success Criteria

### Phase 1 Complete:
- ✅ Can paste job posting → get tailored sections
- ✅ Sections match length/style of originals
- ✅ Can compile `.tex` → PDF with one command
- ✅ Output is truthful (no fabrication)
- ✅ LaTeX validates and compiles correctly

### Phase 2 Complete:
- ✅ Can preview changes before applying
- ✅ Can edit inline and regenerate
- ✅ Smart merge produces complete, valid `.tex`
- ✅ Workflow is smooth and intuitive

### Phase 3 Complete:
- ✅ GUI runs standalone (no notebook needed)
- ✅ Can upload, tailor, preview, download all in browser
- ✅ PDF generates and displays in UI
- ✅ Non-technical users can use it

---

## Notes

**Current bottlenecks:**
- Incomplete LaTeX generation (fix first!)
- File-based workflow (simplify to paste)
- No PDF rendering (easy win)

**Future enhancements:**
- Multiple resume templates support
- Job posting library (save analyzed jobs)
- A/B testing (try different phrasings)
- Version control (track all tailored versions)
- Analytics (which keywords appear most, match scores)

**Out of scope (for now):**
- AI-powered job search integration
- Automatic application submission
- Cover letter generation (separate project)
- LinkedIn profile updates

---

## Get Started

**Today (0 hours - just planning):**
- ✅ Read this TODO
- ✅ Understand priorities
- ✅ Decide which phase to tackle first

**Next session (2-3 hours):**
1. Update system prompt for length matching
2. Create section-only update function
3. Add PDF compilation helper
4. Test with real job posting

**This week (5-8 hours):**
- Complete Phase 1
- Test end-to-end workflow
- Document results

**Next week:**
- Start Phase 2 if Phase 1 works well
- OR jump to GUI if you prefer visual tools

---

**Ready to build! 🚀**

Pick a priority, start coding, and iterate!
