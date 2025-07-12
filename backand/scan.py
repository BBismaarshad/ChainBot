from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Keys
VT_API_KEY = os.getenv("VT_API_KEY")
IPQS_API_KEY = os.getenv("IPQS_API_KEY")
GSB_API_KEY = os.getenv("GSB_API_KEY")

class ScanRequest(BaseModel):
    url: str

@app.post("/scan")
async def scan_url(scan: ScanRequest):
    url = scan.url
    results = {}

    async with httpx.AsyncClient() as client:

        # --- 1. VirusTotal ---
        try:
            vt_submit = await client.post(
                "https://www.virustotal.com/api/v3/urls",
                headers={"x-apikey": VT_API_KEY, "Content-Type": "application/x-www-form-urlencoded"},
                data=f"url={url}"
            )
            vt_id = vt_submit.json()["data"]["id"]

            vt_result = await client.get(
                f"https://www.virustotal.com/api/v3/analyses/{vt_id}",
                headers={"x-apikey": VT_API_KEY}
            )
            results["virustotal"] = vt_result.json()
        except Exception as e:
            results["virustotal"] = {"error": str(e)}

        # --- 2. IPQualityScore ---
        try:
            ipqs_url = f"https://ipqualityscore.com/api/json/url/{IPQS_API_KEY}/{url}"
            ipqs_response = await client.get(ipqs_url)
            results["ipqualityscore"] = ipqs_response.json()
        except Exception as e:
            results["ipqualityscore"] = {"error": str(e)}

        # --- 3. Google Safe Browsing ---
        try:
            gsb_body = {
                "client": {
                    "clientId": "yourcompanyname",
                    "clientVersion": "1.0"
                },
                "threatInfo": {
                    "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE", "POTENTIALLY_HARMFUL_APPLICATION"],
                    "platformTypes": ["ANY_PLATFORM"],
                    "threatEntryTypes": ["URL"],
                    "threatEntries": [{"url": url}]
                }
            }
            gsb_response = await client.post(
                f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={GSB_API_KEY}",
                json=gsb_body
            )
            results["google_safebrowsing"] = gsb_response.json()
        except Exception as e:
            results["google_safebrowsing"] = {"error": str(e)}

    return results
