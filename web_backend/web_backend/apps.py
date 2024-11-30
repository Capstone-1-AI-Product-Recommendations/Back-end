from django.apps import AppConfig

class WebBackendConfig(AppConfig):
    name = 'web_backend'

    def ready(self):
        import web_backend.signals  # Kết nối signals ở đây
