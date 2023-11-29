import os
import random
from flask import Flask, send_file, Blueprint
from flask_cors import CORS 
from flasgger import Swagger, swag_from

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

# Create a blueprint for API version 1
api_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1')

@api_v1.route('/image')
# @swag_from('swagger/image_endpoint.yml')  # Path to your Swagger YAML file for the endpoint documentation
def get_image():

    """
    Get a random image.

    This endpoint returns a random image from the 'aculei-images' directory.
    ---
    responses:
      200:
        description: A random image file.
        content:
          image/jpeg:
            schema:
              type: string
              format: binary
      404:
        description: No images found.
    """

    if not image_names:
        return 'No images found', 404  # If no images are found, return a 404 error
    
    random_image_name = random.choice(image_names)
    
    image_path = os.path.join(image_directory, random_image_name)
    
    return send_file(image_path, mimetype='image/jpeg')

# Register the blueprint with the app
app.register_blueprint(api_v1)

# Initialize Swagger with your app
Swagger(app)

if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))

