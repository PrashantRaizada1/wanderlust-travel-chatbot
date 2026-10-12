"""
Load, categorize, and split WanderNest travel documents.
"""

from pathlib import Path
from typing import List

import pandas as pd
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.config import Config


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"


class TravelDataLoader:
    """Load travel documents from the data directory."""

    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

    @staticmethod
    def _categorize_document(filename: str) -> str:
        """Categorize a document using its filename."""
        filename_lower = filename.lower()

        # Put the most specific categories first.
        if (
            "air-india" in filename_lower
            or "air india" in filename_lower
            or "ai-schedule" in filename_lower
        ):
            return "air_india_policies"

        if (
            "u.s. department" in filename_lower
            or "department of transportation" in filename_lower
        ):
            return "us_dot_regulations"

        if "refund" in filename_lower:
            return "refund_policies"

        if "privacy" in filename_lower:
            return "privacy_policies"

        if "baggage" in filename_lower:
            return "baggage_policies"

        if (
            "booking" in filename_lower
            or "reservation" in filename_lower
        ):
            return "booking_policies"

        return "general"

    def load_pdfs_from_data_directory(self) -> List:
        """Load PDFs directly from data/."""
        documents = []

        if not DATA_DIR.exists():
            print(f"Warning: {DATA_DIR} does not exist")
            return documents

        pdf_files = sorted(DATA_DIR.glob("*.pdf"))
        print(f"Found {len(pdf_files)} PDF files in data/")

        for pdf_file in pdf_files:
            try:
                loader = PyPDFLoader(str(pdf_file))
                docs = loader.load()
                category = self._categorize_document(
                    pdf_file.name
                )

                for doc in docs:
                    doc.metadata.update(
                        {
                            "source": pdf_file.name,
                            "file_type": "pdf",
                            "category": category,
                        }
                    )

                documents.extend(docs)

                print(
                    f"  Loaded: {pdf_file.name} "
                    f"({len(docs)} pages) "
                    f"- Category: {category}"
                )

            except Exception as exc:
                print(
                    f"  Error loading {pdf_file.name}: {exc}"
                )

        return documents

    def load_csvs_from_data_directory(self) -> List:
        """Convert each row of each CSV to a Document."""
        documents = []

        if not DATA_DIR.exists():
            print(f"Warning: {DATA_DIR} does not exist")
            return documents

        csv_files = sorted(DATA_DIR.glob("*.csv"))
        print(f"Found {len(csv_files)} CSV files in data/")

        for csv_file in csv_files:
            try:
                dataframe = pd.read_csv(csv_file)
                category = self._categorize_document(
                    csv_file.name
                )

                for row_index, row in dataframe.iterrows():
                    content = " | ".join(
                        f"{column}: {value}"
                        for column, value in row.items()
                    )

                    documents.append(
                        Document(
                            page_content=content,
                            metadata={
                                "source": csv_file.name,
                                "file_type": "csv",
                                "category": category,
                                "row_index": int(row_index),
                            },
                        )
                    )

                print(
                    f"  Loaded: {csv_file.name} "
                    f"({len(dataframe)} rows)"
                )

            except Exception as exc:
                print(
                    f"  Error loading {csv_file.name}: {exc}"
                )

        return documents

    def load_all_travel_documents(self) -> List:
        """Load PDFs and CSV files."""
        print("\nLoading travel knowledge base...")
        print("=" * 60)

        documents = []
        documents.extend(
            self.load_pdfs_from_data_directory()
        )
        documents.extend(
            self.load_csvs_from_data_directory()
        )

        if Config.INGESTION_LIMIT > 0:
            documents = documents[
                :Config.INGESTION_LIMIT
            ]

        print("=" * 60)
        print(f"Total documents loaded: {len(documents)}")

        return documents

    def split_documents(
        self,
        documents: List[Document],
    ) -> List:
        """Split documents into overlapping text chunks."""
        print(
            f"\nSplitting {len(documents)} documents..."
        )

        chunks = self.text_splitter.split_documents(
            documents
        )

        # Add stable, visible chunk identifiers.
        for chunk_index, chunk in enumerate(chunks):
            chunk.metadata["chunk_id"] = chunk_index

        average_size = (
            sum(len(chunk.page_content) for chunk in chunks)
            // max(len(chunks), 1)
        )

        print(f"Created {len(chunks)} chunks")
        print(f"Average chunk size: {average_size} chars")

        return chunks


if __name__ == "__main__":
    loader = TravelDataLoader()
    documents = loader.load_all_travel_documents()
    chunks = loader.split_documents(documents)

    print(f"\nTotal chunks: {len(chunks)}")