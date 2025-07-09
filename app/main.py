from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import openai, os

# Simple tool: ask ChatGPT and return the answer
class ChatRequest(BaseModel):
    prompt: str
    model: str | None = "gpt-4o-mini"

class ChatResponse(BaseModel):
    text: str

app = FastAPI(
    title="JARVYS MCP Server",
    version="0.1.0"
)

@app.get("/v1/tool-metadata")
def metadata():
    """
    Minimal MCP metadata endpoint – declares a single tool 'ask_llm'
    """
    return {
        "schema_version": "1",
        "name_for_human": "JARVYS LLM Bridge",
        "description_for_human": "Forward prompts to OpenAI and return answers",
        "endpoints": [
            {
                "name": "ask_llm",
                "description": "Send prompt to OpenAI",
                "url": "/v1/tool-invocations/ask_llm",
                "method": "POST",
                "request_body": ChatRequest.schema(),
                "response_body": ChatResponse.schema(),
            }
        ],
    }

@app.post("/v1/tool-invocations/ask_llm", response_model=ChatResponse)
def ask_llm(req: ChatRequest):
    openai.api_key = os.environ["OPENAI_API_KEY"]
    try:
        resp = openai.chat.completions.create(
            model=req.model, messages=[{"role": "user", "content": req.prompt}]
        )
        return ChatResponse(text=resp.choices[0].message.content.strip())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/", include_in_schema=False)
def root():
    """Health‑check endpoint for Cloud Run."""
    return {"status": "ok"}
