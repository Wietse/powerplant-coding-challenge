import logging

from flask import current_app, request, jsonify, Blueprint

from pcc.lib import distribute_load
from .exceptions import APIError


blueprint = Blueprint('pcd', __name__)


def register_blueprint(app):
    app.register_blueprint(blueprint)


def validate_mandatory_keys(keys, payload):
    for key in keys:
        if key not in payload:
            raise APIError(payload={'reason': f'Missing key "{key}"'})


@blueprint.route('/')
def hello_worl():
    return 'Hello from pcd!\n'


@blueprint.route('/productionplan', methods=['POST'])
def productionplan():
    current_app.logger.debug('productionplan is called')
    if not request.is_json:
        raise APIError()
    json = request.json
    current_app.logger.info('about to validate input')
    validate_mandatory_keys(('load', 'fuels', 'powerplants'), json)
    current_app.logger.debug('productionplan: payload = %s', json)
    result = distribute_load(json)
    current_app.logger.debug('productionplan: result = %s', result)
    return jsonify(result)
