from langchain_community.vectorstores import Chroma
from utils.embeddings import get_embeddings

CHROMA_DB = "chroma_db"

def store_documents(chunks):
    embeddings = get_embeddings()

    # Remove duplicate chunks
    unique_chunks = []
    seen = set()

    for chunk in chunks:
        if chunk.page_content not in seen:
            unique_chunks.append(chunk)
            seen.add(chunk.page_content)

    # STEP 1: Load existing DB (NOT recreate)
    vector_store = Chroma(
        persist_directory=CHROMA_DB,
        embedding_function=embeddings
    )

    # STEP 2: ADD new documents only (not rebuild)
    vector_store.add_documents(unique_chunks)

    # STEP 3: Persist safely
    vector_store.persist()

    return vector_store