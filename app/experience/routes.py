import os
import random
import re
from flask import Blueprint, Response, request, send_file
from flask import jsonify
from app.db import df
from app.db import selecta_df
from app.utils.exceptions import CustomException
import logging

logger = logging.getLogger(__name__)
experience_bp = Blueprint('experience_bp', __name__)

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
        
        # Handle Nan values filling with null
        image_row = image_row.fillna('null')

        return image_row.to_dict(orient='records')
    except Exception as e:
        logger.exception('An exception occurred during a request.', str(e))
        return jsonify({'error': 'error in getting random selecta image'})