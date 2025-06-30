from django.urls import path, re_path
from teamapp.consumers import HitAndBlowConsumer, OthelloConsumer, SugorokuGameConsumer
from . import consumers

websocket_urlpatterns = [
    path('ws/hit_and_blow_game/', HitAndBlowConsumer.as_asgi()),
    re_path(r"ws/othello_index/(?P<room_name>\w+)/$", OthelloConsumer.as_asgi()),
    re_path(r'ws/sugoroku/(?P<room_name>\w+)/$', consumers.SugorokuGameConsumer.as_asgi())
]

