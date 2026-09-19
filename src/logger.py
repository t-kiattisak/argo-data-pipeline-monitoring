import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any, Optional


class JsonFormatter(logging.Formatter):
    """
    Format logs as single-line JSON strings (JSONL) suitable for 
    Fluentbit, Kafka Producer, and Elasticsearch/Kibana ingestion.
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

        # Include optional operational metrics if available
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


class KafkaLoggingHandler(logging.Handler):
    """
    Custom logging handler that asynchronously produces structured JSON logs
    directly into an Apache Kafka topic.
    """
    def __init__(self, bootstrap_servers: str, topic: str):
        super().__init__()
        self.topic = topic
        try:
            from kafka import KafkaProducer
            self.producer = KafkaProducer(
                bootstrap_servers=bootstrap_servers.split(","),
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                acks=0,  # Fire-and-forget for non-blocking high throughput
                retries=3,
                max_block_ms=3000,
            )
        except Exception as e:
            self.producer = None
            sys.stderr.write(f"Warning: Failed to initialize KafkaProducer: {e}\n")

    def emit(self, record: logging.LogRecord):
        if not self.producer:
            return
        try:
            msg_str = self.format(record)
            payload = json.loads(msg_str)
            self.producer.send(self.topic, value=payload)
        except Exception as e:
            self.handleError(record)

    def close(self):
        if self.producer:
            try:
                self.producer.flush(timeout=5)
                self.producer.close()
            except Exception:
                pass
        super().close()


def setup_logger(name: str = "extractor") -> logging.Logger:
    from src.config import config

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if not logger.handlers:
        formatter = JsonFormatter()

        # 1. Standard Output Handler (for Console / K8s stdout)
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setFormatter(formatter)
        logger.addHandler(stdout_handler)

        # 2. Kafka Producer Handler (if enabled)
        if config.KAFKA_ENABLED:
            kafka_handler = KafkaLoggingHandler(
                bootstrap_servers=config.KAFKA_BOOTSTRAP_SERVERS,
                topic=config.KAFKA_LOG_TOPIC,
            )
            kafka_handler.setFormatter(formatter)
            logger.addHandler(kafka_handler)

    return logger
