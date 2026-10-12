"""
Application configuration for WanderNest Travels.

Configuration values are loaded from environment variables
and the local .env file using Pydantic Settings.
"""

from typing import Optional

from dotenv import load_dotenv
from pydantic import Field, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


# ---------------------------------------------------------------------
# Load environment variables from .env
# ---------------------------------------------------------------------

load_dotenv()


# ---------------------------------------------------------------------
# Pydantic Settings
# ---------------------------------------------------------------------

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Sensitive values such as API keys should be stored in .env
    and must not be hard-coded in the application.
    """
    # -----------------------------------------------------------------
    # Document Chunking
    # -----------------------------------------------------------------

    chunk_size: int = 1000
    chunk_overlap: int = 200

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # -----------------------------------------------------------------
    # Azure OpenAI
    # -----------------------------------------------------------------

    azure_openai_api_key: str

    azure_openai_endpoint: HttpUrl

    azure_openai_api_version: str = "2024-10-21"

    azure_openai_chat_deployment: str = Field(
        validation_alias="AZURE_OPENAI_DEPLOYMENT_NAME"
    )

    azure_openai_embedding_deployment: str = Field(
        validation_alias="AZURE_OPENAI_EMBEDDING_DEPLOYMENT"
    )

    # -----------------------------------------------------------------
    # Vector Store
    # -----------------------------------------------------------------

    # Supported values expected by the project/test suite:
    # "chroma"
    # "azure_search"
    vector_store_type: str = "azure_search"

    # -----------------------------------------------------------------
    # Azure AI Search
    # -----------------------------------------------------------------

    azure_search_endpoint: HttpUrl

    azure_search_admin_key: str = Field(
        validation_alias="AZURE_SEARCH_KEY"
    )

    azure_search_index_name: str = "wandernest-travel-index"

    # -----------------------------------------------------------------
    # Azure AI Content Safety
    # -----------------------------------------------------------------

    azure_content_safety_endpoint: Optional[HttpUrl] = None

    azure_content_safety_key: Optional[str] = None

    # -----------------------------------------------------------------
    # Azure Storage
    # -----------------------------------------------------------------

    azure_storage_connection_string: Optional[str] = None

    azure_storage_container_name: str = "travel-documents"

        # -----------------------------------------------------------------
    # MLflow
    # -----------------------------------------------------------------

    mlflow_tracking_uri: str = "http://localhost:5000"

    mlflow_experiment_name: str = "wandernest-travel-rag"

    # -----------------------------------------------------------------
    # Azure Application Insights
    # -----------------------------------------------------------------

    applicationinsights_connection_string: str = ""

    # -----------------------------------------------------------------
    # Ingestion
    # -----------------------------------------------------------------

    ingestion_limit: int = 0
    
    # -----------------------------------------------------------------
    # Helper methods
    # -----------------------------------------------------------------

    def content_safety_enabled(self) -> bool:
        """
        Return True only when both the Content Safety endpoint
        and API key are configured.
        """

        endpoint_present = (
            self.azure_content_safety_endpoint is not None
        )

        key_present = bool(
            self.azure_content_safety_key
        )

        return endpoint_present and key_present


# ---------------------------------------------------------------------
# Load Settings
# ---------------------------------------------------------------------

_settings = Settings()


# ---------------------------------------------------------------------
# Backward-compatible Config interface
# ---------------------------------------------------------------------

class Config:
    """
    Application-wide configuration interface.

    Existing modules can access configuration through attributes such as:

        Config.AZURE_OPENAI_API_KEY
        Config.AZURE_SEARCH_ENDPOINT
        Config.VECTOR_STORE_TYPE
        Config.MLFLOW_TRACKING_URI
    """
    # -----------------------------------------------------------------
    # Document Chunking
    # -----------------------------------------------------------------

    CHUNK_SIZE = _settings.chunk_size
    CHUNK_OVERLAP = _settings.chunk_overlap
    # -----------------------------------------------------------------
    # Azure OpenAI
    # -----------------------------------------------------------------

    AZURE_OPENAI_API_KEY = (
        _settings.azure_openai_api_key
    )

    AZURE_OPENAI_ENDPOINT = str(
        _settings.azure_openai_endpoint
    ).rstrip("/")

    AZURE_OPENAI_API_VERSION = (
        _settings.azure_openai_api_version
    )

    AZURE_OPENAI_DEPLOYMENT_NAME = (
        _settings.azure_openai_chat_deployment
    )

    AZURE_OPENAI_EMBEDDING_DEPLOYMENT = (
        _settings.azure_openai_embedding_deployment
    )

    # -----------------------------------------------------------------
    # Vector Store
    # -----------------------------------------------------------------

    VECTOR_STORE_TYPE = (
        _settings.vector_store_type
    )

    # -----------------------------------------------------------------
    # Azure AI Search
    # -----------------------------------------------------------------

    AZURE_SEARCH_ENDPOINT = str(
        _settings.azure_search_endpoint
    ).rstrip("/")

    AZURE_SEARCH_KEY = (
        _settings.azure_search_admin_key
    )

    AZURE_SEARCH_INDEX_NAME = (
        _settings.azure_search_index_name
    )

    # -----------------------------------------------------------------
    # Azure AI Content Safety
    # -----------------------------------------------------------------

    AZURE_CONTENT_SAFETY_ENDPOINT = (
        str(
            _settings.azure_content_safety_endpoint
        ).rstrip("/")
        if _settings.azure_content_safety_endpoint
        else None
    )

    AZURE_CONTENT_SAFETY_KEY = (
        _settings.azure_content_safety_key
    )
    # ------------------------------------------------------------
    # Azure Application Insights
    # ------------------------------------------------------------

    APPLICATIONINSIGHTS_CONNECTION_STRING = (
    _settings.applicationinsights_connection_string
    )
    CONTENT_SAFETY_ENABLED = (
        _settings.content_safety_enabled()
    )

    # -----------------------------------------------------------------
    # Azure Storage
    # -----------------------------------------------------------------

    AZURE_STORAGE_CONNECTION_STRING = (
        _settings.azure_storage_connection_string
    )

    AZURE_STORAGE_CONTAINER_NAME = (
        _settings.azure_storage_container_name
    )

    # -----------------------------------------------------------------
    # MLflow
    # -----------------------------------------------------------------

    MLFLOW_TRACKING_URI = (
        _settings.mlflow_tracking_uri
    )

    MLFLOW_EXPERIMENT_NAME = (
        _settings.mlflow_experiment_name
    )

    # -----------------------------------------------------------------
    # Ingestion
    # -----------------------------------------------------------------

    INGESTION_LIMIT = (
        _settings.ingestion_limit
    )