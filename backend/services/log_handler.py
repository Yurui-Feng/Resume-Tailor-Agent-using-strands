"""
Custom logging handler to capture logs for specific jobs.
"""

import logging
from datetime import datetime
from typing import List, Dict


class LogCaptureHandler(logging.Handler):
    """Captures log messages for a specific job"""

    def __init__(self, job_id: str, logs_store: Dict[str, List[dict]]):
        """
        Initialize the log capture handler.

        Args:
            job_id: The job ID to capture logs for
            logs_store: Shared dictionary to store logs for all jobs
        """
        super().__init__()
        self.job_id = job_id
        self.logs_store = logs_store

        # Initialize log list for this job
        if job_id not in self.logs_store:
            self.logs_store[job_id] = []

    def emit(self, record: logging.LogRecord):
        """
        Capture and store log record.

        Args:
            record: The logging record to capture
        """
        try:
            message = record.getMessage()

            # Filter out unwanted debug logs
            skip_patterns = [
                "HTTP Request:",
                "HTTP/1.1 200 OK",
                "Creating Strands MetricsClient",
                "api.openai.com",
                "Retrying request",
                "Connection pool"
            ]

            # Skip if message contains any unwanted patterns
            if any(pattern in message for pattern in skip_patterns):
                return

            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "level": record.levelname,
                "message": message
            }

            self.logs_store[self.job_id].append(log_entry)

            # Limit to last 100 logs to prevent memory issues
            if len(self.logs_store[self.job_id]) > 100:
                self.logs_store[self.job_id].pop(0)

        except Exception:
            # Don't raise exceptions in logging handler
            self.handleError(record)
