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

import random

@app.get("/attacks/top")
async def get_top_attacks():
    if CLOUDFLARE_API_TOKEN == "PASTE_YOUR_TOKEN_HERE":
        # Return mock data for demonstration
        countries = [
            ("US", "United States"), ("CN", "China"), ("RU", "Russia"), ("BR", "Brazil"),
            ("IN", "India"), ("GB", "United Kingdom"), ("DE", "Germany"), ("FR", "France"),
            ("JP", "Japan"), ("AU", "Australia"), ("CA", "Canada"), ("IT", "Italy"),
            ("ES", "Spain"), ("MX", "Mexico"), ("KR", "South Korea"), ("ZA", "South Africa")
        ]

        mock_attacks = []
        # Create more variety in mock data
        available_dest = countries.copy()
        for i in range(min(len(countries), 10)):
            orig = countries[i]
            # Pick a different random destination
            dest = random.choice([c for c in countries if c[0] != orig[0]])
            mock_attacks.append({
                "originCountryAlpha2": orig[0], "originCountryName": orig[1],
                "targetCountryAlpha2": dest[0], "targetCountryName": dest[1],
                "value": round(random.uniform(0.01, 0.15), 4)
            })

        return {
            "is_mock": True,
            "result": {
                "top_0": sorted(mock_attacks, key=lambda x: x['value'], reverse=True)
            }
        }

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

            # Synthesize attack pairs for visualization since the public API doesn't provide pairs directly
            synthesized_attacks = []
            for i in range(min(len(origins), len(targets))):
                synthesized_attacks.append({
                    "originCountryAlpha2": origins[i]['clientCountryAlpha2'],
                    "originCountryName": origins[i]['clientCountryName'],
                    "targetCountryAlpha2": targets[i]['clientCountryAlpha2'],
                    "targetCountryName": targets[i]['clientCountryName'],
                    "value": (origins[i]['value'] + targets[i]['value']) / 2
                })

            return {
                "is_mock": False,
                "result": {
                    "top_0": synthesized_attacks
                }
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

@app.get("/my-ip")
async def get_my_ip():
    # In a real FastAPI app, you can get the client IP from the Request object
    # For this demo, we'll use a public API to show how it can be done
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.ipify.org?format=json")
        return response.json()

@app.get("/anomalies")
async def get_anomalies():
    if CLOUDFLARE_API_TOKEN == "PASTE_YOUR_TOKEN_HERE":
        countries = ["United States", "China", "Germany", "Brazil", "Russia", "India", "Japan", "France"]
        mock_anomalies = []
        for _ in range(random.randint(3, 6)):
            mock_anomalies.append({
                "locationName": random.choice(countries),
                "impact": random.randint(1, 5),
                "confidence": random.randint(1, 5),
                "type": random.choice(["DDoS", "Traffic Spike", "BGP Hijack"]),
                "start": "2023-10-01T10:00:00Z"
            })
        data = {
            "is_mock": True,
            "result": {
                "trafficAnomalies": mock_anomalies
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
