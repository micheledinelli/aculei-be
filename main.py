import os
import random
from flask import Flask, send_file, Blueprint, request, jsonify
from flask_cors import CORS 
from flasgger import Swagger, swag_from
import time
import pandas as pd

app = Flask(__name__)

CORS(app)  # Enable CORS for all routes in the app

# Path to your 'aculei-images' directory
image_directory = 'aculei-images'

# Initialize an empty list to store image names
image_names = []

# Get a list of all JPEG files in the directory at server startup
def load_image_names():
    global image_names
    image_names = [f for f in os.listdir(image_directory) if f.endswith('.jpg') or f.endswith('.jpeg')]

# Load image names when the server starts
load_image_names()

# Load csv
df = pd.read_csv("aculei.csv")

# Create a blueprint for API version 1
api_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1')

@api_v1.route('/image')
# @swag_from('swagger/image_endpoint.yml')  # Path to your Swagger YAML file for the endpoint documentation
def get_image():
    if not image_names:
      return 'No images found', 404

    cam_number = request.args.get('cam-number')    

    if cam_number != None:
      return send_image_from_cam_filter(cam_number=cam_number)
        
    random_image_name = random.choice(image_names)
    image_path = os.path.join(image_directory, random_image_name)
    return send_file(image_path, mimetype='image/jpeg')

def send_image_from_cam_filter(cam_number):    
    if cam_number is None:
      return jsonify({'error': 'Please provide a valid cam_number'})
    
    cam_number = str(cam_number)
    
    # Find the image for the given cam_number
    try:
      rows_with_cam_number = df[df['cam'] == cam_number]
    
      if len(rows_with_cam_number) == 0:
          return jsonify({'error': 'No rows found for the given cam_number'})
      
      # Select a random row index from filtered rows
      random_index = random.randint(0, len(rows_with_cam_number) - 1)
      random_row = rows_with_cam_number.iloc[random_index]
      image_name = random_row['image_name']
        
      # Set the path to the image (change 'image_dir' to your directory)
      image_path = os.path.join(image_directory, image_name)
      
      # Return the image file
      return send_file(image_path, mimetype='image/jpeg')
    
    except IndexError:
        return jsonify({'error': 'No row found for the given cam_number'})

# Register the blueprint with the app
app.register_blueprint(api_v1)

# Initialize Swagger with your app
Swagger(app)

if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))

