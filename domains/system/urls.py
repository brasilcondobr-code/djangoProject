from django.urls import path

from domains.system.views import (
    connected_users_data,
    connected_users_heartbeat,
    connected_users_list,
)

app_name = "system"

urlpatterns = [
    path("connected-users/", connected_users_list, name="connected_users"),
    path("connected-users/data/", connected_users_data, name="connected_users_data"),
    path(
        "connected-users/heartbeat/",
        connected_users_heartbeat,
        name="connected_users_heartbeat",
    ),
]