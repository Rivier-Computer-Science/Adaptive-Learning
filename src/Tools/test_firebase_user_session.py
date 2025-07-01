"""
File: test_firebase_user_session.py
Author: RakeshMadikanti

Description:
-------------
This script connects to Firestore and validates all session documents under each user UID.

Each session is checked for:
- Required field presence
- Valid FSM state (using a known whitelist)
- Proper format for messages (list) and suggestions (list of dicts)

Each session is checked for structure consistency, including presence of required fields,
valid FSM state, and suggestions format.

Incase of any changes in the fsm state in future, the script can be easily updated
to include new states or modify validation rules.

Features:
- Retrieves all user UIDs from `/users/`
- Validates all sessions under `/users/<uid>/sessions/`
- Flags sessions missing any required fields or invalid structure
- Logs issues with detailed messages
- Grouped summary report: shows session status grouped under each user
- Supports saving sessions as local JSON via --save-json flag and saves them in an archive directory
- Saves logs and reports in dedicated directories with timestamps

Usage:
-------
    python src/Tools/test_firebase_user_session.py - to validate all users and their sessions
    python src/Tools/test_firebase_user_session.py --save-json - to save session JSONs for all users
    python src/Tools/test_firebase_user_session.py --user=<user_uid> --save-json - to validate a specific user and save their session JSONs
    
This is part of Task 4 under User Story #399:
"Verify that Firebase session data is accurate, isolated per user, and structurally sound."

"""

import os
import json
import logging
import argparse
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore

# === Setup Firebase ===
load_dotenv()
SERVICE_ACCOUNT_KEY_PATH = os.getenv('FIREBASE_SERVICE_ACCOUNT_KEY_PATH')
if not SERVICE_ACCOUNT_KEY_PATH:
    raise ValueError("Missing FIREBASE_SERVICE_ACCOUNT_KEY_PATH")

if not firebase_admin._apps:
    cred = credentials.Certificate(SERVICE_ACCOUNT_KEY_PATH)
    firebase_admin.initialize_app(cred)
db = firestore.client()

# === CLI Arguments ===
parser = argparse.ArgumentParser(description="Validate Firebase user session documents")
parser.add_argument("--user", help="Only validate a specific user UID")
parser.add_argument("--save-json", action="store_true", help="Save downloaded session JSONs to archive")
args = parser.parse_args()

