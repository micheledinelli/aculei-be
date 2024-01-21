import os
import random
import json
import re
import time

import pandas as pd

from flask import Flask, send_file, Blueprint, request, jsonify, make_response, Response
from flask_cors import CORS 
from flasgger import Swagger

app = Flask(__name__)
CORS(app)

image_directory = 'aculei-images-test'
video_directory = 'aculei-videos'
csv_directory = './datasets'

global df 
df = pd.read_pickle(csv_directory + "/aculei-test.pkl")

global centroid_df
centroid_df = pd.read_pickle(csv_directory + "/clusters.pkl")

def load_video_names():
  global video_names
  video_names = [f for f in os.listdir(video_directory) if f.endswith('.webm')]

load_video_names()

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
  total_rows = len(df)
  random_index = random.randint(0, total_rows - 1)

  # Extract a random row based on the random index
  random_row = df.iloc[random_index]

  random_image_name = random_row['image_name']
  image_path = os.path.join(image_directory, random_image_name)

  image_response = make_response(send_file(image_path, mimetype='image/jpg'))

  image_response.headers['x-sha256'] = random_row['sha256']
  image_response.headers['Access-Control-Expose-Headers'] = 'x-sha256'
  return image_response

@api_v1.route('/image/<sha256>')
def get_image_by_sha(sha256):
  image_row = df[df['sha256'] == sha256]

  if image_row.empty:
    return "Image not found for the given SHA-256 value", 404
  
  if image_row.shape[0] != 1:
     return "Multiple images found for the given SHA-256 value", 404
  
  # Extract a random row based on the random index
  image_name = image_row['image_name'].iloc[0]
  image_path = os.path.join(image_directory, image_name)

  image_response = make_response(send_file(image_path, mimetype='image/jpg'))

  image_response.headers['x-sha256'] = image_row['sha256'].iloc[0]
  image_response.headers['Access-Control-Expose-Headers'] = 'x-sha256'
  return image_response

@api_v1.route('/image/<sha256>/details', methods=['GET'])
def get_image_detail(sha256):
  image_row = df[df['sha256'] == sha256]

  if image_row.empty:
    return "Image not found for the given SHA-256 value", 404

  image_row['sha256'] = None
  # Convert the row to a dictionary and then to JSON
  image_data = image_row.to_dict(orient='records')

  # Clean up the NaN values from the dictionary
  cleaned_data = [{k: v for k, v in item.items() if pd.notnull(v)} for item in image_data]
  return jsonify(cleaned_data[0])

@api_v1.route('/clusters/<cluster>/image', methods=['GET'])
def get_cluster_image(cluster):
  df_cluster = df[df['cluster'] == float(cluster)]
  if df_cluster.empty:
    return "Image not found for the given SHA-256 value", 404

  image_row = df_cluster.sample(1)
  random_image_name = image_row['image_name'].iloc[0]
  image_path = os.path.join(image_directory, random_image_name)

  image_response = make_response(send_file(image_path, mimetype='image/jpg'))

  image_response.headers['x-sha256'] = image_row['sha256'].iloc[0]
  image_response.headers['Access-Control-Expose-Headers'] = 'x-sha256'
  return image_response

@api_v1.route('/clusters/<cluster>', methods=['GET'])
def get_cluster_details(cluster):
  cluster_info = centroid_df.iloc[int(cluster), :]
  print(f"Information for Cluster {cluster}:\n{cluster_info}")

  data = cluster_info.to_dict()

  return jsonify(data)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok"})

@app.route('/', methods=['GET'])
def default():
    return jsonify({"hello": "from aculei-be!"})

app.register_blueprint(api_v1)
Swagger(app)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=os.getenv("PORT", default=5001))