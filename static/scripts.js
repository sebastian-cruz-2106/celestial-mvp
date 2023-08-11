let map;
let drawnItems;

function initializeMap() {
    map = L.map('map').setView([51.505, -0.09], 13);  // Default to London. Adjust as necessary.

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);

    // Initialize the FeatureGroup to store editable layers
    drawnItems = new L.FeatureGroup();
    map.addLayer(drawnItems);

    // Initialize the draw control and pass it the FeatureGroup of editable layers
    const drawControl = new L.Control.Draw({
        edit: {
            featureGroup: drawnItems
        },
        draw: {
            polygon: false,
            polyline: false,
            rectangle: true,
            circle: false,
            marker: false,
            circlemarker: false,
        }
    });
    map.addControl(drawControl);

    // Initialise the FeatureGroup to store editable layers
    map.addLayer(drawnItems);
    map.on('draw:created', function (e) {
        var type = e.layerType,
            layer = e.layer;

        if (type === 'rectangle') {
            // here you can get the coordinates of the drawn rectangle
            const coords = layer.toGeoJSON().geometry.coordinates;
            // Do something with the coordinates, e.g., console log them
            console.log(coords);
        }

        // Add the drawn layer to the map
        drawnItems.addLayer(layer);
    });

}

function fetchData() {
    const startDate = document.getElementById("startDate").value;
    const endDate = document.getElementById("endDate").value;
    const band = document.getElementById("bandSelect").value;

    if (!startDate || !endDate) {
        alert("Please select both start and end dates.");
        return;
    }

    if (drawnItems.getLayers().length === 0) {
        alert("Please draw a bounding box on the map.");
        return;
    }

    // Get the GeoJSON coordinates directly
    const coords = drawnItems.getLayers()[0].toGeoJSON().geometry.coordinates;
    console.log("Drawn bounding box:", coords);
    // Send an AJAX request to the backend
    fetch("/fetch-satellite-data", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            startDate: startDate,
            endDate: endDate,
            boundingBox: {
                "type": "Polygon",
                "coordinates": coords
            },
        //  band: band
        })
    }).then(response => response.json())
    .then(data => {
        console.log(data); // Log the returned data to the console
        if (data.urls && data.urls.length) {
          // Display the URLs
          const urlDisplayArea = document.getElementById("urlDisplayArea"); // div created in HTML
          urlDisplayArea.innerHTML = ""; // Clear previous URLs
          data.urls.forEach(url => {
              const anchor = document.createElement("a");
              anchor.href = url;
              anchor.target = "_blank";
              anchor.innerText = url;
              urlDisplayArea.appendChild(anchor);
              urlDisplayArea.appendChild(document.createElement("br"));
          });
        } else {
            alert("No imagery found for the given dates and bounding box.");
        }
    }).catch(error => {
        console.error("Error fetching imagery:", error);
    });
}


initializeMap();

