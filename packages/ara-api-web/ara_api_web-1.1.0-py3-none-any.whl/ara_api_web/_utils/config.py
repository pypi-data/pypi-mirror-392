from pathlib import Path

# =====================================================================
# LOGGER CONFIGURATION
# =====================================================================


class LOGGER_CONFIG:
    LOG_LEVEL: str = "DEBUG"  # Уровень логирования
    LOG_TO_FILE: bool = False  # Логировать ли в файл
    LOG_TO_TERMINAL: bool = True  # Логировать ли в терминал
    LOG_DIR: str = "logs"  # Директория для логов


# =====================================================================
# REST CONFIGURATION
# =====================================================================


class REST_CONFIG:
    HOST: str = "0.0.0.0"
    PORT: int = 8080


# =====================================================================
# gRPC CONFIGURATION
# =====================================================================


class MSPConfigGRPC:
    HOST: str = "localhost"
    PORT: str = "50051"


class NavigationConfigGRPC:
    HOST: str = "localhost"
    PORT: str = "50052"


class VisionConfigGRPC:
    HOST: str = "localhost"
    PORT: str = "50053"


# =====================================================================
# PATHS CONFIGURATION
# =====================================================================


BASE_DIR: Path = Path(__file__).parent.parent
STATIC_DIR: Path = BASE_DIR / "_utils" / "static"