# === Directory Setup ===
BASE_DIR = Path(__file__).resolve().parents[2]
LOGS_DIR = BASE_DIR / 'tests' / 'logs'
REPORTS_DIR = BASE_DIR / 'tests' / 'reports'
ARCHIVE_DIR = BASE_DIR / 'tests' / 'archive'
for path in [LOGS_DIR, REPORTS_DIR, ARCHIVE_DIR]:
    path.mkdir(parents=True, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_file = LOGS_DIR / f"validation_log_{timestamp}.log"
report_file = REPORTS_DIR / f"validation_report_{timestamp}.json"
archive_run_dir = ARCHIVE_DIR / timestamp
archive_run_dir.mkdir(parents=True, exist_ok=True)

# === Logger Setup ===
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
print(f"**** SCRIPT START ****")
logger.info("Firebase Users Session Validation Script Started")

# === Validation Rules ===
REQUIRED_FIELDS = ["session_uid", "user_uid", "fsm_state", "messages", "actions", "suggestions"]
VALID_FSM_STATES = [
    "awaiting_topic", "presenting_lesson", "awaiting_problem", "awaiting_answer",
    "verifying_answer", "writing_program", "running_code", "verifying_code",
    "updating_model", "adapting_level", "motivating"
]

# === Grouped Summary Format ===
summary = {
    "timestamp": timestamp,
    "stats": {
        "total_users": 0,
        "users_with_sessions": 0,
        "users_without_sessions": 0,
        "total_sessions": 0,
        "valid_sessions": 0,
        "invalid_sessions": 0,
        "users_with_invalid_sessions": []
    },
    "users": {}
}

def validate_session(data, session_id):
    errors = []
    fields_status = {}

    # Check all required fields
    for field in REQUIRED_FIELDS:
        if field not in data:
            fields_status[field] = "Missing"
            errors.append(f"Missing field: {field}")
        else:
            fields_status[field] = "OK"

    # FSM state content validation
    if "fsm_state" not in data:
        fields_status["fsm_state_validity"] = "Invalid (fsm_state field is missing)"
    elif data["fsm_state"] in [None, "", " "]:
        fields_status["fsm_state_validity"] = "Invalid (Missing fsm field value)"
    elif data["fsm_state"] not in VALID_FSM_STATES:
        fields_status["fsm_state_validity"] = f"Invalid (Unrecognized FSM state: {data['fsm_state']})"
        errors.append(f"Invalid FSM state: {data['fsm_state']}")
    else:
        fields_status["fsm_state_validity"] = "Valid"

    # messages field must be a list
    if "messages" in data and not isinstance(data["messages"], list):
        fields_status["messages_type"] = "Invalid (not a list)"
        errors.append("messages must be a list")
    else:
        fields_status["messages_type"] = "Valid"

    # suggestions field must be a list of dicts with valid structure
    if "suggestions" in data:
        is_valid = True
        if not isinstance(data["suggestions"], list):
            is_valid = False
        else:
            for i, sug in enumerate(data["suggestions"]):
                if not isinstance(sug, dict):
                    is_valid = False
                    break
                valid = (
                    all(k in sug for k in ("agent", "content")) or
                    all(k in sug for k in ("topic", "confidence")) or
                    all(k in sug for k in ("text", "created_at", "suggestion_id", "agent"))
                )
                if not valid:
                    errors.append(f"Suggestion {i} has invalid format")
                    is_valid = False
        fields_status["suggestions_format"] = "Valid" if is_valid else "Invalid (bad format)"
    else:
        fields_status["suggestions_format"] = "Valid"

    return {
        "session_id": session_id,
        "status": "valid" if not errors else "invalid",
        "fields_status": fields_status,
        "errors": errors if errors else None
    }

def process_user_sessions(user_uid):
    logger.info(f"👤 Processing user: {user_uid}")
    user_sessions = []

    sessions_ref = db.collection("users").document(user_uid).collection("sessions")
    sessions = list(sessions_ref.stream())

    if not sessions:
        summary["stats"]["users_without_sessions"] += 1
        summary["users"][user_uid] = {"note": "No session data found for this user"}
        logger.info(f"------- 0 sessions validated for {user_uid} -------")
        return

    summary["stats"]["users_with_sessions"] += 1
    user_dir = archive_run_dir / user_uid
    if args.save_json:
        user_dir.mkdir(parents=True, exist_ok=True)

    for doc in sessions:
        session_id = doc.id
        data = doc.to_dict()

        if args.save_json:
            with open(user_dir / f"{session_id}.json", "w") as f:
                json.dump(data, f, indent=2)

        result = validate_session(data, session_id)
        user_sessions.append(result)

        if result["status"] == "valid":
            logger.info(f"{user_uid}/{session_id} validated")
        else:
            logger.warning(f"{user_uid}/{session_id} - Errors: {result['errors']}")

    total = len(user_sessions)
    invalid = sum(1 for s in user_sessions if s["status"] == "invalid")
    valid = total - invalid

    if invalid > 0:
        summary["stats"]["users_with_invalid_sessions"].append(user_uid)

    summary["stats"]["total_sessions"] += total
    summary["stats"]["valid_sessions"] += valid
    summary["stats"]["invalid_sessions"] += invalid

    summary["users"][user_uid] = {
        "total_sessions": total,
        "sessions": user_sessions
    }
    logger.info(f"{total} sessions validated for {user_uid}")

# === Run Validation ===
if args.user:
    summary["stats"]["total_users"] = 1
    process_user_sessions(args.user)
else:
    all_users = list(db.collection("users").stream())
    summary["stats"]["total_users"] = len(all_users)
    for doc in all_users:
        process_user_sessions(doc.id)

# === Write Report ===
with open(report_file, "w") as f:
    json.dump(summary, f, indent=2)

logger.info("Script validation complete.")
logger.info(f"📄 Summary Report: {report_file.name}")
print(f"Validation complete.\n📄 Summary Report: {report_file}\n🪵 Log: {log_file}")
print(f"**** SCRIPT END ****")
