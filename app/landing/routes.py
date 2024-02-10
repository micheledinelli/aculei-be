import os
import random
import re
from flask import Blueprint, Response, request
from flask import jsonify
import logging

from app.db import df
from app.db import camera_df
from app.utils.exceptions import CustomException

logger = logging.getLogger(__name__)
landing_bp = Blueprint('landing_bp', __name__)

# Get the video names and directory
video_directory = 'app/db/static/videos'
video_names = os.listdir(video_directory)

@landing_bp.route('/cameras', methods=['GET'])
def get_cameras():
    """
    Information about cameras
    ---
    tags:
        - cameras
    responses:
      200:
        description: List of cameras
      500:
        description: Server error
    """
    try:
        data = []
        for index, row in camera_df.iterrows():
            row_dict = row.to_dict()
            data.append(row_dict)
        return data
    except Exception as e:
        logger.exception('An exception occurred during a request.', str(e))
        raise CustomException('Error', 500)

@landing_bp.route('/cameras/<int:camera_id>', methods=['GET'])
def get_camera(camera_id=None):
    """
    Information about a specific camera
    ---
    tags:
        - cameras
    parameters:
        - name: camera_id
          in: path
          type: int
          
    responses:
      200:
        description: Camera detail
      500:
        description: Server error
    """
    try:
        if not camera_df.hunter_camera.isin([camera_id]).any():
            raise CustomException('Camera not found', 404)

        camera = camera_df.loc[camera_df['hunter_camera'] == camera_id]
        data = {
            'hunter_camera': camera['hunter_camera'].values[0],
            'description': camera['description'].values[0],
            'coordinates': camera['coordinates'].values[0],
            'last_image': camera['last_image'].values[0],
        }
    
        return jsonify(data)
    
    except CustomException as e:
        raise e
    except Exception as e:
        logger.exception('An exception occurred during a request.', str(e))
        raise CustomException('Error', 500)

@landing_bp.route('/dataset', methods=['GET'])
def df_stats():
    """
    Information about the dataset
    ---
    tags:
        - dataset
    responses:
      200:
        description: Dataset insights
      500:
        description: Server error
    """
    try:
        return df.animal.value_counts().to_dict()
    except Exception as e:
        logger.exception('An exception occurred during a request.', str(e))
        return CustomException('Error', 500)

@landing_bp.route('/video')
def get_video():
    """ 
    A random video
    ---
    tags:
        - videos
    responses:
      200:
        description: Video content
      206:
        description: Partial Content
      500:
        description: Server error
    """
    try:
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
    except Exception as e:
        logger.exception('An exception occurred during a request.', str(e))
        raise CustomException('Error', 500)