from domains.system.repositories import SystemRepository
from domains.system.selectors import SystemSelector
from django.conf import settings
from django.db import transaction
from django.utils import timezone
import hashlib
import logging
from datetime import timedelta

from domains.system.models import ConnectedUser

logger = logging.getLogger(__name__)

class SystemService:
    @staticmethod
    def get_all_technical_support_tickets():
        return SystemSelector.get_all_technical_support_tickets()

    @staticmethod
    def get_all_system_logs():
        return SystemSelector.get_all_system_logs()

    @staticmethod
    def get_all_automated_routines():
        return SystemSelector.get_all_automated_routines()

    @staticmethod
    def get_all_trainings():
        return SystemSelector.get_all_trainings()

    @staticmethod
    def get_all_integration_tokens():
        return SystemSelector.get_all_integration_tokens()

    @staticmethod
    def register_connection(user, session_key, ip_address=None, user_agent=""):
        now = timezone.now()
        with transaction.atomic():
            connection, created = ConnectedUser.objects.get_or_create(
                session_key=session_key,
                defaults={
                    "user": user,
                    "last_activity": now,
                    "ip_address": ip_address,
                    "user_agent": user_agent[:512],
                },
            )
            if not created:
                update_fields = []
                if connection.user_id != user.pk:
                    connection.user = user
                    update_fields.append("user")
                if not connection.is_connected:
                    connection.is_connected = True
                    connection.disconnected_at = None
                    update_fields.extend(("is_connected", "disconnected_at"))
                if update_fields:
                    connection.ip_address = ip_address
                    connection.user_agent = user_agent[:512]
                    update_fields.extend(("ip_address", "user_agent", "updated_at"))
                    connection.save(update_fields=update_fields)
        logger.info(
            "connected_user_registered",
            extra={"user_id": user.pk, "session_id_hash": _hash_session(session_key)},
        )
        return connection

    @staticmethod
    def update_activity(session_key):
        threshold = timezone.now() - timedelta(
            seconds=getattr(settings, "CONNECTED_USER_ACTIVITY_UPDATE_INTERVAL", 60)
        )
        updated = ConnectedUser.objects.filter(
            session_key=session_key,
            is_connected=True,
        ).filter(last_activity__lt=threshold).update(
            last_activity=timezone.now(),
            updated_at=timezone.now(),
        )
        if updated:
            logger.info(
                "connected_user_activity_updated",
                extra={"session_id_hash": _hash_session(session_key)},
            )
        return updated

    @staticmethod
    def mark_session_disconnected(session_key):
        return ConnectedUser.objects.filter(
            session_key=session_key,
            is_connected=True,
        ).update(
            is_connected=False,
            disconnected_at=timezone.now(),
            updated_at=timezone.now(),
        )

    @staticmethod
    def expire_inactive_sessions():
        threshold = timezone.now() - timedelta(
            seconds=getattr(settings, "CONNECTED_USER_TIMEOUT", 300)
        )
        expired = ConnectedUser.objects.filter(
            is_connected=True,
            last_activity__lt=threshold,
        ).update(
            is_connected=False,
            disconnected_at=timezone.now(),
            updated_at=timezone.now(),
        )
        if expired:
            logger.info("connected_user_session_expired", extra={"count": expired})
        return expired

    @staticmethod
    def cleanup_stale_sessions():
        expired = SystemService.expire_inactive_sessions()
        logger.info("connected_user_cleanup_executed", extra={"count": expired})
        return expired

    @staticmethod
    def get_all_connected_users(**filters):
        return SystemSelector.get_all_connected_users(**filters)

    @staticmethod
    def get_connected_users(**filters):
        return SystemService.get_all_connected_users(**filters)


def _hash_session(session_key):
    return hashlib.sha256(session_key.encode()).hexdigest()[:16]
