import logging
from flask import Flask


def _configure_logging(app):
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
    app.logger.debug('logging configured with level %s', app.logger.level)


def create_app():
    from .exceptions import init_error_handlers
    from .api import register_blueprint

    app = Flask(__name__)
    _configure_logging(app)
    init_error_handlers(app)
    register_blueprint(app)
    return app
