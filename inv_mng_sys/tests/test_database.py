"""Database unit tests.

Verifies:
1. Database and table creation.
2. Q13 index and trigger initialization.
3. Persistent storage across closing and reopening connection sessions.
4. Idempotent initialization (never overwrites or wipes existing data on restart).
5. Transaction rollback integrity on failure.
6. Index utilization verification with EXPLAIN QUERY PLAN (Q13).
"""

from __future__ import annotations

import os
import shutil
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.database.connection import create_connection, get_db_connection
from app.database.queries import (
    execute_insert,
    execute_update_or_delete,
    explain_query_plan,
    fetch_all,
    fetch_one,
    get_setting,
    table_exists,
)
from app.database.schema import CURRENT_SCHEMA_VERSION, init_database


class TestDatabaseLayer(unittest.TestCase):
    """Test suite for SQLite connection, schema, and persistence."""

    def setUp(self) -> None:
        """Create an isolated temporary directory for test database files."""
        self.test_dir = tempfile.mkdtemp()
        self.db_path = Path(self.test_dir) / "test_ims.db"

    def tearDown(self) -> None:
        """Clean up the temporary directory after tests."""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_init_database_creates_tables_and_indexes(self) -> None:
        """Confirm database initializes required tables and Q13 indexes."""
        status = init_database(self.db_path)

        self.assertTrue(status["success"])
        self.assertFalse(status["existed_before"])
        self.assertTrue(self.db_path.exists())

        # Check required tables exist
        self.assertTrue(table_exists("users", self.db_path))
        self.assertTrue(table_exists("products", self.db_path))
        self.assertTrue(table_exists("app_settings", self.db_path))

        # Check schema version setting
        version = get_setting("schema_version", custom_path=self.db_path)
        self.assertEqual(version, CURRENT_SCHEMA_VERSION)

        # Check required indexes exist
        expected_indexes = {
            "idx_products_product_id",
            "idx_products_name",
            "idx_products_category",
            "idx_products_supplier",
            "idx_products_stock_status",
            "idx_products_cat_sup",
            "idx_users_username",
        }
        actual_indexes = set(status["indexes"])
        for idx in expected_indexes:
            self.assertIn(idx, actual_indexes, f"Missing required index: {idx}")

    def test_persistence_across_connection_reopen(self) -> None:
        """Confirm data persists across connection close, reopen, and app restart."""
        # 1. Initialize database
        init_database(self.db_path)

        # 2. Insert test user and test product
        user_id = execute_insert(
            """
            INSERT INTO users (username, password_hash, salt, full_name, organization_name, keep_logged_in)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            ("admin", "hash123", "salt123", "Lokesh Paneru", "Apex Logistics", 1),
            custom_path=self.db_path,
        )
        self.assertGreater(user_id, 0)

        product_id = execute_insert(
            """
            INSERT INTO products (product_id, name, category, supplier, quantity, price, stock_status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            ("SKU-1001", "Precision Multimeter", "Electronics", "TechCorp", 25, 49.99, "In Stock"),
            custom_path=self.db_path,
        )
        self.assertGreater(product_id, 0)

        # 3. Simulate closing and reopening by creating a brand new isolated connection
        conn = create_connection(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?", ("admin",))
            user_row = cursor.fetchone()
            self.assertIsNotNone(user_row)
            self.assertEqual(user_row["full_name"], "Lokesh Paneru")
            self.assertEqual(user_row["organization_name"], "Apex Logistics")
            self.assertEqual(user_row["keep_logged_in"], 1)

            cursor.execute("SELECT * FROM products WHERE product_id = ?", ("SKU-1001",))
            prod_row = cursor.fetchone()
            self.assertIsNotNone(prod_row)
            self.assertEqual(prod_row["name"], "Precision Multimeter")
            self.assertEqual(prod_row["quantity"], 25)
            self.assertEqual(prod_row["price"], 49.99)
        finally:
            conn.close()

        # 4. Simulate application restart: running init_database again must NOT wipe existing data!
        restart_status = init_database(self.db_path)
        self.assertTrue(restart_status["existed_before"])

        # Verify data is still intact after simulated restart
        persisted_prod = fetch_one(
            "SELECT * FROM products WHERE product_id = ?",
            ("SKU-1001",),
            custom_path=self.db_path,
        )
        self.assertIsNotNone(persisted_prod)
        self.assertEqual(persisted_prod["name"], "Precision Multimeter")

    def test_transaction_rollback_on_failure(self) -> None:
        """Confirm database rolls back failed transactions properly."""
        init_database(self.db_path)

        # Insert initial product
        execute_insert(
            """
            INSERT INTO products (product_id, name, category, supplier, quantity, price, stock_status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            ("SKU-ORIG", "Original Item", "Tools", "Alpha", 10, 15.0, "In Stock"),
            custom_path=self.db_path,
        )

        # Attempt transaction that deliberately fails halfway
        with self.assertRaises(sqlite3.IntegrityError):
            with get_db_connection(self.db_path) as conn:
                cursor = conn.cursor()
                # Valid insert
                cursor.execute(
                    """
                    INSERT INTO products (product_id, name, category, supplier, quantity, price, stock_status)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    ("SKU-TEMP", "Temp Item", "Tools", "Alpha", 5, 10.0, "In Stock"),
                )
                # Invalid insert (duplicate product_id violates UNIQUE constraint)
                cursor.execute(
                    """
                    INSERT INTO products (product_id, name, category, supplier, quantity, price, stock_status)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    ("SKU-ORIG", "Duplicate Item", "Tools", "Alpha", 2, 20.0, "In Stock"),
                )

        # Confirm SKU-TEMP was rolled back and never committed
        temp_row = fetch_one("SELECT * FROM products WHERE product_id = ?", ("SKU-TEMP",), custom_path=self.db_path)
        self.assertIsNone(temp_row)

    def test_constraints_and_validation(self) -> None:
        """Confirm database table constraints prevent invalid data storage."""
        init_database(self.db_path)

        # Negative quantity should violate CHECK (quantity >= 0)
        with self.assertRaises(sqlite3.IntegrityError):
            execute_insert(
                """
                INSERT INTO products (product_id, name, category, supplier, quantity, price, stock_status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                ("SKU-NEG", "Negative Item", "Tools", "Beta", -5, 10.0, "In Stock"),
                custom_path=self.db_path,
            )

        # Negative price should violate CHECK (price >= 0.0)
        with self.assertRaises(sqlite3.IntegrityError):
            execute_insert(
                """
                INSERT INTO products (product_id, name, category, supplier, quantity, price, stock_status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                ("SKU-PRICENEG", "Negative Price Item", "Tools", "Beta", 5, -10.0, "In Stock"),
                custom_path=self.db_path,
            )

    def test_q13_explain_query_plan_uses_index(self) -> None:
        """Verify that SQLite query planner utilizes indexes for fast lookup (Q13)."""
        init_database(self.db_path)

        # Populate a few sample rows
        for i in range(10):
            execute_insert(
                """
                INSERT INTO products (product_id, name, category, supplier, quantity, price, stock_status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (f"SKU-{i:04d}", f"Product {i}", "Hardware", "Acme", 10 + i, 19.99, "In Stock"),
                custom_path=self.db_path,
            )

        # Check query plan for product_id search
        plan = explain_query_plan(
            "SELECT * FROM products WHERE product_id = ?",
            ("SKU-0005",),
            custom_path=self.db_path,
        )
        plan_details = " ".join(str(step["detail"]) for step in plan)
        # SQLite should report USING INDEX idx_products_product_id
        self.assertIn("USING INDEX idx_products_product_id", plan_details)


if __name__ == "__main__":
    unittest.main()
