import tkinter as tk
from explanation_algorithm import ExplanationGenerationAlgorithm

class ExplanationApp:
    def __init__(self, root):
        self.algorithm = ExplanationGenerationAlgorithm()
        self.root = root
        self.root.title("Explanation Generator")
        
        self.input_label = tk.Label(root, text="Enter Question:")
        self.input_label.pack()
        
        self.input_entry = tk.Entry(root)
        self.input_entry.pack()
        
        self.answer_label = tk.Label(root, text="Enter Answer:")
        self.answer_label.pack()
        
        self.answer_entry = tk.Entry(root)
        self.answer_entry.pack()
        
        self.level_label = tk.Label(root, text="Enter User Level:")
        self.level_label.pack()
        
        self.level_entry = tk.Entry(root)
        self.level_entry.pack()
        
        self.generate_button = tk.Button(root, text="Generate Explanation", command=self.generate_explanation)
        self.generate_button.pack()
        
        self.explanation_label = tk.Label(root, text="Explanation:")
        self.explanation_label.pack()
        
        self.explanation_text = tk.Text(root, height=10, width=50)
        self.explanation_text.pack()
        
        self.practice_label = tk.Label(root, text="Additional Practice Problems:")
        self.practice_label.pack()
        
        self.practice_text = tk.Text(root, height=10, width=50)
        self.practice_text.pack()
        
    def generate_explanation(self):
        question = self.input_entry.get()
        answer = self.answer_entry.get()
        user_level = self.level_entry.get()
        explanation = self.algorithm.generate_explanation(question, answer, user_level)
        self.explanation_text.delete(1.0, tk.END)
        self.explanation_text.insert(tk.END, explanation)
        
        practice_problems = self.get_additional_practice_problems(question)
        self.practice_text.delete(1.0, tk.END)
        self.practice_text.insert(tk.END, practice_problems)
    
    def get_additional_practice_problems(self, question):
        # Placeholder function to return practice problems based on question
        return "Practice Problem 1\nPractice Problem 2\nPractice Problem 3"

if __name__ == "__main__":
    root = tk.Tk()
    app = ExplanationApp(root)
    root.mainloop()
