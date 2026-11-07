from datetime import date
from decimal import Decimal

import pytest

from domains.financial.exceptions import (
    NewReleaseTransitionError,
    NewReleaseValidationError,
)
from domains.financial.models import NewRelease
from domains.financial.services import NewReleaseService


@pytest.mark.django_db
class TestNewReleaseServiceValidation:

    def test_normalize_scope(self):
        assert NewReleaseService.normalize_scope(date(2026, 1, 31)) == date(
            2026, 1, 1
        )
        assert NewReleaseService.normalize_scope(None) is None
        assert NewReleaseService.normalize_scope("") is None

    @pytest.mark.parametrize(
        "raw, expected",
        [
            ("1.234,56", Decimal("1234.56")),
            ("1234,56", Decimal("1234.56")),
            ("1234.56", Decimal("1234.56")),
            (" 10 ", Decimal("10")),
            (Decimal("99.90"), Decimal("99.90")),
        ],
    )
    def test_parse_value_valid(self, raw, expected):
        assert NewReleaseService.parse_value(raw) == expected

    @pytest.mark.parametrize(
        "raw",
        [None, "", "   ", Decimal("0")],
    )
    def test_parse_value_empty_or_zero(self, raw):
        if raw in (None, "", "   "):
            assert NewReleaseService.parse_value(raw) is None
        else:
            with pytest.raises(NewReleaseValidationError):
                NewReleaseService.parse_value(raw)

    @pytest.mark.parametrize("raw", ["abc", "1,234", "1.2.3", "10,999"])
    def test_parse_value_invalid_format(self, raw):
        with pytest.raises(NewReleaseValidationError):
            NewReleaseService.parse_value(raw)

    def test_parse_value_rejects_negative(self):
        with pytest.raises(NewReleaseValidationError):
            NewReleaseService.parse_value("-10,00")

    def test_parse_value_rejects_above_field_precision(self):
        with pytest.raises(NewReleaseValidationError):
            NewReleaseService.parse_value("1.000.000.000.000,00")

    def test_apply_sign_debit_is_negative(self):
        assert NewReleaseService.apply_sign(
            Decimal("10"), NewRelease.LaunchType.DEBITO
        ) == Decimal("-10")

    def test_apply_sign_credit_is_positive(self):
        assert NewReleaseService.apply_sign(
            Decimal("10"), NewRelease.LaunchType.CREDITO
        ) == Decimal("10")

    def test_apply_sign_zero_is_rejected(self):
        with pytest.raises(NewReleaseValidationError):
            NewReleaseService.apply_sign(
                Decimal("0"), NewRelease.LaunchType.DEBITO
            )

    def test_apply_sign_invalid_type_is_rejected(self):
        with pytest.raises(NewReleaseValidationError):
            NewReleaseService.apply_sign(Decimal("10"), "X")


@pytest.mark.django_db
class TestNewReleaseServiceSave:

    def _build_release(
        self,
        unit,
        resident,
        chart_account,
        fund,
        title="Novo Lançamento",
        scope=date(2026, 6, 15),
        launch_date=date(2026, 6, 20),
        launch_type=NewRelease.LaunchType.DEBITO,
        value=Decimal("150.00"),
    ):
        return NewRelease(
            condominium=unit,
            paymaster=resident,
            title=title,
            scope=scope,
            launchDate=launch_date,
            chartOfAccounts=chart_account,
            fund=fund,
            launchType=launch_type,
            value=value,
        )

    def test_create_sets_server_side_fields(
        self,
        _unit,
        _resident,
        _chart_account,
        _fund,
        _user,
    ):
        release = self._build_release(
            _unit, _resident, _chart_account, _fund, title="  Taxa  "
        )

        saved = NewReleaseService.save_instance(
            release, user=_user, is_new=True
        )

        assert saved.pk is not None
        assert saved.title == "Taxa"
        assert saved.scope == date(2026, 6, 1)
        assert saved.value == Decimal("-150.00")
        assert saved.status == NewRelease.Status.LANCAMENTO
        assert saved.created_by == _user
        assert saved.updated_by == _user

    def test_create_credit_is_positive(
        self,
        _unit,
        _resident,
        _chart_account,
        _fund,
        _user,
    ):
        release = self._build_release(
            _unit,
            _resident,
            _chart_account,
            _fund,
            launch_type=NewRelease.LaunchType.CREDITO,
            value=Decimal("250.00"),
        )

        saved = NewReleaseService.save_instance(
            release, user=_user, is_new=True
        )

        assert saved.value == Decimal("250.00")

    def test_create_without_value(
        self,
        _unit,
        _resident,
        _chart_account,
        _fund,
        _user,
    ):
        release = self._build_release(
            _unit,
            _resident,
            _chart_account,
            _fund,
            value=None,
        )

        saved = NewReleaseService.save_instance(
            release, user=_user, is_new=True
        )

        assert saved.value is None

    def test_create_rejects_paymaster_of_another_unit(
        self,
        _unit,
        _resident_two,
        _chart_account,
        _fund,
        _user,
    ):
        release = self._build_release(
            _unit, _resident_two, _chart_account, _fund
        )

        with pytest.raises(NewReleaseValidationError):
            NewReleaseService.save_instance(
                release, user=_user, is_new=True
            )

    def test_create_rejects_chart_of_account_of_another_condominium(
        self,
        _unit,
        _resident,
        _chart_account_other,
        _fund,
        _user,
    ):
        release = self._build_release(
            _unit, _resident, _chart_account_other, _fund
        )

        with pytest.raises(NewReleaseValidationError):
            NewReleaseService.save_instance(
                release, user=_user, is_new=True
            )

    def test_create_rejects_fund_of_another_condominium(
        self,
        _unit,
        _resident,
        _chart_account,
        _fund_other,
        _user,
    ):
        release = self._build_release(
            _unit, _resident, _chart_account, _fund_other
        )

        with pytest.raises(NewReleaseValidationError):
            NewReleaseService.save_instance(
                release, user=_user, is_new=True
            )

    def test_create_rejects_duplicate(
        self, _new_release, _unit, _resident, _chart_account, _fund, _user
    ):
        release = self._build_release(
            _unit,
            _resident,
            _chart_account,
            _fund,
            title=_new_release.title,
            scope=date(2026, 1, 1),
            launch_date=_new_release.launchDate,
        )

        with pytest.raises(NewReleaseValidationError):
            NewReleaseService.save_instance(
                release, user=_user, is_new=True
            )

    def test_create_rejects_zero_value(
        self,
        _unit,
        _resident,
        _chart_account,
        _fund,
        _user,
    ):
        release = self._build_release(
            _unit,
            _resident,
            _chart_account,
            _fund,
            value=Decimal("0"),
        )

        with pytest.raises(NewReleaseValidationError):
            NewReleaseService.save_instance(
                release, user=_user, is_new=True
            )

    def test_update_keeps_created_by_and_updates_updated_by(
        self, _new_release, _user, _staff_user
    ):
        original_created_by = _new_release.created_by_id
        original_updated_at = _new_release.updated_at

        instance = NewRelease.objects.get(pk=_new_release.pk)
        instance.title = "Taxa Atualizada"
        instance.value = Decimal("175.00")

        saved = NewReleaseService.save_instance(
            instance, user=_staff_user, is_new=False
        )

        assert saved.created_by_id == original_created_by
        assert saved.updated_by_id == _staff_user.pk
        assert saved.value == Decimal("-175.00")
        assert saved.updated_at >= original_updated_at
        assert saved.status == NewRelease.Status.LANCAMENTO

    def test_update_is_blocked_for_billing(
        self, _billing_release, _user
    ):
        instance = NewRelease.objects.get(pk=_billing_release.pk)
        instance.title = "Tentativa de alteração"

        with pytest.raises(NewReleaseTransitionError):
            NewReleaseService.save_instance(
                instance, user=_user, is_new=False
            )

        instance.refresh_from_db()
        assert instance.title == "Lançamento Cobrado"

    def test_update_missing_record(self, _user):
        instance = NewRelease(pk=999999)

        with pytest.raises(NewReleaseValidationError):
            NewReleaseService.save_instance(
                instance, user=_user, is_new=False
            )


