"""
ASGI config for config project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application
#from channels.routing import ProtocolTypeRouter, URLRouter
import teamapp.routing
import cardgame.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# WebSocket用のルートを統合
websocket_urlpatterns = teamapp.routing.websocket_urlpatterns + cardgame.routing.websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AllowedHostsOriginValidator(  
        AuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)  
        )
    ),
})