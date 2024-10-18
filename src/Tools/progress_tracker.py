import json
import os

class ProgressTracker:
    def __init__(self, file_path):
        self.file_path = file_path
        self.progress = self.load_progress()

    def load_progress(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as file:
                return json.load(file)
        return {}

    def save_progress(self):
        with open(self.file_path, 'w') as file:
            json.dump(self.progress, file)

    def update_topic_progress(self, topic, mastered):
        self.progress[topic] = mastered
        self.save_progress()

    def get_overall_progress(self):
        if not self.progress:
            return 0
        return sum(self.progress.values()) / len(self.progress)

    def get_next_topic(self):
        for topic, mastered in self.progress.items():
            if not mastered:
                return topic
        return None  # All topics mastered
