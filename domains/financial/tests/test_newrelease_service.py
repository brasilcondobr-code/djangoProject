from datetime import date
from decimal import Decimal

import pytest
from django.utils import timezone

from domains.financial.exceptions import (
    NewReleaseTransitionError,
    NewReleaseValidationError,
)
from domains.financial.models import Collection, NewRelease
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

    def test_parse_value_accepts_sign_and_returns_magnitude(self):
        assert NewReleaseService.parse_value("-10,00") == Decimal("10.00")

    def test_parse_value_rejects_above_field_precision(self):
        with pytest.raises(NewReleaseValidationError):
            NewReleaseService.parse_value("1.000.000.000.000,00")

    def test_apply_sign_debit_is_positive(self):
        assert NewReleaseService.apply_sign(
            Decimal("10"), NewRelease.LaunchType.DEBITO
        ) == Decimal("10")

    def test_apply_sign_credit_is_negative(self):
        assert NewReleaseService.apply_sign(
            Decimal("10"), NewRelease.LaunchType.CREDITO
        ) == Decimal("-10")

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
        assert saved.value == Decimal("150.00")
        assert saved.status == NewRelease.Status.LANCAMENTO
        assert saved.created_by == _user
        assert saved.updated_by == _user

    def test_create_credit_is_negative(
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

        assert saved.value == Decimal("-250.00")

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
        assert saved.value == Decimal("175.00")
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


def _make_release(
    unit,
    resident,
    chart,
    fund,
    user,
    *,
    title,
    value,
    scope=None,
    launch_date=None,
    status=NewRelease.Status.LANCAMENTO,
):
    today = timezone.localdate()
    launch_type = (
        NewRelease.LaunchType.DEBITO
        if value is not None and value >= 0
        else NewRelease.LaunchType.CREDITO
    )
    return NewRelease.objects.create(
        condominium=unit,
        paymaster=resident,
        title=title,
        scope=scope or today.replace(day=1),
        launchDate=launch_date or today,
        chartOfAccounts=chart,
        fund=fund,
        launchType=launch_type,
        value=value,
        status=status,
        created_by=user,
        updated_by=user,
    )


@pytest.mark.django_db
class TestNewReleaseGenerateBilling:

    def test_creates_collection_and_links_release(
        self, _current_release, _staff_user
    ):
        created_by = _current_release.created_by_id

        results = NewReleaseService.generate_billing(
            [_current_release.pk], user=_staff_user
        )

        assert results == [
            {"id": _current_release.pk, "success": True, "reason": ""}
        ]
        _current_release.refresh_from_db()
        assert _current_release.status == NewRelease.Status.COBRANCA
        assert _current_release.updated_by_id == _staff_user.pk
        assert _current_release.created_by_id == created_by
        assert _current_release.collection_id is not None

        collection = _current_release.collection
        assert collection.condominium_id == _current_release.condominium_id
        assert collection.scope == timezone.localdate().replace(day=1)
        assert collection.billingDate == timezone.localdate()
        assert collection.originalValue == Decimal("150.00")
        assert collection.totalAmount == Decimal("150.00")
        assert collection.balance == Decimal("150.00")
        assert collection.dueDate == _current_release.launchDate
        assert (
            collection.discountDeadline == _current_release.launchDate
        )
        assert collection.status == Collection.Status.TO_BE_WON
        assert collection.created_by_id == _staff_user.pk
        assert collection.updated_by_id == _staff_user.pk
        assert list(
            collection.new_releases.values_list("pk", flat=True)
        ) == [_current_release.pk]

    def test_acceptance_example_groups_and_sums(
        self,
        _unit,
        _resident,
        _chart_account,
        _fund,
        _user,
    ):
        releases = [
            _make_release(
                _unit,
                _resident,
                _chart_account,
                _fund,
                _user,
                title=f"Taxa {index}",
                value=value,
            )
            for index, value in enumerate(
                (
                    Decimal("347.11"),
                    Decimal("250.00"),
                    Decimal("347.11"),
                ),
                start=1,
            )
        ]

        results = NewReleaseService.generate_billing(
            [release.pk for release in releases],
            user=_user,
        )

        assert all(result["success"] for result in results)
        collection = Collection.objects.get()
        assert collection.originalValue == Decimal("944.22")
        assert collection.totalAmount == Decimal("944.22")
        assert collection.balance == Decimal("944.22")
        assert set(
            collection.new_releases.values_list("pk", flat=True)
        ) == {release.pk for release in releases}
        for release in releases:
            release.refresh_from_db()
            assert release.status == NewRelease.Status.COBRANCA
            assert release.collection_id == collection.pk

    def test_groups_by_unit(
        self,
        _unit,
        _unit_two,
        _resident,
        _resident_two,
        _chart_account,
        _fund,
        _user,
    ):
        first = _make_release(
            _unit,
            _resident,
            _chart_account,
            _fund,
            _user,
            title="Taxa unidade 1",
            value=Decimal("100.00"),
        )
        second = _make_release(
            _unit_two,
            _resident_two,
            _chart_account,
            _fund,
            _user,
            title="Taxa unidade 2",
            value=Decimal("200.00"),
        )

        results = NewReleaseService.generate_billing(
            [first.pk, second.pk],
            user=_user,
        )

        assert all(result["success"] for result in results)
        assert Collection.objects.count() == 2
        first.refresh_from_db()
        second.refresh_from_db()
        assert first.collection_id != second.collection_id
        assert first.collection.originalValue == Decimal("100.00")
        assert second.collection.originalValue == Decimal("200.00")

    def test_credit_nets_debit_in_same_group(
        self,
        _unit,
        _resident,
        _chart_account,
        _fund,
        _user,
    ):
        debit = _make_release(
            _unit,
            _resident,
            _chart_account,
            _fund,
            _user,
            title="Débito",
            value=Decimal("300.00"),
        )
        credit = _make_release(
            _unit,
            _resident,
            _chart_account,
            _fund,
            _user,
            title="Crédito",
            value=Decimal("-100.00"),
        )

        results = NewReleaseService.generate_billing(
            [debit.pk, credit.pk],
            user=_user,
        )

        assert all(result["success"] for result in results)
        collection = Collection.objects.get()
        assert collection.originalValue == Decimal("200.00")
        assert set(
            collection.new_releases.values_list("pk", flat=True)
        ) == {debit.pk, credit.pk}

    def test_net_zero_group_is_rejected(
        self,
        _unit,
        _resident,
        _chart_account,
        _fund,
        _user,
    ):
        debit = _make_release(
            _unit,
            _resident,
            _chart_account,
            _fund,
            _user,
            title="Débito",
            value=Decimal("100.00"),
        )
        credit = _make_release(
            _unit,
            _resident,
            _chart_account,
            _fund,
            _user,
            title="Crédito",
            value=Decimal("-100.00"),
        )

        results = NewReleaseService.generate_billing(
            [debit.pk, credit.pk],
            user=_user,
        )

        assert [result["success"] for result in results] == [False, False]
        assert "maior que zero" in results[0]["reason"]
        assert Collection.objects.count() == 0
        for release in (debit, credit):
            release.refresh_from_db()
            assert release.status == NewRelease.Status.LANCAMENTO
            assert release.collection_id is None

    def test_processes_only_selected_ids(
        self,
        _unit,
        _resident,
        _chart_account,
        _fund,
        _user,
    ):
        selected = _make_release(
            _unit,
            _resident,
            _chart_account,
            _fund,
            _user,
            title="Selecionado",
            value=Decimal("100.00"),
        )
        other = _make_release(
            _unit,
            _resident,
            _chart_account,
            _fund,
            _user,
            title="Não selecionado",
            value=Decimal("50.00"),
        )

        results = NewReleaseService.generate_billing(
            [selected.pk],
            user=_user,
        )

        assert results[0]["success"] is True
        selected.refresh_from_db()
        other.refresh_from_db()
        assert selected.status == NewRelease.Status.COBRANCA
        assert other.status == NewRelease.Status.LANCAMENTO
        assert other.collection_id is None
        assert selected.collection.new_releases.count() == 1

    def test_rejects_release_from_other_scope(
        self,
        _unit,
        _resident,
        _chart_account,
        _fund,
        _user,
    ):
        release = _make_release(
            _unit,
            _resident,
            _chart_account,
            _fund,
            _user,
            title="Competência antiga",
            value=Decimal("100.00"),
            scope=date(2000, 1, 1),
            launch_date=date(2000, 1, 10),
        )

        results = NewReleaseService.generate_billing(
            [release.pk], user=_user
        )

        assert results[0]["success"] is False
        assert "competência" in results[0]["reason"]
        assert Collection.objects.count() == 0
        release.refresh_from_db()
        assert release.status == NewRelease.Status.LANCAMENTO

    def test_rejects_release_without_value(
        self,
        _unit,
        _resident,
        _chart_account,
        _fund,
        _user,
    ):
        release = _make_release(
            _unit,
            _resident,
            _chart_account,
            _fund,
            _user,
            title="Sem valor",
            value=None,
        )

        results = NewReleaseService.generate_billing(
            [release.pk], user=_user
        )

        assert results[0]["success"] is False
        assert "não possui valor" in results[0]["reason"]
        assert Collection.objects.count() == 0

    def test_expired_collection_is_created_for_past_due_date(
        self,
        _unit,
        _resident,
        _chart_account,
        _fund,
        _user,
    ):
        release = _make_release(
            _unit,
            _resident,
            _chart_account,
            _fund,
            _user,
            title="Lançamento vencido",
            value=Decimal("100.00"),
            launch_date=date(2000, 1, 10),
        )

        results = NewReleaseService.generate_billing(
            [release.pk], user=_user
        )

        assert results[0]["success"] is True
        collection = Collection.objects.get()
        assert collection.status == Collection.Status.EXPIRED
        assert collection.dueDate == date(2000, 1, 10)

    def test_rejects_billing_record(
        self,
        _unit,
        _resident,
        _chart_account,
        _fund,
        _user,
    ):
        release = _make_release(
            _unit,
            _resident,
            _chart_account,
            _fund,
            _user,
            title="Já cobrado",
            value=Decimal("100.00"),
            status=NewRelease.Status.COBRANCA,
        )

        results = NewReleaseService.generate_billing(
            [release.pk], user=_user
        )

        assert results[0]["success"] is False
        assert "Cobrança" in results[0]["reason"]
        assert Collection.objects.count() == 0

    def test_rejects_release_already_linked(
        self, _current_release, _collection, _user
    ):
        _current_release.collection = _collection
        _current_release.save(
            update_fields=["collection", "updated_at"]
        )

        results = NewReleaseService.generate_billing(
            [_current_release.pk], user=_user
        )

        assert results[0]["success"] is False
        assert "já está vinculado" in results[0]["reason"]
        assert Collection.objects.count() == 1
        _current_release.refresh_from_db()
        assert _current_release.collection_id == _collection.pk

    def test_rejects_missing_record(self, _user):
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

    def test_partial_success(
        self,
        _current_release,
        _billing_release,
        _user,
    ):
        results = NewReleaseService.generate_billing(
            [_current_release.pk, _billing_release.pk, 999999],
            user=_user,
        )

        assert [result["success"] for result in results] == [
            True,
            False,
            False,
        ]
        _current_release.refresh_from_db()
        _billing_release.refresh_from_db()
        assert _current_release.status == NewRelease.Status.COBRANCA
        assert _current_release.collection_id is not None
        assert _billing_release.status == NewRelease.Status.COBRANCA
        assert _billing_release.collection_id is None
        assert Collection.objects.count() == 1

    def test_reexecution_does_not_duplicate(
        self, _current_release, _user
    ):
        first = NewReleaseService.generate_billing(
            [_current_release.pk], user=_user
        )
        second = NewReleaseService.generate_billing(
            [_current_release.pk], user=_user
        )

        assert first[0]["success"] is True
        assert second[0]["success"] is False
        assert Collection.objects.count() == 1
        _current_release.refresh_from_db()
        assert _current_release.collection.new_releases.count() == 1

    def test_group_failure_rolls_back_collection_and_status(
        self,
        _unit,
        _resident,
        _chart_account,
        _fund,
        _user,
    ):
        today = timezone.localdate()
        release = _make_release(
            _unit,
            _resident,
            _chart_account,
            _fund,
            _user,
            title="Conflito",
            value=Decimal("100.00"),
            launch_date=today,
        )
        Collection.objects.create(
            condominium=_unit,
            billingDate=today,
            scope=today.replace(day=1),
            dueDate=today,
            discountDeadline=today,
            originalValue=Decimal("10.00"),
            totalAmount=Decimal("10.00"),
            balance=Decimal("10.00"),
            status=Collection.Status.TO_BE_WON,
            created_by=_user,
            updated_by=_user,
        )

        results = NewReleaseService.generate_billing(
            [release.pk], user=_user
        )

        assert results[0]["success"] is False
        release.refresh_from_db()
        assert release.status == NewRelease.Status.LANCAMENTO
        assert release.collection_id is None
        assert Collection.objects.count() == 1


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
