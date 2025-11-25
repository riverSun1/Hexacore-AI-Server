import redis
from config.settings import get_settings

# Redis 인스턴스 생성 (Singleton)
_redis_instance = None


def get_redis() -> redis.Redis:
    """Redis 클라이언트 반환"""
    global _redis_instance
    if _redis_instance is None:
        settings = get_settings()
        _redis_instance = redis.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis_instance


def close_redis():
    """Redis 연결 종료"""
    global _redis_instance
    if _redis_instance is not None:
        _redis_instance.close()
        _redis_instance = None
