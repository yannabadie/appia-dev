import os

from fastapi import FastAPI, HTTPException
from openai import OpenAI
from pydantic import BaseModel


# Simple tool: ask ChatGPT and return the answer
class ChatRequest(BaseModel):
    prompt: str
    model: str | None = "gpt-4o-mini"


class ChatResponse(BaseModel):
    text: str


app = FastAPI(title="JARVYS MCP Server", version="0.1.0")


@app.get("/v1/tool-metadata")
def metadata():
    """
    Minimal MCP metadata endpoint – declares a single tool 'ask_llm'
    """
    return {
        "schema_version": "1",
        "name_for_human": "JARVYS LLM Bridge",
        "description_for_human": "Forward prompts to OpenAI and return answers",  # noqa: E501
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
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY not configured")

    client = OpenAI(api_key=api_key)
    try:
        resp = client.chat.completions.create(
            model=req.model, messages=[{"role": "user", "content": req.prompt}]
        )
        return ChatResponse(text=resp.choices[0].message.content.strip())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/", include_in_schema=False)
def root():
    return {"message": "JARVYS MCP Server is running", "docs": "/docs"}


async def root() -> dict[str, str]:
    """Root health endpoint."""
    return {"status": "ok"}
