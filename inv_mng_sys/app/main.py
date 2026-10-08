"""Main application entry point.

Initializes the persistent database layer and prepares for authentication and GUI workflows.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_DIR = Path(__file__).resolve().parent.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from app.database.schema import init_database

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("ims")


def main() -> int:
    """Bootstrap application initialization."""
    logger.info("Initializing Inventory Management System (BBAT104 - Q13)...")
    status = init_database()
    logger.info("Database status: %s", status)
    print("==================================================")
    print("Inventory Management System (IMS) - Offline Desktop")
    print("Quality Objective: Q13 — Faster Search & Retrieval")
    print(f"Database Location: {status['database_path']}")
    print(f"Tables Initialized: {', '.join(status['tables'])}")
    print(f"Q13 Indexes Initialized: {', '.join(status['indexes'])}")
    print("==================================================")
    return 0


if __name__ == "__main__":
    sys.exit(main())
