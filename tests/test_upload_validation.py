
import unittest
from io import BytesIO

import polars as pl
import tempfile
from pathlib import Path
from unittest.mock import patch

import pandas as pd

from dashboard.admin_workspace import load_admin_data
from dashboard.admin_workspace import (
    REQUIRED_COLUMNS,
    process_uploaded_dataset,
    read_uploaded_file,
    validate_columns,
)


class FakeUpload(BytesIO):
    def __init__(self, content, name):
        super().__init__(content)
        self.name = name


class TestUploadValidation(unittest.TestCase):
    def test_rejects_unsupported_extension(self):
        upload = FakeUpload(b"test", "invalid.txt")

        with self.assertRaisesRegex(ValueError, "Only CSV and Parquet"):
            read_uploaded_file(upload)

    def test_detects_missing_required_columns(self):
        df = pl.DataFrame(
            {
                "transaction_id": [1],
                "customer_id": [101],
            }
        )

        missing = validate_columns(df)

        self.assertEqual(
            set(missing),
            set(REQUIRED_COLUMNS) - {"transaction_id", "customer_id"},
        )

    def test_accepts_all_required_columns(self):
        df = pl.DataFrame(
            {column: [None] for column in REQUIRED_COLUMNS}
        )

        self.assertEqual(validate_columns(df), [])

    def test_invalid_upload_does_not_create_processed_data(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            upload = FakeUpload(
                b"transaction_id,customer_id\n1,101\n",
                "invalid.csv",
            )

            with patch(
                "dashboard.admin_workspace.UPLOAD_ROOT", root
            ):
                result = process_uploaded_dataset(upload, 303)

            self.assertFalse(result["success"])
            self.assertIn("Missing required columns", result["error"])
            self.assertFalse((root / "303").exists())

if __name__ == "__main__":
    unittest.main()
