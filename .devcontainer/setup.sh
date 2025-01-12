#!/bin/bash

echo "Creating adaptive conda environment. This will take some time (minutes)"

# Ensure Conda is initialized for the current shell
eval "$(conda shell.bash hook)"

# Create the Conda environment
conda env create -f conda_env.yml -n adaptive 

# Clean up unnecessary files
conda clean -a --yes

# Initialize bashrc
conda init

# display environments
conda info --envs

# Activate the environment
conda activate adaptive    

echo "Setup completed successfully!"
