#!/bin/bash

echo "Creating uv environment."

# install uv and venv
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env
uv venv --python 3.12
source .venv/bin/activate
uv pip install -r requirements.txt

# New installs will have the wrong decryption key by default. So, reinitialize them.
rm portfolio_*

echo "Setup completed successfully!"