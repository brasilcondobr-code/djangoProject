from datetime import date
from decimal import Decimal

import pytest
from django.db import IntegrityError, transaction
from django.db.models import ProtectedError

from domains.financial.models import NewRelease


@pytest.mark.django_db
class TestNewReleaseModel:

    def test_defaults(self, _new_release):
        assert _new_release.status == NewRelease.Status.LANCAMENTO
        assert _new_release.is_active is True
        assert _new_release.launchType == NewRelease.LaunchType.DEBITO

    def test_str_uses_title_and_scope(self, _new_release):
        assert str(_new_release) == "Taxa Condominial - 01/2026"

    def test_str_falls_back_without_scope(self):
        release = NewRelease(title="Sem competência")
        assert str(release) == "Sem competência"
        assert str(NewRelease()) == "07. Lançamento"

    def test_save_normalizes_scope_to_first_day(
        self, _unit, _resident, _chart_account, _fund
    ):
        release = NewRelease.objects.create(
            condominium=_unit,
            paymaster=_resident,
            title="Competência normalizada",
            scope=date(2026, 3, 18),
            launchDate=date(2026, 3, 20),
            chartOfAccounts=_chart_account,
            fund=_fund,
            launchType=NewRelease.LaunchType.CREDITO,
            value=Decimal("10.00"),
        )
        release.refresh_from_db()
        assert release.scope == date(2026, 3, 1)

    def test_unique_constraint_is_composite(
        self, _new_release
    ):
        duplicate = NewRelease(
            condominium=_new_release.condominium,
            paymaster=_new_release.paymaster,
            title=_new_release.title,
            scope=_new_release.scope,
            launchDate=_new_release.launchDate,
            chartOfAccounts=_new_release.chartOfAccounts,
            fund=_new_release.fund,
            launchType=NewRelease.LaunchType.DEBITO,
            value=Decimal("-10.00"),
        )
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                duplicate.save()

    def test_unique_constraint_allows_different_scope(
        self, _new_release
    ):
        other = NewRelease.objects.create(
            condominium=_new_release.condominium,
            paymaster=_new_release.paymaster,
            title=_new_release.title,
            scope=date(2026, 2, 1),
            launchDate=_new_release.launchDate,
            chartOfAccounts=_new_release.chartOfAccounts,
            fund=_new_release.fund,
            launchType=NewRelease.LaunchType.DEBITO,
            value=Decimal("-10.00"),
        )
        assert other.pk is not None

    def test_check_constraint_rejects_positive_debit(
        self, _unit, _resident, _chart_account, _fund
    ):
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                NewRelease.objects.create(
                    condominium=_unit,
                    paymaster=_resident,
                    title="Débito positivo",
                    scope=date(2026, 4, 1),
                    launchDate=date(2026, 4, 1),
                    chartOfAccounts=_chart_account,
                    fund=_fund,
                    launchType=NewRelease.LaunchType.DEBITO,
                    value=Decimal("10.00"),
                )

    def test_check_constraint_rejects_negative_credit(
        self, _unit, _resident, _chart_account, _fund
    ):
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                NewRelease.objects.create(
                    condominium=_unit,
                    paymaster=_resident,
                    title="Crédito negativo",
                    scope=date(2026, 4, 1),
                    launchDate=date(2026, 4, 1),
                    chartOfAccounts=_chart_account,
                    fund=_fund,
                    launchType=NewRelease.LaunchType.CREDITO,
                    value=Decimal("-10.00"),
                )

    def test_value_can_be_null(
        self, _unit, _resident, _chart_account, _fund
    ):
        release = NewRelease.objects.create(
            condominium=_unit,
            paymaster=_resident,
            title="Sem valor",
            scope=date(2026, 5, 1),
            launchDate=date(2026, 5, 1),
            chartOfAccounts=_chart_account,
            fund=_fund,
            launchType=NewRelease.LaunchType.DEBITO,
            value=None,
        )
        assert release.value is None

    def test_related_names(
        self, _new_release, _unit, _resident, _user
    ):
        assert _new_release in _unit.new_releases.all()
        assert _new_release in _resident.new_releases_as_paymaster.all()
        assert _new_release in _user.created_new_releases.all()
        assert _new_release in _user.updated_new_releases.all()

    def test_protect_prevents_unit_deletion(self, _new_release, _unit):
        with pytest.raises(ProtectedError):
            _unit.delete()

    def test_meta_ordering(self):
        assert NewRelease._meta.ordering == ["-launchDate", "-id"]

    def test_expected_fields(self):
        field_names = {field.name for field in NewRelease._meta.fields}
        assert {
            "condominium",
            "paymaster",
            "title",
            "scope",
            "launchDate",
            "chartOfAccounts",
            "fund",
            "launchType",
            "value",
            "notes",
            "is_active",
            "status",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        } <= field_names

    def test_status_is_not_editable(self):
        field = NewRelease._meta.get_field("status")
        assert field.editable is False
