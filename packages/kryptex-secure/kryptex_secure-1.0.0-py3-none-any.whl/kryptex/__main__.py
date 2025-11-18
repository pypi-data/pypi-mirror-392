"""
Entry point for running kryptex as a module: python -m kryptex
"""

import sys
from kryptex.cli import main

if __name__ == "__main__":
    sys.exit(main())