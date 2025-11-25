from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """애플리케이션 전체 설정"""

    # Database URL (필수)
    DATABASE_URL: str

    # Redis URL (필수)
    REDIS_URL: str

    # Google OAuth (필수)
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str

    # OpenAI Settings (필수)
    OPENAI_API_KEY: str

    class Config:
        env_file = ".env"
        case_sensitive = True

    @property
    def database_url(self) -> str:
        """SQLAlchemy용 URL 반환 (mysql:// -> mysql+pymysql://)"""
        if self.DATABASE_URL.startswith("mysql://"):
            return self.DATABASE_URL.replace("mysql://", "mysql+pymysql://", 1)
        return self.DATABASE_URL


@lru_cache()
def get_settings() -> Settings:
    """설정 싱글톤 반환 (캐싱)"""
    return Settings()