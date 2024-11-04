# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import openai
import os
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
client = AsyncIOMotorClient(MONGODB_URL)
db = client.chatbot_db

# OpenAI configuration
openai.api_key = os.getenv("OPENAI_API_KEY")

class Message(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatSession(BaseModel):
    session_id: str
    messages: List[dict]
    created_at: datetime
    updated_at: datetime

@app.post("/api/chat")
async def chat(message: Message):
    try:
        # Retrieve or create chat session
        session = None
        if message.session_id:
            session = await db.sessions.find_one({"_id": ObjectId(message.session_id)})
        
        if not session:
            session = {
                "messages": [],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            result = await db.sessions.insert_one(session)
            session["_id"] = result.inserted_id

        # Prepare conversation history
        conversation = session["messages"] + [{"role": "user", "content": message.message}]

        # Get response from OpenAI
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=conversation,
            temperature=0.7,
            max_tokens=150,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )

        assistant_message = response.choices[0].message.content

        # Update session with new messages
        new_messages = conversation + [{"role": "assistant", "content": assistant_message}]
        await db.sessions.update_one(
            {"_id": session["_id"]},
            {
                "$set": {
                    "messages": new_messages,
                    "updated_at": datetime.utcnow()
                }
            }
        )

        return {
            "response": assistant_message,
            "session_id": str(session["_id"])
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Route to get chat history
@app.get("/api/chat/{session_id}")
async def get_chat_history(session_id: str):
    try:
        session = await db.sessions.find_one({"_id": ObjectId(session_id)})
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {
            "session_id": str(session["_id"]),
            "messages": session["messages"],
            "created_at": session["created_at"],
            "updated_at": session["updated_at"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Embedded iframe code generator
@app.get("/api/embed")
async def get_embed_code(website_url: str):
    iframe_code = f"""
    <iframe
        src="{website_url}/chatbot"
        width="400"
        height="600"
        style="position: fixed; bottom: 20px; right: 20px; border: none; border-radius: 10px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);"
    ></iframe>
    """
    return {"embed_code": iframe_code}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
