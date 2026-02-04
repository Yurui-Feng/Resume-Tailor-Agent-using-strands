"""
Google Sheets Job Application Tracker

Tracks job applications in a Google Sheet for integration with moltbot.
Supports OAuth 2.0 authentication (opens browser once, stores refresh token).
"""
import logging
from pathlib import Path
from typing import Optional

from backend.config import (
    GOOGLE_SHEETS_ENABLED,
    GOOGLE_SHEETS_ID,
    GOOGLE_SHEETS_CREDENTIALS_PATH,
    PROJECT_ROOT,
)

logger = logging.getLogger(__name__)

# Google API imports (lazy load to avoid import errors when disabled)
_sheets_service = None
_headers_verified = False  # Cache header check

# Scopes required for Sheets access
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# Token storage path (alongside credentials)
TOKEN_PATH = PROJECT_ROOT / "credentials" / "sheets_token.json"


def _get_sheets_service():
    """
    Get authenticated Google Sheets service (cached).

    Uses OAuth 2.0 flow:
    - First run: Opens browser for authorization
    - Subsequent runs: Uses stored refresh token

    Returns:
        Google Sheets API service object

    Raises:
        ImportError: If google packages are not installed
        FileNotFoundError: If credentials file doesn't exist
        Exception: If authentication fails
    """
    global _sheets_service

    if _sheets_service is not None:
        return _sheets_service

    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build

    creds = None
    creds_path = Path(GOOGLE_SHEETS_CREDENTIALS_PATH)
    token_path = Path(TOKEN_PATH)

    # Check for existing token
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    # If no valid credentials, run OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # Refresh expired token
            creds.refresh(Request())
            logger.info("Refreshed Google Sheets token")
        else:
            # Run full OAuth flow
            if not creds_path.exists():
                raise FileNotFoundError(
                    f"Google OAuth credentials not found: {creds_path}\n\n"
                    "Setup instructions:\n"
                    "1. Go to Google Cloud Console → APIs & Services → Credentials\n"
                    "2. Create OAuth 2.0 Client ID (Desktop app type)\n"
                    "3. Download JSON and save to: {creds_path}\n"
                    "4. Run again - browser will open for authorization"
                )

            from google_auth_oauthlib.flow import Flow
            import os

            # Use localhost redirect - user copies code from URL
            redirect_uri = 'http://localhost:8085/'
            flow = Flow.from_client_secrets_file(
                str(creds_path),
                scopes=SCOPES,
                redirect_uri=redirect_uri
            )

            auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')

            # Check if auth code was provided via environment
            code = os.environ.get('GOOGLE_AUTH_CODE', '').strip()

            if not code:
                print("\n" + "="*70)
                print("1. Visit this URL to authorize:")
                print()
                print(auth_url)
                print()
                print("2. After authorizing, you'll be redirected to localhost (it will fail)")
                print("3. Copy the 'code' parameter from the URL bar:")
                print("   http://localhost:8085/?code=XXXXX&scope=...")
                print("                              ^^^^^ copy this part")
                print("="*70)
                code = input("Paste the code here: ").strip()

            flow.fetch_token(code=code)
            creds = flow.credentials
            logger.info("Completed Google Sheets OAuth authorization")

        # Save token for next run
        token_path.parent.mkdir(parents=True, exist_ok=True)
        with open(token_path, 'w') as token_file:
            token_file.write(creds.to_json())
        logger.info(f"Saved Google Sheets token to {token_path}")

    _sheets_service = build('sheets', 'v4', credentials=creds)
    logger.info("Google Sheets service authenticated successfully")

    return _sheets_service


def _ensure_headers_exist():
    """
    Ensure the sheet has the correct header row.
    Creates headers if the sheet is empty.
    Only checks once per session (cached).
    """
    global _headers_verified

    if _headers_verified:
        return

    service = _get_sheets_service()

    # Define expected headers
    headers = [
        'job_id',
        'company',
        'position',
        'applied_date',
        'job_url',
        'resume_path',
        'job_posting_path',
        'status',
        'notes',
        'follow_up_date'
    ]

    # Check if first row exists
    result = service.spreadsheets().values().get(
        spreadsheetId=GOOGLE_SHEETS_ID,
        range='A1:J1'
    ).execute()

    existing_values = result.get('values', [])

    if not existing_values or existing_values[0] != headers:
        # Write headers
        service.spreadsheets().values().update(
            spreadsheetId=GOOGLE_SHEETS_ID,
            range='A1:J1',
            valueInputOption='RAW',
            body={'values': [headers]}
        ).execute()
        logger.info("Created/updated header row in Google Sheet")

    _headers_verified = True


