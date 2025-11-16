# Quick Start Guide - Resume Tailor Agent

**Last Updated**: 2025-11-16

---

## 🚀 Get Started in 3 Steps

### 1. Start Jupyter Notebook
```bash
cd d:\Strands-agent
jupyter notebook resume_tailor.ipynb
```

### 2. Run Setup Cells (1-14)
Click "Run All" on cells 1 through 14 to:
- ✅ Load environment and API keys
- ✅ Configure logging
- ✅ Create agent with all tools
- ✅ Initialize helper functions

**Expected output**: "✅ Resume Tailor Agent created! ... Tools: 9 tools available"

### 3. Tailor Your Resume
Paste a job posting and run!

---

## 📋 Common Tasks

### Task 1: Quick Resume Tailoring (Direct Paste)

**What it does**: Generate tailored resume sections from job posting

**How to use**:
```python
# In a new cell:
job_posting_text = """
Senior ML Engineer - Fraud Detection
Requirements:
- Python, AWS (SageMaker, Bedrock)
- Real-time ML inference
- Team leadership
"""

# Method 1: Use paste_and_tailor (if defined in notebook)
result = paste_and_tailor(job_posting_text)

# Method 2: Use section_agent directly
section_agent(f"""
Read the original resume from: data/original/AI_engineer.tex
Tailor it for this job:

{job_posting_text}

Generate ONLY these sections:
1. Subtitle (job title with escaped LaTeX characters)
2. Professional Summary
3. Technical Proficiencies

Then call merge_sections() to save to: data/tailored_versions/new_resume.tex
""")
```

**Output**: `data/tailored_versions/new_resume.tex` with updated sections

---

### Task 2: View Logs

**What it does**: Shows recent agent operations and tool calls

**How to use**:
```python
# View last 20 log entries (all levels)
view_latest_logs(20)

# View only errors
view_latest_logs(level_filter="ERROR")

# View only debug messages
view_latest_logs(100, level_filter="DEBUG")

# Count tool usage
count_tool_calls()
```

**Output**: Formatted log entries with timestamps and messages

---

### Task 3: Validate Generated Resume

**What it does**: Check LaTeX syntax before compiling

**How to use**:
```python
# Read the generated file
with open("data/tailored_versions/new_resume.tex", 'r') as f:
    content = f.read()

# Validate
validation = resume_agent.tool.validate_latex(latex_content=content)
print(validation)
```

**Output**: Validation report with errors/warnings

---

### Task 4: ANALYSIS MODE (Get Suggestions)

**What it does**: Get analysis and suggestions WITHOUT generating LaTeX

**How to use**:
```python
analysis_prompt = """
You are now in ANALYSIS MODE.

1. Read my resume: data/original/AI_engineer.tex
2. Read the job posting: data/job_postings/quanlom.txt
3. Analyze the job requirements
4. Suggest specific edits to my resume
5. Point out gaps

DO NOT output LaTeX - only analysis and suggestions.
"""

analysis = resume_agent(analysis_prompt)
print(analysis)
```

**Output**: Natural-language analysis (no LaTeX)

---

### Task 5: GENERATE MODE (Create Tailored Resume)

**What it does**: Generate complete tailored LaTeX resume

**How to use**:
```python
generate_prompt = """
You are now in GENERATE MODE.

Based on our previous analysis, produce the final tailored resume.

Requirements:
- Return ONLY complete LaTeX code
- NO explanations, markdown fences, or commentary
- Preserve preamble and macros
- Use merge_sections() to save

Output: data/tailored_versions/final_resume.tex
"""

result = resume_agent(generate_prompt)
```

**Output**: Complete LaTeX file ready to compile

---

### Task 6: Export Readable Logs

**What it does**: Convert JSON logs to human-readable text

**How to use**:
```python
# Export to default filename (timestamped)
export_logs_to_readable()

# Export to specific file
export_logs_to_readable("my_debug_session.txt")
```

**Output**: `logs/readable_log_YYYYMMDD_HHMMSS.txt`

---

### Task 7: Reset Agent (Fresh Start)

**What it does**: Clear conversation history and start over

**How to use**:
```python
# Re-run Cell 14 (agent creation)
# Or restart the notebook kernel:
# Kernel → Restart & Clear Output
```

---

## 🔧 Troubleshooting

### Problem: "Agent doesn't call tools"

**Symptoms**: Agent describes what it will do but doesn't execute

**Fix**:
```python
# Check logs
view_latest_logs(50, level_filter="DEBUG")

# Look for tool registry messages
# Verify agent has correct mode (ANALYSIS vs GENERATE)
```

---

### Problem: "Validation fails"

**Symptoms**: Unbalanced braces, missing document markers

**Fix**:
```python
# Check what errors occurred
view_latest_logs(level_filter="ERROR")

# View the problematic file
with open("data/tailored_versions/new_resume.tex", 'r') as f:
    print(f.read())

# Look for:
# - Incomplete sections
# - Unescaped special characters (&, %, $, etc.)
# - Missing \begin{document} or \end{document}
```

---

### Problem: "LaTeX compile error"

**Symptoms**: `pdflatex` fails with error

