"""
export.py

This module provides file export functionality for chat session history
in the Adaptive Learning platform. It supports exporting chat data
in multiple user-friendly formats: JSON, CSV, TXT, and PDF.

Exports include chat messages (with timestamp, role, and content)
and can optionally include the current topic/tab name for context.

Main Features:
- Handles missing fields gracefully (e.g., missing timestamps).
- Logs missing/invalid data fields for debugging and auditability.
- Supports both simple lists of message dicts and custom message objects.
- Designed to integrate with Panel UI's FileDownload widget for user-driven export.

Exported File Format Details:
- JSON: List of message dicts or dict with "topic" and "messages".
- CSV: Rows with columns for topic, timestamp, role, content.
- TXT: Readable log lines with topic header if available.
- PDF: Transcript-style PDF using ReportLab, with optional topic header.

Typical Usage:
    content, filename = get_export_data(
        chat_history, 
        format_type="csv", 
        topic=current_topic
    )

Module Functions:
- get_export_data(...): Main routing function to select export type.
- export_to_json(...), export_to_csv(...), export_to_txt(...), export_to_pdf(...): Format-specific exporters.

Dependencies:
- reportlab (for PDF export)

Author: Rakesh Madikanti(SU25)
Issue Link: https://github.com/Rivier-Computer-Science/Adaptive-Learning/issues/460 (Linked to issue #399)
"""


# import json
# import csv
# from io import StringIO, BytesIO
# from datetime import datetime
# import os, csv
# import panel as pn, tempfile
# from weasyprint import HTML

# from reportlab.lib.pagesizes import letter
# from reportlab.lib.styles import getSampleStyleSheet
# from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

# import tempfile
# import panel as pn
# from weasyprint import HTML
# import logging
# from panel.io.save import save

# from reportlab.lib.pagesizes import letter
# from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
# from reportlab.lib.styles import getSampleStyleSheet
# from io import BytesIO

# logger = logging.getLogger(__name__)

# """
# export.py

# This module provides export functionality for chat session history
# in multiple formats: JSON, CSV, TXT, and PDF.

# Each export function takes in structured chat data and returns
# the serialized file content in the requested format.

# The main entry point is `get_export_data()`, which routes to the
# appropriate format-specific exporter.

# Expected chat history input format:
# [
#     {
#         "timestamp": datetime or ISO string,
#         "role": "user" | "assistant" | "agent",
#         "content": "message text"
#     },
#     ...
# ]

# ### PDF Export Compatibility (WeasyPrint)

# - To enable styled PDF export (matching UI layout):
#   - We use **WeasyPrint**, which requires:
#     - `libpango`, `libgdk-pixbuf2`, and `libcairo`
#     - On macOS: Install with `brew install cairo pango gdk-pixbuf libffi`
#     - On Windows: Download GTK runtime from https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer
#   - This method supports emojis, HTML formatting, and CSS layout.

# """
# def format_timestamp(ts):
#     from datetime import datetime
#     if isinstance(ts, datetime):
#         return ts.strftime("%Y-%m-%d %H:%M:%S")
#     try:
#         return datetime.fromisoformat(ts).strftime("%Y-%m-%d %H:%M:%S")
#     except Exception:
#         return "realtime" if not ts or ts == "N/A" else str(ts)



# def export_to_json(data):
#     """
#     Export chat history to JSON format.
#     :param data: List of chat messages
#     :return: JSON-formatted string
#     """
#     logger.info("Exporting chat history to JSON format.")
#     message_dicts = []
#     for msg in data:
#         msg_dict = msg.to_dict() if hasattr(msg, "to_dict") else dict(msg)
#         if "timestamp" in msg_dict and hasattr(msg_dict["timestamp"], "strftime"):
#             msg_dict["timestamp"] = msg_dict["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
#         message_dicts.append(msg_dict)
#     logger.info(f"Exported {len(message_dicts)} messages to JSON format.")
#     return json.dumps(message_dicts, indent=2)


# def export_to_csv(data):
#     logger.info("Exporting chat history to CSV format.")
#     output = StringIO()
#     writer = csv.DictWriter(output, fieldnames=["timestamp", "role", "content"])
#     writer.writeheader()
#     for i, row in enumerate(data):
#         timestamp = row.get("timestamp", "N/A")
#         role = row.get("role", "unknown")
#         content = row.get("content", "[No content]")
#         missing = [k for k in ("timestamp", "role", "content") if k not in row]
#         if missing:
#             logger.warning(f"[CSV Export] Row {i} missing keys: {missing} – Data: {row}")
#         writer.writerow({
#             "timestamp": format_timestamp(timestamp),
#             "role": role,
#             "content": content
#         })
#     logger.info(f"Exported {len(data)} rows to CSV format.")
#     return output.getvalue()


