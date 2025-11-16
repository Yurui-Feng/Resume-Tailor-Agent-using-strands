# Resume Tailor Agent

An intelligent AI agent built with [Strands Agents SDK](https://strandsagents.com) that tailors your LaTeX resume to specific job postings while preserving formatting and maintaining accuracy.

## Features

🎯 **Job-Focused Tailoring**
- Analyzes job postings to extract key requirements
- Matches your experience to job needs
- Emphasizes relevant skills and projects
- Incorporates keywords naturally for ATS optimization

📝 **LaTeX-Safe Processing**
- Preserves all LaTeX formatting and syntax
- Validates output before saving
- Supports all major LaTeX resume templates (moderncv, res.cls, custom)
- Never breaks document structure

🔄 **Iterative Refinement**
- Supports multiple revision rounds
- Conversational interface for feedback
- Tracks context across iterations
- Suggests improvements before applying

🛠️ **Custom Tools**
- File reading/writing
- LaTeX validation
- Keyword extraction
- Job requirement analysis
- Resume comparison

---

## Quick Start

### Prerequisites

- Python 3.10+
- API credentials (OpenAI or AWS Bedrock)
- A LaTeX resume file

### Installation

```bash
# Activate virtual environment
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux

# All dependencies are already installed!
```

### Configuration

Choose your AI provider and configure credentials in `.env` file:

#### Option 1: OpenAI (Easiest to get started)

```bash
OPENAI_API_KEY=sk-your-openai-key-here
```

Get your API key from: https://platform.openai.com/api-keys

#### Option 2: AWS Bedrock (Production-ready)

```bash
# Using long-term API key (recommended)
AWS_BEARER_TOKEN_BEDROCK=your-long-term-api-key
AWS_REGION=us-east-1

# OR using standard AWS credentials
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1
```

**For Bedrock**, make sure you have:
1. A long-term Bedrock API key (not short-term)
2. Model access enabled for Claude 4 in AWS Bedrock console
3. Appropriate region (us-east-1 or us-west-2)

The notebook will automatically detect which credentials are available and use the appropriate provider.

### Usage

1. **Add your resume**: Place your LaTeX resume in `data/original/resume.tex`
2. **Add job postings**: Save job postings as `.txt` files in `data/job_postings/`
3. **Open the notebook**: `jupyter notebook resume_tailor.ipynb`
4. **Run the cells** and start tailoring!

---

## Project Structure

```
resume-tailor-agent/
├── .venv/                      # Virtual environment
├── .env                        # AWS credentials (keep private!)
├── prompts/
│   ├── system_prompt.txt      # Agent instructions
│   └── latex_rules.txt        # LaTeX preservation rules
├── tools/
│   └── resume_tools.py        # Custom tools for resume processing
├── data/
│   ├── original/              # Your original resume(s)
│   ├── job_postings/          # Job posting files
│   ├── tailored_versions/     # Generated tailored resumes
│   └── README.md              # Data organization guide
├── resume_tailor.ipynb        # Main Jupyter notebook
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

---

## How It Works

### 1. Job Analysis
The agent reads the job posting and extracts:
- Required skills and technologies
- Preferred qualifications
- Years of experience needed
- Keywords and industry terms

### 2. Resume Tailoring
The agent then:
- Highlights relevant experience
- Reorders sections for impact
- Incorporates job-specific keywords
- Adjusts bullet points for relevance
- Maintains your professional voice

### 3. LaTeX Preservation
Throughout the process:
- All LaTeX syntax is preserved
- Document structure remains intact
- Custom commands are maintained
- Output is validated before saving

### 4. Iterative Refinement
You can:
- Request specific changes
- Emphasize certain experiences
- Adjust tone or focus
- Generate multiple versions

---

## Example Workflow

```python
# In resume_tailor.ipynb

# 1. Create the agent (already configured in notebook)
resume_agent = Agent(model=bedrock_model, system_prompt=full_prompt, tools=[...])

# 2. Analyze a job posting
analysis = resume_agent("""
Read the job posting from 'data/job_postings/ml_engineer.txt'
and extract key requirements.
""")

# 3. Request tailoring
tailored = resume_agent("""
Tailor my resume from 'data/original/resume.tex' for this job.
Focus on:
- ML and Python experience
- AWS cloud projects
- Leadership roles

Save to 'data/tailored_versions/resume_ml_engineer.tex'
""")

# 4. Iterate and refine
refinement = resume_agent("""
Make the first experience section more quantitative.
Add metrics for impact.
""")

# 5. Validate
validation = resume_agent("Validate the LaTeX syntax in the tailored resume")
```

---

## Customization

### Modify Agent Behavior

Edit the system prompts to change how the agent works:

**`prompts/system_prompt.txt`** - Core agent instructions
**`prompts/latex_rules.txt`** - LaTeX handling rules

### Add Custom Tools

Add new tools in `tools/resume_tools.py`:

```python
from strands import tool

@tool
def my_custom_tool(param: str) -> str:
    """Tool description."""
    # Your logic here
    return result
```

---

## Tips for Best Results

### Job Posting Quality
- Include complete job descriptions
- Keep original formatting/structure
- Include both requirements and nice-to-haves
- Save as plain .txt files

### Resume Preparation
- Start with a well-formatted LaTeX resume
- Keep your original resume comprehensive
- Include quantitative achievements
- Use standard section names

### Tailoring Strategy
1. **Start with analysis** - Let the agent analyze before tailoring
2. **Be specific** - Tell the agent what to emphasize
3. **Iterate** - Do 2-3 rounds of refinement
4. **Validate** - Always check LaTeX compiles
5. **Track versions** - Keep notes on which version sent where

---

## Troubleshooting

### Agent Connection Issues

**Problem**: `ModelThrottledException` or quota errors (OpenAI)

**Solutions**:
1. Check your OpenAI usage: https://platform.openai.com/usage
2. Verify you have credits/billing configured
3. Consider switching to AWS Bedrock (see Configuration section)

**Problem**: Authentication errors (Bedrock)

**Solutions**:
1. Check `AWS_BEARER_TOKEN_BEDROCK` is set correctly
2. Use a **long-term** API key (not short-term)
3. Enable model access in Bedrock console
4. Verify your region is correct (us-east-1 or us-west-2)

### LaTeX Validation Errors

**Problem**: Generated resume won't compile

**Solutions**:
1. Run validation: `resume_agent.tool.validate_latex(content)`
2. Check error messages
3. Compare with original structure
4. Ask agent to fix specific issues

### File Path Issues

**Problem**: Agent can't find files

**Solutions**:
1. Use relative paths: `data/original/resume.tex`
2. Verify file exists
3. Check file permissions

---

## Advanced Features

### Batch Processing

```python
results = batch_tailor(
    resume_path="data/original/resume.tex",
    job_folder="data/job_postings",
    output_folder="data/tailored_versions"
)
```

### Resume Comparison

```python
comparison = resume_agent.tool.compare_resumes(
    original_path="data/original/resume.tex",
    tailored_path="data/tailored_versions/resume_ml_engineer.tex"
)
```

### Keyword Analysis

```python
keywords = resume_agent.tool.extract_keywords(job_text)
```

---

## Security & Privacy

⚠️ **Never commit sensitive information**:

1. `.env` file (API keys)
2. Resume files
3. Job postings

The `.gitignore` is already configured to exclude these!

---

## Resources

### Strands Agents SDK
- **Docs**: https://strandsagents.com
- **GitHub**: https://github.com/strands-agents/sdk-python

### AWS Bedrock
- **API Keys**: https://docs.aws.amazon.com/bedrock/latest/userguide/getting-started-api-keys.html
- **Pricing**: https://aws.amazon.com/bedrock/pricing/

---

## License

Apache 2.0 (via Strands Agents SDK)

Your resume content remains your own!

---

**Happy job hunting! 🎯📄✨**

*Transform your resume for every opportunity while keeping your LaTeX formatting perfect.*

---

## About Strands Agents SDK

This project is built with Strands Agents, an open-source Python SDK by AWS for building AI agents. For more information about Strands, see `README_old.md` or visit https://strandsagents.com
