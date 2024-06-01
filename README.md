This guide will walk you through setting up and running the Llemma7b model locally on a Windows machine from hugging face hu. This allows you to use the model without incurring ongoing costs associated with commercial APIs like ChatGPT.This documentation is suitable for both professors and students, ensuring ease of use across different operating systems.

### ***Prerequisites:***

- **Python 3.12+:** Ensure Python is installed and added to the system PATH.
- **pip**: The package installer for Python.
- **Git:** Required to clone repositories.
- **Github for windows:** to pull and push the changes from local to remote repository.
- **Huggigface hub:** It is a central repository where you can find a variety of pre-trained models and datasets, making it easier for - developers and researchers to build and deploy machine learning applications.
- **Llemma LLM model:** a model or method that deals with lemmatization in natural language processing (NLP).
(Lemmatization is the process of reducing words to their base or dictionary form, known as a lemma. For example, the words "running" and "ran" can be reduced to the lemma "run".)

## Steps to setup LLM locally:

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

### 7. **Github and CodeEditor:**

   - Download and intall the Github desktop software.
   - Several popular code editors availabe widely used by developers but one of the popular one is VS Code. 
   - Install and download Plugins for Visual Studio Code or GitHub Desktop are recommended.

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

### 11.**Hugging Face using Conda:**

#### Installation Steps

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

#### Uninstallation Steps

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
=======
- **Conda:** A package manager that helps to find and install packages.
- **pytorch:** open-source machine learning library developed by Facebook's AI Research lab (FAIR).
- **Huggigface hub:** It is a central repository where you can find a variety of pre-trained models and datasets, making it easier for - developers and researchers to build and deploy machine learning applications.
- **Llemma LLM model:** a model or method that deals with lemmatization in natural language processing (NLP).
(Lemmatization is the process of reducing words to their base or dictionary form, known as a lemma. For example, the words "running" and "ran" can be reduced to the lemma "run".)
- **Git:** Required to clone repositories.
- **Github for windows:** to pull and push the changes from local to remote repository.


To install PyTorch using Anaconda (Conda), you can follow these steps. The instructions vary slightly depending on your operating system (Windows, macOS, or Linux) and whether you want to use CPU-only or GPU (CUDA) versions of PyTorch.

Here’s a step-by-step guide:


### 1. Install Anaconda

- First, ensure that you have Anaconda installed. If you do not have it installed, you can download and install it from the [official Anaconda website](https://www.anaconda.com/products/individual).

- Open the Anaconda Prompt (Windows) or your terminal (macOS/Linux).

- It is often a good practice to create a new conda environment for your projects to avoid package conflicts.

```sh
conda create -n myenv python=3.9
conda activate myenv
```

Replace `myenv` with your desired environment name.

### 2. Install PyTorch using conda.

- To install PyTorch, you need to specify the correct command based on your operating system and whether you want to use CPU or GPU. Below are the general installation commands. For the most accurate and updated instructions, visit the [PyTorch installation page](https://pytorch.org/get-started/locally/).

#### CPU Only

For a CPU-only version of PyTorch, use the following command:

```sh
conda install pytorch torchvision torchaudio cpuonly -c pytorch
```

#### GPU (CUDA) Version

If you have an NVIDIA GPU and want to utilize CUDA, you need to specify the appropriate version of CUDA. Here are some common commands:

**CUDA 11.7:**

```sh
conda install pytorch torchvision torchaudio cudatoolkit=11.7 -c pytorch -c nvidia
```

**CUDA 11.6:**

```sh
conda install pytorch torchvision torchaudio cudatoolkit=11.6 -c pytorch -c nvidia
```

**CUDA 11.3:**

```sh
conda install pytorch torchvision torchaudio cudatoolkit=11.3 -c pytorch
```

**CUDA 10.2:**

```sh
conda install pytorch torchvision torchaudio cudatoolkit=10.2 -c pytorch
```

**Example Installation Command:**
If you are using Windows, have a CUDA 11.7-compatible GPU, and want to create a new environment with PyTorch installed, you would run:

```sh
conda create -n pytorch_env python=3.9
conda activate pytorch_env
conda install pytorch torchvision torchaudio cudatoolkit=11.7 -c pytorch -c nvidia
```

### Verify the Installation

After installation, you can verify that PyTorch is installed correctly by running a simple Python script.

1. Open Python in your terminal:

```sh
python
```

2. Import PyTorch and print the version:

```python
import torch
print(torch.__version__)
print(torch.cuda.is_available())  # Check if CUDA is available (optional)
```

If PyTorch is installed correctly, it will display the version number and `True` if CUDA is available (for GPU installations).

### 3. Install Hugging Face using Conda.

- It is recommended to create a new conda environment for your projects to avoid package conflicts.

```sh
conda create -n huggingface_env python=3.9
conda activate huggingface_env
```

Replace `huggingface_env` with your desired environment name.

#### Install the `transformers` Library

- Use the following command to install the `transformers` library from the `huggingface` channel on Conda:

```sh
conda install -c huggingface transformers
```

#### Verify the Installation

After installation, you can verify that the `transformers` library is installed correctly by running a simple Python script.

1. Open Python in your terminal:

```sh
python
```

2. Import the `transformers` library and print the version:

```python
import transformers
print(transformers.__version__)
```

If the library is installed correctly, it will display the version number.

#### Additional Libraries

Depending on your use case, you might also need to install additional libraries such as `datasets`, `tokenizers`, and others. You can install them using the following commands:

```sh
conda install -c huggingface datasets
conda install -c huggingface tokenizers
```

### Verify the Llemma model.

- To verify the installation and download the `lemma 7B` model using a script called `verify_installation.py`, you need to ensure that your script is correctly set up to download the model from the Hugging Face Hub. Here’s how you can do it

####  Update `verify_installation.py`

First, you need to update the `verify_installation.py` script to download the `lemma 7B` model. Here’s an example of how you can write or update this script:

```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

def main():
    # Define the model name
    model_name = "huggingface/lemma-7b"
    
    # Load the tokenizer and model
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)
    
    # Print a message to verify that the model is loaded successfully
    print(f"Successfully loaded {model_name}")

    # Perform a simple inference to verify the model works
    inputs = tokenizer("Hello, how are you?", return_tensors="pt")
    outputs = model(**inputs)

    # Print the output logits
    print(outputs.logits)

if __name__ == "__main__":
    main()
```

Make sure to replace `"huggingface/lemma-7b"` with the actual model identifier from the Hugging Face Hub if it's different.

#### Install Dependencies

Ensure you have the necessary dependencies installed. If you haven't already installed them, run:

```sh
conda install -c huggingface transformers
```

If your script uses specific versions of the libraries, ensure those versions are specified in your installation.

#### Run `verify_installation.py`

Run the updated script to download and verify the `lemma 7B` model:

```sh
python verify_installation.py
```

####  Example Output

If everything is set up correctly, you should see output similar to this:

```
Successfully loaded huggingface/lemma-7b
tensor([[...]], grad_fn=<AddBackward0>)
```

This output indicates that the model has been loaded successfully and a simple inference was performed.

### Notes

1. **Model Identifier**: Ensure that the model identifier (`"huggingface/lemma-7b"`) is correct and points to the correct model on the Hugging Face Hub.
2. **Internet Access**: Make sure your environment has internet access to download the model the first time you run the script.
3. **GPU Support**: If you are using a GPU, make sure PyTorch is configured to use it. You might need to install the CUDA toolkit if it’s not already installed.
