"""
File: test_firebase_session_json.py
Author: RakeshMadikanti

Description:
-------------
This script validates session JSON files exported from the Adaptive Learning system (e.g., saved from Firebase).
It performs structural and data integrity checks to ensure each file is well-formed and consistent with the expected schema.

Main validation features:
- Ensures required fields exist: session_uid, user_uid, fsm_state, messages, actions, suggestions
- Verifies correct FSM state values from a predefined list
- Checks timestamp fields for valid ISO 8601 format
- Logs issues and results to timestamped logs
- Outputs a JSON report summarizing all validations
- Archives processed JSON files by timestamp

Directory structure assumed:
- tests/test_data/    → Contains input JSON session files
- tests/logs/         → Validation logs go here
- tests/reports/      → Summary reports are saved here
- tests/archive/      → Processed JSON files are moved here by run timestamp

Usage:
-------
Run from the project root:
    python src/Tools/test_firebase_session_json.py

This is part of Task 4 under User Story #399:
"Verify that Firebase session data is accurate, isolated per user, and structurally sound."
"""

import os
import json
import logging
import shutil
from pathlib import Path
from datetime import datetime

# === Setup Paths ===
BASE_DIR = Path(__file__).resolve().parents[2]
TEST_DATA_DIR = BASE_DIR / 'tests' / 'test_data'
LOGS_DIR = BASE_DIR / 'tests' / 'logs'
REPORTS_DIR = BASE_DIR / 'tests' / 'reports'
ARCHIVE_DIR = BASE_DIR / 'tests' / 'archive'

for dir_path in [TEST_DATA_DIR, LOGS_DIR, REPORTS_DIR, ARCHIVE_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_file = LOGS_DIR / f"validation_log_{timestamp}.log"
archive_run_dir = ARCHIVE_DIR / timestamp
archive_run_dir.mkdir(exist_ok=True)

# === Logger Configuration ===
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)
logger.info("********** JSON Session Validation Script Started **********")

# === Validation Rules ===
REQUIRED_FIELDS = ["session_uid", "user_uid", "fsm_state", "messages", "actions", "suggestions"]
VALID_FSM_STATES = [
    "awaiting_topic", "presenting_lesson", "awaiting_problem", "awaiting_answer",
    "verifying_answer", "writing_program", "running_code", "verifying_code",
    "updating_model", "adapting_level", "motivating"
]

# === Summary Tracking ===
summary = {
    "total_files": 0,
    "valid_files": 0,
    "invalid_files": 0,
    "files": [],
    "invalid_details": []
}

def is_valid_isoformat(timestamp: str) -> bool:
    try:
        datetime.fromisoformat(timestamp)
        return True
    except Exception:
        return False

def validate_json_file(filepath):
    file_result = {
        "file": filepath.name,
        "status": "valid"
    }

    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
    except Exception as e:
        logger.error(f">>>>>>>>>>>>> Failed to parse JSON: {filepath} | Error: {e} <<<<<<<<<<<<<<")
        summary["invalid_files"] += 1
        summary["invalid_details"].append({"file": filepath.name, "error": f"JSON Parse Error: {str(e)}"})
        file_result["status"] = "invalid"
        summary["files"].append(file_result)
        return

    # Check Required Fields
    missing = [field for field in REQUIRED_FIELDS if field not in data]
    if missing:
        msg = f"Missing fields: {missing}"
        logger.warning(f"xxxxxxxxxxxx {msg} in {filepath.name} xxxxxxxxxxxxxx")
        summary["invalid_files"] += 1
        summary["invalid_details"].append({"file": filepath.name, "error": msg})
        file_result["status"] = "invalid"
        summary["files"].append(file_result)
        return

    # FSM Validation
    if data["fsm_state"] not in VALID_FSM_STATES:
        logger.warning(f"⚠️ Invalid FSM state: {data['fsm_state']} in {filepath.name}")

    # Validate Steps Completed
    for i, step in enumerate(data.get("steps_completed", [])):
        if "description" not in step or "completed_at" not in step:
            logger.warning(f"⚠️ Step {i} missing fields in {filepath.name}")
        elif not is_valid_isoformat(step["completed_at"]):
            logger.warning(f"⚠️ Step {i} has invalid timestamp format in {filepath.name}")

    # Validate Suggestions
    for i, sug in enumerate(data.get("suggestions", [])):
        valid_styles = [
            all(k in sug for k in ("agent", "content")),
            all(k in sug for k in ("topic", "confidence")),
            all(k in sug for k in ("text", "created_at", "suggestion_id", "agent"))
        ]
        if not any(valid_styles):
            logger.warning(
                f"⚠️ Suggestion {i} in {filepath.name} is invalid. Present keys: {list(sug.keys())}"
            )

    summary["valid_files"] += 1
    summary["files"].append(file_result)
    logger.info(f"********** Validated: {filepath.name} **********")

# === Process Files ===
json_files = list(TEST_DATA_DIR.glob("*.json"))
summary["total_files"] = len(json_files)

if not json_files:
    logger.warning("xxxxxxxxxxxx No JSON files found in test_data directory. xxxxxxxxxxxx")

for json_file in json_files:
    validate_json_file(json_file)
    shutil.move(json_file, archive_run_dir / json_file.name)

# === Save Report ===
report_path = REPORTS_DIR / f"validation_report_{timestamp}.json"
with open(report_path, "w") as rf:
    json.dump(summary, rf, indent=4)

logger.info(f"********** Validation complete. Report saved to {report_path.name} **********")
logger.info("********** Script Finished **********")

print(f"Validation complete.\n- Log: {log_file}\n- Report: {report_path}")
