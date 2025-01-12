#!/bin/bash

echo "Creating adaptive conda environment. This will take some time (minutes)"

# Create the Conda environment
conda env create -f conda_env.yml -n adaptive 
conda clean -a 
conda activate adaptive    

echo "Setup completed successfully!"
