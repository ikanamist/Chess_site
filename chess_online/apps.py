from django.apps import AppConfig


class ChessOnlineConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "chess_online"

    def ready(self):
        import chess_online.signals  # Импортируем сигналы
