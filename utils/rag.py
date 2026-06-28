import os
from dotenv import load_dotenv

from langchain_community.vectorstores import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI

from utils.embeddings import get_embeddings

load_dotenv()

CHROMA_DB = "chroma_db"

# 🔹 Embeddings
embeddings = get_embeddings()

# 🔹 Load existing vector store
vector_store = Chroma(
    persist_directory=CHROMA_DB,
    embedding_function=embeddings
)

# 🔹 Gemini LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0
)


def ask_question(question):
    try:
        # 🚀 STEP 1: Better retrieval (MMR = best practice)
        docs = vector_store.max_marginal_relevance_search(
    question,
    k=1,
    fetch_k=5
)
        if not docs:
            return {
                "answer": "No relevant information found in the uploaded document.",
                "sources": [],
                "retrieved_chunks": []
            }

        # 🚀 STEP 2: Remove duplicates
        seen = set()
        unique_docs = []

        for doc in docs:
            if doc.page_content not in seen:
                unique_docs.append(doc)
                seen.add(doc.page_content)

        # 🚀 STEP 3: Build clean context
        context = "\n\n".join(
            f"[Chunk {i+1}]\n{doc.page_content}"
            for i, doc in enumerate(unique_docs)
        )

        # 🚀 STEP 4: Strict prompt (reduces hallucination)
        prompt = f"""
You are a precise document QA assistant.

RULES:
- Use ONLY the provided context
- If the answer is not in the context, say "Not found in document"
- Be short, clear, and accurate

Context:
{context}

Question:
{question}
"""

        response = llm.invoke(prompt)

        # 🚀 STEP 5: Clean source tracking
        page = unique_docs[0].metadata.get("page", 0)

        sources = [f"Page {page + 1}"]

        # 🚀 STEP 6: Final output
        return {
            "answer": response.content,
            "sources": sources,
            "retrieved_chunks": [doc.page_content for doc in unique_docs]
        }

    except Exception as e:
        print("ERROR:", e)
        raise