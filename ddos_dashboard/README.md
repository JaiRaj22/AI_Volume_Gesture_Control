# DDoS Monitoring Dashboard

This project provides a real-time visualization of global DDoS attacks and traffic anomalies using Cloudflare Radar data.

## Features
- **FastAPI Backend**: Fetches real-time data from Cloudflare Radar API.
- **Machine Learning**: Classifies traffic spikes as anomalies or potential attacks.
- **Interactive 3D Globe**: Visualizes attack origins and targets globally.

## Setup Instructions

### 1. Cloudflare API Token
To use this dashboard, you need a Cloudflare API Token:
1. Log in to your [Cloudflare Dashboard](https://dash.cloudflare.com/).
2. Go to **My Profile > API Tokens**.
3. Click **Create Token**.
4. Select **Create Custom Token**.
5. Give it a name (e.g., "Radar Read").
6. In **Permissions**, add:
   - `Account | Radar | Read`
7. Click **Continue to summary** and then **Create Token**.
8. Copy the token.
9. Copy `backend/.env.example` to `backend/.env` and paste your token: `CLOUDFLARE_API_TOKEN=your_token_here`.

### 2. Backend Setup
1. Install dependencies: `pip install -r backend/requirements.txt`
2. Start the backend from the project root: `python start_backend.py`

### 3. Frontend Setup
1. Open `frontend/index.html` in your browser (or use a simple live server).

## How it works
- The backend polls Cloudflare Radar's attack and anomaly endpoints.
- The ML module in `backend/ml_model.py` uses an **IsolationForest** model to classify traffic spikes by comparing them against a baseline of normal activity.
- The frontend renders an interactive globe where red arcs represent DDoS traffic flows and red points represent traffic anomalies.

## IP Address Fetching
Cloudflare Radar API provides aggregated data (ASNs and Locations) rather than specific individual IP addresses for privacy and security reasons.
- To fetch **User IP**: Use a service like `https://api.ipify.org` or read the `X-Forwarded-For` header in FastAPI.
- To analyze **Specific IPs**: You would need your own Cloudflare logs (via Logpush) or use the Cloudflare Intel API if you have a specific IP to check.
