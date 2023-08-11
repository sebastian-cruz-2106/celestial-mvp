from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

SEARCH_ENDPOINT = "https://earth-search.aws.element84.com/v0/search"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/fetch-satellite-data', methods=['POST'])
def fetch_satellite_data():
    data = request.json
    polygon = data.get('boundingBox', {}).get('coordinates', [[]])[0]
    startDate = data.get('startDate')
    endDate = data.get('endDate')

    if not polygon or not startDate or not endDate:
        return jsonify({'error': 'Missing parameters'}), 400

    min_x, min_y, max_x, max_y = float('inf'), float('inf'), float('-inf'), float('-inf')
    for coord in polygon:
        lon, lat = coord
        min_x = min(min_x, lon)
        min_y = min(min_y, lat)
        max_x = max(max_x, lon)
        max_y = max(max_y, lat)

    search_payload = {
        "bbox": [min_x, min_y, max_x, max_y],
        "datetime": f"{startDate}/{endDate}",
        "collections": ["sentinel-s2-l1c"],
        "limit": 5
    }

    app.logger.info('Search payload: %s', search_payload)
    try:
        response = requests.post(SEARCH_ENDPOINT, json=search_payload)
        response.raise_for_status()  # Raise an HTTPError if the HTTP request returned an unsuccessful status code.

        assets = response.json().get("features", [])
        
        urls = [asset["assets"]["thumbnail"]["href"] for asset in assets if "thumbnail" in asset["assets"]]
        
        if urls:
            app.logger.info('Thumbnails: %s', urls)
            return jsonify({'urls': urls}), 200
        else:
            return jsonify({'error': 'No thumbnails found for the given criteria'}), 400

    except requests.RequestException as e:
        app.logger.error('Request error: %s', e)
        return jsonify({'error': 'Unable to fetch imagery due to a server error'}), 500

if __name__ == '__main__':
    app.run()  # Set to True for better error messages and auto-reloading
