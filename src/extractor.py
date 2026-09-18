import csv
import io
import time
from typing import Dict, List, Tuple
import psycopg2
from psycopg2.extras import RealDictCursor
from src.config import config
from src.logger import setup_logger

logger = setup_logger("extractor")


class DatabaseExtractor:
    def __init__(self, batch_id: str, export_date: str):
        self.batch_id = batch_id
        self.export_date = export_date

    def get_connection(self):
        return psycopg2.connect(
            host=config.DB_HOST,
            port=config.DB_PORT,
            dbname=config.DB_NAME,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
        )

    def extract_device_telemetry(self) -> Tuple[bytes, int]:
        """
        Extracts and flattens JSONB device telemetry events for the target export_date.
        Formats to RFC 4180 CSV with UTF-8 BOM and QUOTE_ALL.
        """
        start_time = time.time()
        dataset_name = "DEVICE_TELEMETRY"

        query = """
            SELECT 
                id AS event_id,
                payload->>'device_id' AS device_id,
                created_at AS timestamp,
                (payload->>'battery_level')::NUMERIC AS battery_level,
                (payload->>'temperature_c')::NUMERIC AS temperature_c,
                payload->>'firmware_version' AS firmware_version,
                (payload->>'signal_strength_dbm')::INTEGER AS signal_strength_dbm,
                (payload->>'cpu_usage_pct')::NUMERIC AS cpu_usage_pct,
                (payload->>'memory_usage_pct')::NUMERIC AS memory_usage_pct,
                payload->>'operating_mode' AS operating_mode,
                payload->>'network_type' AS network_type,
                payload->>'ip_address' AS ip_address,
                status,
                created_at,
                %s AS export_date,
                %s AS batch_id
            FROM iot_device_events
            WHERE DATE(created_at) = %s::DATE
            ORDER BY created_at ASC;
        """

        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, (self.export_date, self.batch_id, self.export_date))
                rows = cur.fetchall()

            duration_ms = int((time.time() - start_time) * 1000)
            row_count = len(rows)

            logger.info(
                f"Successfully extracted {row_count} rows from PostgreSQL",
                extra={
                    "service": config.SERVICE_NAME,
                    "dataset": dataset_name,
                    "stage": "EXTRACT_DB",
                    "batch_id": self.batch_id,
                    "export_date": self.export_date,
                    "row_count": row_count,
                    "duration_ms": duration_ms,
                },
            )

            # Convert to CSV (UTF-8 BOM + QUOTE_ALL)
            csv_bytes = self._convert_to_csv(rows)
            return csv_bytes, row_count
        finally:
            conn.close()

    def extract_order_events(self) -> Tuple[bytes, int]:
        """
        Extracts and flattens JSONB order events for the target export_date.
        """
        start_time = time.time()
        dataset_name = "ORDER_EVENTS"

        query = """
            SELECT 
                id AS order_id,
                payload->>'customer_id' AS customer_id,
                created_at AS event_timestamp,
                payload->>'event_type' AS event_type,
                payload->>'currency' AS currency,
                (payload->>'total_amount')::NUMERIC AS total_amount,
                (payload->>'discount_amount')::NUMERIC AS discount_amount,
                (payload->>'item_count')::INTEGER AS item_count,
                payload->>'payment_method' AS payment_method,
                payload->>'shipping_carrier' AS shipping_carrier,
                payload->>'delivery_country' AS delivery_country,
                created_at,
                %s AS export_date,
                %s AS batch_id
            FROM store_order_events
            WHERE DATE(created_at) = %s::DATE
            ORDER BY created_at ASC;
        """

        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, (self.export_date, self.batch_id, self.export_date))
                rows = cur.fetchall()

            duration_ms = int((time.time() - start_time) * 1000)
            row_count = len(rows)

            logger.info(
                f"Successfully extracted {row_count} rows from PostgreSQL",
                extra={
                    "service": config.SERVICE_NAME,
                    "dataset": dataset_name,
                    "stage": "EXTRACT_DB",
                    "batch_id": self.batch_id,
                    "export_date": self.export_date,
                    "row_count": row_count,
                    "duration_ms": duration_ms,
                },
            )

            csv_bytes = self._convert_to_csv(rows)
            return csv_bytes, row_count
        finally:
            conn.close()

    def _convert_to_csv(self, rows: List[Dict]) -> bytes:
        start_time = time.time()
        output = io.StringIO()

        if rows:
            fieldnames = list(rows[0].keys())
            writer = csv.DictWriter(
                output,
                fieldnames=fieldnames,
                quoting=csv.QUOTE_ALL,
                lineterminator="\n"
            )
            writer.writeheader()
            writer.writerows(rows)

        csv_content = output.getvalue()
        # Encode with UTF-8 BOM
        csv_bytes = csv_content.encode("utf-8-sig")

        logger.info(
            f"Formatted CSV buffer with UTF-8 BOM, size: {len(csv_bytes)} bytes",
            extra={
                "service": config.SERVICE_NAME,
                "stage": "WRITE_CSV",
                "batch_id": self.batch_id,
                "export_date": self.export_date,
                "duration_ms": int((time.time() - start_time) * 1000),
            },
        )
        return csv_bytes
