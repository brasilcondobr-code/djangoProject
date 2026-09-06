from domains.system.models import (
    TechnicalSupportTicket, SystemLog, AutomatedRoutine, Training, 
    IntegrationToken, ConnectedUser
)
from datetime import timedelta

from django.conf import settings
from django.contrib.sessions.models import Session
from django.db.models import Exists, OuterRef, Q
from django.utils import timezone

class SystemSelector:
    @staticmethod
    def get_all_technical_support_tickets():
        return TechnicalSupportTicket.objects.all()

    @staticmethod
    def get_all_system_logs():
        return SystemLog.objects.all()

    @staticmethod
    def get_all_automated_routines():
        return AutomatedRoutine.objects.all()

    @staticmethod
    def get_all_trainings():
        return Training.objects.all()

    @staticmethod
    def get_all_integration_tokens():
        return IntegrationToken.objects.all()

    @staticmethod
    def get_all_connected_users(
        search="",
        group_id=None,
        is_staff=None,
        page_number=None,
        page_size=None,
    ):
        timeout = getattr(settings, "CONNECTED_USER_TIMEOUT", 300)
        active_since = timezone.now() - timedelta(seconds=timeout)
        valid_session = Session.objects.filter(
            session_key=OuterRef("session_key"),
            expire_date__gt=timezone.now(),
        )
        queryset = (
            ConnectedUser.objects.filter(
                is_connected=True,
                last_activity__gte=active_since,
                user__is_active=True,
            )
            .annotate(session_is_valid=Exists(valid_session))
            .filter(session_is_valid=True)
            .select_related("user")
            .prefetch_related("user__groups")
            .order_by("-last_activity")
        )

        if search:
            queryset = queryset.filter(
                Q(user__username__icontains=search)
                | Q(user__email__icontains=search)
            )
        if group_id:
            queryset = queryset.filter(user__groups__id=group_id)
        if is_staff in ("true", "false"):
            queryset = queryset.filter(user__is_staff=is_staff == "true")
        if page_number and page_size:
            start = (page_number - 1) * page_size
            queryset = queryset[start:start + page_size]
        return queryset
