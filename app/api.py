from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from .services.event_service import EventService

api = Blueprint('api', __name__, url_prefix='/api')

@api.route('/events/<int:id>/like', methods=['POST'])
@login_required
def toggle_like(id):
    """Toggle like status for an event."""
    is_liked = EventService.toggle_like(id, current_user.id)
    return jsonify({'liked': is_liked})

@api.route('/events/<int:id>/attend', methods=['POST'])
@login_required
def toggle_attendance(id):
    """Toggle attendance status for an event."""
    is_attending = EventService.toggle_attendance(id, current_user.id)
    return jsonify({'attending': is_attending})

@api.route('/events/<int:id>/wishlist', methods=['POST'])
@login_required
def toggle_wishlist(id):
    """Toggle wishlist status for an event."""
    in_wishlist = EventService.toggle_wishlist(id, current_user.id)
    return jsonify({'in_wishlist': in_wishlist}) 