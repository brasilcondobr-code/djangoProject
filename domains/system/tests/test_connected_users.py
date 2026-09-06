from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import Client
from django.utils import timezone

from domains.system.admin import ConnectedUserAdmin
from domains.system.models import ConnectedUser
from domains.system.services import SystemService


User = get_user_model()


@pytest.fixture
def view_user(db):
    user = User.objects.create_user(
        username="viewer",
        password="password",
        is_staff=True,
    )
    permission = Permission.objects.get(
        codename="view_connecteduser",
        content_type__app_label="system",
    )
    user.user_permissions.add(permission)
    return user


def create_session_connection(user, last_activity=None):
    client = Client()
    client.force_login(user)
    session_key = client.cookies["sessionid"].value
    connection = SystemService.register_connection(user, session_key)
    if last_activity:
        ConnectedUser.objects.filter(pk=connection.pk).update(
            last_activity=last_activity,
        )
    return client


@pytest.mark.django_db
def test_connected_users_requires_permission(view_user):
    response = Client().get("/system/connected-users/data/")
    assert response.status_code in (301, 302)

    no_permission = User.objects.create_user(
        username="without-permission",
        password="password",
        is_staff=True,
    )
    client = Client()
    client.force_login(no_permission)
    assert client.get("/system/connected-users/data/").status_code == 403


@pytest.mark.django_db
def test_data_returns_only_active_recent_sessions(view_user, settings):
    settings.CONNECTED_USER_TIMEOUT = 300
    active_client = create_session_connection(view_user)
    inactive = User.objects.create_user(
        username="inactive",
        password="password",
        is_active=False,
    )
    create_session_connection(inactive)
    stale = User.objects.create_user(username="stale", password="password")
    create_session_connection(stale, timezone.now() - timedelta(minutes=10))

    response = active_client.get("/system/connected-users/data/")

    assert response.status_code == 200
    assert [item["username"] for item in response.json()["results"]] == ["viewer"]


@pytest.mark.django_db
def test_connected_user_admin_is_read_only():
    admin = ConnectedUserAdmin(ConnectedUser, None)
    request = object()

    assert admin.has_add_permission(request) is False
    assert admin.has_change_permission(request) is False
    assert admin.has_delete_permission(request) is False
    assert "session_key" in admin.readonly_fields
