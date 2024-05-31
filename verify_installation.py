from transformers import AutoModelForCausalLM, AutoTokenizer

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

if __name__ == "__main__":
    verify_installation()
