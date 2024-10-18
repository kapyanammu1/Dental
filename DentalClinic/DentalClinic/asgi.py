import os
from django.urls import path
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
# from DentalClinic.routing import websocket_urlpatterns  # Import your routing module where WebSocket routes are defined
from .consumers import NotificationConsumer  # Adjust to your app name
from DentalClinic import routing
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DentalClinic.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            routing.websocket_urlpatterns  # Your WebSocket URL patterns
        )
    ),
})
