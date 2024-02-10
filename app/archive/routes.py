import os
import random
import re
from flask import Blueprint, Response, request, send_file
from flask import jsonify
from app.db import df

import logging

logger = logging.getLogger(__name__)
archive_bp = Blueprint('archive_bp', __name__)

# Get the video names and directory
selecta_directory = 'app/db/static/selecta'
image_names = os.listdir(selecta_directory)

@archive_bp.route('archive/filters', methods=['GET'])
def get_filters():
    """
    Return the filters
    ---
    tags:
        - filters
    responses:
      200:
        description: The filters
      500:
        description: Server error
    """
    try:
        filters_labels = df.columns.tolist()

        return jsonify({'filters': filters_labels})
    except Exception as e:
        logger.exception('An exception occurred during a request.', str(e))
        return jsonify({'error': 'error in getting filters'})

@archive_bp.route('archive/images', methods=['GET'])
def get_filtered_images():
    """
    Return the images according to the filters
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
        random_row = df.sample(1)
        sha_256 = random_row['sha256'].values[0]

        # With the sha256 retrieve the image from the selecta
        
        # image_path = os.path.join("db/static/selecta", image_name)
        # response = send_file(image_path, mimetype='image/webp')
        # response.headers['x-sha256'] = '*'
        return jsonify({'image': "image"})
    except Exception as e:
        logger.exception('An exception occurred during a request.', str(e))
        return jsonify({'error': 'error in getting random selecta image'})