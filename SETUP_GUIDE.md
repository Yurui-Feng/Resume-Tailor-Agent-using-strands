# Setup Guide - Resume Tailor Agent

Quick start guide for getting your Resume Tailor Agent running with OpenAI.

## Current Status

✅ Virtual environment created
✅ All packages installed
✅ Project structure ready
✅ OpenAI API key detected (in .env file)

## Next Steps

### 1. Verify Your .env File

Your `.env` file should contain:

```bash
OPENAI_API_KEY=sk-...your-key...
```

### 2. Start Jupyter Notebook

```bash
# Make sure you're in the project directory
cd d:\Strands-agent

# Activate virtual environment
.venv\Scripts\activate

# Launch Jupyter
jupyter notebook resume_tailor.ipynb
```

### 3. Run the Notebook Cells

When you open `resume_tailor.ipynb`, run the cells in order:

1. **API Provider Configuration** (markdown) - Read this
2. **Setup** (markdown) - Read this
3. **Import libraries** - Run this cell
4. **Configuration** - Run this cell
   - Should show: ✅ OpenAI API key found
   - Provider: openai
   - Model: gpt-4o

5. **Load System Prompts** - Run this cell
6. **Custom Tools** - Run this cell
7. **Create Agent** - Run this cell
   - Should show: ✅ Resume Tailor Agent created!

8. **Test Connection** - Run the example cell:
   ```python
   response = resume_agent("Hello! Can you help me tailor my resume?")
   print(response)
   ```

If you see a response, you're all set! 🎉

## Adding Your Resume

1. Create your LaTeX resume file
2. Save it as: `data/original/resume.tex`
3. Add job postings as `.txt` files in: `data/job_postings/`

## Model Options

The notebook uses **GPT-4o** by default with OpenAI. If you want to change the model:

1. Edit the configuration cell in the notebook
2. Change `MODEL_ID` to one of:
   - `gpt-4o` (default, fastest GPT-4)
   - `gpt-4-turbo` (good balance)
   - `gpt-4` (most capable, slower)
   - `gpt-3.5-turbo` (faster, cheaper, less capable)

Example:
```python
if has_openai:
    print("✅ OpenAI API key found")
    MODEL_PROVIDER = "openai"
    MODEL_ID = "gpt-4-turbo"  # Change this line
```

## Switching to AWS Bedrock Later

If you want to switch to AWS Bedrock (for Claude models):

1. Get a long-term Bedrock API key
2. Add to `.env`:
   ```bash
   AWS_BEARER_TOKEN_BEDROCK=your-bedrock-key
   AWS_REGION=us-east-1
   ```
3. Comment out or remove `OPENAI_API_KEY` from `.env`
4. Restart the notebook kernel

The notebook will automatically detect and use Bedrock.

## Cost Considerations

### OpenAI Pricing (approximate)
- GPT-4o: $2.50 / 1M input tokens, $10 / 1M output tokens
- GPT-4-turbo: $10 / 1M input tokens, $30 / 1M output tokens
- GPT-3.5-turbo: $0.50 / 1M input tokens, $1.50 / 1M output tokens

**Typical resume tailoring**: ~5,000-10,000 tokens per job
**Estimated cost**: $0.05 - $0.30 per resume with GPT-4o

### AWS Bedrock Pricing (approximate)
- Claude Sonnet: $3 / 1M input tokens, $15 / 1M output tokens

Check current pricing:
- OpenAI: https://openai.com/pricing
- AWS Bedrock: https://aws.amazon.com/bedrock/pricing/

## Troubleshooting

### "No API credentials found"
- Check that `.env` file exists in project root
- Verify `OPENAI_API_KEY` is set correctly
- Try restarting the notebook kernel

### OpenAI quota exceeded
- Check usage: https://platform.openai.com/usage
- Add billing: https://platform.openai.com/account/billing
- Or switch to AWS Bedrock

### Import errors
- Make sure virtual environment is activated: `.venv\Scripts\activate`
- Check all packages installed: `pip list | grep strands`

### LaTeX errors
- Use the `validate_latex()` tool to check syntax
- Compare with your original resume structure
- Ask the agent to fix specific validation errors

## Tips for Best Results

1. **Start with analysis**: Don't generate the full resume immediately
2. **Iterate**: Run 2-3 rounds of refinement
3. **Be specific**: Tell the agent exactly what to emphasize
4. **Validate**: Always check LaTeX compiles before sending
5. **Track versions**: Name outputs clearly (e.g., `resume_google_swe.tex`)

## Example First Run

```python
# After creating the agent, try this:

# 1. Save a job posting
job_text = """
Software Engineer - Python
Requirements:
- 3+ years Python
- Experience with AWS
- Strong problem-solving skills
"""

with open("data/job_postings/test_job.txt", "w") as f:
    f.write(job_text)

# 2. Ask agent to analyze it
response = resume_agent("""
Read and analyze the job posting at data/job_postings/test_job.txt.
What are the key requirements?
""")
print(response)
```

## Need Help?

- Check the main [README.md](README.md) for detailed documentation
- Review [data/README.md](data/README.md) for file organization
- See example workflows in the notebook
- Troubleshooting section in README

---

**You're all set! Open the notebook and start tailoring! 🚀**
