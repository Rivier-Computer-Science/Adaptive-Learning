

## Running the Module Version of the code
```sh
(math) jglossner@jglossner-Alienware-Aurora-R7:~/TestGit/Adaptive-Learning$ python -m src.UI.panel_gui_unconstrained
```


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