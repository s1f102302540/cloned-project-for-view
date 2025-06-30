from . import consumers
from channels.auth import AuthMiddlewareStack
from django.urls import path, re_path


websocket_urlpatterns = [

    re_path(r'ws/cardgame/(?P<session_id>\w+)/(?P<deck_id>\w+)/$', consumers.CardGameConsumer.as_asgi()),
]