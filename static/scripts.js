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
          // Process and display imagery data here
          console.log(data); // Log the returned data to the console
          if (data.product_ids) {
            alert("Fetched Product IDs: " + data.product_ids.join(", "));
          }
      }).catch(error => {
          console.error("Error fetching imagery:", error);
      });
}


initializeMap();

