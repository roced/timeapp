from flask import render_template
from flask import Blueprint

errors = Blueprint('errors', __name__)

@errors.app_errorhandler(404)
def page_not_found(error):
    """Handle 404 errors."""
    return render_template('errors/404.html'), 404

@errors.app_errorhandler(500)
def internal_server_error(error):
    """Handle 500 errors."""
    return render_template('errors/500.html'), 500