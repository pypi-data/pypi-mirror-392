class LOGGER_CONFIG:
    LOG_LEVEL: str = "INFO"  # Уровень логирования
    LOG_TO_FILE: bool = False  # Логировать ли в файл
    LOG_TO_TERMINAL: bool = True  # Логировать ли в терминал
    LOG_DIR: str = "logs"  # Директория для логов


class MSPConfigGRPC:
    HOST: str = "localhost"  # Адрес gRPC сервера
    PORT: str = "50051"  # Порт gRPC сервера


class NavigationConfigGRPC:
    HOST: str = "localhost"  # Адрес gRPC сервера навигации
    PORT: str = "50052"  # Порт gRPC сервера навигации


class VisionConfigGRPC:
    HOST: str = "localhost"  # Адрес gRPC сервера визуализации
    PORT: str = "50053"  # Порт gRPC сервера визуализации
