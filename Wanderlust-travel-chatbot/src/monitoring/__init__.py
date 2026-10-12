"""
Optional MLflow and Azure Monitor configuration.
"""

import mlflow

from src.config import Config


def configure_monitoring():
    """Configure only the monitoring services that are enabled."""
    if Config.MLFLOW_TRACKING_URI:
        try:
            mlflow.set_tracking_uri(
                Config.MLFLOW_TRACKING_URI
            )
            mlflow.set_experiment(
                Config.MLFLOW_EXPERIMENT_NAME
            )

            print(
                "MLflow configured: "
                f"{Config.MLFLOW_TRACKING_URI}"
            )

        except Exception as exc:
            print(
                f"Warning: MLflow setup failed: {exc}"
            )

    if Config.APPLICATIONINSIGHTS_CONNECTION_STRING:
        try:
            from azure.monitor.opentelemetry import (
                configure_azure_monitor,
            )

            configure_azure_monitor(
                connection_string=(
                    Config
                    .APPLICATIONINSIGHTS_CONNECTION_STRING
                )
            )

            print("Azure Monitor configured.")

    # -----------------------------------------------------------------
    # Azure Application Insights
    # -----------------------------------------------------------------


        except Exception as exc:
            print(
                "Warning: Azure Monitor setup "
                f"failed: {exc}"
            )


configure_monitoring()