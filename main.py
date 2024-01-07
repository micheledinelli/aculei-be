import os
import random
from flask import Flask, send_file, Blueprint, request, jsonify
from flask_cors import CORS 
from flasgger import Swagger
import pandas as pd
import re
from flask import Response

app = Flask(__name__)
CORS(app)

image_directory = 'aculei-images-test'
video_directory = 'aculei-videos'
csv_directory = 'aculei-test.csv'

image_names = []
video_names = []

def load_video_names():
  global video_names
  video_names = [f for f in os.listdir(video_directory) if f.endswith('.webm')]

def load_image_names():
  global image_names
  image_names = [f for f in os.listdir(image_directory) if f.endswith('.jpg') or f.endswith('.jpeg')]

load_image_names()
load_video_names()

df = pd.read_csv(csv_directory)

api_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1')

@api_v1.route('/video')
def get_video():
  random_video_name = random.choice(video_names)
  video_path = os.path.join(video_directory, random_video_name)
  
  range_header = request.headers.get('Range')
  file_size = os.path.getsize(video_path)
  
  start, end = 0, None
  length = file_size
  
  if range_header:
      range_match = re.match(r'bytes=(\d+)-(\d*)', range_header)
      if range_match:
          start = int(range_match.group(1))
          end = int(range_match.group(2)) if range_match.group(2) else file_size - 1
          length = end - start + 1
  
  headers = {
      'Content-Type': 'video/webm',
      'Accept-Ranges': 'bytes',
  }
  
  if start != 0 or end is not None:
      headers['Content-Range'] = f'bytes {start}-{end}/{file_size}'
      headers['Content-Length'] = length
      status_code = 206  # Partial Content
  else:
      status_code = 200  # Full Content
  
  with open(video_path, 'rb') as video_file:
      video_file.seek(start)
      data = video_file.read(length)
  
  response = Response(
    data,
    mimetype='video/webm',
    headers={
        'Accept-Ranges': 'bytes',
        'Content-Range': f'bytes {start}-{end}/{file_size}',
        'Content-Length': length
    },
    status=status_code
  )
  return response 

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

