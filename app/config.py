from dotenv import load_dotenv
import os

load_dotenv()


class Settings:

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://root:root@localhost:3306/db_ramais"
    )

    SECRET_KEY: str = os.getenv(
        "SECRET_KEY",
        "super-secret-key"
    )

    ALGORITHM: str = os.getenv(
        "ALGORITHM",
        "HS256"
    )

    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv(
            "ACCESS_TOKEN_EXPIRE_MINUTES",
            30
        )
    )

    REFRESH_TOKEN_EXPIRE_DAYS: int = int(
        os.getenv(
            "REFRESH_TOKEN_EXPIRE_DAYS",
            7
        )
    )

    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "https://jvrfurtado.github.io"
    ]


settings = Settings()