def append_job_to_sheet(job_data: dict) -> Optional[dict]:
    """
    Append a job application to the Google Sheet.

    Args:
        job_data: Dictionary with keys:
            - job_id: Unique identifier
            - company: Company name
            - position: Job title
            - applied_date: ISO timestamp
            - job_url: Source URL
            - resume_path: Path to tailored resume PDF
            - job_posting_path: Path to job posting text file
            - status: Application status (default: "applied")
            - notes: Free-form notes (default: "")
            - follow_up_date: Follow-up date (default: "")

    Returns:
        API response dict on success, None on failure

    Note:
        This function is designed to be non-fatal - it catches and logs
        exceptions rather than raising them to avoid disrupting the
        resume tailoring workflow.
    """
    if not GOOGLE_SHEETS_ENABLED:
        logger.debug("Google Sheets tracking disabled, skipping")
        return None

    try:
        service = _get_sheets_service()

        # Ensure headers exist on first call
        _ensure_headers_exist()

        # Prepare row data in column order
        row = [
            job_data.get('job_id', ''),
            job_data.get('company', ''),
            job_data.get('position', ''),
            job_data.get('applied_date', ''),
            job_data.get('job_url', ''),
            job_data.get('resume_path', ''),
            job_data.get('job_posting_path', ''),
            job_data.get('status', 'applied'),
            job_data.get('notes', ''),
            job_data.get('follow_up_date', ''),
        ]

        # Append row to sheet
        result = service.spreadsheets().values().append(
            spreadsheetId=GOOGLE_SHEETS_ID,
            range='A:J',
            valueInputOption='USER_ENTERED',
            insertDataOption='INSERT_ROWS',
            body={'values': [row]}
        ).execute()

        logger.info(f"Added job application to Google Sheet: {job_data.get('company')} - {job_data.get('position')}")
        return result

    except ImportError as e:
        logger.warning(
            f"Google Sheets API packages not installed: {e}\n"
            "Install with: pip install google-api-python-client google-auth google-auth-oauthlib"
        )
        return None

    except Exception as e:
        logger.warning(f"Failed to update Google Sheet (non-fatal): {e}")
        return None


def sort_sheet_by_date_descending() -> bool:
    """
    Sort the sheet by applied_date column in descending order (newest first).

    Returns:
        True on success, False on failure
    """
    if not GOOGLE_SHEETS_ENABLED:
        return False

    try:
        service = _get_sheets_service()

        # Get sheet ID (not spreadsheet ID)
        sheet_metadata = service.spreadsheets().get(
            spreadsheetId=GOOGLE_SHEETS_ID
        ).execute()
        sheet_id = sheet_metadata['sheets'][0]['properties']['sheetId']

        # Sort by column D (applied_date, index 3) descending, skip header row
        request = {
            'requests': [{
                'sortRange': {
                    'range': {
                        'sheetId': sheet_id,
                        'startRowIndex': 1,  # Skip header
                        'startColumnIndex': 0,
                        'endColumnIndex': 10
                    },
                    'sortSpecs': [{
                        'dimensionIndex': 3,  # Column D (applied_date)
                        'sortOrder': 'DESCENDING'
                    }]
                }
            }]
        }

        service.spreadsheets().batchUpdate(
            spreadsheetId=GOOGLE_SHEETS_ID,
            body=request
        ).execute()

        logger.info("Sorted sheet by applied_date (newest first)")
        return True

    except Exception as e:
        logger.warning(f"Failed to sort sheet: {e}")
        return False


def update_job_in_sheet(job_id: str, updates: dict) -> bool:
    """
    Update an existing job entry in the sheet.

    Args:
        job_id: The job_id to find and update
        updates: Dict of column names to new values

    Returns:
        True on success, False on failure
    """
    if not GOOGLE_SHEETS_ENABLED:
        return False

    try:
        service = _get_sheets_service()

        # Get all data to find the row
        result = service.spreadsheets().values().get(
            spreadsheetId=GOOGLE_SHEETS_ID,
            range='A:J'
        ).execute()

        rows = result.get('values', [])
        if len(rows) < 2:
            return False

        headers = rows[0]

        # Find the row with matching job_id
        job_id_col = headers.index('job_id') if 'job_id' in headers else 0
        row_index = None

        for i, row in enumerate(rows[1:], start=2):  # Start at 2 (1-indexed, skip header)
            if len(row) > job_id_col and row[job_id_col] == job_id:
                row_index = i
                break

        if row_index is None:
            logger.warning(f"Job {job_id} not found in sheet")
            return False

        # Update specific cells
        for col_name, value in updates.items():
            if col_name in headers:
                col_index = headers.index(col_name)
                col_letter = chr(ord('A') + col_index)
                cell_range = f'{col_letter}{row_index}'

                service.spreadsheets().values().update(
                    spreadsheetId=GOOGLE_SHEETS_ID,
                    range=cell_range,
                    valueInputOption='USER_ENTERED',
                    body={'values': [[value]]}
                ).execute()

        logger.info(f"Updated job {job_id} in sheet")
        return True

    except Exception as e:
        logger.warning(f"Failed to update job in sheet: {e}")
        return False


def get_all_jobs() -> list:
    """
    Retrieve all job applications from the sheet.

    Returns:
        List of dicts with job data, or empty list on failure
    """
    if not GOOGLE_SHEETS_ENABLED:
        return []

    try:
        service = _get_sheets_service()

        result = service.spreadsheets().values().get(
            spreadsheetId=GOOGLE_SHEETS_ID,
            range='A:J'
        ).execute()

        rows = result.get('values', [])
        if len(rows) < 2:
            return []

        headers = rows[0]
        jobs = []

        for row in rows[1:]:
            # Pad row to match headers length
            padded_row = row + [''] * (len(headers) - len(row))
            jobs.append(dict(zip(headers, padded_row)))

        return jobs

    except Exception as e:
        logger.warning(f"Failed to read from Google Sheet: {e}")
        return []
