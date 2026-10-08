"""Bootstrap script for running the Inventory Management System."""

import sys
from pathlib import Path

# Add project root and app directory to sys.path
PROJECT_DIR = Path(__file__).resolve().parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from app.main import main

if __name__ == "__main__":
    sys.exit(main())
