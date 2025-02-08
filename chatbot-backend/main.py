from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import openai
import psycopg2

app = FastAPI()

openai.api_key = "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"

# Database Connection (PostgreSQL)
conn = psycopg2.connect(database="chatbot_db", user="user", password="password", host="localhost")
cursor = conn.cursor()

class ChatRequest(BaseModel):
    user_id: str
    message: str

@app.post("/chat/")
def chat_with_bot(request: ChatRequest):
    # Retrieve chat history
    cursor.execute("SELECT message FROM chat_history WHERE user_id = %s", (request.user_id,))
    history = cursor.fetchall()

    # Create prompt with memory retention
    prompt = "Patient Chat History:\n" + "\n".join([h[0] for h in history]) + "\nPatient: " + request.message
    
    # Get AI Response
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    # Store response in chat history
    cursor.execute("INSERT INTO chat_history (user_id, message) VALUES (%s, %s)", (request.user_id, request.message))
    conn.commit()

    return {"response": response["choices"][0]["message"]["content"]}
