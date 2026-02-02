const globe = Globe()
    (document.getElementById('globeViz'))
    .globeImageUrl('https://unpkg.com/three-globe/example/img/earth-night.jpg')
    .bumpImageUrl('https://unpkg.com/three-globe/example/img/earth-topology.png')
    .backgroundImageUrl('https://unpkg.com/three-globe/example/img/night-sky.png')
    .arcColor(() => 'rgba(255, 0, 0, 0.5)')
    .arcDashLength(0.4)
    .arcDashGap(2)
    .arcDashAnimateTime(1500)
    .arcsTransitionDuration(1000)
    .pointColor(() => 'red')
    .pointRadius(0.8)
    .pointsMerge(true)
    .pointLabel('label');

const countryCoords = {
    'US': [37.09, -95.71], 'CN': [35.86, 104.19], 'RU': [61.52, 105.31], 'BR': [-14.23, -51.92],
    'IN': [20.59, 78.96], 'GB': [55.37, -3.43], 'DE': [51.16, 10.45], 'FR': [46.22, 2.21],
    'JP': [36.2, 138.25], 'AU': [-25.27, 133.77], 'CA': [56.13, -106.34], 'IT': [41.87, 12.56],
    'ES': [40.46, -3.74], 'MX': [23.63, -102.55], 'KR': [35.9, 127.76], 'ZA': [-30.55, 22.93],
    'EG': [26.82, 30.8], 'SA': [23.88, 45.07], 'ID': [-0.78, 113.92], 'TR': [38.96, 35.24],
    'VN': [14.05, 108.27], 'TH': [15.87, 100.99], 'PH': [12.87, 121.77], 'PK': [30.37, 69.34],
    'NG': [9.08, 8.67], 'AR': [-38.41, -63.61], 'CO': [4.57, -74.3], 'UA': [48.37, 31.16],
    'NL': [52.13, 5.29], 'SG': [1.35, 103.81], 'MY': [4.21, 101.97], 'PL': [51.91, 19.14],
    'SE': [60.12, 18.64], 'NO': [60.47, 8.46], 'FI': [61.92, 25.74], 'DK': [56.26, 9.5],
    'CH': [46.81, 8.22], 'AT': [47.51, 14.55], 'BE': [50.5, 4.46], 'PT': [39.39, -8.22],
    'GR': [39.07, 21.82], 'IL': [31.04, 34.85], 'AE': [23.42, 53.84], 'NZ': [-40.9, 174.88],
    'IR': [32.42, 53.68], 'IQ': [33.22, 43.67], 'SN': [14.49, -14.45], 'GA': [-0.8, 11.6], 'GN': [9.94, -9.69]
};

async function fetchAttacks() {
    try {
        const response = await fetch('http://localhost:8000/attacks/top');
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to fetch attack data');
        }
        const data = await response.json();

        const attacks = data.result?.top_0 || [];

        const arcsData = attacks.map(attack => {
            const start = countryCoords[attack.originCountryAlpha2] || [Math.random() * 180 - 90, Math.random() * 360 - 180];
            const end = countryCoords[attack.targetCountryAlpha2] || [Math.random() * 180 - 90, Math.random() * 360 - 180];

            return {
                startLat: start[0],
                startLng: start[1],
                endLat: end[0],
                endLng: end[1],
                label: `${attack.ml_classification}: ${attack.originCountryName} -> ${attack.targetCountryName}`
            };
        });

        globe.arcsData(arcsData);

        if (attacks.length === 0) {
            document.getElementById('attack-list').innerHTML = '<div class="attack-item">No active attacks reported.</div>';
        } else {
            const listHtml = attacks.slice(0, 10).map(a => `
                <div class="attack-item" style="border-left-color: ${a.ml_classification.includes('CRITICAL') ? '#ff4d4d' : '#ff9900'}">
                    <strong>${a.originCountryName} &rarr; ${a.targetCountryName}</strong><br>
                    Classification: ${a.ml_classification}<br>
                    Magnitude: ${(a.value * 100).toFixed(2)}%
                </div>
            `).join('');
            document.getElementById('attack-list').innerHTML = listHtml;
        }

    } catch (err) {
        console.error("Error fetching attack data:", err);
        document.getElementById('attack-list').innerHTML = `<div class="attack-item" style="border-left-color: #ff9900;">Error: ${err.message}</div>`;
    }
}

async function fetchAnomalies() {
    try {
        const response = await fetch('http://localhost:8000/anomalies');
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to fetch anomalies');
        }
        const data = await response.json();
        const anomalies = data.result?.trafficAnomalies || [];

        const pointsData = anomalies.map(a => {
            const loc = a.locationDetails || a.asnDetails?.location || {};
            const code = loc.code;
            const name = loc.name || "Unknown";
            const coords = countryCoords[code] || [Math.random() * 180 - 90, Math.random() * 360 - 180];

            return {
                lat: coords[0],
                lng: coords[1],
                size: 0.5,
                color: a.status === 'VERIFIED' ? 'red' : 'yellow',
                label: `${name}: ${a.ml_classification} (${a.type})`
            };
        });

        globe.pointsData(pointsData);
        document.getElementById('status').innerText = `Active Monitoring: ${anomalies.length} anomalies classified.`;

    } catch (err) {
        console.error("Error fetching anomaly data:", err);
        document.getElementById('status').innerText = `Status: ${err.message}`;
    }
}

function updateData() {
    fetchAttacks();
    fetchAnomalies();
}

// Initial fetch and set interval
updateData();
setInterval(updateData, 30000); // Update every 30 seconds