# def export_to_txt(data):
#     logger.info("Exporting chat history to TXT format.")
#     lines = []
#     for i, row in enumerate(data):
#         timestamp = row.get("timestamp", "N/A")
#         role = row.get("role", "unknown")
#         content = row.get("content", "[No content]")

#         # Log missing keys (for debugging)
#         missing = [k for k in ("timestamp", "role", "content") if k not in row]
#         if missing:
#             logger.warning(f"[TXT Export] Row {i} missing keys: {missing} – Data: {row}")

#         line = f"[{format_timestamp(timestamp)}] {role.capitalize()}: {content}"
#         lines.append(line)
#     logger.info(f"Exported {len(lines)} lines to TXT format.")  
#     return "\n".join(lines)


# def export_to_pdf(chat_history):
#     logger.info("Exporting chat history to PDF format.")
#     buffer = BytesIO()
#     doc = SimpleDocTemplate(buffer, pagesize=letter)
#     styles = getSampleStyleSheet()
#     content = []
#     for msg in chat_history:
#         timestamp = msg.get("timestamp", "")
#         role = msg.get("role", "")
#         text = msg.get("content", "")
#         content.append(Paragraph(f"[{timestamp}] {role}: {text}", styles["Normal"]))
#         content.append(Spacer(1, 6))
#     doc.build(content)
#     buffer.seek(0)
#     logger.info("PDF export completed successfully.")
#     return buffer.read(), "chat_export.pdf"

# def get_export_data(chat_history, format_type,topic=None, chat_ui_layout=None):
#     """
#     Export logic routing for all formats.
#     PDF format uses the actual UI layout as visual export.

#     :param chat_history: groupchat object or list of messages
#     :param format_type: 'pdf', 'json', 'csv', 'txt'
#     :return: (bytes or string, filename)
#     """
#     from datetime import datetime

#     # Normalize input
#     if hasattr(chat_history, "get_messages") and callable(chat_history.get_messages):
#         chat_history = chat_history.get_messages()

#     # Default message if nothing to export
#     if not chat_history:
#         now = datetime.now()
#         placeholder = "No chat history to export."
#         data = [{"timestamp": now, "role": "system", "content": placeholder}]
#         filename = f"empty_chat.{format_type}"
#         if format_type == "pdf":
#             from panel.pane import Markdown
#             return export_to_pdf(Markdown(placeholder)), filename
#         elif format_type == "csv":
#             return export_to_csv(data), filename
#         elif format_type == "txt":
#             return placeholder, filename
#         elif format_type == "json":
#             return json.dumps([], indent=2), filename
#         else:
#             return placeholder, filename

#     filename = f"chat_export.{format_type}"

#     # Route by format
#     if format_type == "json":
#         return export_to_json(chat_history), filename
#     elif format_type == "csv":
#         return export_to_csv(chat_history), filename
#     elif format_type == "txt":
#         return export_to_txt(chat_history), filename
#     elif format_type == "pdf":
#         return export_to_pdf(chat_history)
#     else:
#         return "Unsupported format", filename
# --- Imports for handling data formats, timestamps, and PDF creation ---
import json               # For JSON export
import csv                # For CSV export
from io import StringIO, BytesIO   # For creating in-memory files
from datetime import datetime      # For formatting timestamps
import logging            # For logging missing fields or warnings

# For PDF export (generates simple text-based PDFs)
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

logger = logging.getLogger(__name__)

def format_timestamp(ts):
    """
    Safely format a timestamp as a string.
    - Handles Python datetime objects, ISO strings, and fallback to a default label.
    - Returns "realtime" if value is missing.
    """
    if isinstance(ts, datetime):
        return ts.strftime("%Y-%m-%d %H:%M:%S")
    try:
        return datetime.fromisoformat(ts).strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        # If not a valid date, label as "realtime"
        return "realtime" if not ts or ts == "N/A" else str(ts)

