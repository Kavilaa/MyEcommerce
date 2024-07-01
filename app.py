from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config
from models import db, User
from auth import auth_bp
from product_routes import product_bp
from routes import bp as main_bp
from cart_routes import cart_bp
from comment_routes import comment_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate = Migrate(app, db)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.template_filter('sum_cart_total')
    def sum_cart_total(cart_items):
        return sum(item.product.price * item.quantity for item in cart_items)

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(product_bp, url_prefix='/products')
    app.register_blueprint(cart_bp, url_prefix='/cart')
    app.register_blueprint(main_bp)
    app.register_blueprint(comment_bp)

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
