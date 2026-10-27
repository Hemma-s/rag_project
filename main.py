from fastapi import FastAPI, Depends, HTTPException, Query
from pydantic import BaseModel
from auth import authenticate, create_token, current_user
from rag import answer_as
from audit import who_retrieved

app = FastAPI(title="SecureDocs RAG")


class Login(BaseModel):
    username: str
    password: str


class Ask(BaseModel):
    question: str


@app.post("/login")
def login(body: Login):
    user = authenticate(body.username, body.password)
    if not user:
        raise HTTPException(status_code=401, detail="Wrong username or password")
    return {"access_token": create_token(user), "token_type": "bearer"}


@app.post("/ask")
def ask(body: Ask, user=Depends(current_user)):
    return answer_as(user, body.question)

@app.get("/audit")
def audit_query(doc_id: str, days: int = Query(30, ge=1, le=365),
                user=Depends(current_user)):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admins only")
    # scoped to the admin's own company, taken from the token
    return {"doc_id": doc_id, "days": days,
            "retrievals": who_retrieved(doc_id, user["tenant_id"], days)}
