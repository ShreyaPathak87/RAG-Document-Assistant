from langchain_community.vectorstores import Chroma
from utils.embeddings import get_embeddings

CHROMA_DB = "chroma_db"

def store_documents(chunks):
    embeddings = get_embeddings()

    # Remove duplicate chunks based on text
    unique_chunks = []
    seen = set()

    for chunk in chunks:
        if chunk.page_content not in seen:
            unique_chunks.append(chunk)
            seen.add(chunk.page_content)

    # Create or update Chroma database
    vector_store = Chroma.from_documents(
        documents=unique_chunks,
        embedding=embeddings,
        persist_directory=CHROMA_DB
    )

    vector_store.persist()

    return vector_store