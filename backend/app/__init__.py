from app.main import app

def create_app(config_class=None):
    return app

__all__ = ["app", "create_app"]
