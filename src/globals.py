input_future = None
initiate_chat_task_created = None

# General app settings
MAX_ROUNDS = 300
APP_NAME = "AdaptiveTutor"
IS_TERMINATION_MSG = "TERMINATE"

# Mastery testing configurations
MASTERY_THRESHOLD = 0.8
MIN_QUESTIONS_PER_TOPIC = 3
MAX_QUESTIONS_PER_TOPIC = 5
MASTERY_TEST_TIMEOUT = 1800  # 30 minutes in seconds

# Progress tracking configurations
PROGRESS_FILE_PATH = 'progress.json'
SAVE_INTERVAL = 300  