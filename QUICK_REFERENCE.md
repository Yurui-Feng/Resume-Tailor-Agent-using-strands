# Quick Reference - Resume Tailor Agent

## Common Prompts for Resume Tailoring

### 1. Analyze Job Posting

```python
response = resume_agent("""
Read and analyze the job posting at data/job_postings/ml_engineer_google.txt.
What are the must-have requirements, nice-to-haves, and key keywords?
""")
```

### 2. Compare Resume to Job

```python
response = resume_agent("""
Compare my resume at data/original/AI_engineer.tex to the job posting at
data/job_postings/ml_engineer_google.txt.

Focus on:
- Which of my experiences best match this role
- What keywords I should emphasize
- Any gaps in requirements
""")
```

### 3. Get Tailoring Suggestions

```python
response = resume_agent("""
Suggest specific improvements to tailor my resume for this ML Engineer role.
Show me:
- Which bullets to move to the top
- How to rephrase bullets with job keywords
- Which technologies to emphasize in Skills section

DO NOT generate LaTeX yet - just provide suggestions.
""")
```

### 4. Request Specific Section Updates

```python
response = resume_agent("""
Generate ONLY the LaTeX code for an updated Professional Summary that:
- Emphasizes SageMaker, Bedrock, and production ML deployment
- Uses keywords from the job posting
- Stays under 150 words
- Uses my resume's exact \resumeEntryS macro

Return ONLY LaTeX code, no explanation.
""")
```

### 5. Update Experience Bullets

```python
response = resume_agent("""
Rewrite the first 3 bullets from my AWS experience to emphasize:
- Real-time ML inference
- Model deployment and monitoring
- Collaboration with data scientists

Show me before/after for each bullet using my \resumeItem macro.
""")
```

### 6. Reorder Bullets for Relevance

```python
response = resume_agent("""
For the AWS Cloud Support Engineer role, reorder all 5 bullets to put
the most ML-relevant ones first. Show me the new order with rationale.
""")
```

### 7. Update Skills Section

```python
response = resume_agent("""
Update my Technical Proficiencies section to emphasize:
- Python and ML frameworks (SageMaker, Bedrock, PyTorch)
- AWS services for ML (Lambda, Step Functions, ECS)
- MLOps tools

Generate ONLY the LaTeX code for the entire Skills section using \resumeEntryS.
""")
```

### 8. Generate Full Tailored Resume

```python
response = resume_agent("""
Generate a complete tailored resume for the Senior ML Engineer role at Google.

Apply these changes:
1. Updated Professional Summary emphasizing ML production experience
2. Reordered experience bullets (most ML-relevant first)
3. Updated Skills section with job keywords
4. Keep Education and Certifications unchanged

Output ONLY valid LaTeX code using my exact template macros.
Save to: data/tailored_versions/resume_google_ml_engineer.tex
""")
```

### 9. Validate LaTeX Output

```python
# After generating LaTeX
validation = resume_agent("""
Validate the LaTeX in data/tailored_versions/resume_google_ml_engineer.tex.
Check for:
- Balanced braces
- Correct macro usage
- Complete document structure
""")
```

### 10. Iterative Refinement

```python
# After seeing initial version
response = resume_agent("""
The Professional Summary is good, but make it more quantitative.
Add emphasis on the "5M rows" and "production-ready services" from my experience.
Regenerate just the Professional Summary section.
""")
```

## Quick Workflow

```python
# Step 1: Analyze
analysis = resume_agent("Analyze job at data/job_postings/job.txt")

# Step 2: Get suggestions
suggestions = resume_agent("Suggest tailoring improvements")

# Step 3: Request specific changes
summary = resume_agent("Generate updated Professional Summary in LaTeX")

# Step 4: Iterate
refined = resume_agent("Make it more technical and add SageMaker keyword")

# Step 5: Generate full resume
full_resume = resume_agent("""
Generate complete tailored resume.
Save to: data/tailored_versions/resume_company_role.tex
""")

# Step 6: Validate
validation = resume_agent.tool.validate_latex(latex_content=full_resume)
```

## File Naming Convention

```
data/job_postings/
  ├── ml_engineer_google.txt
  ├── ai_engineer_meta.txt
  └── data_scientist_amazon.txt

data/tailored_versions/
  ├── resume_google_ml_engineer.tex
  ├── resume_meta_ai_engineer.tex
  └── resume_amazon_data_scientist.tex
```

## Common Issues & Solutions

### Issue: Agent generates code when you want suggestions

**Solution:**
```python
# Be explicit
response = resume_agent("""
Analyze the job posting. DO NOT generate LaTeX code.
Just provide suggestions and analysis.
""")
```

### Issue: Wrong LaTeX macros used

**Solution:**
```python
response = resume_agent("""
Generate Professional Summary using my EXACT template macros:
\resumeEntryS{}{content goes here}

NOT: \cventry or other formats.
""")
```

### Issue: Agent invents experience

**Solution:**
The updated prompts prevent this, but if it happens:
```python
response = resume_agent("""
IMPORTANT: Only use experiences, technologies, and achievements
that are ALREADY in my resume. Do not invent or add new ones.
""")
```

### Issue: LaTeX won't compile

**Solution:**
```python
# Use validation tool
validation = resume_agent.tool.validate_latex(latex_content=code)
print(validation)

# Ask agent to fix
fix = resume_agent("""
The LaTeX has these errors: {errors}
Fix them and regenerate.
""")
```

## Tips for Best Results

1. **Start with analysis**: Don't jump straight to code generation
2. **Be specific**: Tell the agent exactly what to emphasize
3. **Iterate**: Refine in 2-3 rounds rather than one big request
4. **Validate**: Always check LaTeX before compiling to PDF
5. **Save versions**: Keep different versions for different job types

## Direct Tool Access

```python
# Read files directly
content = resume_agent.tool.read_file(filepath="data/original/AI_engineer.tex")

# Write files directly
resume_agent.tool.write_file(filepath="data/test.tex", content=latex_code)

# Validate directly
validation = resume_agent.tool.validate_latex(latex_content=code)

# Extract keywords
keywords = resume_agent.tool.extract_keywords(text=job_posting)

# Compare versions
comparison = resume_agent.tool.compare_resumes(
    original_path="data/original/AI_engineer.tex",
    tailored_path="data/tailored_versions/resume_ml_engineer.tex"
)
```

---

**Keep this reference handy while tailoring! 📋**
