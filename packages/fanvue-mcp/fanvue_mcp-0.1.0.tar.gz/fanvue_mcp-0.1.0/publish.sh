#!/bin/bash
set -e

# Ensure we're in the right directory
cd "$(dirname "$0")"

# Build the project
echo "Building project..."
uv build

# Check if token is provided
if [ -z "$PYPI_TOKEN" ]; then
    echo "Error: PYPI_TOKEN environment variable is not set."
    echo "Please set it with your PyPI API token:"
    echo "export PYPI_TOKEN=pypi-..."
    exit 1
fi

# Publish to PyPI
echo "Publishing to PyPI..."
# uv build outputs to workspace dist folder (../dist)
uv publish --token "$PYPI_TOKEN" ../dist/*

echo "Done!"

