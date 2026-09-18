import unittest
import json
import os
import logging
from src.logger import JsonFormatter, setup_logger
from src.storage import StorageHandler
from src.config import config


class TestPipelineComponents(unittest.TestCase):
    def test_json_logging_format(self):
        formatter = JsonFormatter()
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test log entry",
            args=(),
            exc_info=None,
        )
        record.service = "batch-data-extractor"
        record.dataset = "TEST_DATA"
        record.stage = "TEST_STAGE"
        record.batch_id = "test-uuid"
        record.export_date = "2026-09-18"
        record.row_count = 100
        record.duration_ms = 45

        log_json_str = formatter.format(record)
        data = json.loads(log_json_str)

        self.assertEqual(data["service"], "batch-data-extractor")
        self.assertEqual(data["dataset"], "TEST_DATA")
        self.assertEqual(data["stage"], "TEST_STAGE")
        self.assertEqual(data["row_count"], 100)
        self.assertEqual(data["duration_ms"], 45)
        self.assertIn("timestamp", data)

    def test_local_storage_saving(self):
        config.STORAGE_BACKEND = "local"
        config.LOCAL_STORAGE_DIR = "./tests/test_data_dir"

        handler = StorageHandler(batch_id="test-batch-123", export_date="2026-09-18")
        test_bytes = b"header1,header2\nval1,val2\n"

        result = handler.save(test_bytes, "UNITTEST_DATASET")

        self.assertEqual(result["storage_backend"], "local")
        self.assertTrue(os.path.exists(result["file_path"]))
        self.assertEqual(int(result["file_size_bytes"]), len(test_bytes))

        # Clean up test output
        if os.path.exists(result["file_path"]):
            os.remove(result["file_path"])
        if os.path.exists("./tests/test_data_dir"):
            import shutil
            shutil.rmtree("./tests/test_data_dir")


if __name__ == "__main__":
    unittest.main()
