import redis
from app.core.config import settings
from app.utils.logger import rag_logger

class RedisService:
    def __init__(self):
        self.redis_client = None
        self.memory_blocklist = set()
        self._init_redis()
        
    def _init_redis(self):
        try:
            url = getattr(settings, 'REDIS_URL', 'redis://localhost:6379/0')
            self.redis_client = redis.from_url(url, decode_responses=True, socket_connect_timeout=1)
            self.redis_client.ping()
            rag_logger.info("Successfully connected to Redis.")
        except Exception as e:
            rag_logger.warning(f"Failed to connect to Redis, using in-memory blocklist fallback: {e}")
            self.redis_client = None

    def init_app(self, app):
        self._init_redis()

    def add_token_to_blocklist(self, jti, expires_in=3600):
        """
        Add a JWT to the blocklist in Redis or in-memory fallback.
        """
        self.memory_blocklist.add(jti)
        if self.redis_client:
            try:
                self.redis_client.setex(f"jwt:blocklist:{jti}", expires_in, "true")
            except Exception as e:
                rag_logger.error(f"Redis blocklist add failed: {e}")

    def is_token_blocklisted(self, jti):
        """
        Check if a JWT is in the blocklist.
        """
        if jti in self.memory_blocklist:
            return True
        if self.redis_client:
            try:
                result = self.redis_client.get(f"jwt:blocklist:{jti}")
                return result == "true"
            except Exception as e:
                rag_logger.error(f"Redis blocklist check failed: {e}")
        return False

redis_service = RedisService()
