import os
import random
from flask import Flask, send_file, Blueprint, request, jsonify
from flask_cors import CORS 
from flasgger import Swagger
import time
import pandas as pd

app = Flask(__name__)
CORS(app)

image_directory = 'aculei-images-test'
csv_directory = 'aculei-test.csv'

image_names = []

def load_image_names():
  global image_names
  image_names = [f for f in os.listdir(image_directory) if f.endswith('.jpg') or f.endswith('.jpeg')]

load_image_names()
df = pd.read_csv(csv_directory)

api_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1')

@api_v1.route('/image')
def get_image():
    if not image_names:
      return 'No images found', 404

    cam_number = request.args.get('cam')    

    if cam_number != None:
      return send_image_from_cam_filter(cam_number=cam_number)
        
    random_image_name = random.choice(image_names)
    image_path = os.path.join(image_directory, random_image_name)
    return send_file(image_path, mimetype='image/jpeg')

def send_image_from_cam_filter(cam_number):    
    if cam_number is None:
      return 'Please provide a valid cam number', 404
        
    cam_number = str(cam_number)

    try:
      rows_with_cam_number = df[df['cam'] == cam_number]
    
      if len(rows_with_cam_number) == 0:
        return f'Cam {cam_number} has no images at the moment', 404
      
      random_index = random.randint(0, len(rows_with_cam_number) - 1)
      random_row = rows_with_cam_number.iloc[random_index]
      image_name = random_row['image_name']
      image_path = os.path.join(image_directory, image_name)      
      
      return send_file(image_path, mimetype='image/jpeg')
    except IndexError:
        return jsonify({'error': 'No row found for the given cam_number'})

app.register_blueprint(api_v1)

Swagger(app)

if __name__ == '__main__':
  app.run(debug=True, port=os.getenv("PORT", default=5000))

