# Resume Tailor - Docker Image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
# - texlive-latex-base: For PDF compilation
# - texlive-fonts-recommended: Additional fonts
# - texlive-latex-extra: Extra LaTeX packages
# - texlive-fonts-extra: Additional font packages (includes fontawesome)
RUN apt-get update && apt-get install -y \
    texlive-latex-base \
    texlive-fonts-recommended \
    texlive-latex-extra \
    texlive-fonts-extra \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ ./backend/
COPY frontend/ ./frontend/
COPY tools/ ./tools/
COPY prompts/ ./prompts/

# Create necessary directories
RUN mkdir -p data/original data/job_postings data/tailored_versions logs

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/api/health')"

# Run the application
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
