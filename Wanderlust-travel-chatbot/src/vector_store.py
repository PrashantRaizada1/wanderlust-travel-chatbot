"""
Azure AI Search vector-store configuration.
"""

from langchain_community.vectorstores import AzureSearch

from src.config import Config


def get_vector_store(embedding_function):
    """Create and return the Azure AI Search vector store."""
    endpoint = Config.AZURE_SEARCH_ENDPOINT
    key = Config.AZURE_SEARCH_KEY
    index_name = Config.AZURE_SEARCH_INDEX_NAME

    if not endpoint:
        raise ValueError(
            "AZURE_SEARCH_ENDPOINT must be set."
        )

    if not key:
        raise ValueError(
            "AZURE_SEARCH_KEY must be set."
        )

    if not index_name:
        raise ValueError(
            "AZURE_SEARCH_INDEX_NAME must be set."
        )

    vector_store = AzureSearch(
        azure_search_endpoint=endpoint,
        azure_search_key=key,
        index_name=index_name,
        embedding_function=embedding_function.embed_query,
    )

    print(
        "Initialized Azure AI Search index "
        f"'{index_name}'"
    )

    return vector_store