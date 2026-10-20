from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import urlparse

from pydantic import BaseModel, Field
from dotenv import load_dotenv


load_dotenv(Path(__file__).resolve().parents[1] / ".env")


class Settings(BaseModel):
    app_name: str = "Product AI Agent"
    app_version: str = "0.1.0"
    debug: bool = False
    max_upload_size_bytes: int = Field(default=5 * 1024 * 1024)
    supported_marketplaces: tuple[str, ...] = ("amazon", "tiktok", "ebay", "shopify")
    output_dir: str = "output"
    product_store_dir: str = "output/products"
    import_store_dir: str = "output/imports"
    local_output_enabled: bool = False
    auth_enabled: bool = False
    jwt_access_secret: str | None = None
    mongodb_enabled: bool = False
    mongodb_uri: str | None = None
    mongodb_db_name: str = "product_ai_agent"
    mongodb_products_collection: str = "product_ai_products"
    mongodb_imports_collection: str = "product_ai_imports"
    mongodb_runs_collection: str = "product_ai_runs"
    mongodb_users_collection: str = "product_ai_users"
    openai_enabled: bool = False
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o"
    openai_image_model: str = "gpt-image-1"
    openai_text_enabled: bool = False
    openai_image_enabled: bool = False
    gemini_enabled: bool = False
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-2.5-flash"
    gemini_image_model: str = "gemini-2.5-flash-image"
    gemini_text_enabled: bool = False
    gemini_image_enabled: bool = False
    text_provider_preference: str = "auto"
    image_provider_preference: str = "auto"
    gemini_api_base_url: str = "https://generativelanguage.googleapis.com/v1beta"
    aws_region: str | None = None
    aws_s3_bucket: str | None = None
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None
    aws_s3_prefix: str = "product-ai-agent"
    market_research_realtime_enabled: bool = False
    ebay_research_enabled: bool = False
    ebay_client_id: str | None = None
    ebay_client_secret: str | None = None
    ebay_marketplace_id: str = "EBAY_US"
    ebay_api_base_url: str = "https://api.ebay.com"
    ebay_identity_base_url: str = "https://api.ebay.com"
    ebay_search_limit: int = 5


def get_settings() -> Settings:
    mongodb_uri = os.getenv("MONGODB_URI")
    mongodb_enabled_default = "true" if mongodb_uri else "false"
    mongodb_db_name = os.getenv("MONGODB_DB_NAME") or _db_name_from_mongodb_uri(mongodb_uri) or "product_ai_agent"
    openai_legacy_enabled = os.getenv("OPENAI_ENABLED", "false").lower() == "true"
    gemini_legacy_enabled = os.getenv("GEMINI_ENABLED", "false").lower() == "true"
    openai_text_enabled = os.getenv("OPENAI_TEXT_ENABLED", str(openai_legacy_enabled)).lower() == "true"
    openai_image_enabled = os.getenv("OPENAI_IMAGE_ENABLED", str(openai_legacy_enabled)).lower() == "true"
    gemini_text_enabled = os.getenv("GEMINI_TEXT_ENABLED", str(gemini_legacy_enabled)).lower() == "true"
    gemini_image_enabled = os.getenv("GEMINI_IMAGE_ENABLED", str(gemini_legacy_enabled)).lower() == "true"
    return Settings(
        debug=os.getenv("DEBUG", "false").lower() == "true",
        max_upload_size_bytes=int(
            os.getenv("MAX_UPLOAD_SIZE_BYTES", str(5 * 1024 * 1024))
        ),
        output_dir=os.getenv("OUTPUT_DIR", "output"),
        product_store_dir=os.getenv("PRODUCT_STORE_DIR", "output/products"),
        import_store_dir=os.getenv("IMPORT_STORE_DIR", "output/imports"),
        local_output_enabled=os.getenv("LOCAL_OUTPUT_ENABLED", "false").lower() == "true",
        auth_enabled=os.getenv("AUTH_ENABLED", "false").lower() == "true",
        jwt_access_secret=os.getenv("JWT_ACCESS_SECRET"),
        mongodb_enabled=os.getenv("MONGODB_ENABLED", mongodb_enabled_default).lower() == "true",
        mongodb_uri=mongodb_uri,
        mongodb_db_name=mongodb_db_name,
        mongodb_products_collection=os.getenv("MONGODB_PRODUCTS_COLLECTION", "product_ai_products"),
        mongodb_imports_collection=os.getenv("MONGODB_IMPORTS_COLLECTION", "product_ai_imports"),
        mongodb_runs_collection=os.getenv("MONGODB_RUNS_COLLECTION", "product_ai_runs"),
        mongodb_users_collection=os.getenv("MONGODB_USERS_COLLECTION", "product_ai_users"),
        openai_enabled=openai_legacy_enabled or openai_text_enabled or openai_image_enabled,
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4o"),
        openai_image_model=os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-1"),
        openai_text_enabled=openai_text_enabled,
        openai_image_enabled=openai_image_enabled,
        gemini_enabled=gemini_legacy_enabled or gemini_text_enabled or gemini_image_enabled,
        gemini_api_key=os.getenv("GEMINI_API_KEY"),
        gemini_model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
        gemini_image_model=os.getenv("GEMINI_IMAGE_MODEL", "gemini-2.5-flash-image"),
        gemini_text_enabled=gemini_text_enabled,
        gemini_image_enabled=gemini_image_enabled,
        text_provider_preference=os.getenv("TEXT_PROVIDER_PREFERENCE", "auto").strip().lower(),
        image_provider_preference=os.getenv("IMAGE_PROVIDER_PREFERENCE", "auto").strip().lower(),
        gemini_api_base_url=os.getenv("GEMINI_API_BASE_URL", "https://generativelanguage.googleapis.com/v1beta"),
        aws_region=os.getenv("AWS_REGION"),
        aws_s3_bucket=os.getenv("AWS_S3_BUCKET"),
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        aws_s3_prefix=os.getenv("AWS_S3_PREFIX", "product-ai-agent"),
        market_research_realtime_enabled=os.getenv("MARKET_RESEARCH_REALTIME_ENABLED", "false").lower() == "true",
        ebay_research_enabled=os.getenv("EBAY_RESEARCH_ENABLED", "false").lower() == "true",
        ebay_client_id=os.getenv("EBAY_CLIENT_ID"),
        ebay_client_secret=os.getenv("EBAY_CLIENT_SECRET"),
        ebay_marketplace_id=os.getenv("EBAY_MARKETPLACE_ID", "EBAY_US"),
        ebay_api_base_url=os.getenv("EBAY_API_BASE_URL", "https://api.ebay.com"),
        ebay_identity_base_url=os.getenv("EBAY_IDENTITY_BASE_URL", "https://api.ebay.com"),
        ebay_search_limit=int(os.getenv("EBAY_SEARCH_LIMIT", "5")),
    )


def _db_name_from_mongodb_uri(mongodb_uri: str | None) -> str | None:
    if not mongodb_uri:
        return None
    path = urlparse(mongodb_uri).path.strip("/")
    if not path:
        return None
    return path.split("/", 1)[0] or None
