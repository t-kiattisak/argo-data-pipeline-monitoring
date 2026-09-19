import json
import logging
import sys
from datetime import datetime, timezone


class JsonFormatter(logging.Formatter):
    """
    Format application logs as standard single-line JSON strings (JSONL)
    suitable for local debugging and standard container stdout.
    """
    def format(self, record: logging.LogRecord) -> str:
        log_payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "service": getattr(record, "service", "batch-data-extractor"),
            "dataset": getattr(record, "dataset", "system"),
            "stage": getattr(record, "stage", "GENERAL"),
            "batch_id": getattr(record, "batch_id", "N/A"),
            "export_date": getattr(record, "export_date", "N/A"),
            "message": record.getMessage(),
        }

        if hasattr(record, "row_count"):
            log_payload["row_count"] = record.row_count
        if hasattr(record, "duration_ms"):
            log_payload["duration_ms"] = record.duration_ms
        if hasattr(record, "extra_fields"):
            log_payload.update(record.extra_fields)

        if record.exc_info:
            log_payload["error_details"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else "UnknownException",
                "message": str(record.exc_info[1]),
                "traceback": self.formatException(record.exc_info),
            }

        return json.dumps(log_payload, ensure_ascii=False)


def setup_logger(name: str = "extractor") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if not logger.handlers:
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setFormatter(JsonFormatter())
        logger.addHandler(stdout_handler)

    return logger
