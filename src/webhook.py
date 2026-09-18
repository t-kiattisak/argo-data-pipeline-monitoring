import time
from datetime import datetime, timezone, timedelta
from typing import Any, Dict
import jwt
import requests
from src.config import config
from src.logger import setup_logger

logger = setup_logger("webhook")


class WebhookNotifier:
    def __init__(self, batch_id: str, export_date: str):
        self.batch_id = batch_id
        self.export_date = export_date

    def generate_jwt_token(self) -> str:
        payload = {
            "iss": config.SERVICE_NAME,
            "sub": "batch-completion-event",
            "batch_id": self.batch_id,
            "iat": datetime.now(timezone.utc),
            "exp": datetime.now(timezone.utc) + timedelta(minutes=15),
        }
        return jwt.encode(payload, config.JWT_SECRET_KEY, algorithm=config.JWT_ALGORITHM)

    def trigger_downstream(self, payload_data: Dict[str, Any]) -> int:
        """
        Sends an authenticated HTTP POST webhook to API Gateway.
        """
        start_time = time.time()
        token = self.generate_jwt_token()

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-Batch-ID": self.batch_id,
        }

        body = {
            "batch_id": self.batch_id,
            "export_date": self.export_date,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "datasets": payload_data,
        }

        response = requests.post(
            config.API_GATEWAY_WEBHOOK_URL,
            json=body,
            headers=headers,
            timeout=10,
        )

        duration_ms = int((time.time() - start_time) * 1000)

        if response.status_code in [200, 201, 202]:
            logger.info(
                f"Successfully triggered downstream webhook (Status: {response.status_code})",
                extra={
                    "service": config.SERVICE_NAME,
                    "stage": "POST_WEBHOOK",
                    "batch_id": self.batch_id,
                    "export_date": self.export_date,
                    "duration_ms": duration_ms,
                    "extra_fields": {"http_status": response.status_code},
                },
            )
        else:
            logger.error(
                f"Downstream webhook failed (Status: {response.status_code}, Response: {response.text})",
                extra={
                    "service": config.SERVICE_NAME,
                    "stage": "POST_WEBHOOK",
                    "batch_id": self.batch_id,
                    "export_date": self.export_date,
                    "duration_ms": duration_ms,
                    "extra_fields": {"http_status": response.status_code},
                },
            )
            response.raise_for_status()

        return response.status_code
