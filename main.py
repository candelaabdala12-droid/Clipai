
 from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import anthropic
import os
import re
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

class VideoRequest(BaseModel):
    video_id: str

@app.post("/api/analyze")
def analyze(req: VideoRequest):
    prompt = f"""Eres un editor experto en clips virales para streams. El video es: https://youtube.com/watch?v={req.video_id}

Identificá 6 momentos potencialmente virales con timestamps realistas para un stream de 1-3 horas de contenido variado.

Responde ÚNICAMENTE con JSON válido, sin texto extra ni backticks:
{{"videoTitle":"nombre del stream","viralScore":75,"clips":[{{"title":"título corto","type":"viral","startSeconds":120,"endSeconds":175,"reason":"por qué es buen clip"}},{{"title":"título","type":"funny","startSeconds":600,"endSeconds":650,"reason":"razón"}},{{"title":"título","type":"highlight","startSeconds":1800,"endSeconds":1860,"reason":"razón"}},{{"title":"título","type":"debate","startSeconds":3200,"endSeconds":3260,"reason":"razón"}},{{"title":"título","type":"emotional","startSeconds":5400,"endSeconds":5460,"reason":"razón"}},{{"title":"título","type":"viral","startSeconds":7200,"endSeconds":7260,"reason":"razón"}}]}}

Tipos válidos: viral, funny, emotional, debate, highlight."""

    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}]
    )

    text = message.content[0].text
    json_match = re.search(r'\{[\s\S]*\}', text)
    if not json_match:
        return {"error": "No se pudo generar respuesta"}
    return json.loads(json_match.group())

@app.get("/")
def root():
    return FileResponse("static/index.html")

app.mount("/", StaticFiles(directory="static"), name="static")
 
