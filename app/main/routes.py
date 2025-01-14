from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from ..services.search_service import SearchService

@main.route('/search')
@login_required
def search():
    query = request.args.get('q', '')
    if not query:
        return render_template('main/search.html', query=query)
        
    events = SearchService.search_events(query, current_user.id)
    memos = SearchService.search_memos(query, current_user.id)
    
    return render_template('main/search.html',
                         query=query,
                         events=events,
                         memos=memos)

@main.route('/api/search')
@login_required
def api_search():
    query = request.args.get('q', '')
    type = request.args.get('type', 'all')
    
    results = {
        'events': [],
        'memos': []
    }
    
    if type in ['all', 'events']:
        events = SearchService.search_events(query, current_user.id)
        results['events'] = [{
            'id': e.id,
            'title': e.title,
            'start_date': e.start_date.strftime('%Y-%m-%d'),
            'location': e.location
        } for e in events]
        
    if type in ['all', 'memos']:
        memos = SearchService.search_memos(query, current_user.id)
        results['memos'] = [{
            'id': m.id,
            'title': m.title,
            'created_at': m.created_at.strftime('%Y-%m-%d %H:%M')
        } for m in memos]
    
    return jsonify(results) 