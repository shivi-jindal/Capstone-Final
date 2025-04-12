from django.urls import path
from write_on_cue import consumers

websocket_urlpatterns = [
    path("ws/bpm/", consumers.BPMConsumer.as_asgi()),
]