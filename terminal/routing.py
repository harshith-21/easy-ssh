from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/terminal/(?P<host_id>\d+)/(?P<credential_id>\d+)/(?P<session_num>\d+)/$', consumers.TerminalConsumer.as_asgi()),
]

