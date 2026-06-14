from flask import Flask
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config import Config
from models import db
import os

bcrypt = Bcrypt()
jwt = JWTManager()

def create_app():
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    CORS(app)
    
    # Create upload folder
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    
    # Register blueprints
    from routes.auth import auth_bp
    from routes.upload import upload_bp
    from routes.pages import pages_bp
    from routes.mobile import mobile_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(upload_bp, url_prefix='/api')
    app.register_blueprint(pages_bp)
    app.register_blueprint(mobile_bp, url_prefix='/api')

    # Lightweight health check endpoint
    @app.route('/health')
    def health():
        return {"status": "ok"}, 200
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
