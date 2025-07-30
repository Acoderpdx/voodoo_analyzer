#!/bin/bash
# Run the analyzer with the correct Python

cd "$(dirname "$0")"

# Use the full path to ensure we use the right Python
/opt/anaconda3/bin/python main.py