#!/usr/bin/env python3
"""
Backfill Google Sheet with Existing Resumes

Scans data/tailored_resumes/ and populates the Google Sheet with existing
job applications, using file timestamps for applied_date.

Usage:
    python scripts/backfill_sheets.py [--dry-run]

Options:
    --dry-run    Preview what would be added without actually updating the sheet
"""
import os
import sys
import re
import argparse
import logging
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.config import OUTPUT_DIR, GOOGLE_SHEETS_ENABLED
from backend.integrations.sheets_tracker import append_job_to_sheet, get_all_jobs


def extract_url_from_posting(posting_path: Path) -> str:
    """
    Extract Source URL from job posting file if present.

    Looks for line starting with "Source URL:" at the beginning of the file.
    """
    if not posting_path.exists():
        return ''

    try:
        with open(posting_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith('Source URL:'):
                    return line.replace('Source URL:', '').strip()
                # Only check first few lines
                if not line.startswith('Source') and line:
                    break
        return ''
    except Exception:
        return ''


def parse_filename(filename: str) -> dict:
    """
    Parse company and position from resume filename.

    Expected format: CompanyName_Job_Title.pdf
    Example: Affirm_Senior_Software_Engineer_Backend_Loans_Platform.pdf

    Returns:
        dict with 'company' and 'position' keys
    """
    # Remove extension
    name = Path(filename).stem

    # Remove _job_posting suffix if present (for txt files)
    if name.endswith('_job_posting'):
        name = name[:-12]

    # Split on first underscore to get company
    parts = name.split('_', 1)

    if len(parts) == 2:
        company = parts[0]
        # Replace underscores with spaces in position
        position = parts[1].replace('_', ' ')
    else:
        company = name
        position = ""

    return {
        'company': company,
        'position': position
    }


def find_existing_resumes() -> list:
    """
    Scan tailored_resumes directory and collect resume metadata.

    Returns:
        List of dicts with resume information
    """
    resumes = []
    seen_bases = set()

    if not OUTPUT_DIR.exists():
        print(f"Error: Output directory not found: {OUTPUT_DIR}")
        return []

    # Prefer PDF files, but fall back to TEX if no PDF exists
    for pdf_file in sorted(OUTPUT_DIR.glob("*.pdf")):
        base_name = pdf_file.stem
        if base_name in seen_bases:
            continue

        seen_bases.add(base_name)

        # Parse metadata from filename
        parsed = parse_filename(pdf_file.name)

        # Look for associated job posting file
        job_posting_path = OUTPUT_DIR / f"{base_name}_job_posting.txt"

        # Extract URL from job posting if available
        job_url = extract_url_from_posting(job_posting_path)

        # Get file modification time as applied_date
        file_stat = pdf_file.stat()
        applied_date = datetime.fromtimestamp(file_stat.st_mtime)

        resumes.append({
            'job_id': f"backfill-{base_name}",
            'company': parsed['company'],
            'position': parsed['position'],
            'applied_date': applied_date.isoformat(),
            'job_url': job_url,
            'resume_path': str(pdf_file.relative_to(PROJECT_ROOT)),
            'job_posting_path': str(job_posting_path.relative_to(PROJECT_ROOT)) if job_posting_path.exists() else '',
            'status': 'applied',
            'notes': 'Backfilled from existing files',
            'follow_up_date': ''
        })

    # Also check for TEX files without PDFs
    for tex_file in sorted(OUTPUT_DIR.glob("*.tex")):
        base_name = tex_file.stem
        if base_name in seen_bases:
            continue

        # Skip log files misnamed as tex (sanity check)
        if base_name.endswith('.log'):
            continue

        seen_bases.add(base_name)

        parsed = parse_filename(tex_file.name)
        job_posting_path = OUTPUT_DIR / f"{base_name}_job_posting.txt"
        job_url = extract_url_from_posting(job_posting_path)
        file_stat = tex_file.stat()
        applied_date = datetime.fromtimestamp(file_stat.st_mtime)

        resumes.append({
            'job_id': f"backfill-{base_name}",
            'company': parsed['company'],
            'position': parsed['position'],
            'applied_date': applied_date.isoformat(),
            'job_url': job_url,
            'resume_path': str(tex_file.relative_to(PROJECT_ROOT)),
            'job_posting_path': str(job_posting_path.relative_to(PROJECT_ROOT)) if job_posting_path.exists() else '',
            'status': 'applied',
            'notes': 'Backfilled from existing files (TEX only)',
            'follow_up_date': ''
        })

    return resumes


def main():
    parser = argparse.ArgumentParser(description='Backfill Google Sheet with existing resumes')
    parser.add_argument('--dry-run', action='store_true',
                        help='Preview what would be added without updating the sheet')
    parser.add_argument('--auth-code', type=str,
                        help='Google OAuth authorization code (for non-interactive use)')
    args = parser.parse_args()

    # Pass auth code to environment for sheets_tracker to use
    if args.auth_code:
        os.environ['GOOGLE_AUTH_CODE'] = args.auth_code

    # Log configuration
    from backend.config import GOOGLE_SHEETS_ENABLED, GOOGLE_SHEETS_ID, GOOGLE_SHEETS_CREDENTIALS_PATH
    logger.info(f"GOOGLE_SHEETS_ENABLED: {GOOGLE_SHEETS_ENABLED}")
    logger.info(f"GOOGLE_SHEETS_ID: {GOOGLE_SHEETS_ID[:20]}..." if GOOGLE_SHEETS_ID else "GOOGLE_SHEETS_ID: (empty)")
    logger.info(f"GOOGLE_SHEETS_CREDENTIALS_PATH: {GOOGLE_SHEETS_CREDENTIALS_PATH}")
    logger.info(f"Credentials file exists: {Path(GOOGLE_SHEETS_CREDENTIALS_PATH).exists()}")

    print("Scanning for existing resumes...")
    resumes = find_existing_resumes()

    if not resumes:
        print("No resumes found to backfill.")
        return

    print(f"Found {len(resumes)} resumes")

    if args.dry_run:
        print("\n--- DRY RUN MODE ---")
        print("The following entries would be added:\n")

        for i, resume in enumerate(resumes[:10], 1):  # Show first 10
            print(f"{i}. {resume['company']} - {resume['position']}")
            print(f"   Applied: {resume['applied_date'][:10]}")
            print(f"   Resume: {resume['resume_path']}")
            if resume['job_posting_path']:
                print(f"   Posting: {resume['job_posting_path']}")
            print()

        if len(resumes) > 10:
            print(f"... and {len(resumes) - 10} more entries")

        print("\nRun without --dry-run to actually update the sheet.")
        return

    # Check if sheets integration is enabled
    if not GOOGLE_SHEETS_ENABLED:
        print("\nError: Google Sheets integration is not enabled.")
        print("Set GOOGLE_SHEETS_ENABLED=true in your .env file")
        return

    # Get existing entries to avoid duplicates
    print("\nChecking for existing entries in sheet...")
    existing_jobs = get_all_jobs()
    existing_ids = {job.get('job_id', '') for job in existing_jobs}

    # Filter out duplicates
    new_resumes = [r for r in resumes if r['job_id'] not in existing_ids]

    if not new_resumes:
        print("All resumes already exist in the sheet. Nothing to backfill.")
        return

    print(f"Adding {len(new_resumes)} new entries (skipping {len(resumes) - len(new_resumes)} duplicates)")

    # Add entries with rate limiting (60 writes/min = 1 per second)
    import time
    success_count = 0
    for i, resume in enumerate(new_resumes):
        logger.info(f"Adding {i+1}/{len(new_resumes)}: {resume['company']} - {resume['position']}")
        result = append_job_to_sheet(resume)
        logger.info(f"Result: {result}")
        if result:
            success_count += 1
            print(f"  Added: {resume['company']} - {resume['position']}")
        else:
            print(f"  Failed: {resume['company']} - {resume['position']}")
        # Rate limit: wait 1.5 seconds between requests
        time.sleep(1.5)

    print(f"\nBackfill complete: {success_count}/{len(new_resumes)} entries added successfully")


if __name__ == '__main__':
    main()
