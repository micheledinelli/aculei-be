from flask import Flask
from flask import jsonify
from flasgger import Swagger

import logging

from flask_cors import CORS

from app.utils.exceptions import CustomException

from .landing import routes as landing_routes
from .experience import routes as experience_routes
from .archive import routes as archive_routes

app = Flask(__name__)

app.config['APPLICATION_ROOT'] = '/api/v1/'

landing_bp = landing_routes.landing_bp
experience_bp = experience_routes.experience_bp
archive_bp = archive_routes.archive_bp

CORS(app)
CORS(landing_bp)
CORS(experience_bp)

# Registering blueprints
app.register_blueprint(landing_routes.landing_bp, url_prefix=app.config['APPLICATION_ROOT'])
app.register_blueprint(experience_routes.experience_bp, url_prefix=app.config['APPLICATION_ROOT'])
app.register_blueprint(archive_routes.archive_bp, url_prefix=app.config['APPLICATION_ROOT'])


Swagger(app)

# Configure Flask logging
app.logger.setLevel(logging.INFO)
handler = logging.FileHandler('app.log')
app.logger.addHandler(handler)

@app.errorhandler(500)
def server_error(error):
    app.logger.exception('An exception occurred during a request.')
    return jsonify({'error': 'Server error'}), 500

@app.errorhandler(404)
def server_error(error):
    app.logger.exception('An exception occurred during a request.')
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(CustomException)
def handle_custom_exception(error):
    response = jsonify({'error': error.message})
    response.status_code = error.error_code
    return response

@app.route('/', methods=['GET', 'OPTIONS'])
def health_check():
    """
    Health check endpoint
    ---
    tags:
        - health
    responses:
      200:
        description: Service status
    """
    return jsonify({"health": "up"})