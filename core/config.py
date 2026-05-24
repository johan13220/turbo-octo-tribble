from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    seo_api_key: str = ""
    seo_api_base_url: str = "https://api.semrush.com"
    cache_dir: str = "~/.seo_dashboard/cache"
    cache_ttl_hours: int = 24
    default_language: str = "en"
    default_location_id: int = 2840
    max_keywords: int = 100
    report_output_dir: str = "./reports_output"
    gsc_credentials_path: str = ""
    gsc_token_path: str = "~/.seo_dashboard/gsc_token.json"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