def export_to_json(data, topic=None):
    """
    Export chat history as JSON.
    - If topic is provided, wraps the output as {"topic": topic, "messages": [...]}.
    - Otherwise, outputs a list of message dicts.
    - Handles conversion of datetimes to strings.
    """
    message_dicts = []
    for msg in data:
        # Convert objects to dict if needed (for custom message classes)
        msg_dict = msg.to_dict() if hasattr(msg, "to_dict") else dict(msg)
        # Convert timestamp to string if needed
        if "timestamp" in msg_dict and hasattr(msg_dict["timestamp"], "strftime"):
            msg_dict["timestamp"] = msg_dict["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
        message_dicts.append(msg_dict)
    export = {"topic": topic, "messages": message_dicts} if topic else message_dicts
    return json.dumps(export, indent=2)

def export_to_csv(data, topic=None):
    """
    Export chat history as CSV.
    - Adds a "topic" column only for the first row if topic is provided.
    - Logs any missing fields for debugging.
    """
    logger.info("Exporting chat history to CSV format.")
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=["topic", "timestamp", "role", "content"])
    writer.writeheader()
    for i, row in enumerate(data):
        timestamp = row.get("timestamp", "realtime")
        role = row.get("role", "unknown")
        content = row.get("content", "[No content]")
        missing = [k for k in ("timestamp", "role", "content") if k not in row]
        if missing:
            logger.warning(f"[CSV Export] Row {i} missing keys: {missing} – Data: {row}")
        writer.writerow({
            "topic": topic if i == 0 else "",  # Only in the first row
            "timestamp": format_timestamp(timestamp),
            "role": role,
            "content": content
        })
    logger.info(f"Exported {len(data)} rows to CSV format.")
    return output.getvalue()


def export_to_txt(data, topic=None):
    """
    Export chat history as plain TXT.
    - Adds topic as a header if provided.
    - Each message is a readable log line.
    - Logs any missing fields for debugging.
    """
    lines = []
    if topic:
        lines.append(f"Topic: {topic}")
        lines.append("")
    for i, row in enumerate(data):
        timestamp = row.get("timestamp", "realtime")
        role = row.get("role", "unknown")
        content = row.get("content", "[No content]")
        # Log any missing fields
        missing = [k for k in ("timestamp", "role", "content") if k not in row]
        if missing:
            logger.warning(f"[TXT Export] Row {i} missing keys: {missing} – Data: {row}")
        line = f"[{format_timestamp(timestamp)}] {role.capitalize()}: {content}"
        lines.append(line)
    logger.info(f"Exported {len(data)} lines to TXT format.")
    return "\n".join(lines)

def export_to_pdf(chat_history, topic=None):
    """
    Export chat history to PDF (using ReportLab).
    - Adds topic as a header if provided.
    - Each message is a paragraph in the PDF.
    - Logs any missing fields for debugging.
    """
    logger.info("Exporting chat history to PDF format.")
    buffer = BytesIO()  # In-memory PDF buffer
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    content = []
    if topic:
        content.append(Paragraph(f"Topic: {topic}", styles["Heading2"]))
        content.append(Spacer(1, 12))
    for i, row in enumerate(chat_history):
        timestamp = row.get("timestamp", "realtime")
        role = row.get("role", "unknown").capitalize()
        message = row.get("content", "[No content]")
        # Log any missing fields
        missing = [k for k in ("timestamp", "role", "content") if k not in row]
        if missing:
            logger.warning(f"[PDF Export] Row {i} missing keys: {missing} – Data: {row}")
        line = f"[{format_timestamp(timestamp)}] {role}: {message}"
        content.append(Paragraph(line, styles["Normal"]))
        content.append(Spacer(1, 6))
    doc.build(content)
    buffer.seek(0)
    logger.info("PDF export completed successfully.")
    return buffer.read(), "chat_export.pdf"

def get_export_data(chat_history, format_type, topic=None, chat_ui_layout=None):
    """
    Main entry point for export.
    - Selects which export function to call based on format_type.
    - Passes topic as needed.
    - Handles empty session fallback gracefully.
    - Returns (file_content, filename) tuple.
    """
    from datetime import datetime
    # Unwrap from groupchat object if needed
    if hasattr(chat_history, "get_messages") and callable(chat_history.get_messages):
        chat_history = chat_history.get_messages()

    # If session is empty, export a placeholder
    if not chat_history:
        now = datetime.now()
        placeholder = "No chat history to export."
        data = [{"timestamp": now, "role": "system", "content": placeholder}]
        filename = f"empty_chat.{format_type}"
        if format_type == "pdf":
            return export_to_pdf(data, topic)
        elif format_type == "csv":
            return export_to_csv(data, topic), filename
        elif format_type == "txt":
            return export_to_txt(data, topic), filename
        elif format_type == "json":
            return export_to_json([], topic), filename
        else:
            return placeholder, filename

    filename = f"chat_export.{format_type}"
    # Route to the correct export function
    if format_type == "json":
        return export_to_json(chat_history, topic), filename
    elif format_type == "csv":
        return export_to_csv(chat_history, topic), filename
    elif format_type == "txt":
        return export_to_txt(chat_history, topic), filename
    elif format_type == "pdf":
        return export_to_pdf(chat_history, topic)
    else:
        return "Unsupported format", filename
