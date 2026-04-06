from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware

from src.llm.generate_answer import generate_answer,rewrite_query
from .auth import DOCTOR_PASSWORD, create_access_token, decode_token, subject_exists
from src.retrieval.search import search

security = HTTPBearer()
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LoginRequest(BaseModel):
    role: str
    password: Optional[str] = None
    subject_id: Optional[int] = None


class QueryRequest(BaseModel):
    query: str

@app.post("/login")
def login(data: LoginRequest):

    if data.role == "doctor":

        if data.password != DOCTOR_PASSWORD:
            raise HTTPException(status_code=401, detail="Invalid doctor password")

        token = create_access_token({"role": "doctor"})

        return {"access_token": token, "token_type": "bearer"}

    elif data.role == "patient":

        if data.subject_id is None:
            raise HTTPException(status_code=400, detail="subject_id required")

        if not subject_exists(data.subject_id):
            raise HTTPException(status_code=404, detail="Patient not found")

        token = create_access_token({
            "role": "patient",
            "subject_id": data.subject_id
        })

        return {"access_token": token, "token_type": "bearer"}

    else:
        raise HTTPException(status_code=400, detail="Invalid role")

chat_memory = {}
@app.post("/query")
def query(
    data: QueryRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):

    token = credentials.credentials
    user = decode_token(token)

    role = user["role"]
    subject_id = user.get("subject_id")

    user_id = subject_id if role == "patient" else token

    if user_id not in chat_memory:
        chat_memory[user_id] = []
    
    history = chat_memory[user_id][-5:]

    rewritten_query = rewrite_query(data.query, history)

    results = search(
        rewritten_query,
        role=role,
        user_subject_id=subject_id
    )
    if not results:
        return {"answer": "No relevant records found.", "sources": []}

    context = "\n\n".join(
        doc["text"] for doc in results[:5]
    )

    answer = generate_answer(
        rewritten_query,
        context,
        role
    )

    chat_memory[user_id].append({
        "role": "user",
        "content": data.query
    })

    chat_memory[user_id].append({
        "role": "assistant",
        "content": answer
    })

    return {
        "answer": answer,
        "sources": results
    }