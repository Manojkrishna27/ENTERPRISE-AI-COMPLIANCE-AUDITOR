import redis
from app.config import Config
from app.utils.logger import rag_logger

class RedisService:
    def __init__(self):
        self.redis_client = None
        
    def init_app(self, app):
        try:
            # redis://redis:6379/0
            self.redis_client = redis.from_url(app.config['REDIS_URL'], decode_responses=True)
            self.redis_client.ping()
            rag_logger.info("Successfully connected to Redis.")
        except Exception as e:
            rag_logger.error(f"Failed to connect to Redis: {e}")
            self.redis_client = None

    def add_token_to_blocklist(self, jti, expires_in):
        """
        Add a JWT to the blocklist in Redis.
        Expires automatically when the token itself expires.
        """
        if self.redis_client:
            try:
                self.redis_client.setex(f"jwt:blocklist:{jti}", expires_in, "true")
            except Exception as e:
                rag_logger.error(f"Redis blocklist add failed: {e}")

    def is_token_blocklisted(self, jti):
        """
        Check if a JWT is in the blocklist.
        Returns False if Redis is down (fail-open) to not break prod if cache dies.
        """
        if self.redis_client:
            try:
                result = self.redis_client.get(f"jwt:blocklist:{jti}")
                return result == "true"
            except Exception as e:
                rag_logger.error(f"Redis blocklist check failed: {e}")
        return False

redis_service = RedisService()
