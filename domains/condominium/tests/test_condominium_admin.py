"""Testes da remoção da action "Exportar para CSV" nos módulos do condomínio."""

import pytest
from django.contrib import admin

from domains.condominium.admin import (
    CollaboratorsAdmin,
    CondominiumAdmin,
    TypesCollaboratorsAdmin,
)
from domains.condominium.models import Collaborator, Condominium, TypesCollaborator
from shared.admin import BaseModelAdmin

ADMIN_CLASSES = (CondominiumAdmin, TypesCollaboratorsAdmin, CollaboratorsAdmin)


class TestCsvExportActionRemoved:

    def test_admins_do_not_declare_export_action(self):
        for admin_cls in ADMIN_CLASSES:
            actions = admin_cls.actions or []
            assert "export_as_csv" not in actions

    def test_admins_do_not_expose_export_method(self):
        for admin_cls in ADMIN_CLASSES:
            assert not hasattr(admin_cls, "export_as_csv")

    def test_shared_admin_has_no_csv_mixin_or_action(self):
        import shared.admin as shared_admin

        assert not hasattr(shared_admin, "ExportCsvMixin")
        assert not hasattr(BaseModelAdmin, "export_as_csv")
        assert "export_as_csv" not in (BaseModelAdmin.actions or [])

    @pytest.mark.django_db
    def test_get_actions_has_no_csv_export(self, django_user_model, rf):
        superuser = django_user_model.objects.create_superuser(
            username="admin-csv-test", email="admin-csv@test.local", password="x"
        )
        request = rf.get("/admin/condominium/condominium/")
        request.user = superuser

        alvo = (
            (Condominium, CondominiumAdmin),
            (TypesCollaborator, TypesCollaboratorsAdmin),
            (Collaborator, CollaboratorsAdmin),
        )
        for model, admin_cls in alvo:
            model_admin = admin_cls(model, admin.site)
            actions = model_admin.get_actions(request)
            assert "export_as_csv" not in actions

    def test_admins_remain_registered(self):
        for model, admin_cls in (
            (Condominium, CondominiumAdmin),
            (TypesCollaborator, TypesCollaboratorsAdmin),
            (Collaborator, CollaboratorsAdmin),
        ):
            assert isinstance(admin.site._registry[model], admin_cls)
