"""
Document-ingestion pipeline.
"""

import time
import mlflow

from tqdm import tqdm

from src.config import Config
from src.data_loader import TravelDataLoader
from src.search_engine import TravelSearchEngine


def ingest_travel_documents():
    """Load, split, index, and verify travel documents."""
    print("\nStarting Travel Document Ingestion")
    print("=" * 70)

    loader = TravelDataLoader()

    try:
        engine = TravelSearchEngine()
    except Exception as exc:
        print(
            f"Failed to initialize search engine: {exc}"
        )
        return 1

    mlflow_active = False

    if Config.MLFLOW_TRACKING_URI:
        try:
            mlflow.set_tracking_uri(
                Config.MLFLOW_TRACKING_URI
            )
            mlflow.set_experiment(
                Config.MLFLOW_EXPERIMENT_NAME
            )
            mlflow.start_run(
                run_name="document_ingestion"
            )
            mlflow_active = True
        except Exception as exc:
            print(f"MLflow disabled: {exc}")

    try:
        documents = (
            loader.load_all_travel_documents()
        )

        if not documents:
            print("No documents found in data/.")
            return 1

        chunks = loader.split_documents(documents)

        if not chunks:
            print("No chunks were created.")
            return 1

        print(
            f"\nTotal chunks to index: {len(chunks)}"
        )

        if mlflow_active:
            mlflow.log_param(
                "total_source_documents",
                len(documents),
            )
            mlflow.log_param(
                "total_chunks",
                len(chunks),
            )
            mlflow.log_param(
                "chunk_size",
                Config.CHUNK_SIZE,
            )
            mlflow.log_param(
                "chunk_overlap",
                Config.CHUNK_OVERLAP,
            )

        batch_size = 50
        total_batches = (
            len(chunks) + batch_size - 1
        ) // batch_size

        ingested_count = 0
        failed_count = 0

        print(
            "\nIndexing documents in Azure AI Search..."
        )

        for start in tqdm(
            range(0, len(chunks), batch_size),
            desc="Indexing",
            total=total_batches,
        ):
            batch = chunks[
                start:start + batch_size
            ]

            try:
                engine.vector_store.add_documents(
                    batch
                )
                ingested_count += len(batch)

                # Small pause to reduce throttling risk.
                time.sleep(0.25)

            except Exception as exc:
                failed_count += len(batch)
                batch_number = (
                    start // batch_size
                ) + 1

                print(
                    f"Batch {batch_number} failed: {exc}"
                )

        print("\nIngestion completed")
        print(
            f"Successfully indexed: {ingested_count}"
        )
        print(f"Failed: {failed_count}")

        if mlflow_active:
            mlflow.log_metric(
                "ingested_count",
                ingested_count,
            )
            mlflow.log_metric(
                "failed_count",
                failed_count,
            )

        print("\nVerifying the index...")

        test_query = (
            "What is the Air India refund policy?"
        )

        results, _ = engine.search_by_text(
            test_query,
            k=3,
        )

        if not results:
            print(
                "Index verification returned no results."
            )
            return 1

        print("Index verification successful.")
        print(f"Retrieved {len(results)} documents")

        return 0

    except Exception as exc:
        print(f"Ingestion failed: {exc}")
        return 1

    finally:
        if mlflow_active:
            mlflow.end_run()


if __name__ == "__main__":
    raise SystemExit(
        ingest_travel_documents()
    )