"""
Streamlit interface for WanderNest Travels.
"""

import os
import sys
import time

sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
        )
    )
)

import streamlit as st

from src.search_engine import TravelSearchEngine
import src.monitoring  # noqa: F401


st.set_page_config(
    page_title="WanderNest Travels - AI Assistant",
    page_icon="✈️",
    layout="wide",
)

st.title("✈️ WanderNest Travels AI Assistant")
st.markdown(
    "Get grounded answers about airline policies, "
    "baggage, refunds, and travel requirements."
)


@st.cache_resource
def get_engine():
    """Initialize and cache the search engine."""
    try:
        return TravelSearchEngine()
    except Exception as exc:
        st.error(
            f"Failed to initialize the search engine: {exc}"
        )
        return None


def display_results(results, generated_response):
    """Display answer and retrieved source documents."""
    st.success(
        f"Retrieved {len(results)} relevant documents."
    )

    st.subheader("🤖 Grounded Answer")
    with st.container(border=True):
        st.markdown(generated_response)

    if results:
        with st.expander(
            "📚 View Source Documents"
        ):
            for index, document in enumerate(
                results,
                start=1,
            ):
                source = document.metadata.get(
                    "source",
                    "Unknown",
                )
                category = document.metadata.get(
                    "category",
                    "N/A",
                )

                st.markdown(
                    f"**{index}. Source: {source}**"
                )
                st.markdown(
                    f"*Category: {category}*"
                )
                st.write(
                    document.page_content[:500]
                    + "..."
                )
                st.divider()
    else:
        st.warning(
            "No supporting documents were found."
        )


engine = get_engine()

with st.sidebar:
    st.header("ℹ️ About")

    st.info(
        """
        **WanderNest Travels AI Assistant**

        This chatbot supports:

        - Flight policies
        - Baggage rules
        - Visa-information guidance
        - Booking and cancellation policies
        - Refund-policy queries

        Responses are generated from the indexed knowledge base.
        """
    )

    st.header("📊 Statistics")

    if "query_count" not in st.session_state:
        st.session_state.query_count = 0

    st.metric(
        "Total Queries",
        st.session_state.query_count,
    )

    if st.button("Clear application cache"):
        st.cache_resource.clear()
        st.rerun()


st.markdown("### 🔍 Ask a Travel Question")

example_columns = st.columns(3)

if example_columns[0].button("✈️ Baggage Rules"):
    st.session_state.query_text = (
        "What are the baggage allowance rules "
        "for international flights?"
    )

if example_columns[1].button("📋 Visa Information"):
    st.session_state.query_text = (
        "What official sources should I verify "
        "before travelling from India to the UK?"
    )

if example_columns[2].button("🎫 Cancellation Policy"):
    st.session_state.query_text = (
        "What is the cancellation policy "
        "for Air India flights?"
    )


if "query_text" not in st.session_state:
    st.session_state.query_text = ""
query_text = st.text_input(
    "Enter your travel question",
    key="query_text",
    placeholder=(
        "Example: What are the baggage rules "
        "for BLR to LON?"
    ),
    label_visibility="collapsed",
)

search_button = st.button(
    "🔍 Search",
    use_container_width=True,
    type="primary",
)

if search_button:
    if not query_text.strip():
        st.warning(
            "Please enter a travel question."
        )

    elif engine is None:
        st.error(
            "The search engine is unavailable. "
            "Check Azure configuration."
        )

    else:
        st.session_state.query_count += 1

        with st.spinner(
            "Searching the travel knowledge base..."
        ):
            start_time = time.perf_counter()

            try:
                results, processed_query = (
                    engine.search_by_text(
                        query_text,
                        k=5,
                    )
                )

                if not results and processed_query.startswith(
                    "Query blocked"
                ):
                    st.error(processed_query)

                else:
                    generated_response = (
                        engine.synthesize_response(
                            results,
                            query_text,
                        )
                    )

                    elapsed = (
                        time.perf_counter()
                        - start_time
                    )

                    st.caption(
                        f"Completed in {elapsed:.2f} seconds"
                    )

                    display_results(
                        results,
                        generated_response,
                    )

            except Exception as exc:
                st.error(f"Search failed: {exc}")
                st.info(
                    "Please rephrase your question "
                    "or contact support."
                )