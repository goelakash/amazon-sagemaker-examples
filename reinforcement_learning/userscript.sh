#!/bin/bash
git clone https://github.com/goelakash/amazon-sagemaker-examples.git
cd amazon-sagemaker-examples/reinforcement_learning
conda list
yes | conda install -c conda-forge papermill
python testserver.py