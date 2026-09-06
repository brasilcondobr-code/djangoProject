from django.contrib.auth.signals import user_logged_out
from django.dispatch import receiver

from domains.system.services import SystemService


@receiver(user_logged_out)
def mark_connected_user_logged_out(sender, request, user, **kwargs):
    if request and request.session.session_key:
        SystemService.mark_session_disconnected(request.session.session_key)