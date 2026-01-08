#!/bin/bash
# Installation script for bash-skill

echo "Installing bash-skill..."

# Install the package in editable mode
pip install -e .

echo "Installation complete!"
echo ""
echo "To use with Claude Code, run:"
echo "  mcp install src/bash_skill/server.py --name bash-skill"
echo ""
echo "To run tests:"
echo "  pytest"
