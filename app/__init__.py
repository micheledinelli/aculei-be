from flask import Flask
from flask import jsonify
import logging

from flasgger import Swagger

from app.utils.exceptions import CustomException

from .landing import routes as landing_routes
from .experience import routes as experience_routes

app = Flask(__name__)
swagger = Swagger(app)

app.config['APPLICATION_ROOT'] = '/api/v1/'

# Registering blueprints
app.register_blueprint(landing_routes.landing_bp, url_prefix=app.config['APPLICATION_ROOT'])
app.register_blueprint(experience_routes.experience_bp, url_prefix=app.config['APPLICATION_ROOT'])

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