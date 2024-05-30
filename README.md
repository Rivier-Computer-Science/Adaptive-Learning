# Local Setup and Usage of Llemma7b LLM Model

# Introduction
This guide will walk you through setting up and running the Llemma7b model locally on a Windows machine from hugging face hu. This allows you to use the model without incurring ongoing costs associated with commercial APIs like ChatGPT.This documentation is suitable for both professors and students, ensuring ease of use across different operating systems.

# Prerequisites:

Python 3.12+: Ensure Python is installed and added to the system PATH.
pip: The package installer for Python.
Git: Required to clone repositories.
Github for windows: to pull and push the changes from local to remote repository.
Huggigface hub:
Llemma LLM model:

### 1. **Install Anaconda Python:**

   - Use Python 3.12.
   - Anaconda is the preferred choice for the interpreter and libraries.
   - Ensure the base environment is allowed by default. If not, you'll need to start conda every time.

### 2. **Install GUI (Optional):**

   - Anaconda Navigator provides a GUI alternative.
   - To access it in Linux with an active conda environment, type:

     ```bash
     anaconda-navigator
     ```

### 3. **Create an Environment:**

   - Create a new environment named 'math' with Python 3.12 and Anaconda packages:

     ```bash
     conda create -n math python=3.12 anaconda
     conda activate math
     ```

### 4. **Installing Base Software:**

   - Install the 'panel' package:

     ```bash
     conda install panel
     ```

### 5. **Add Channels:**

   - If additional channels are required:

     ```bash
     conda config --env --add channels conda-forge
     ```

     Note: If channels are added via the GUI, open a new terminal or source ~/.bashrc.

### 6. **Packages Only Available with Pip:**

   - Install PyPi packages using pip. However, ensure 'openai' is installed via conda:

     ```bash
     conda config --set pip_interop_enabled True
     pip install openai pyautogen
     ```

### 7. **Github:**

   - Download software from Github.
   - Plugins for Visual Studio Code or GitHub Desktop are recommended.

### 8. **Clone Code Repository:**

   - Clone the repository 'Adaptive-Learning' from: [Adaptive-Learning](https://github.com/Rivier-Computer-Science/Adaptive-Learning)
   
### 9. **Configure Shell:**

   - Add the following to your environment variables (.bashrc on Linux):
     - LINUX: `export OPENAI_API_KEY=sk-proj-bTJnZVozGmjKv3cNlFMaT3BlbkFJ60ejeEufMDrGQMSxFrpM`
     - WINDOWS: `set OPENAI_API_KEY=sk-proj-bTJnZVozGmjKv3cNlFMaT3BlbkFJ60ejeEufMDrGQMSxFrpM`

### 10. **Run Code:**

   - Set the Python interpreter in Visual Studio Code to 'math' using `ctl-shift-P`.
   - Run the following command in your terminal:

     ```bash
     panel serve panel_gui.py --autoreload
     ```

   - Open in a browser the hyperlink you see in the terminal output. Mine was [http://localhost:5006/panel_gui](http://localhost:5006/panel_gui). Your port may be different.

### 11. Installation and Uninstallation of Hugging Face using Conda

### Installation Steps

1. **Create a New Conda Environment (Optional):**
   steps to install and uninstall the Hugging Face library (transformers) using pip,



2. **Install via pip:**
   Open your command line interface and run:

   ```python
   pip install transformers
   ```

3. **Verify Installation:**
   After installation, you can verify if transformers is installed correctly by running:

   ```python
   python -c "import transformers; print(transformers.__version__)"
   ```

### Uninstallation Steps

1. **Uninstall via pip:**
   To uninstall the library, use the following pip command:

   ```python
   pip uninstall transformers
   ```

2. **Verify Uninstallation:**
   To ensure the library has been successfully uninstalled, you can check if the package is still installed by attempting to import it in Python:

   ```python
   python -c "import transformers"
   ```

   If no error is raised, it means the library has been uninstalled successfully.

### 12.**Install the LLM Model:**

-To install and load the `meta-math/MetaMath-Llemma-7B` model from Hugging Face, you can follow these steps

#### Installation Steps

1. **Install via pip:**
   You can install the model using pip:

   ```
   pip install transformers
   ```

#### Loading the Model

Once the Transformers library is installed, you can load the model using the `AutoModelForTokenClassification` class.

```python
from transformers import AutoModelForTokenClassification, AutoTokenizer

# Load the tokenizer and model
tokenizer = AutoTokenizer.from_pretrained("meta-math/MetaMath-Llemma-7B")
model = AutoModelForTokenClassification.from_pretrained("meta-math/MetaMath-Llemma-7B")

# Example input text
input_text = "The quick brown foxes are jumping over the lazy dogs."

# Tokenize the input text
tokens = tokenizer(input_text, return_tensors="pt")

# Perform forward pass through the model
outputs = model(**tokens)

# Process the outputs as needed
```

### Explanation

- `AutoTokenizer.from_pretrained("meta-math/MetaMath-Llemma-7B")` loads the tokenizer for the specified model.
- `AutoModelForTokenClassification.from_pretrained("meta-math/MetaMath-Llemma-7B")` loads the model itself.
- `tokenizer(input_text, return_tensors="pt")` tokenizes the input text and prepares it for input to the model.
- `model(**tokens)` performs a forward pass through the model with the tokenized input.
- You can then process the outputs as needed based on your specific task.

Ensure that you have an internet connection the first time you load the model, as it will download the necessary files from the Hugging Face model hub.

- **Replace "path_to_your_llama_model" with the actual path where the LLaMA model weights are stored**

### 12. **Additional Notes**

1. **Compatibility:** The instructions are tailored for Windows. Adjust paths and commands if necessary for other operating systems.
2. **Performance:** Running large models locally requires significant computational resources. A powerful GPU is recommended for efficient inference.
3. **Legal and Ethical Considerations:** Ensure you comply with the licensing terms provided by Meta for the use of the LLaMA model.

### 13. **Conclusion:**

By following this guide, you will be able to run an LLM locally on your Windows machine, providing a cost-effective and accessible solution for students and educators. This setup ensures you can utilize advanced language models without incurring ongoing costs.
