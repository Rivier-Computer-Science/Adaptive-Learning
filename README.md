

## Running the Module Version of the code
```sh
(math) jglossner@jglossner-Alienware-Aurora-R7:~/TestGit/Adaptive-Learning$ python -m src.UI.panel_gui_unconstrained
```

## Autogen
In Microsoft's AutoGen, the description and system_message fields serve distinct purposes in defining an Agent's behavior:

### System Message (system_message):

    Core Instructions: This field provides the fundamental instructions that guide the Agent's overall behavior and responses. It sets the tone, establishes the Agent's role, and outlines the primary goals it should aim for in conversations.
    Technical Focus: Primarily intended for technical guidance, the system_message often includes details like API usage, specific tasks, or constraints on the Agent's actions.
    Legacy Usage: In older versions of AutoGen, the system_message was used by GroupChat to determine which Agent should respond in a conversation.

### Description (description):

    High-Level Summary: This field offers a concise, human-readable summary of the Agent's role, expertise, or personality. It's designed to be easily understood by users and other Agents.
    GroupChat Orchestration: In newer AutoGen versions (0.2.2 onwards), GroupChat primarily uses the description field to decide which Agent is most suitable to respond in a multi-agent conversation.
    Simplified Communication: The description facilitates clearer communication between Agents and users, as it provides a quick overview of what an Agent is capable of.

### Key Differences and When to Use Each:

    Purpose:
        system_message: Focuses on technical instructions and core behavior.
        description: Provides a high-level summary for easy understanding and GroupChat selection.
    Audience:
        system_message: Primarily intended for developers and system administrators.
        description: Intended for both developers/administrators and end-users interacting with the Agents.
    GroupChat:
        Older AutoGen versions: GroupChat uses system_message.
        Newer AutoGen versions (0.2.2+): GroupChat primarily uses description.

### Recommendation:

In most cases, it's recommended to use both fields:

    Provide detailed technical instructions in the system_message.
    Offer a clear, concise summary of the Agent's capabilities in the description to facilitate effective communication and GroupChat orchestration.


## Hugging Face



This guide will walk you through setting up and running the Llemma7b hugging face model locally. 

# 1. Install Anaconda

- Download and install it from the [official Anaconda website](https://www.anaconda.com/products/individual).

- Create an environment

```sh
conda create -n adaptive python=3.12 anaconda
conda activate adaptive
```

# 2. Install PyTorch using conda.

## 2.1 CPU Only

```sh
conda install pytorch torchvision torchaudio cpuonly -c pytorch
```

## 2.2 GPU (CUDA) Version

```sh
conda install pytorch torchvision torchaudio cudatoolkit -c pytorch
```

If you need a specific version of CUDA.

```sh
conda install pytorch torchvision torchaudio cudatoolkit=11.7 -c pytorch -c nvidia
```

## 2.3 See also: [PyTorch installation page](https://pytorch.org/get-started/locally/).


## 2.4 Verify the Installation

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

# 3. Install Hugging Face using Conda.

## 3.1 Install Libraries

```sh
conda install -c conda-forge transformers huggingface_hub tokenizers datasets
```

## 3.2 Verify the Installation

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

# 4. Download the Llemma 7B model.

## 4.1 Run `verify_installation.py`
This will automatically download and cache the Llemma 7B model.

```sh
python verify_installation.py
```

## 4.2  Example Output

If everything is set up correctly, you should see output similar to this:

```
Successfully loaded huggingface/lemma-7b
tensor([[...]], grad_fn=<AddBackward0>)
```