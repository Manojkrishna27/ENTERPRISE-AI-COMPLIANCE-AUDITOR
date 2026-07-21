import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from app.config import Config
from app.database import db, migrate
from app.services.redis_service import redis_service
from flasgger import Swagger
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import uuid
import datetime
from flask import request, g

jwt = JWTManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Swagger
    app.config['SWAGGER'] = {
        'title': 'Enterprise AI Compliance Auditor API',
        'uiversion': 3,
        'openapi': '3.0.0'
    }
    swagger = Swagger(app)

    # Limiter
    limiter = Limiter(
        get_remote_address,
        app=app,
        storage_uri=app.config.get('REDIS_URL', 'redis://localhost:6379/0'),
        default_limits=["200 per day", "50 per hour"]
    )
    # Store limiter in app extensions so blueprints can use it
    app.extensions['limiter'] = limiter

    # Enable CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    redis_service.init_app(app)

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
    from app.routers.system import system_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(contracts_bp, url_prefix='/api/contracts')
    app.register_blueprint(policies_bp, url_prefix='/api/policies')
    app.register_blueprint(analysis_bp, url_prefix='/api/analysis')
    app.register_blueprint(search_bp, url_prefix='/api/search')
    app.register_blueprint(reports_bp, url_prefix='/api/reports')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(system_bp, url_prefix='/api')

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

    @jwt.token_in_blocklist_loader
    def check_if_token_is_revoked(jwt_header, jwt_payload):
        jti = jwt_payload["jti"]
        return redis_service.is_token_blocklisted(jti)

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return jsonify({"msg": "The token has been revoked", "error": "token_revoked"}), 401

    @app.before_request
    def before_request():
        g.request_id = request.headers.get('X-Request-ID', str(uuid.uuid4()))

    @app.after_request
    def after_request(response):
        response.headers['X-Request-ID'] = g.get('request_id', '')
        return response

    # Global standardized error handler
    @app.errorhandler(Exception)
    def handle_exception(e):
        from werkzeug.exceptions import HTTPException
        import traceback
        import logging
        
        request_id = g.get('request_id', '')
        timestamp = datetime.datetime.utcnow().isoformat()
        
        if isinstance(e, HTTPException):
            return jsonify({
                "status": "error",
                "code": e.name.upper().replace(" ", "_"),
                "message": e.description,
                "request_id": request_id,
                "timestamp": timestamp
            }), e.code
            
        logging.error(f"[{request_id}] Unhandled Exception: {str(e)}\n{traceback.format_exc()}")
        return jsonify({
            "status": "error",
            "code": "INTERNAL_SERVER_ERROR",
            "message": "Unexpected server error.",
            "request_id": request_id,
            "timestamp": timestamp
        }), 500

    return app
