#!/usr/bin/env python3
"""
Entry point for running GitDecomposer as a module.
This allows the package to be executed with: python -m gitdecomposer
"""

from .cli import main

if __name__ == "__main__":
    main()
