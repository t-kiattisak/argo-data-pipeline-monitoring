import time
from typing import Dict
import boto3
from botocore.config import Config
from src.config import config
from src.logger import setup_logger

logger = setup_logger("s3_uploader")


class S3Uploader:
    def __init__(self, batch_id: str, export_date: str):
        self.batch_id = batch_id
        self.export_date = export_date
        
        boto_config = Config(signature_version="s3v4")
        client_kwargs = {
            "service_name": "s3",
            "region_name": config.AWS_REGION,
            "config": boto_config,
        }
        
        # Local testing with MinIO or specific endpoint
        if config.AWS_ENDPOINT_URL:
            client_kwargs["endpoint_url"] = config.AWS_ENDPOINT_URL
            client_kwargs["aws_access_key_id"] = config.AWS_ACCESS_KEY_ID or "minioadmin"
            client_kwargs["aws_secret_access_key"] = config.AWS_SECRET_ACCESS_KEY or "minioadmin"

        self.s3_client = boto3.client(**client_kwargs)

    def upload_file(self, file_bytes: bytes, dataset_name: str) -> Dict[str, str]:
        """
        Uploads CSV bytes to AWS S3 using SSE-KMS encryption and generates
        a 2-hour Presigned URL.
        """
        start_time = time.time()
        s3_key = f"datasets/{dataset_name}/year={self.export_date[:4]}/month={self.export_date[5:7]}/{dataset_name}_{self.export_date}.csv"

        put_params = {
            "Bucket": config.S3_BUCKET_NAME,
            "Key": s3_key,
            "Body": file_bytes,
            "ContentType": "text/csv; charset=utf-8",
        }

        # Apply SSE-KMS only when not using local MinIO
        if not config.AWS_ENDPOINT_URL and config.KMS_KEY_ID:
            put_params["ServerSideEncryption"] = "aws:kms"
            put_params["SSEKMSKeyId"] = config.KMS_KEY_ID

        # Upload Object
        self.s3_client.put_object(**put_params)

        upload_duration_ms = int((time.time() - start_time) * 1000)

        # Generate 2-hour Presigned URL
        presigned_url = self.s3_client.generate_presigned_url(
            ClientMethod="get_object",
            Params={"Bucket": config.S3_BUCKET_NAME, "Key": s3_key},
            ExpiresIn=config.PRESIGNED_URL_EXPIRY_SECONDS,
        )

        logger.info(
            f"Successfully uploaded {dataset_name} to S3 and generated presigned URL",
            extra={
                "service": config.SERVICE_NAME,
                "dataset": dataset_name,
                "stage": "UPLOAD_S3",
                "batch_id": self.batch_id,
                "export_date": self.export_date,
                "duration_ms": upload_duration_ms,
                "extra_fields": {
                    "s3_bucket": config.S3_BUCKET_NAME,
                    "s3_key": s3_key,
                    "file_size_bytes": len(file_bytes),
                    "presigned_url_ttl": config.PRESIGNED_URL_EXPIRY_SECONDS,
                },
            },
        )

        return {
            "s3_bucket": config.S3_BUCKET_NAME,
            "s3_key": s3_key,
            "presigned_url": presigned_url,
            "file_size_bytes": str(len(file_bytes)),
        }
