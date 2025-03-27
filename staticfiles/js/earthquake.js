// earthquake.js

const API_URL = 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/significant_month.geojson';

async function fetchEarthquakeData() {
    try {
        const response = await fetch(API_URL);
        const data = await response.json();
        updateEarthquakeData(data.features);
    } catch (error) {
        console.error('Error fetching earthquake data:', error);
    }
}

function updateEarthquakeData(earthquakes) {
    const totalCountElem = document.getElementById('total-count');
    const maxMagnitudeElem = document.getElementById('max-magnitude');
    const latestTimeElem = document.getElementById('latest-time');
    const earthquakesListElem = document.getElementById('earthquakes-list');

    totalCountElem.textContent = earthquakes.length;
    let maxMagnitude = 0;
    let latestTime = 0;

    earthquakes.forEach(earthquake => {
        const { mag, place, time, geometry } = earthquake;
        const [lon, lat, depth] = geometry.coordinates;

        // Update max magnitude and latest time
        if (mag > maxMagnitude) maxMagnitude = mag;
        if (time > latestTime) latestTime = time;

        // Add earthquake marker to globe
        const marker = createEarthquakeMarker(lat, lon, mag);
        scene.add(marker);

        // Add earthquake details to list
        const listItem = document.createElement('div');
        listItem.className = 'earthquake-item';
        listItem.innerHTML = `
            <div><strong>Magnitude:</strong> ${mag}</div>
            <div><strong>Location:</strong> ${place}</div>
            <div><strong>Time:</strong> ${new Date(time).toLocaleString()}</div>
        `;
        earthquakesListElem.appendChild(listItem);
    });

    maxMagnitudeElem.textContent = maxMagnitude;
    latestTimeElem.textContent = new Date(latestTime).toLocaleString();
    loadingContainer.style.display = 'none';
}

function createEarthquakeMarker(lat, lon, magnitude) {
    const radius = 15;
    const color = magnitude >= 6.0 ? 0xff0000 : magnitude >= 4.0 ? 0xffff00 : 0x00ff00;
    const geometry = new THREE.SphereGeometry(0.1 * magnitude, 8, 8);
    const material = new THREE.MeshBasicMaterial({ color });
    const marker = new THREE.Mesh(geometry, material);

    const { x, y, z } = convertLatLonToXYZ(lat, lon, radius);
    marker.position.set(x, y, z);
    return marker;
}

function convertLatLonToXYZ(lat, lon, radius) {
    const phi = (90 - lat) * (Math.PI / 180);
    const theta = (lon + 180) * (Math.PI / 180);
    const x = -radius * Math.sin(phi) * Math.cos(theta);
    const y = radius * Math.cos(phi);
    const z = radius * Math.sin(phi) * Math.sin(theta);
    return { x, y, z };
}

fetchEarthquakeData();
