"""
Main entry point for the Flask app with PostgreSQL integration
"""
from dotenv import load_dotenv
load_dotenv()

import sys
import os
from waitress import serve as waitress_serve
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))  # DON'T CHANGE THIS !!!

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager

# Import database configuration
from database import init_db
# from database_lite import init_db

# Import blueprints
from routes.auth_routes import auth_bp
from routes.exam_routes import exam_bp

def create_app():
    """Create and configure the Flask application"""
    # Create Flask app
    app = Flask(__name__)
    CORS(app)  # Enable CORS for all routes
    
    # Configure JWT
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 86400  # 24 hours
    jwt = JWTManager(app)
    
    # Initialize the database
    init_db(app)

    # @app.route('/initdb')
    # def initdb():
    #     init_db(app)
    #     return "<h1>Tables already created. All materials already exist.</h1>", 200    
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(exam_bp, url_prefix='/api/exam')
    
    # Serve static files (avoid naming conflict with waitress.serve)
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_static(path):
        # ensure static_folder is string to satisfy type checker
        static_dir = app.static_folder or ''
        if path and os.path.exists(os.path.join(static_dir, path)):
            return send_from_directory(static_dir, path)
        else:
            return send_from_directory(static_dir, 'index.html')
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"message": "Resource not found"}), 404
    
    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"message": "Internal server error"}), 500
    
    return app

# Create app instance
app = create_app()

if __name__ == '__main__':
    # app.run(host='0.0.0.0', port=8000, debug=True) fff
    waitress_serve(app, host="0.0.0.0", port=8000)
