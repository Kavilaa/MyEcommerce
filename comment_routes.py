from flask import Blueprint, request, jsonify, redirect, url_for, flash
from flask_login import current_user, login_required
from models import db, Comment, Product, User
from datetime import datetime

comment_bp = Blueprint('comment', __name__)

@comment_bp.route('/product/<int:product_id>/add_comment', methods=['POST'])
@login_required
def add_comment(product_id):
    body = request.form.get('body')
    
    if not body:
        flash('Comment body is required', 'error')
        return redirect(url_for('product.product_details', product_id=product_id))
    
    product = Product.query.get_or_404(product_id)
    comment = Comment(content=body, author=current_user, product=product)
    
    db.session.add(comment)
    db.session.commit()
    
    flash('Comment added successfully!', 'success')
    return redirect(url_for('product.product_details', product_id=product_id))

@comment_bp.route('/product/<int:product_id>/comments', methods=['GET'])
@login_required
def get_comments(product_id):
    product = Product.query.get_or_404(product_id)
    comments = [{
        'id': comment.id,
        'body': comment.content,
        'author': comment.author.username,
        'timestamp': comment.created_at.strftime('%Y-%m-%d %H:%M:%S') if comment.created_at else None
    } for comment in product.comments]
    
    return jsonify(comments), 200

@comment_bp.route('/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if comment.author_id != current_user.id and not current_user.is_admin:
        flash('You are not authorized to delete this comment!', 'error')
        return redirect(url_for('product.product_details', product_id=comment.product_id))

    db.session.delete(comment)
    db.session.commit()
    flash('Comment deleted successfully!', 'success')
    return redirect(url_for('product.product_details', product_id=comment.product_id))
