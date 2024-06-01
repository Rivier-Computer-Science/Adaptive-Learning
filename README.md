# knowledge

# Local Setup and Usage of Llemma7b LLM Model

### ***Introduction:***

This guide will walk you through setting up and running the Llemma7b model locally on a Windows machine from hugging face hu. This allows you to use the model without incurring ongoing costs associated with commercial APIs like ChatGPT.This documentation is suitable for both professors and students, ensuring ease of use across different operating systems.

### ***Prerequisites:***

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
