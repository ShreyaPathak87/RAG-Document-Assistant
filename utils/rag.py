from langchain_community.vectorstores import Chroma
from utils.embeddings import get_embeddings
from functools import lru_cache

CHROMA_DB = "chroma_db"

embeddings = get_embeddings()

@lru_cache()
def load_db():
    return Chroma(
        persist_directory=CHROMA_DB,
        embedding_function=embeddings
    )


def ask_question(question: str):
    db = load_db()

    docs = db.similarity_search_with_score(question, k=3)

    answers = []
    for doc, score in docs:
        answers.append({
            "text": doc.page_content,
            "metadata": doc.metadata,
            "score": float(score)
        })

    return {
        "question": question,
        "answer": "\n\n---\n\n".join([a["text"] for a in answers]),
        "results": answers,
        "sources": [a["metadata"] for a in answers]
    }