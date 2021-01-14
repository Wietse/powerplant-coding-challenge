from flask import current_app, jsonify
from werkzeug.exceptions import HTTPException


def init_error_handlers(app):
    app.logger.debug('initializing error handlers')
    app.register_error_handler(APIError, _handle_api_error)
    app.register_error_handler(HTTPException, _handle_http_exception)
    app.register_error_handler(Exception, _handle_exception)


def _handle_http_exception(error):
    """Handle HTTPException by creating a json response.

    The default handlers of Flask will return a html page, which is not what we want in a REST application.
    """
    current_app.logger.exception('HTTPException')
    return jsonify({
        'status_code': error.code,
        'error': str(error),
        'description': error.description,
    }), error.code


def _handle_exception(error):
    current_app.logger.exception('Unhandled exception')
    return jsonify({
        'status_code': 500,
        'error': str(error),
        'description': 'Internal Server Error',
    }), 500


def _handle_api_error(error):
    current_app.logger.exception('APIError')
    return jsonify(error.to_dict()), error.status_code


class APIError(Exception):
    """A general exception class to raise for api errors, defaulting to "400, Bad Request".

    If you want to return extra information you can pass in a dict for 'payload'.
    """

    status_code = 400

    def __init__(self, message="Bad Request", status_code=None, payload=None):
        super().__init__()
        self.message = message
        if status_code:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        result = dict(self.payload or ())
        result['error'] = self.message
        result['status_code'] = self.status_code
        return result
