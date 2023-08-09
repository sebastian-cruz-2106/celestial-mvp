from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt
from datetime import date
from boto3 import session, resource
import os

app = Flask(__name__)
CORS(app) # This will enable CORS for all routes

# Configure your Copernicus Open Access Hub credentials
USER = 'juansebascruz'
PASSWORD = '90JsC06&'
API_URL = 'https://scihub.copernicus.eu/dhus'

#Configure AWS
S3_BUCKET_NAME = 'celestial.imagery'

#Initialize the S3 resource
s3 = resource('s3')

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

    # Get product IDs 
    #Right now we will just download 2 images
    product_ids = list(products.keys())[:2]

    for product_id in product_ids:
        # Download the image
        product_info = api.download(product_id)
        download_path = product_info['path']
        
        # Upload to AWS S3
        s3_object_name = os.path.basename(download_path)
        s3.Bucket(S3_BUCKET_NAME).upload_file(download_path, s3_object_name)
        
        # Append the public S3 URL to the list
        s3_url = f"https://{S3_BUCKET_NAME}.s3.amazonaws.com/{s3_object_name}"
        s3_urls.append(s3_url)

        # Optionally, delete the local file after upload to free space
        os.remove(download_path)
    
    return jsonify({'s3_urls': s3_urls})

if __name__ == '__main__':
    app.run(debug=True)
