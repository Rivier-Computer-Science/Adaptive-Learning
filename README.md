# Adaptive Learning

### Create an Account
- http://huggingface.co 
- Links to an external site.

### Join Rivier CS
- https://huggingface.co/organizations/rivier-cs/share/JxILqgwhDbIheptwtscovBQilXPkBezdNa 
- Links to an external site.

## Setup and Installation

### Step 1: Create a Conda Environment

1. **Install Conda:** If you do not have Conda installed, download and install it from [here](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html).

2. **Create and Activate the Conda Environment:**

   conda create -n adaptive-learning python=3.9
   conda activate adaptive-learning

### Step 2: Install Hugging Face and Required Packages

1. **Install Hugging Face Packages:**

conda install -c huggingface transformers datasets

2. **Install Additional Dependencies:**

pip install torch tokenizers huggingface-hub

### Step 3: Verify the Installation

1. **Create a Verification Script:**

Create a Python script named verify_installation.py with the following content:

from transformers import AutoModelForCausalLM, AutoTokenizer

model_name = "EleutherAI/llemma_34b"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

print("Model and tokenizer loaded successfully.")

2. **Run the Verification Script:**

Run the script to ensure everything is set up correctly:

python verify_installation.py

You should see the message "Model and tokenizer loaded successfully."


### Documentation
- See: https://huggingface.co/docs/huggingface_hub/index 
- How-to guides: https://huggingface.co/docs/huggingface_hub/guides/overview

### Models
- Llemma (34b): https://huggingface.co/EleutherAI/llemma_34b 