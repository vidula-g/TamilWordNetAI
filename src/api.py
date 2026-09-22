from fastapi import FastAPI
from pydantic import BaseModel

from src.ai_pipeline import analyze_tamil_sentence


# ==================================================
# CREATE FASTAPI APP
# ==================================================

app = FastAPI(
    title="Tamil Literary Context AI",
    description="Tamil NLP and literary context retrieval API",
    version="1.0"
)


# ==================================================
# REQUEST MODEL
# ==================================================

class TamilQuery(BaseModel):

    text: str

    top_k: int = 3


# ==================================================
# HOME ENDPOINT
# ==================================================

@app.get("/")
def home():

    return {
        "message": "Tamil Literary Context AI is running!"
    }


# ==================================================
# AI ENDPOINT
# ==================================================

@app.post("/analyze")
def analyze(query: TamilQuery):

    result = analyze_tamil_sentence(
        query.text,
        top_k=query.top_k
    )

    return result