import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Pipeline Settings
    SERVICE_NAME: str = "batch-data-extractor"
    EXPORT_DATE: str = ""  # e.g., 2026-09-17, defaults to yesterday if empty

    # Storage Backend: 'local' หรือ 'minio' (หรือ 's3')
    STORAGE_BACKEND: str = "local"
    LOCAL_STORAGE_DIR: str = "./data/storage"

    # PostgreSQL Database
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "appdb"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgrespassword"

    # MinIO / S3 Configuration (ใช้เมื่อ STORAGE_BACKEND=minio หรือ s3)
    AWS_REGION: str = "us-east-1"
    AWS_ENDPOINT_URL: str = "http://localhost:9000"  # MinIO endpoint
    AWS_ACCESS_KEY_ID: str = "minioadmin"
    AWS_SECRET_ACCESS_KEY: str = "minioadmin"
    S3_BUCKET_NAME: str = "data-lake-bucket"
    PRESIGNED_URL_EXPIRY_SECONDS: int = 7200  # 2 hours

    # Downstream API Gateway Webhook (Optional)
    API_GATEWAY_WEBHOOK_URL: str = "http://localhost:8000/events/v1/batch-completed"
    ENABLE_WEBHOOK: bool = False
    JWT_SECRET_KEY: str = "demo-secret-key"
    JWT_ALGORITHM: str = "HS256"


config = AppConfig()
