import os
import random
import re
import pandas as pd
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
        available_filters = [
            "temperature",
            "date_time",
            "moon_phase",
            "animal",
            "hunter_camera"
        ]

        filters_labels = list(filter(lambda x: x in available_filters, df.columns.tolist()))
        
        data = {}
        for filter_label in filters_labels:
            if filter_label == "temperature":
                min_max = (int(df.temperature.min()), 
                           int(df.temperature.max()))
                
                pairs = list()
                for i in range(min_max[0], min_max[1], 5):
                    pairs.append({'min': i, 'max': i + 5})
                data[filter_label] = {'spec': pairs}

            elif filter_label == "moon_phase":
                data[filter_label] = {'spec': list(filter(lambda x: not pd.isna(x), df.moon_phase.unique()))}

            elif filter_label == "animal":
                data[filter_label] = {'spec': list(filter(lambda x: not pd.isna(x), df.animal.unique()))}

            elif filter_label == "date_time":
                dates = pd.to_datetime(df.date_time)
                min = dates.min().date()
                max = dates.max().date()            

                data['date'] = {'spec': {'min': min, 'max': max}}

            elif filter_label == "hunter_camera":
                hunter_cameras = list(filter(lambda x: not pd.isna(x), df.hunter_camera.unique()))
                hunter_cameras = sorted(hunter_cameras)
                data[filter_label] = {'spec': hunter_cameras}
            else:
                data[filter_label] = None

        return jsonify({'filters': data})
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