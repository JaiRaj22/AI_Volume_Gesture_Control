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

@app.get("/")
async def root():
    return {"message": "DDoS Dashboard API is running"}

@app.get("/attacks/layer3")
async def get_layer3_attacks():
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}"}
        response = await client.get(f"{RADAR_API_BASE}/attacks/layer3/timeseries", headers=headers)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Error fetching data from Cloudflare Radar")
        return response.json()

@app.get("/attacks/layer7")
async def get_layer7_attacks():
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}"}
        response = await client.get(f"{RADAR_API_BASE}/attacks/layer7/timeseries", headers=headers)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Error fetching data from Cloudflare Radar")
        return response.json()

@app.get("/attacks/top")
async def get_top_attacks():
    if CLOUDFLARE_API_TOKEN == "YOUR_CLOUDFLARE_API_TOKEN":
        # Return mock data for demonstration
        return {
            "result": {
                "top_0": [
                    {"originCountryAlpha2": "US", "originCountryName": "United States", "targetCountryAlpha2": "CN", "targetCountryName": "China", "value": 0.15},
                    {"originCountryAlpha2": "CN", "originCountryName": "China", "targetCountryAlpha2": "US", "targetCountryName": "United States", "value": 0.12},
                    {"originCountryAlpha2": "RU", "originCountryName": "Russia", "targetCountryAlpha2": "GB", "targetCountryName": "United Kingdom", "value": 0.08},
                    {"originCountryAlpha2": "BR", "originCountryName": "Brazil", "targetCountryAlpha2": "US", "targetCountryName": "United States", "value": 0.05},
                    {"originCountryAlpha2": "IN", "originCountryName": "India", "targetCountryAlpha2": "DE", "targetCountryName": "Germany", "value": 0.04}
                ]
            }
        }

    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}"}
        # Fetching top origin/target pairs for layer7 as an example
        response = await client.get(f"{RADAR_API_BASE}/attacks/layer7/top/attacks", headers=headers)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Error fetching data from Cloudflare Radar")
        return response.json()

@app.get("/my-ip")
async def get_my_ip():
    # In a real FastAPI app, you can get the client IP from the Request object
    # For this demo, we'll use a public API to show how it can be done
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.ipify.org?format=json")
        return response.json()

@app.get("/anomalies")
async def get_anomalies():
    if CLOUDFLARE_API_TOKEN == "YOUR_CLOUDFLARE_API_TOKEN":
        data = {
            "result": {
                "trafficAnomalies": [
                    {"locationName": "United States", "impact": 5, "confidence": 5, "type": "DDoS", "start": "2023-10-01T10:00:00Z"},
                    {"locationName": "China", "impact": 4, "confidence": 3, "type": "Traffic Spike", "start": "2023-10-01T11:00:00Z"},
                    {"locationName": "Germany", "impact": 2, "confidence": 4, "type": "BGP Hijack", "start": "2023-10-01T12:00:00Z"}
                ]
            }
        }
    else:
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
