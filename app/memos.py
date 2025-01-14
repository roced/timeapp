from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from .models import Memo
from .extensions import db
from datetime import datetime
from .forms.memo_form import MemoForm

memos = Blueprint('memos', __name__)

@memos.route('/memos')
@login_required
def list():
    """List all memos for the current user."""
    memos = Memo.query.filter_by(user_id=current_user.id).order_by(Memo.created_at.desc()).all()
    return render_template('memos/list.html', memos=memos)

@memos.route('/memos/create', methods=['GET', 'POST'])
@login_required
def create():
    form = MemoForm()
    if form.validate_on_submit():
        memo = Memo(
            title=form.title.data,
            content=form.content.data,
            due_date=form.due_date.data,
            user_id=current_user.id
        )
        db.session.add(memo)
        db.session.commit()
        flash('Memo created successfully!', 'success')
        return redirect(url_for('memos.view', id=memo.id))
    return render_template('memos/create.html', form=form)

@memos.route('/memos/<int:id>/view')
def view(id):
    memo = db.session.get(Memo, id)
    if not memo:
        abort(404)
    if not current_user.is_authenticated or current_user.id != memo.user_id:
        abort(404)
    return render_template('memos/view.html', memo=memo)

@memos.route('/memos/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    memo = db.session.get(Memo, id)
    if not memo:
        abort(404)
    if memo.user_id != current_user.id:
        abort(403)
    
    form = MemoForm(obj=memo)
    if form.validate_on_submit():
        memo.title = form.title.data
        memo.content = form.content.data
        memo.due_date = form.due_date.data
        db.session.commit()
        flash('Memo updated successfully!', 'success')
        return redirect(url_for('memos.view', id=id))
    
    return render_template('memos/edit.html', form=form, memo=memo)

@memos.route('/memos/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    memo = db.session.get(Memo, id)
    if not memo:
        abort(404)
    if memo.user_id != current_user.id:
        abort(403)
    
    db.session.delete(memo)
    db.session.commit()
    flash('Memo deleted successfully.', 'success')
    return redirect(url_for('memos.list')) 