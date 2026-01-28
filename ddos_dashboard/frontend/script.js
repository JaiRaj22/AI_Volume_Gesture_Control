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

async function fetchAttacks() {
    try {
        const response = await fetch('http://localhost:8000/attacks/top');
        const data = await response.json();

        // Show demo badge if mock data is used
        if (data.is_mock) {
            document.getElementById('demo-badge').style.display = 'inline-block';
        } else {
            document.getElementById('demo-badge').style.display = 'none';
        }

        // Transform Cloudflare data to Globe format
        // Cloudflare Radar returns top origin/target pairs
        const attacks = data.result?.top_0 || [];

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
            'GR': [39.07, 21.82], 'IL': [31.04, 34.85], 'AE': [23.42, 53.84], 'NZ': [-40.9, 174.88]
        };

        const arcsData = attacks.map(attack => {
            const start = countryCoords[attack.originCountryAlpha2] || [Math.random() * 180 - 90, Math.random() * 360 - 180];
            const end = countryCoords[attack.targetCountryAlpha2] || [Math.random() * 180 - 90, Math.random() * 360 - 180];

            return {
                startLat: start[0],
                startLng: start[1],
                endLat: end[0],
                endLng: end[1],
                label: `Attack from ${attack.originCountryName} to ${attack.targetCountryName}`
            };
        });

        globe.arcsData(arcsData);

        const listHtml = attacks.slice(0, 10).map(a => `
            <div class="attack-item">
                <strong>${a.originCountryName} &rarr; ${a.targetCountryName}</strong><br>
                Magnitude: ${(a.value * 100).toFixed(2)}%
            </div>
        `).join('');
        document.getElementById('attack-list').innerHTML = listHtml;

    } catch (err) {
        console.error("Error fetching attack data:", err);
    }
}

async function fetchAnomalies() {
    try {
        const response = await fetch('http://localhost:8000/anomalies');
        const data = await response.json();
        const anomalies = data.result?.trafficAnomalies || [];

        const countryCoords = {
            'United States': [37.09, -95.71], 'China': [35.86, 104.19], 'Russia': [61.52, 105.31], 'Brazil': [-14.23, -51.92],
            'India': [20.59, 78.96], 'United Kingdom': [55.37, -3.43], 'Germany': [51.16, 10.45], 'France': [46.22, 2.21],
            'Japan': [36.2, 138.25], 'Australia': [-25.27, 133.77], 'Canada': [56.13, -106.34], 'Italy': [41.87, 12.56],
            'Spain': [40.46, -3.74], 'Mexico': [23.63, -102.55], 'South Korea': [35.9, 127.76], 'South Africa': [-30.55, 22.93],
            'Netherlands': [52.13, 5.29], 'Singapore': [1.35, 103.81], 'Malaysia': [4.21, 101.97], 'Poland': [51.91, 19.14],
            'Sweden': [60.12, 18.64], 'Norway': [60.47, 8.46], 'Finland': [61.92, 25.74], 'Denmark': [56.26, 9.5],
            'Switzerland': [46.81, 8.22], 'Austria': [47.51, 14.55], 'Belgium': [50.5, 4.46], 'Portugal': [39.39, -8.22],
            'Greece': [39.07, 21.82], 'Israel': [31.04, 34.85], 'UAE': [23.42, 53.84], 'New Zealand': [-40.9, 174.88]
        };

        const pointsData = anomalies.map(a => {
            const coords = countryCoords[a.locationName] || [Math.random() * 180 - 90, Math.random() * 360 - 180];
            return {
                lat: coords[0],
                lng: coords[1],
                size: a.impact / 5,
                color: a.impact > 3 ? 'red' : 'yellow',
                label: `${a.locationName}: ${a.ml_classification}`
            };
        });

        globe.pointsData(pointsData);
        document.getElementById('status').innerText = `Active Monitoring: ${anomalies.length} anomalies classified.`;

    } catch (err) {
        console.error("Error fetching anomaly data:", err);
    }
}

function updateData() {
    fetchAttacks();
    fetchAnomalies();
}

// Initial fetch and set interval
updateData();
setInterval(updateData, 30000); // Update every 30 seconds
