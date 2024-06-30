from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
import os
from models import db, Product
from flask_login import current_user, login_required
from functools import wraps
from config import Config

product_bp = Blueprint('product', __name__)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash('Only admins can access this page.', 'danger')
            return redirect(url_for('main.home'))
        return f(*args, **kwargs)
    return decorated_function



@product_bp.route('/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        file = request.files['image']

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(current_app.static_folder, 'uploads', filename)
            file.save(file_path)

            new_product = Product(
                name=name,
                description=description,
                price=price,
                image_url='uploads/' + filename  
            )
            db.session.add(new_product)
            db.session.commit()
            flash('Product added successfully!')
            return redirect(url_for('product.view_products'))

    return render_template('add_product.html')

@product_bp.route('/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)

    if request.method == 'POST':
        product.name = request.form['name']
        product.description = request.form['description']
        product.price = float(request.form['price'])

        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
                file.save(file_path)
                product.image_url = file_path.replace('\\', '/')

        db.session.commit()
        flash('Product updated successfully!')
        return redirect(url_for('product.view_products'))
    product = Product.query.get_or_404(product_id)
    return render_template('edit_product.html', product=product)


@product_bp.route('/delete/<int:product_id>', methods=['POST'])
@login_required
@admin_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    
  
    db.session.delete(product)
    db.session.commit()
    
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('product.view_products'))


@product_bp.route('/product/<int:product_id>', methods=['GET'])
@login_required
def product_details(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('product_details.html', product=product)


@product_bp.route('/buy_product/<int:product_id>', methods=['GET', 'POST'])
@login_required
def buy_product(product_id):
    product = Product.query.get_or_404(product_id)
    # Handle the buying process here
    # For now, we'll just render a simple confirmation page
    return render_template('buy_product.html', product=product)


@product_bp.route('/products', methods=['GET'])
@login_required
def view_products():
    products = Product.query.all()
    return render_template('products.html', products=products)
