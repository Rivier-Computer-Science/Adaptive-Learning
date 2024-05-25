from transformers import AutoModelForCausalLM, AutoTokenizer

model_name = "EleutherAI/llemma_34b"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

print("Model and tokenizer loaded successfully.")
