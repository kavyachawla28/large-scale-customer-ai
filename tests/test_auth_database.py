
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from auth.database import (
    initialize_database,
    create_user,
    get_user_by_id,
)


class TestAuthDatabase(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_users.db"

        self.db_patch = patch(
            "auth.database.DB_PATH",
            self.db_path,
        )
        self.db_patch.start()

        initialize_database()

    def tearDown(self):
        self.db_patch.stop()
        self.temp_dir.cleanup()

    def test_retrieves_existing_admin_by_id(self):
        create_user(
            name="Test Admin",
            email="admin@test.com",
            password_hash="test_hash",
            role="admin",
        )

        user = get_user_by_id(1)

        self.assertIsNotNone(user)
        self.assertEqual(user[1], "Test Admin")
        self.assertEqual(user[2], "admin@test.com")
        self.assertEqual(user[4], "admin")

    def test_rejects_nonexistent_user_id(self):
        user = get_user_by_id(9999)

        self.assertIsNone(user)

    def test_retrieves_customer_role_from_database(self):
        create_user(
            name="Test Customer",
            email="customer@test.com",
            password_hash="test_hash",
            role="customer",
        )

        user = get_user_by_id(1)

        self.assertEqual(user[4], "customer")

    def test_database_rejects_invalid_role(self):
        created = create_user(
            name="Invalid User",
            email="invalid@test.com",
            password_hash="test_hash",
            role="superadmin",
        )

        self.assertFalse(created)
        self.assertIsNone(get_user_by_id(1))


if __name__ == "__main__":
    unittest.main()
