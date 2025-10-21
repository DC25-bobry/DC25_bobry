from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # app config
    app_name: str
    debug: bool
    host: str
    port: int

    # frontend
    frontend_url: str
    frontend_api_key: str

    # backend
    backend_url: str
    backend_api_key: str

    # google drive configuration
    google_drive_client_id: str
    google_drive_dir_id: str
    google_token: str
    google_key: str

    # db configuration
    db_name: str
    db_user: str
    db_password: str
    db_host: str
    db_port: int

    # smtp configuration
    smtp_encryption: str
    smtp_port: int
    smtp_user: str
    smtp_password: str
    smtp_email: str
    smtp_host: str

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding = 'utf-8',
        case_sensitive = False
    )

