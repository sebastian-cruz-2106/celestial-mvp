from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import boto3
import botocore
import mgrs
import requests
from datetime import datetime, timedelta

#Create a session usinng Amazon S3
session = boto3.session.Session()

#Create an S3 client
# This `s3` client to interact with the bucket without needing credentials as the library is public.
s3 = session.client('s3', config=botocore.client.Config(signature_version=botocore.UNSIGNED))

app = Flask(__name__)
CORS(app)

S3_BUCKET_NAME = 'sentinel-s2-l1c'
AWS_BASE_URL = f'https://{S3_BUCKET_NAME}.s3.amazonaws.com/tiles'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/fetch-satellite-data', methods=['POST'])
def fetch_satellite_data():
    s3_urls = []

    boundingBox = request.json.get('boundingBox')
    startDate = request.json.get('startDate')
    endDate = request.json.get('endDate')

    if not (boundingBox and startDate and endDate):
        return jsonify({'error': 'Missing parameters'}), 400

    tiles = region_to_tile(boundingBox)

    year, month, day = startDate.split("-")
    prefix = f'{tiles}/{year}/{month}/{day}/'  # Correct format as per example
    url = f'{AWS_BASE_URL}/{prefix}'

    print(f"Fetching data from: {url}")

    response = requests.get(url)
    if response.status_code == 200:
        # Here, you might need to parse the response content to extract the list of objects.
        # This step might need to be adjusted depending on the format of the response.
        # For now, I will assume it returns a list of file paths:

        paths = response.text.split('\n')  # Assuming the response is a list of paths separated by new lines
        for path in paths[:5]:  # Taking first 5 images
            if path:  # Check if path is not empty
                s3_urls.append(f'{AWS_BASE_URL}/{path}')

    return jsonify({'s3_urls': s3_urls})

def region_to_tile(geojson):
    m = mgrs.MGRS()

    coordinates = geojson['coordinates'][0]  # Extract the outer coordinates list from the polygon

    # Compute bounding box min and max values
    min_x = min(coord[0] for coord in coordinates)
    max_x = max(coord[0] for coord in coordinates)
    min_y = min(coord[1] for coord in coordinates)
    max_y = max(coord[1] for coord in coordinates)

    # Calculate the center of the bounding box
    center = [(min_x + max_x) / 2, (min_y + max_y) / 2]
    
    mgrs_str = m.toMGRS(center[1], center[0], MGRSPrecision=4)
    
    # Extract UTM code, latitude band, and square
    utm_code = mgrs_str[:2]
    lat_band = mgrs_str[2]
    square = mgrs_str[3:5]
    
    return f"{utm_code}/{lat_band}/{square}"


if __name__ == "__main__":
    app.run(debug=True)
