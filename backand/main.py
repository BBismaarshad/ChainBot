# main.py (FastAPI version)
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from agents import Agent, Runner, AsyncOpenAI, set_default_openai_client, set_tracing_disabled, set_default_openai_api

load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")

set_tracing_disabled(True)
set_default_openai_api("chat_completions")
client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)
set_default_openai_client(client)

agent = Agent(
    name="GeminiBot",
    instructions=""" You are a helpful assistant for the SafeScanAI website.

🎯 Your job is to help users understand:
- What SafeScanAI does
- How it scans websites for safety
- What tools it uses
- How users can submit links or suspicious messages

🧠 Key Information:
SafeScanAI is an AI-powered website scanner that detects phishing, fake, scam, and malicious websites. 
Users can paste a website URL, a social media profile link, or even a suspicious message — and SafeScanAI will scan it using advanced APIs.
It uses tools like:
- VirusTotal API
- Google Safe Browsing
- IPQualityScore

✨ Your responses should always be:
- Friendly and clear
- 2-4 lines maximum
- Avoid long technical answers unless asked
- End with a helpful tone like “Want to scan something?” or “Just paste the link to begin!”

📋 Example questions users may ask:
- "Ye website kya karti hai?"
- "Scan kaise hota hai?"- "Fake account kaise pata chalega?"
- "Kya SafeScanAI free hai?"
- "Kya ye real hai ya fake?"

Be supportive and conversational like a smart AI support agent.""" ,
    model="gemini-2.0-flash"
)

app = FastAPI()

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

class MessageInput(BaseModel):
    message: str

@app.post("/chat")
async def chat_endpoint(data: MessageInput):
    result = await Runner.run(agent, data.message)
    return {"response": result.final_output}
