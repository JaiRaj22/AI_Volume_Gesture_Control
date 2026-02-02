from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import asyncio
from config import CLOUDFLARE_API_TOKEN
from ml_model import l3_detector, l7_detector, classify_anomaly, detect_anomalies_in_series
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="DDoS Dashboard API - Production")

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

async def fetch_historical_data():
    """
    Fetches 30 days of historical data to train the ML models on startup.
    """
    if not CLOUDFLARE_API_TOKEN or CLOUDFLARE_API_TOKEN == "PASTE_YOUR_TOKEN_HERE":
        logger.warning("No API token found. Skipping historical data fetch.")
        return

    headers = {"Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}"}
    async with httpx.AsyncClient() as client:
        try:
            logger.info("Fetching historical data for ML training...")
            # Fetch L7 historical data
            l7_resp = await client.get(f"{RADAR_API_BASE}/attacks/layer7/timeseries?dateRange=30d", headers=headers)
            if l7_resp.status_code == 200:
                values = l7_resp.json().get('result', {}).get('serie_0', {}).get('values', [])
                if values:
                    l7_detector.train([float(v) for v in values])

            # Fetch L3 historical data
            l3_resp = await client.get(f"{RADAR_API_BASE}/attacks/layer3/timeseries?dateRange=30d", headers=headers)
            if l3_resp.status_code == 200:
                values = l3_resp.json().get('result', {}).get('serie_0', {}).get('values', [])
                if values:
                    l3_detector.train([float(v) for v in values])

        except Exception as e:
            logger.error(f"Failed to fetch historical data: {e}")

@app.on_event("startup")
async def startup_event():
    await fetch_historical_data()

@app.get("/")
async def root():
    return {"message": "DDoS Dashboard API is running", "ml_status": {"l7": l7_detector.is_trained, "l3": l3_detector.is_trained}}

@app.get("/attacks/layer3")
async def get_layer3_attacks(dateRange: str = "1d"):
    check_token()
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}"}
        response = await client.get(f"{RADAR_API_BASE}/attacks/layer3/timeseries?dateRange={dateRange}", headers=headers)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Error fetching data from Cloudflare Radar")

        data = response.json()
        values = data.get('result', {}).get('serie_0', {}).get('values', [])
        if values:
            data['ml_anomalies'] = detect_anomalies_in_series([float(v) for v in values])

        return data

@app.get("/attacks/layer7")
async def get_layer7_attacks(dateRange: str = "1d"):
    check_token()
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}"}
        response = await client.get(f"{RADAR_API_BASE}/attacks/layer7/timeseries?dateRange={dateRange}", headers=headers)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Error fetching data from Cloudflare Radar")

        data = response.json()
        values = data.get('result', {}).get('serie_0', {}).get('values', [])
        if values:
            data['ml_anomalies'] = detect_anomalies_in_series([float(v) for v in values])

        return data

@app.get("/attacks/top")
async def get_top_attacks(dateRange: str = "1d"):
    check_token()
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}"}

        try:
            origins_resp = await client.get(f"{RADAR_API_BASE}/attacks/layer7/top/locations/origin?dateRange={dateRange}", headers=headers)
            targets_resp = await client.get(f"{RADAR_API_BASE}/attacks/layer7/top/locations/target?dateRange={dateRange}", headers=headers)

            if origins_resp.status_code != 200 or targets_resp.status_code != 200:
                raise HTTPException(status_code=500, detail="Error fetching data from Cloudflare Radar")

            origins = origins_resp.json().get('result', {}).get('top_0', [])
            targets = targets_resp.json().get('result', {}).get('top_0', [])

            synthesized_attacks = []
            for i in range(min(len(origins), len(targets))):
                origin = origins[i]
                target = targets[i]
                synthesized_attacks.append({
                    "originCountryAlpha2": origin.get('originCountryAlpha2'),
                    "originCountryName": origin.get('originCountryName'),
                    "targetCountryAlpha2": target.get('targetCountryAlpha2'),
                    "targetCountryName": target.get('targetCountryName'),
                    "value": (float(origin.get('value', 0)) + float(target.get('value', 0))) / 2,
                    "ml_classification": classify_anomaly(float(origin.get('value', 0)), "l7")
                })

            return {
                "result": {
                    "top_0": synthesized_attacks
                }
            }
        except Exception as e:
            logger.error(f"Error in /attacks/top: {e}")
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(status_code=500, detail=str(e))

@app.get("/my-ip")
async def get_my_ip():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.ipify.org?format=json")
        return response.json()

@app.get("/anomalies")
async def get_anomalies(dateRange: str = "1d"):
    check_token()
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}"}
        response = await client.get(f"{RADAR_API_BASE}/traffic_anomalies?dateRange={dateRange}", headers=headers)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Error fetching data from Cloudflare Radar")

        data = response.json()
        for anomaly in data.get('result', {}).get('trafficAnomalies', []):
            anomaly['ml_classification'] = "UNUSUAL ACTIVITY" if anomaly.get('status') == 'VERIFIED' else "POTENTIAL SPIKE"

        return data