@pytest.mark.django_db
class TestNewReleaseServiceDelete:

    def test_delete_only_lancamento(self, _new_release, _user):
        new_release_id = _new_release.pk

        NewReleaseService.delete_instance(_new_release, user=_user)

        assert not NewRelease.objects.filter(pk=new_release_id).exists()

    def test_delete_is_blocked_for_billing(
        self, _billing_release, _user
    ):
        with pytest.raises(NewReleaseTransitionError):
            NewReleaseService.delete_instance(
                _billing_release, user=_user
            )

        assert NewRelease.objects.filter(pk=_billing_release.pk).exists()

    def test_delete_missing_record(self, _user):
        with pytest.raises(NewReleaseValidationError):
            NewReleaseService.delete_instance(
                NewRelease(pk=999999), user=_user
            )


@pytest.mark.django_db
class TestNewReleaseGenerateBilling:

    def test_generate_billing_updates_status_and_audit(
        self, _new_release, _staff_user
    ):
        created_by = _new_release.created_by_id

        results = NewReleaseService.generate_billing(
            [_new_release.pk], user=_staff_user
        )

        assert results == [
            {"id": _new_release.pk, "success": True, "reason": ""}
        ]
        _new_release.refresh_from_db()
        assert _new_release.status == NewRelease.Status.COBRANCA
        assert _new_release.updated_by_id == _staff_user.pk
        assert _new_release.created_by_id == created_by

    def test_generate_billing_rejects_billing_record(
        self, _billing_release, _user
    ):
        results = NewReleaseService.generate_billing(
            [_billing_release.pk], user=_user
        )

        assert results[0]["success"] is False
        assert "Cobrança" in results[0]["reason"]

    def test_generate_billing_rejects_missing_record(self, _user):
        results = NewReleaseService.generate_billing(
            [999999], user=_user
        )

        assert results == [
            {
                "id": 999999,
                "success": False,
                "reason": "Lançamento não encontrado.",
            }
        ]

    def test_generate_billing_partial_success(
        self, _new_release, _billing_release, _user
    ):
        results = NewReleaseService.generate_billing(
            [_new_release.pk, _billing_release.pk, 999999],
            user=_user,
        )

        assert [result["success"] for result in results] == [
            True,
            False,
            False,
        ]
        _new_release.refresh_from_db()
        _billing_release.refresh_from_db()
        assert _new_release.status == NewRelease.Status.COBRANCA
        assert _billing_release.status == NewRelease.Status.COBRANCA


@pytest.mark.django_db
class TestNewReleaseDeleteMany:

    def test_delete_many_partial_success(
        self, _new_release, _billing_release, _user
    ):
        results = NewReleaseService.delete_many(
            [_new_release.pk, _billing_release.pk, 999999],
            user=_user,
        )

        assert [result["success"] for result in results] == [
            True,
            False,
            False,
        ]
        assert not NewRelease.objects.filter(pk=_new_release.pk).exists()
        assert NewRelease.objects.filter(pk=_billing_release.pk).exists()
