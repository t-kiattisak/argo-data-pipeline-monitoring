import os
import time
from typing import Dict
from src.config import config
from src.logger import setup_logger

logger = setup_logger("storage")


class StorageHandler:
    def __init__(self, batch_id: str, export_date: str):
        self.batch_id = batch_id
        self.export_date = export_date
        self.backend = config.STORAGE_BACKEND.lower()

        if self.backend in ["minio", "s3"]:
            import boto3
            from botocore.config import Config

            client_kwargs = {
                "service_name": "s3",
                "region_name": config.AWS_REGION,
                "config": Config(signature_version="s3v4"),
            }
            if config.AWS_ENDPOINT_URL:
                client_kwargs["endpoint_url"] = config.AWS_ENDPOINT_URL
            if config.AWS_ACCESS_KEY_ID:
                client_kwargs["aws_access_key_id"] = config.AWS_ACCESS_KEY_ID
            if config.AWS_SECRET_ACCESS_KEY:
                client_kwargs["aws_secret_access_key"] = config.AWS_SECRET_ACCESS_KEY

            self.s3_client = boto3.client(**client_kwargs)

            # Auto-ensure bucket exists
            try:
                self.s3_client.create_bucket(Bucket=config.S3_BUCKET_NAME)
            except Exception:
                pass  # Bucket may already exist

    def save(self, file_bytes: bytes, dataset_name: str) -> Dict[str, str]:
        """
        Saves exported CSV to either Local Filesystem or Local MinIO (S3 compatible).
        """
        if self.backend == "local":
            return self._save_to_local_disk(file_bytes, dataset_name)
        else:
            return self._save_to_minio_or_s3(file_bytes, dataset_name)

    def _save_to_local_disk(self, file_bytes: bytes, dataset_name: str) -> Dict[str, str]:
        start_time = time.time()
        
        target_dir = os.path.join(
            config.LOCAL_STORAGE_DIR,
            "datasets",
            dataset_name,
            f"year={self.export_date[:4]}",
            f"month={self.export_date[5:7]}",
        )
        os.makedirs(target_dir, exist_ok=True)

        filename = f"{dataset_name}_{self.export_date}.csv"
        file_path = os.path.join(target_dir, filename)

        with open(file_path, "wb") as f:
            f.write(file_bytes)

        duration_ms = int((time.time() - start_time) * 1000)

        logger.info(
            f"Saved {dataset_name} to Local Filesystem successfully",
            extra={
                "service": config.SERVICE_NAME,
                "dataset": dataset_name,
                "stage": "SAVE_LOCAL_STORAGE",
                "batch_id": self.batch_id,
                "export_date": self.export_date,
                "duration_ms": duration_ms,
                "extra_fields": {
                    "storage_backend": "local",
                    "file_path": os.path.abspath(file_path),
                    "file_size_bytes": len(file_bytes),
                },
            },
        )

        return {
            "storage_backend": "local",
            "file_path": os.path.abspath(file_path),
            "file_size_bytes": str(len(file_bytes)),
        }

    def _save_to_minio_or_s3(self, file_bytes: bytes, dataset_name: str) -> Dict[str, str]:
        start_time = time.time()
        s3_key = f"datasets/{dataset_name}/year={self.export_date[:4]}/month={self.export_date[5:7]}/{dataset_name}_{self.export_date}.csv"

        self.s3_client.put_object(
            Bucket=config.S3_BUCKET_NAME,
            Key=s3_key,
            Body=file_bytes,
            ContentType="text/csv; charset=utf-8",
        )

        presigned_url = self.s3_client.generate_presigned_url(
            ClientMethod="get_object",
            Params={"Bucket": config.S3_BUCKET_NAME, "Key": s3_key},
            ExpiresIn=config.PRESIGNED_URL_EXPIRY_SECONDS,
        )

        duration_ms = int((time.time() - start_time) * 1000)

        logger.info(
            f"Uploaded {dataset_name} to MinIO/S3 successfully",
            extra={
                "service": config.SERVICE_NAME,
                "dataset": dataset_name,
                "stage": "UPLOAD_S3",
                "batch_id": self.batch_id,
                "export_date": self.export_date,
                "duration_ms": duration_ms,
                "extra_fields": {
                    "storage_backend": self.backend,
                    "s3_bucket": config.S3_BUCKET_NAME,
                    "s3_key": s3_key,
                    "file_size_bytes": len(file_bytes),
                    "presigned_url": presigned_url,
                },
            },
        )

        return {
            "storage_backend": self.backend,
            "s3_bucket": config.S3_BUCKET_NAME,
            "s3_key": s3_key,
            "presigned_url": presigned_url,
            "file_size_bytes": str(len(file_bytes)),
        }
