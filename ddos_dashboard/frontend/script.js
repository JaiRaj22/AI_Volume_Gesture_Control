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

        // Transform Cloudflare data to Globe format
        // Cloudflare Radar returns top origin/target pairs
        const attacks = data.result?.top_0 || [];

        const countryCoords = {
            'US': [37.0902, -95.7129],
            'CN': [35.8617, 104.1954],
            'RU': [61.5240, 105.3188],
            'BR': [-14.2350, -51.9253],
            'IN': [20.5937, 78.9629],
            'GB': [55.3781, -3.4360],
            'DE': [51.1657, 10.4515],
            'FR': [46.2276, 2.2137],
            'JP': [36.2048, 138.2529],
            'AU': [-25.2744, 133.7751]
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
            'United States': [37.0902, -95.7129],
            'China': [35.8617, 104.1954],
            'Russia': [61.5240, 105.3188],
            'Brazil': [-14.2350, -51.9253],
            'India': [20.5937, 78.9629],
            'United Kingdom': [55.3781, -3.4360],
            'Germany': [51.1657, 10.4515],
            'France': [46.2276, 2.2137],
            'Japan': [36.2048, 138.2529],
            'Australia': [-25.2744, 133.7751]
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
