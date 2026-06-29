from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from collections import deque

from utils.pdf_loader import load_pdf
from utils.chunker import split_documents
from utils.vector_store import store_documents
from utils.rag import ask_question

import os
import shutil

# ========================
# APP INIT
# ========================
app = FastAPI(title="RAG Document Assistant")

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Keep only last 20 chats (prevents memory crash)
chat_history = deque(maxlen=20)


# ========================
# MODELS
# ========================
class QuestionRequest(BaseModel):
    question: str


# ========================
# ROUTES
# ========================
@app.get("/")
def home():
    return {
        "message": "Welcome to RAG Document Assistant 🚀"
    }


# ========================
# UPLOAD PDF
# ========================
@app.post("/upload", tags=["Document"])
async def upload_pdf(file: UploadFile = File(...)):

    # Validate file type
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed."
        )

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Load PDF
    documents = load_pdf(file_path)

    # Split into chunks
    chunks = split_documents(documents)

    # Store in vector DB (IMPORTANT: memory safe version)
    store_documents(chunks)

    return {
        "message": "PDF embedded successfully! 🚀",
        "filename": file.filename,
        "pages": len(documents),
        "chunks": len(chunks),
        "status": "Stored in ChromaDB"
    }


# ========================
# ASK QUESTION
# ========================
@app.post("/ask", tags=["Question Answering"])
def ask(request: QuestionRequest):

    result = ask_question(request.question)

    chat_history.append({
        "question": request.question,
        "answer": result.get("answer"),
        "sources": result.get("sources", [])
    })

    return result


# ========================
# CHAT HISTORY
# ========================
@app.get("/history", tags=["Chat History"])
def get_history():
    return {
        "chat_history": list(chat_history)
    }


@app.delete("/history", tags=["Chat History"])
def clear_history():
    chat_history.clear()
    return {
        "message": "Chat history cleared ✔"
    }


# ========================
# HEALTH CHECK
# ========================
@app.get("/health")
def health():
    return {
        "status": "OK",
        "message": "RAG Document Assistant is running 🚀"
    }