import logging

from domains.system.services import SystemService

logger = logging.getLogger(__name__)


class ConnectedUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and request.session.session_key:
            try:
                SystemService.register_connection(
                    request.user,
                    request.session.session_key,
                    request.META.get("REMOTE_ADDR"),
                    request.META.get("HTTP_USER_AGENT", ""),
                )
                SystemService.update_activity(request.session.session_key)
            except Exception:
                logger.exception("connected_user_activity_failed")
        return self.get_response(request)