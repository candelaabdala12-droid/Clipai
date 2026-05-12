



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

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

class VideoRequest(BaseModel):
    video_id: str

@app.post("/api/analyze")
def analyze(req: VideoRequest):
    prompt = "Eres un editor experto en clips virales. El video es: https://youtube.com/watch?v=" + req.video_id + "\n\nIdentifica 6 momentos virales con timestamps realistas para un stream de 1-3 horas.\n\nResponde SOLO con JSON sin backticks:\n{\"videoTitle\":\"nombre\",\"viralScore\":75,\"clips\":[{\"title\":\"titulo\",\"type\":\"viral\",\"startSeconds\":120,\"endSeconds\":175,\"reason\":\"razon\"},{\"title\":\"titulo\",\"type\":\"funny\",\"startSeconds\":600,\"endSeconds\":650,\"reason\":\"razon\"},{\"title\":\"titulo\",\"type\":\"highlight\",\"startSeconds\":1800,\"endSeconds\":1860,\"reason\":\"razon\"},{\"title\":\"titulo\",\"type\":\"debate\",\"startSeconds\":3200,\"endSeconds\":3260,\"reason\":\"razon\"},{\"title\":\"titulo\",\"type\":\"emotional\",\"startSeconds\":5400,\"endSeconds\":5460,\"reason\":\"razon\"},{\"title\":\"titulo\",\"type\":\"viral\",\"startSeconds\":7200,\"endSeconds\":7260,\"reason\":\"razon\"}]}"
    message = client.messages.create(model="claude-sonnet-4-5", max_tokens=1500, messages=[{"role": "user", "content": prompt}])
    text = message.content[0].text
    match = re.search(r'\{[\s\S]*\}', text)
    if not match:
        return {"error": "Sin respuesta"}
    return json.loads(match.group())

@app.get("/")
def root():
    return FileResponse("static/index.html")

app.mount("/", StaticFiles(directory="static"), name="static")