**Common Causes**:
1. **Unescaped `&` in subtitle**: Should be `\&`
2. **Unbalanced braces**: Use `validate_latex()` first
3. **Missing macros**: Agent shouldn't modify preamble

**Fix**:
```python
# Validate first
validation = resume_agent.tool.validate_latex(latex_content=content)
print(validation)

# Check for special characters in subtitle
# Example: "Cloud & AI Engineer" should be "Cloud \& AI Engineer"
```

---

### Problem: "Generated file incomplete"

**Symptoms**: File has "omitted for brevity" or cut-off sections

**Fix**:
```python
# Use section-only workflow (prevents incomplete generation)
# Ensure agent uses merge_sections() not write_file()

# Check logs
view_latest_logs(level_filter="DEBUG")

# Look for merge_sections() call
# If missing, agent used wrong workflow
```

---

## 📁 File Locations

### Input Files
```
data/original/AI_engineer.tex       # Your LaTeX resume
data/job_postings/*.txt             # Job postings (plain text)
```

### Output Files
```
data/tailored_versions/*.tex        # Generated resumes
logs/strands_agent_*.log            # JSON logs
logs/readable_log_*.txt             # Exported readable logs
```

### Configuration
```
.env                                # API keys (OPENAI_API_KEY or AWS_*)
prompts/system_prompt.txt           # Agent instructions
```

---

## 🎯 Best Practices

### 1. Always Start with ANALYSIS MODE
```python
# First, get suggestions
analysis = resume_agent("ANALYSIS MODE: analyze this job...")

# Review suggestions

# Then generate
result = resume_agent("GENERATE MODE: create tailored resume...")
```

### 2. Use Section-Only Workflow
```python
# Good: Generate only sections, merge with original
section_agent("Generate ONLY: subtitle, summary, skills")

# Bad: Regenerate full template (causes errors)
resume_agent("Generate complete LaTeX document")  # ❌ Don't do this
```

### 3. Validate Before Compiling
```python
# Always validate first
validation = resume_agent.tool.validate_latex(latex_content=content)

if validation['is_valid']:
    # Proceed to pdflatex
    pass
else:
    # Fix errors first
    print(validation['errors'])
```

### 4. Check Logs for Debugging
```python
# After any operation, check logs
view_latest_logs(20)

# If errors occurred
view_latest_logs(level_filter="ERROR")
```

### 5. Keep Job Titles Exact
```python
# Agent will automatically escape special characters
# Just provide the exact job title from posting

# Example:
# Job posting: "Cloud & AI Software Engineer"
# Generated: \def \subtitle {Cloud \& AI Software Engineer}  ✅
```

---

## 🔄 Typical Workflow

```
1. Open notebook → Run cells 1-14 (setup)
   ↓
2. Paste job posting → Run ANALYSIS MODE
   ↓
3. Review suggestions → Adjust if needed
   ↓
4. Run GENERATE MODE (section-only)
   ↓
5. Agent calls merge_sections() → Validates
   ↓
6. Check logs → view_latest_logs()
   ↓
7. Validate output → validate_latex()
   ↓
8. Compile PDF → pdflatex new_resume.tex
   ↓
9. Success! ✅
```

---

## 📊 Logging Quick Reference

### Log Levels
- **DEBUG**: Everything (tool calls, decisions, data)
- **INFO**: General progress updates
- **WARNING**: Potential issues (rate limits, deprecations)
- **ERROR**: Failures (validation errors, exceptions)

### Where Logs Go
- **File** (`logs/strands_agent_*.log`): DEBUG (everything)
- **Console** (notebook output): WARNING+ (errors only)

### Log Analysis
```python
# Recent activity
view_latest_logs(20)

# Errors only
view_latest_logs(level_filter="ERROR")

# Tool usage stats
count_tool_calls()

# Export for sharing
export_logs_to_readable("debug_session.txt")
```

---

## 🆘 Getting Help

### Check Documentation
1. [LOGGING_SETUP.md](LOGGING_SETUP.md) - Logging details
2. [FIX_VALIDATION_ISSUES.md](FIX_VALIDATION_ISSUES.md) - Validation fixes
3. [NOTEBOOK_UPDATES.md](NOTEBOOK_UPDATES.md) - Notebook changes
4. [TODO_NEXT.md](TODO_NEXT.md) - Roadmap
5. [VERIFICATION_COMPLETE.md](VERIFICATION_COMPLETE.md) - Implementation summary

### Debug Checklist
- [ ] Check logs: `view_latest_logs()`
- [ ] Verify tool calls: `count_tool_calls()`
- [ ] Validate output: `validate_latex(content)`
- [ ] Check file exists: `Path("output.tex").exists()`
- [ ] Review agent mode: ANALYSIS vs GENERATE

---

## ✅ Success Criteria

Your resume tailoring is successful when:

- ✅ Agent generates ONLY sections (not full template)
- ✅ merge_sections() called automatically
- ✅ Validation passes (no unbalanced braces)
- ✅ LaTeX compiles without errors
- ✅ Output matches job posting requirements
- ✅ No fabricated experience or skills
- ✅ Length matches original (~1 page)
- ✅ Logs show clean execution

---

**Ready to start? Open [resume_tailor.ipynb](resume_tailor.ipynb) and run cells 1-14!** 🚀
