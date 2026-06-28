import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="AI Document Assistant",
    page_icon="📄",
    layout="wide"
)

st.title("🤖 AI-Powered Document Assistant (RAG)")
st.write("Upload a PDF and ask questions about its contents.")

# ==========================
# Sidebar
# ==========================

with st.sidebar:

    st.header("📄 Upload PDF")

    uploaded_file = st.file_uploader(
        "Choose a PDF",
        type=["pdf"]
    )

    if uploaded_file is not None:

        st.write(f"**File:** {uploaded_file.name}")
        st.write(f"**Size:** {uploaded_file.size/1024:.2f} KB")

        if st.button("Upload PDF"):

            with st.spinner("Processing PDF..."):

                response = requests.post(
                    f"{API_URL}/upload",
                    files={
                        "file": (
                            uploaded_file.name,
                            uploaded_file.getvalue(),
                            "application/pdf"
                        )
                    }
                )

            if response.status_code == 200:
                st.success("✅ PDF uploaded successfully!")
            else:
                st.error(response.text)

    st.divider()

    st.subheader("ℹ️ Instructions")

    st.write("""
    1. Upload a PDF.
    2. Wait for processing.
    3. Ask questions in the main window.
    """)

# ==========================
# Main Chat Area
# ==========================

st.header("💬 Ask Questions")

question = st.text_input(
    "Enter your question"
)

if st.button("Ask"):

    if question.strip() == "":
        st.warning("Please enter a question.")

    else:

        with st.spinner("Thinking..."):

            response = requests.post(
                f"{API_URL}/ask",
                json={
                    "question": question
                }
            )

        if response.status_code == 200:

            result = response.json()

            st.subheader("🤖 Answer")
            st.success(result["answer"])

            st.subheader("📄 Source")
            st.write(result["sources"])

            with st.expander("🔍 Retrieved Chunk"):
                for chunk in result["retrieved_chunks"]:
                    st.write(chunk)

        else:
            st.error(response.text)