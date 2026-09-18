import os
import sys
import uuid
from datetime import datetime, timezone, timedelta
from src.config import config
from src.extractor import DatabaseExtractor
from src.logger import setup_logger
from src.storage import StorageHandler
from src.webhook import WebhookNotifier

logger = setup_logger("main")


def get_default_export_date() -> str:
    """Defaults to yesterday's date in YYYY-MM-DD format."""
    yesterday = datetime.now(timezone.utc) - timedelta(days=1)
    return yesterday.strftime("%Y-%m-%d")


def run():
    batch_id = str(uuid.uuid4())
    export_date = config.EXPORT_DATE or os.getenv("EXPORT_DATE") or get_default_export_date()

    logger.info(
        f"Starting batch extraction pipeline for date: {export_date} (Storage: {config.STORAGE_BACKEND})",
        extra={
            "service": config.SERVICE_NAME,
            "stage": "PIPELINE_START",
            "batch_id": batch_id,
            "export_date": export_date,
            "extra_fields": {"storage_backend": config.STORAGE_BACKEND},
        },
    )

    try:
        extractor = DatabaseExtractor(batch_id, export_date)
        storage = StorageHandler(batch_id, export_date)

        payload_manifest = {}

        # 1. Process Device Telemetry Dataset
        telemetry_csv, telemetry_count = extractor.extract_device_telemetry()
        telemetry_storage_meta = storage.save(telemetry_csv, "DEVICE_TELEMETRY")
        payload_manifest["device_telemetry"] = {
            **telemetry_storage_meta,
            "row_count": telemetry_count,
        }

        # 2. Process Order Events Dataset
        orders_csv, orders_count = extractor.extract_order_events()
        orders_storage_meta = storage.save(orders_csv, "ORDER_EVENTS")
        payload_manifest["order_events"] = {
            **orders_storage_meta,
            "row_count": orders_count,
        }

        # 3. Optional: Trigger Downstream Webhook
        if config.ENABLE_WEBHOOK:
            webhook = WebhookNotifier(batch_id, export_date)
            webhook.trigger_downstream(payload_manifest)

        logger.info(
            "Batch extraction pipeline completed successfully",
            extra={
                "service": config.SERVICE_NAME,
                "stage": "PIPELINE_SUCCESS",
                "batch_id": batch_id,
                "export_date": export_date,
            },
        )
        sys.exit(0)

    except Exception as exc:
        logger.critical(
            f"Pipeline failed unexpectedly: {str(exc)}",
            exc_info=True,
            extra={
                "service": config.SERVICE_NAME,
                "stage": "PIPELINE_FAILURE",
                "batch_id": batch_id,
                "export_date": export_date,
            },
        )
        sys.exit(1)


if __name__ == "__main__":
    run()
