import logging

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_POST

from django.contrib.auth.models import Group

from domains.system.services import SystemService

logger = logging.getLogger(__name__)
PAGE_SIZE = 25


def _require_view_permission(request):
    if not request.user.is_staff or not request.user.has_perm("system.view_connecteduser"):
        raise PermissionDenied


def _filters(request):
    return {
        "search": request.GET.get("search", "").strip(),
        "group_id": request.GET.get("group", ""),
        "is_staff": request.GET.get("is_staff", ""),
    }


def _user_data(connection):
    return {
        "username": connection.user.get_username(),
        "email": connection.user.email,
        "groups": [group.name for group in connection.user.groups.all()],
        "is_active": connection.user.is_active,
        "is_staff": connection.user.is_staff,
        "last_login": connection.user.last_login.isoformat() if connection.user.last_login else None,
        "last_activity": connection.last_activity.isoformat(),
    }


@login_required
def connected_users_list(request):
    _require_view_permission(request)
    paginator = Paginator(
        SystemService.get_all_connected_users(**_filters(request)),
        PAGE_SIZE,
    )
    page_obj = paginator.get_page(request.GET.get("page", 1))
    return render(
        request,
        "system/connecteduser/list.html",
        {
            "page_obj": page_obj,
            "groups": Group.objects.order_by("name"),
            "poll_interval": getattr(settings, "CONNECTED_USER_POLL_INTERVAL", 30) * 1000,
            "data_url": reverse("system:connected_users_data"),
        },
    )


@login_required
@require_GET
def connected_users_data(request):
    _require_view_permission(request)
    try:
        paginator = Paginator(
            SystemService.get_all_connected_users(**_filters(request)),
            PAGE_SIZE,
        )
        page_obj = paginator.get_page(request.GET.get("page", 1))
        return JsonResponse({
            "results": [_user_data(item) for item in page_obj.object_list],
            "page": page_obj.number,
            "pages": paginator.num_pages,
            "count": paginator.count,
        })
    except Exception:
        logger.exception(
            "connected_user_query_failed",
            extra={"user_id": request.user.pk},
        )
        return JsonResponse(
            {"detail": "Não foi possível atualizar os usuários conectados."},
            status=500,
        )


@login_required
@require_POST
def connected_users_heartbeat(request):
    _require_view_permission(request)
    session_key = request.session.session_key
    if not session_key:
        return JsonResponse({"detail": "Sessão inválida."}, status=401)
    SystemService.update_activity(session_key)
    return JsonResponse({"ok": True})