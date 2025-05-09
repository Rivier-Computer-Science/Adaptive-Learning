from .conversable_agent import MyConversableAgent

class LanguageTeachingAgent(MyConversableAgent):
    description="""LanguageTeachingAgent is a proficient and engaging language teacher specializing in helping StudentAgent learn and master any specified language. 
            LanguageTeachingAgent is designed to provide an immersive language learning experience, covering essential vocabulary, grammar, and conversational skills. 
            Through a structured progression of lessons, quizzes, and multimedia content, LanguageTeachingAgent ensures that StudentAgent builds a solid foundation in the target language, 
                from basic greetings to advanced sentence construction.
            LanguageTeachingAgent adapts the content and difficulty based on the StudentAgent's performance, providing personalized guidance at each step of the learning journey.
            Whether StudentAgent is learning the alphabet, forming sentences, or engaging in conversational practice, LanguageTeachingAgent ensures that the material is both informative 
                and enjoyable, fostering a deep connection with the language and its cultural context."""
    system_message = """
            You are LanguageTeachingAgent, an agent specialized in teaching the {language} language to StudentAgent. 
            Your role is to guide StudentAgent through a series of well-structured lessons, quizzes, and multimedia resources designed to build proficiency in {language}. 
            Present clear and concise content on topics such as vocabulary, grammar, and conversational skills. 
            Your lessons should be engaging and interactive, using text to demonstrate correct usage. 
            Based on StudentAgent's performance, you will dynamically adjust the difficulty of the material, ensuring that the learning experience remains challenging yet achievable. 
            Provide constructive feedback during quizzes and offer additional examples or practice where necessary. 
            Your goal is to help StudentAgent become confident in understanding and speaking {language}, while making the learning process enjoyable and culturally enriching.
            """
    def __init__(self, language="Telugu", **kwargs):
        # Store the language
        self.language = language
        # Format the system message with the specified language
        formatted_system_message = self.system_message.format(language=self.language)
        super().__init__(
            name=f"{self.language}TeachingAgent",
            system_message=kwargs.pop('system_message', formatted_system_message),
            description=kwargs.pop('description', self.description),
            **kwargs
        )
        # Initial agent state
        self.lessons = self.create_lessons()
        self.current_lesson = 0
        self.skill_level = 0
        self.quiz_results = []

    def create_lessons(self):
        # Define lessons in increasing complexity for the specified language
        # For simplicity, we'll provide a basic structure that can be expanded
        # In a real application, you might fetch lessons from a database or external source
        language_lessons = {
            "Telugu": [
                {"lesson_name": "Basic Greetings", "content": "Namaste - Hello", "difficulty": 1},
                {"lesson_name": "Numbers", "content": "Oka, Rendu, Mūḍu - One, Two, Three", "difficulty": 1},
                {"lesson_name": "Basic Sentences", "content": "Ela unnaru? - How are you?", "difficulty": 2},
                {"lesson_name": "Advanced Sentences", "content": "Naku Telugu chala ishtam - I love Telugu", "difficulty": 3}
            ],
            "Spanish": [
                {"lesson_name": "Basic Greetings", "content": "Hola - Hello", "difficulty": 1},
                {"lesson_name": "Numbers", "content": "Uno, Dos, Tres - One, Two, Three", "difficulty": 1},
                {"lesson_name": "Basic Sentences", "content": "¿Cómo estás? - How are you?", "difficulty": 2},
                {"lesson_name": "Advanced Sentences", "content": "Me gusta mucho el español - I love Spanish a lot", "difficulty": 3}
            ],
            "French": [
                {"lesson_name": "Basic Greetings", "content": "Bonjour - Hello", "difficulty": 1},
                {"lesson_name": "Numbers", "content": "Un, Deux, Trois - One, Two, Three", "difficulty": 1},
                {"lesson_name": "Basic Sentences", "content": "Comment vas-tu? - How are you?", "difficulty": 2},
                {"lesson_name": "Advanced Sentences", "content": "J'aime beaucoup le français - I love French a lot", "difficulty": 3}
            ]
            # Add more languages as needed
        }
        # Return lessons for the specified language, default to Telugu if language not found
        return language_lessons.get(self.language, language_lessons["Telugu"])

    def present_lesson(self):
        lesson = self.lessons[self.current_lesson]
        # Display text content
        return f"Lesson: {lesson['lesson_name']}\nContent: {lesson['content']}"

    def present_quiz(self):
        lesson = self.lessons[self.current_lesson]
        quiz_question = f"Translate this {self.language} sentence: {lesson['content'].split('-')[1].strip()}"
        return quiz_question

    def evaluate_quiz(self, user_answer):
        correct_answer = self.lessons[self.current_lesson]["content"].split('-')[0].strip()
        if user_answer.lower() == correct_answer.lower():
            self.quiz_results.append(True)
            return "Correct!"
        else:
            self.quiz_results.append(False)
            return f"Incorrect. The correct answer is '{correct_answer}'."

    def adjust_difficulty(self):
        # Adjust difficulty based on the last three quiz results
        if len(self.quiz_results) >= 3 and all(self.quiz_results[-3:]):
            self.skill_level += 1
            self.current_lesson = min(self.current_lesson + 1, len(self.lessons) - 1)
        elif len(self.quiz_results) >= 3 and not any(self.quiz_results[-3:]):
            self.skill_level = max(0, self.skill_level - 1)
            self.current_lesson = max(0, self.current_lesson - 1)

    def run_lesson(self, user_input=None):
        if user_input is None:
            return self.present_lesson()
        else:
            # Evaluate user answer for quiz
            quiz_feedback = self.evaluate_quiz(user_input)
            self.adjust_difficulty()
            return quiz_feedback
"""
# Example Usage
language_agent = LanguageTeachingAgent(language="Spanish")

# Display the first lesson
print(language_agent.present_lesson())

# Simulate quiz evaluation
print(language_agent.run_lesson("Hola"))

# Adjust difficulty and present next lesson
print(language_agent.run_lesson())
"""