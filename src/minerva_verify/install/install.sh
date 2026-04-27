#!/usr/bin/env bash

if ! command -v git &> /dev/null; then
    echo "Error: git is not installed. Please install git and try again."
    exit 1
fi

TARGET="$HOME/minerva-verify"

if [ ! -d "$TARGET" ]; then
    echo "Cloning dotfiles..."
    git clone https://github.com/marshfellow42/minerva-verify.git "$TARGET"
else
    echo "minerva-verify directory already exists. Skipping clone."
fi

# Move into the directory and run setup
cd "$TARGET" || exit
chmod +x src/minerva_verify/install/setup.py
./src/minerva_verify/install/setup.py