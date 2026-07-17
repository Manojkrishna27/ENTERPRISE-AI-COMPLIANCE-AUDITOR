import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from app.config import Config
from app.database import db, migrate

jwt = JWTManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Enable CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # Ensure upload directory exists
    if app.config['USE_LOCAL_STORAGE']:
        os.makedirs(app.config['LOCAL_STORAGE_DIR'], exist_ok=True)

    # Register blueprints (we will create these routers in the next steps)
    from app.routers.auth import auth_bp
    from app.routers.contracts import contracts_bp
    from app.routers.policies import policies_bp
    from app.routers.analysis import analysis_bp
    from app.routers.search import search_bp
    from app.routers.reports import reports_bp
    from app.routers.dashboard import dashboard_bp
    from app.routers.admin import admin_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(contracts_bp, url_prefix='/api/contracts')
    app.register_blueprint(policies_bp, url_prefix='/api/policies')
    app.register_blueprint(analysis_bp, url_prefix='/api/analysis')
    app.register_blueprint(search_bp, url_prefix='/api/search')
    app.register_blueprint(reports_bp, url_prefix='/api/reports')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')

    # JWT Error handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({"msg": "Token has expired", "error": "token_expired"}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({"msg": "Signature verification failed", "error": "token_invalid"}), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({"msg": "Request does not contain an access token", "error": "token_missing"}), 401

    # Simple health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health():
        return jsonify({"status": "healthy", "service": "compliance-auditor"}), 200

    return app
