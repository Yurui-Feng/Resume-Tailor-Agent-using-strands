# Prompt Template Updates

Based on your AI_engineer.tex resume, I've refined the system prompts to match your specific LaTeX template and enforce truthfulness.

## Key Changes Made

### 1. Added Template-Specific Macro Documentation

**In `prompts/system_prompt.txt`:**
- Documented your exact custom macros:
  - `\resumeEntryStart` / `\resumeEntryEnd`
  - `\resumeEntryTSDL{Title}{Date}{Subtitle}{Location}`
  - `\resumeEntryTD{Title}{Date}`
  - `\resumeEntryS{Label}{Content}`
  - `\resumeItemListStart` / `\resumeItemListEnd`
  - `\resumeItem{text}`
  - `\section{\faIcon}{Title}`

**Why this matters:**
- Agent will use YOUR exact macro structure, not generic LaTeX
- Prevents mixing template styles (e.g., won't use `\cventry` from moderncv)
- Ensures output compiles correctly

### 2. Strengthened "No Fabrication" Rules

**Critical additions:**
```
ABSOLUTE REQUIREMENTS:
1. NEVER FABRICATE:
   - Employers, job titles, dates, or locations
   - Technologies, tools, or frameworks not in original resume
   - Degrees, certifications, or educational achievements
   - Metrics, numbers, or quantitative achievements
   - Project names or specific accomplishments

2. ONLY REPHRASE AND REORGANIZE existing content
```

**Why this matters:**
- Explicitly prevents inventing experience
- Limits agent to truthful tailoring only
- Aligns with your original prompt philosophy

### 3. Added Specific Output Format Guidelines

**Three modes defined:**

1. **Analysis/Suggestions** (default):
   - Detailed job requirement analysis
   - Specific improvement recommendations
   - No code generation unless requested

2. **LaTeX Generation** (on request):
   - Output ONLY valid LaTeX code
   - Use exact template macros
   - Return specific sections or full resume

3. **Iterative Refinement**:
   - Show before/after comparisons
   - Explain rationale for changes
   - Confirm major structural changes

**Why this matters:**
- Clarifies when to generate code vs. provide guidance
- Supports iterative workflow you described
- Prevents unwanted code dumps

### 4. Updated LaTeX Rules with Template Examples

**In `prompts/latex_rules.txt`:**

Added correct vs. incorrect examples using YOUR macros:

```latex
✅ Correct:
\resumeEntryStart
  \resumeEntryTSDL{Cloud Support Engineer}{01/2025 -- Present}{Amazon Web Services}{Toronto, ON}
  \resumeItemListStart
    \resumeItem{Bullet point text}
  \resumeItemListEnd
\resumeEntryEnd

❌ Wrong macro:
\cventry{Title}{Date}{Company}{Location}

❌ Wrong parameter order:
\resumeEntryTSDL{01/2025}{Title}{Location}{Company}
```

**Why this matters:**
- Provides concrete examples from YOUR resume
- Shows exact syntax the agent must follow
- Reduces LaTeX formatting errors

### 5. Enhanced Skills Section Handling

**Documented the special format:**
```latex
\resumeEntryS{Languages}{\textbf{Python} (primary), SQL, Bash}
\resumeEntryS{MLOps \& ML}{\textbf{SageMaker}, \textbf{Bedrock}, PyTorch}
```

Note: First parameter is label, second is content (NOT the other way around)

### 6. Professional Summary Format

**Documented the unique format:**
```latex
\resumeEntryS{}{
  Your professional summary text with \textbf{keywords} bolded
}
```

Note: First parameter is empty, second contains full summary

## How This Improves Your Experience

### Before Updates:
- Agent might use generic LaTeX commands
- Risk of fabricating experience to "fill gaps"
- Unclear when it should generate code vs. suggestions
- Template-agnostic validation

### After Updates:
- Agent uses YOUR exact macro structure
- Strictly prohibited from inventing experience
- Clear workflow: analyze → suggest → generate (on request)
- Template-specific validation and examples

## Testing the Updates

Try this workflow in the notebook:

```python
# 1. Load a job posting
job_text = """
Senior ML Engineer
Requirements:
- 5+ years Python, AWS, SageMaker
- Production ML deployment experience
- Strong communication skills
"""

with open("data/job_postings/test_ml.txt", "w") as f:
    f.write(job_text)

# 2. Ask for analysis (default mode)
analysis = resume_agent("""
Analyze the job posting at data/job_postings/test_ml.txt against my resume at
data/original/AI_engineer.tex. What are the key matches and gaps?
""")

# 3. Ask for specific improvements
suggestions = resume_agent("""
Based on the analysis, suggest specific improvements to my Professional Summary
and first two experience bullets. Show me before/after examples.
""")

# 4. Request LaTeX generation
latex_code = resume_agent("""
Generate ONLY the LaTeX code for an updated Professional Summary that emphasizes
SageMaker and production ML deployment experience. Use my resume's exact macros.
""")

# 5. Validate
validation = resume_agent.tool.validate_latex(latex_content=latex_code)
```

## What to Watch For

**Good signs the updates are working:**
- Agent references your exact macros (`\resumeEntryTSDL`, etc.)
- Suggestions focus on rephrasing existing content
- No invented technologies or metrics
- LaTeX validates correctly
- Clear distinction between analysis and code generation

**Red flags to report:**
- Uses wrong macros (e.g., `\cventry` instead of `\resumeEntryTSDL`)
- Invents experience not in your resume
- Mixes parameter order
- Breaks LaTeX syntax
- Generates code when you asked for suggestions

## Files Modified

1. **`prompts/system_prompt.txt`**
   - Added template-specific macro documentation
   - Strengthened no-fabrication rules
   - Added output format guidelines
   - Enhanced truthfulness requirements

2. **`prompts/latex_rules.txt`**
   - Added template-specific examples
   - Documented correct macro usage
   - Added common mistakes specific to your template
   - Enhanced validation guidelines

## Next Steps

1. ✅ Updated prompts are ready
2. 📝 Test with a real job posting
3. 📝 Verify LaTeX output compiles
4. 📝 Iterate on prompts based on results
5. 📝 Add job-specific examples to prompts

## Customizing Further

You can continue refining the prompts by:

1. **Adding domain-specific keywords**
   Edit `prompts/system_prompt.txt` to emphasize certain skill categories

2. **Adjusting tone**
   Add sections about preferred writing style (technical, business-focused, etc.)

3. **Emphasis rules**
   Specify which sections should be prioritized for different job types

4. **Validation strictness**
   Modify `prompts/latex_rules.txt` to add/remove validation checks

The prompts are in plain text files, so you can edit them anytime without touching code!

---

**Ready to tailor your resume with accurate, template-compliant outputs! 🎯**
