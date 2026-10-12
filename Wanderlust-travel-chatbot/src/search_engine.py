"""
WanderNest Travels RAG Search Engine.

RUBRIC:
- TravelSearchEngine initialized correctly
- search_by_text performs similarity search
- synthesize_response generates grounded answers
- Governance checks integrated
"""

import contextlib
import mlflow

from langchain_openai import (
    AzureChatOpenAI,
    AzureOpenAIEmbeddings,
)

from src.config import Config
from governance.governance_gate import GovernanceGate
from src.vector_store import get_vector_store


class TravelSearchEngine:
    """
    RAG-powered search engine for WanderNest Travels.

    Main responsibilities:

    1. Validate the user query.
    2. Retrieve relevant documents from Azure AI Search.
    3. Generate grounded responses using Azure OpenAI.
    4. Validate the generated response using governance checks.
    5. Record retrieval and generation metrics in MLflow.
    """

    def __init__(self):
        """
        Initialize the search engine.

        Components initialized:

        1. Governance gate
        2. Azure OpenAI chat model
        3. Azure OpenAI embedding model
        4. Azure AI Search vector store
        """

        # -------------------------------------------------------------
        # Step 1: Initialize governance and safety checks
        # -------------------------------------------------------------

        self.governance_gate = GovernanceGate()

        # -------------------------------------------------------------
        # Step 2: Initialize Azure OpenAI chat model
        # -------------------------------------------------------------

        self.llm = AzureChatOpenAI(
            api_key=Config.AZURE_OPENAI_API_KEY,
            azure_endpoint=Config.AZURE_OPENAI_ENDPOINT,
            api_version=Config.AZURE_OPENAI_API_VERSION,
            azure_deployment=(
                Config.AZURE_OPENAI_DEPLOYMENT_NAME
            ),
        )

        # -------------------------------------------------------------
        # Step 3: Initialize Azure OpenAI embedding model
        # -------------------------------------------------------------

        self.embeddings = AzureOpenAIEmbeddings(
            api_key=Config.AZURE_OPENAI_API_KEY,
            azure_endpoint=Config.AZURE_OPENAI_ENDPOINT,
            azure_deployment=(
                Config.AZURE_OPENAI_EMBEDDING_DEPLOYMENT
            ),
            api_version=Config.AZURE_OPENAI_API_VERSION,
        )

        # -------------------------------------------------------------
        # Step 4: Initialize Azure AI Search vector store
        # -------------------------------------------------------------

        self.vector_store = get_vector_store(
            self.embeddings
        )

    @staticmethod
    def _mlflow_run(run_name: str):
        """
        Return an MLflow run context.

        Behavior:

        1. If MLflow is not configured, return a null context.
        2. If another MLflow run is already active, reuse it.
        3. Otherwise, configure MLflow and start a new run.

        Reusing an active run prevents the ingestion pipeline from
        starting a second non-nested run during index verification.
        """

        # -------------------------------------------------------------
        # MLflow is optional
        # -------------------------------------------------------------

        if not Config.MLFLOW_TRACKING_URI:
            return contextlib.nullcontext()

        # -------------------------------------------------------------
        # Reuse an existing MLflow run
        # -------------------------------------------------------------
        # ingestion.py may already have started "document_ingestion".
        # search_by_text() must not start another non-nested run.
        # -------------------------------------------------------------

        active_run = mlflow.active_run()

        if active_run is not None:
            return contextlib.nullcontext(active_run)

        # -------------------------------------------------------------
        # No active run exists, configure MLflow
        # -------------------------------------------------------------

        mlflow.set_tracking_uri(
            Config.MLFLOW_TRACKING_URI
        )

        mlflow.set_experiment(
            Config.MLFLOW_EXPERIMENT_NAME
        )

        # -------------------------------------------------------------
        # Start a standalone MLflow run
        # -------------------------------------------------------------

        return mlflow.start_run(
            run_name=run_name
        )

    def search_by_text(
        self,
        query_text: str,
        k: int = 5,
    ):
        """
        Retrieve relevant travel documents through similarity search.

        Processing steps:

        1. Validate that the query is not empty.
        2. Run input governance checks.
        3. Perform Azure AI Search similarity search.
        4. Record retrieval metrics in MLflow.
        5. Return retrieved documents and the processed query.
        """

        # -------------------------------------------------------------
        # Step 1: Validate the query
        # -------------------------------------------------------------

        if not query_text or not query_text.strip():
            return (
                [],
                "Please enter a travel question.",
            )

        # -------------------------------------------------------------
        # Step 2: Start or reuse an MLflow run
        # -------------------------------------------------------------

        with self._mlflow_run(
            "search_travel_info"
        ):

            print(
                f"DEBUG: Text Query: {query_text}"
            )

            # ---------------------------------------------------------
            # Step 3: Run input governance checks
            # ---------------------------------------------------------

            governance_result = (
                self.governance_gate.validate_input(
                    query_text
                )
            )

            if not governance_result["passed"]:

                if Config.MLFLOW_TRACKING_URI:
                    mlflow.log_param(
                        "governance_status",
                        "blocked",
                    )

                    mlflow.log_metric(
                        "governance_violation_count",
                        len(
                            governance_result[
                                "violations"
                            ]
                        ),
                    )

                return (
                    [],
                    "Query blocked by security checks.",
                )

            # ---------------------------------------------------------
            # Step 4: Log safe retrieval parameters
            # ---------------------------------------------------------

            if Config.MLFLOW_TRACKING_URI:
                mlflow.log_param(
                    "retrieval_top_k",
                    k,
                )

                # Do not log the raw customer query because it could
                # contain PII or other sensitive information.
                mlflow.log_param(
                    "query_length",
                    len(query_text),
                )

            # ---------------------------------------------------------
            # Step 5: Perform similarity search
            # ---------------------------------------------------------

            documents = (
                self.vector_store.similarity_search(
                    query_text,
                    k=k,
                )
            )

            # ---------------------------------------------------------
            # Step 6: Log retrieval result count
            # ---------------------------------------------------------

            if Config.MLFLOW_TRACKING_URI:
                mlflow.log_metric(
                    "results_count",
                    len(documents),
                )

            return documents, query_text

    def synthesize_response(
        self,
        docs,
        user_query: str,
    ) -> str:
        """
        Generate a grounded response from retrieved documents.

        Processing steps:

        1. Handle an empty retrieval result.
        2. Build context from the retrieved documents.
        3. Construct a grounding prompt.
        4. Invoke Azure OpenAI.
        5. Validate the generated output.
        6. Record the final response in MLflow.
        """

        # -------------------------------------------------------------
        # Step 1: Start or reuse an MLflow run
        # -------------------------------------------------------------

        with self._mlflow_run(
            "synthesize_response"
        ):

            # ---------------------------------------------------------
            # Step 2: Handle empty retrieval
            # ---------------------------------------------------------

            if not docs:
                return (
                    "I could not find sufficient information "
                    "in the travel knowledge base to answer "
                    "this question. Please consult an official "
                    "airline, government authority, or "
                    "WanderNest travel specialist."
                )

            # ---------------------------------------------------------
            # Step 3: Build grounded context
            # ---------------------------------------------------------

            context_parts = []

            for index, document in enumerate(
                docs,
                start=1,
            ):
                source = document.metadata.get(
                    "source",
                    "Unknown",
                )

                category = document.metadata.get(
                    "category",
                    "general",
                )

                context_parts.append(
                    f"[Source {index}: {source}]\n"
                    f"Category: {category}\n"
                    f"{document.page_content}"
                )

            context = "\n\n".join(
                context_parts
            )

            # ---------------------------------------------------------
            # Step 4: Create grounding prompt
            # ---------------------------------------------------------

            prompt = f"""
You are a helpful travel-policy assistant for WanderNest Travels.

Answer the customer's question using only the supplied
knowledge-base context.

Mandatory response rules:

1. Do not invent airline policies.
2. Do not invent baggage allowances.
3. Do not invent cancellation charges.
4. Do not invent refund amounts or compensation percentages.
5. Do not invent visa or immigration requirements.
6. Do not claim that live flight, weather, security, visa, or
   geopolitical information is current unless the supplied context
   explicitly confirms it.
7. If the context is insufficient, clearly state that the available
   sources do not contain enough information.
8. Mention the supporting source filename using this format:
   [Source: filename]
9. Separate confirmed policy information from general guidance.
10. Recommend verification with the relevant airline or government
    authority when the matter is time-sensitive.

Knowledge-base context:

{context}

Customer question:

{user_query}

Grounded answer:
"""

            # ---------------------------------------------------------
            # Step 5: Invoke Azure OpenAI
            # ---------------------------------------------------------

            llm_message = self.llm.invoke(
                prompt
            )

            response = llm_message.content

            # Some model integrations can return structured content.
            # Convert non-string content to text before validation.
            if not isinstance(response, str):
                response = str(response)

            # ---------------------------------------------------------
            # Step 6: Validate generated output
            # ---------------------------------------------------------

            governance_result = (
                self.governance_gate.validate_output(
                    response
                )
            )

            if not governance_result["passed"]:

                if Config.MLFLOW_TRACKING_URI:
                    mlflow.log_param(
                        "output_governance_status",
                        "blocked",
                    )

                    mlflow.log_metric(
                        "output_violation_count",
                        len(
                            governance_result[
                                "violations"
                            ]
                        ),
                    )

                return (
                    "A response was generated, but it did "
                    "not pass the required safety and "
                    "compliance checks."
                )

            # ---------------------------------------------------------
            # Step 7: Log safe response metadata
            # ---------------------------------------------------------

            if Config.MLFLOW_TRACKING_URI:
                mlflow.log_param(
                    "output_governance_status",
                    "passed",
                )

                mlflow.log_metric(
                    "response_length",
                    len(response),
                )

                mlflow.log_text(
                    response,
                    "final_response.txt",
                )

            return response