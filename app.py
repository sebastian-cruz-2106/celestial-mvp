from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt
from datetime import date

app = Flask(__name__)
CORS(app) # This will enable CORS for all routes

# Configure your Copernicus Open Access Hub credentials
USER = 'juansebascruz'
PASSWORD = '90JsC06&'
API_URL = 'https://scihub.copernicus.eu/dhus'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/fetch-satellite-data', methods=['POST'])
def fetch_satellite_data():
    # Get the bounding box from the POST request
    boundingBox = request.json.get('boundingBox', None)
    startDate = request.json.get('startDate', None)
    endDate = request.json.get('endDate', None)

    print(request.json)

    if not boundingBox or not startDate or not endDate:
        return jsonify({'error': 'Invalid parameters'}), 400

    # Convert the coordinates into a format that sentinelsat can use
    #geojson = {
    #    "type": "Polygon",
    #    "coordinates": [boundingBox]
    #}
    geojson=boundingBox
    #Convert dates to Sentinel format
    startDate = startDate.replace("-", "")
    endDate = endDate.replace("-", "")
    
    # Connect to the Sentinel API
    api = SentinelAPI(USER, PASSWORD, API_URL)

    footprint = geojson_to_wkt(geojson)
    products = api.query(footprint,
                         date=(startDate, endDate),
                         platformname='Sentinel-2',
                         cloudcoverpercentage=(0, 30))

    # For now, just return the product ids. In a real application, you might want to
    # download the data, process it, and/or store it.
    product_ids = list(products.keys())

    return jsonify({'product_ids': product_ids})

if __name__ == '__main__':
    app.run(debug=True)
