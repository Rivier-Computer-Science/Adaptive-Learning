from transformers import AutoModelForCausalLM, AutoTokenizer

<<<<<<< HEAD
def verify_installation():
    print("Starting verification...")
    
    # Load tokenizer
    tokenizer_name = "EleutherAI/llemma_7b"
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)
    print("Tokenizer loaded successfully.")
    
    # Load model
    print("Attempting to load the model...")
    model = AutoModelForCausalLM.from_pretrained(tokenizer_name)
    print("Model loaded successfully.")
    
    print("Verification completed successfully.")
=======
model_name = "EleutherAI/llemma_7b"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)
>>>>>>> origin/SU24-Sprint-1

if __name__ == "__main__":
    verify_installation()
