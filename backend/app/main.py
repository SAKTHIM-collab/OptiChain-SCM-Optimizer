import sys
import os

# --- The Bulletproof Path Fix ---
# This forces Python to recognize the 'backend' folder as the root directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# --------------------------------

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.services.rag_pipeline import generate_supply_chain_insight 

app = FastAPI(title="SupplyChainGPT API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    message: str
    warehouse_id: str = "WH-TRICHY-01"

@app.post("/api/chat")
async def chat_endpoint(query: QueryRequest):
    try:
        # Call the actual LangChain RAG pipeline
        ai_reply = generate_supply_chain_insight(query.message)
        return {"reply": ai_reply, "status": "success"}
    except Exception as e:
        return {"reply": f"System Error executing RAG pipeline: {str(e)}", "status": "error"}

if __name__ == "__main__":
    import uvicorn
    # This allows you to safely run it using `python app/main.py` directly!
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)