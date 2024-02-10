import os
import random
import re
from flask import Blueprint, Response, request, send_file
from flask import jsonify

import logging

logger = logging.getLogger(__name__)
experience_bp = Blueprint('experience_bp', __name__)

# Get the video names and directory
selecta_directory = 'app/db/static/selecta'
image_names = os.listdir(selecta_directory)

@experience_bp.route('selecta/images/image', methods=['GET'])
def get_random_image():
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
        image_name = random.choice(image_names)
        image_path = os.path.join("db/static/selecta", image_name)
        return send_file(image_path, mimetype='image/webp')
    except Exception as e:
        logger.exception('An exception occurred during a request.', str(e))
        return jsonify({'error': 'error in getting random selecta image'})
    
@experience_bp.route('selecta/images/image/<int:image_id>', methods=['GET'])
def get_image(image_id=None):
    """
    A specific selected image
    ---
    tags:
        - images
    parameters:
        - name: image_id
          in: path
          type: int
    responses:
      200:
        description: An image with the given id
      500:
        description: Server error
    """
    try:
        image_name = random.choice(image_names)
        image_path = os.path.join("db/static/selecta", image_name)
        return send_file(image_path, mimetype='image/webp')
    except Exception as e:
        logger.exception('An exception occurred during a request.', str(e))
        return jsonify({'error': 'error in getting random selecta image'})