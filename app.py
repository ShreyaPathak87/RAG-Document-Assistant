from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel

from utils.pdf_loader import load_pdf
from utils.chunker import split_documents
from utils.vector_store import store_documents
from utils.rag import ask_question

import os
import shutil

app = FastAPI(title="RAG Document Assistant")

class QuestionRequest(BaseModel):
    question: str

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.get("/")
def home():
    return {
        "message": "Welcome to RAG Document Assistant"
    }

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):

    # Allow only PDF files
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed."
        )

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    # Save uploaded PDF
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Load PDF
    documents = load_pdf(file_path)

    # Split into chunks
    chunks = split_documents(documents)
    vector_store = store_documents(chunks)

    return {
    "message": "PDF embedded successfully!",
    "filename": file.filename,
    "pages": len(documents),
    "chunks": len(chunks),
    "status": "Stored in ChromaDB"
}

@app.post("/ask")
def ask(request: QuestionRequest):

    result = ask_question(request.question)

    return result

@app.get("/health")
def health():
    return {
        "status": "OK",
        "message": "RAG Document Assistant is running"
    }