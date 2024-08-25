import tkinter as tk

class FeedbackForm:
    def __init__(self, root):
        self.root = root
        self.root.title("User Feedback Form")
        
        self.feedback_label = tk.Label(root, text="Please provide your feedback:")
        self.feedback_label.pack()
        
        self.feedback_text = tk.Text(root, height=10, width=50)
        self.feedback_text.pack()
        
        self.submit_button = tk.Button(root, text="Submit", command=self.submit_feedback)
        self.submit_button.pack()
        
        self.message_label = tk.Label(root, text="")
        self.message_label.pack()
    
    def submit_feedback(self):
        feedback = self.feedback_text.get(1.0, tk.END).strip()
        if feedback:
            self.save_feedback(feedback)
            self.message_label.config(text="Thank you for your feedback!", fg="green")
            self.feedback_text.delete(1.0, tk.END)
        else:
            self.message_label.config(text="Please enter your feedback before submitting.", fg="red")
    
    def save_feedback(self, feedback):
        with open("user_feedback.txt", "a") as file:
            file.write(feedback + "\n")
    
if __name__ == "__main__":
    root = tk.Tk()
    app = FeedbackForm(root)
    root.mainloop()
