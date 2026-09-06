from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import Client, TestCase, override_settings
from django.utils import timezone

from domains.system.admin import ConnectedUserAdmin
from domains.system.models import ConnectedUser
from domains.system.services import SystemService


class ConnectedUsersTests(TestCase):
    @override_settings(ALLOWED_HOSTS=["testserver"])
    def setUp(self):
        self.user = self.create_user("viewer", is_staff=True)
        permission = Permission.objects.get(
            codename="view_connecteduser",
            content_type__app_label="system",
        )
        self.user.user_permissions.add(permission)

    def create_user(self, username, is_staff=False, is_active=True):
        return get_user_model().objects.create_user(
            username=username,
            password="password",
            is_staff=is_staff,
            is_active=is_active,
        )

    def create_connection(self, user, last_activity=None):
        client = Client()
        client.force_login(user)
        session_key = client.cookies["sessionid"].value
        connection = SystemService.register_connection(user, session_key)
        if last_activity:
            ConnectedUser.objects.filter(pk=connection.pk).update(
                last_activity=last_activity,
            )
        return client

    @override_settings(ALLOWED_HOSTS=["testserver"])
    def test_data_returns_only_active_recent_sessions(self):
        client = self.create_connection(self.user)
        inactive = self.create_user("inactive")
        inactive.is_active = False
        inactive.save(update_fields=["is_active"])
        self.create_connection(inactive)
        stale = self.create_user("stale")
        self.create_connection(stale, timezone.now() - timedelta(minutes=10))

        response = client.get("/system/connected-users/data/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [item["username"] for item in response.json()["results"]],
            ["viewer"],
        )

    @override_settings(ALLOWED_HOSTS=["testserver"])
    def test_endpoint_requires_permission(self):
        user = self.create_user("without-permission", is_staff=True)
        client = Client()
        client.force_login(user)

        self.assertEqual(
            client.get("/system/connected-users/data/").status_code,
            403,
        )

    def test_admin_is_read_only(self):
        admin = ConnectedUserAdmin(ConnectedUser, None)
        request = object()

        self.assertFalse(admin.has_add_permission(request))
        self.assertFalse(admin.has_change_permission(request))
        self.assertFalse(admin.has_delete_permission(request))
        self.assertIn("session_key", admin.exclude)
