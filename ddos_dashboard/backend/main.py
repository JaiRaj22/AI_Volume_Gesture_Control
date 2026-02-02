from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
from config import CLOUDFLARE_API_TOKEN
from ml_model import classify_spike

app = FastAPI(title="DDoS Dashboard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

RADAR_API_BASE = "https://api.cloudflare.com/client/v4/radar"

def check_token():
    if not CLOUDFLARE_API_TOKEN or CLOUDFLARE_API_TOKEN == "PASTE_YOUR_TOKEN_HERE":
        raise HTTPException(status_code=401, detail="Cloudflare API Token is missing or not configured.")

@app.get("/")
async def root():
    return {"message": "DDoS Dashboard API is running"}

@app.get("/attacks/layer3")
async def get_layer3_attacks():
    check_token()
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}"}
        response = await client.get(f"{RADAR_API_BASE}/attacks/layer3/timeseries", headers=headers)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Error fetching data from Cloudflare Radar")
        return response.json()

@app.get("/attacks/layer7")
async def get_layer7_attacks():
    check_token()
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}"}
        response = await client.get(f"{RADAR_API_BASE}/attacks/layer7/timeseries", headers=headers)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Error fetching data from Cloudflare Radar")
        return response.json()

@app.get("/attacks/top")
async def get_top_attacks():
    check_token()
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}"}

        # Cloudflare Radar API v4 provides top origins and targets separately
        try:
            origins_resp = await client.get(f"{RADAR_API_BASE}/attacks/layer7/top/locations/origin", headers=headers)
            targets_resp = await client.get(f"{RADAR_API_BASE}/attacks/layer7/top/locations/target", headers=headers)

            if origins_resp.status_code != 200 or targets_resp.status_code != 200:
                raise HTTPException(status_code=500, detail="Error fetching data from Cloudflare Radar")

            origins = origins_resp.json().get('result', {}).get('top_0', [])
            targets = targets_resp.json().get('result', {}).get('top_0', [])

            # Cloudflare Radar API v4 provides separate ranking lists for attack origins and targets.
            # Direct flow pairs (Origin -> Target) are not currently available in the public ranking API.
            # We synthesize pairs here for visualization on the 3D globe.
            synthesized_attacks = []
            for i in range(min(len(origins), len(targets))):
                synthesized_attacks.append({
                    "originCountryAlpha2": origins[i]['clientCountryAlpha2'],
                    "originCountryName": origins[i]['clientCountryName'],
                    "targetCountryAlpha2": targets[i]['targetCountryAlpha2'],
                    "targetCountryName": targets[i]['targetCountryName'],
                    "value": (origins[i]['value'] + targets[i]['value']) / 2
                })

            return {
                "result": {
                    "top_0": synthesized_attacks
                }
            }
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(status_code=500, detail=str(e))

@app.get("/my-ip")
async def get_my_ip():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.ipify.org?format=json")
        return response.json()

@app.get("/anomalies")
async def get_anomalies():
    check_token()
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}"}
        response = await client.get(f"{RADAR_API_BASE}/traffic_anomalies", headers=headers)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Error fetching data from Cloudflare Radar")
        data = response.json()

    # Apply ML Classification
    for anomaly in data.get('result', {}).get('trafficAnomalies', []):
        anomaly['ml_classification'] = classify_spike(anomaly)

    return data
