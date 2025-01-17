import os
from flask import Blueprint, send_file
from flask_cors import CORS

from flask import jsonify
from app.db import selecta_df
from app.utils.exceptions import CustomException
import logging

logger = logging.getLogger(__name__)
experience_bp = Blueprint('experience_bp', __name__, url_prefix='/api/v1')

CORS(experience_bp)

# Get the video names and directory
selecta_directory = 'app/db/static/selecta'
image_names = os.listdir(selecta_directory)

@experience_bp.route('selecta/images/random', methods=['GET'])
def get_random_selecta_image():
    """
    One of the selected images
    ---
    tags:
        - images
    responses:
      200:
        description: A random image
      500:
        description: Server error
    """
    try:
        random_row = selecta_df.sample(1)
        sha_256 = random_row['sha256'].values[0]
        image_name = random_row['image_name'].values[0]          
        image_path = os.path.join("db/static/selecta", image_name + '.webp')
        response = send_file(image_path, mimetype='image/webp')
        response.headers['x-sha256'] = sha_256
        response.headers['Access-Control-Expose-Headers'] = 'x-sha256'
        response.headers['x-image-name'] = image_name
        return response
    except Exception as e:
        logger.exception('An exception occurred during a request.', str(e))
        return jsonify({'error': 'error in getting random selecta image'})
    
@experience_bp.route('selecta/images/<image_id>', methods=['GET'])
def get_image(image_id=None):
    """
    A specific selected image
    ---
    tags:
        - images
    parameters:
        - name: image_id
          in: path
    responses:
      200:
        description: An image with the given id
      500:
        description: Server error
    """
    try:
      image_row = selecta_df[selecta_df['image_name'] == image_id]
      if image_row.empty:
        image_row = selecta_df[selecta_df['sha256'] == image_id]

      if image_row.empty:
        raise CustomException('Image not found', 404)
      # Keep the first row
      image_row = image_row.head(1)
      
      # Handle Nan values filling with null
      image_row = image_row.fillna('null')

      # Convert the DataFrame to a dictionary
      image_dict = image_row.to_dict(orient='records')

      data_to_keep = ['animal', 'temperature', 'moon_phase', 'date_time', 'hunter_camera']

      # If the DataFrame was not empty, image_dict will be a list with one dictionary.
      # We return this dictionary. If the DataFrame was empty, we return an empty dictionary.
      if image_dict:
        image = image_dict[0]
        image = {k: v for k, v in image.items() if k in data_to_keep and v != 'null'}
        return image
      else:
        raise CustomException('Image not found', 404)
    
    except Exception as e:
        logger.exception('An exception occurred during a request.', str(e))
        return jsonify({'error': 'error in getting random selecta image'})