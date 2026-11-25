from datetime import date, timedelta
from decimal import Decimal

import pytest
from django.utils import timezone

from domains.financial.exceptions import (
    CollectionTransitionError,
    CollectionValidationError,
)
from domains.financial.models import Collection, NewRelease, Payment
from domains.financial.services import CollectionService


def _new_collection(unit, **overrides):
    data = {
        "condominium": unit,
        "scope": date(2026, 5, 1),
        "originalValue": Decimal("1000.00"),
        "discountPercent": Decimal("10.00"),
        "penaltyPercent": Decimal("2.00"),
        "feesPercent": Decimal("1.00"),
        "chargesPercent": Decimal("0.50"),
        "discountDeadline": date(2026, 5, 10),
        "dueDate": date(2099, 5, 10),
    }
    data.update(overrides)
    return Collection(**data)


@pytest.mark.django_db
class TestCollectionCreation:

    def test_create_sets_server_fields_and_calculated_values(
        self, _unit, _user
    ):
        collection = _new_collection(_unit)

        result = CollectionService.save_instance(
            collection, user=_user, is_new=True
        )

        assert result.billingDate == timezone.localdate()
        assert result.status == Collection.Status.TO_BE_WON
        assert result.discountAmount == Decimal("100.00")
        assert result.fineAmount == Decimal("20.00")
        assert result.interestAmount == Decimal("10.00")
        assert result.chargesAmount == Decimal("5.00")
        assert result.totalAmount == Decimal("935.00")
        assert result.balance == Decimal("935.00")
        assert result.created_by == _user
        assert result.updated_by == _user

    def test_create_marks_expired_when_due_date_is_in_the_past(
        self, _unit, _user
    ):
        collection = _new_collection(
            _unit,
            dueDate=timezone.localdate() - timedelta(days=1),
        )

        result = CollectionService.save_instance(
            collection, user=_user, is_new=True
        )

        assert result.status == Collection.Status.EXPIRED

    def test_due_date_today_is_to_be_won(self, _unit, _user):
        collection = _new_collection(
            _unit,
            dueDate=timezone.localdate(),
        )

        result = CollectionService.save_instance(
            collection, user=_user, is_new=True
        )

        assert result.status == Collection.Status.TO_BE_WON

    def test_discount_is_subtracted_from_total(self, _unit, _user):
        collection = _new_collection(
            _unit,
            originalValue=Decimal("100.00"),
            discountPercent=Decimal("10.00"),
            penaltyPercent=None,
            feesPercent=None,
            chargesPercent=None,
        )

        result = CollectionService.save_instance(
            collection, user=_user, is_new=True
        )

        assert result.discountAmount == Decimal("10.00")
        assert result.totalAmount == Decimal("90.00")

    def test_original_value_is_optional(self, _unit, _user):
        collection = _new_collection(
            _unit,
            originalValue=None,
            discountPercent=None,
            penaltyPercent=None,
            feesPercent=None,
            chargesPercent=None,
        )

        result = CollectionService.save_instance(
            collection, user=_user, is_new=True
        )

        assert result.totalAmount is None
        assert result.discountAmount is None
        assert result.balance == Decimal("0.00")
        assert result.status == Collection.Status.TO_BE_WON

    def test_percent_above_limit_is_rejected(self, _unit, _user):
        collection = _new_collection(
            _unit,
            discountPercent=Decimal("100.01"),
        )

        with pytest.raises(CollectionValidationError):
            CollectionService.save_instance(
                collection, user=_user, is_new=True
            )

    def test_client_supplied_amounts_are_ignored(self, _unit, _user):
        collection = _new_collection(_unit)
        collection.discountAmount = Decimal("1.00")
        collection.totalAmount = Decimal("1.00")
        collection.balance = Decimal("1.00")
        collection.status = Collection.Status.PAID

        result = CollectionService.save_instance(
            collection, user=_user, is_new=True
        )

        assert result.discountAmount == Decimal("100.00")
        assert result.totalAmount == Decimal("935.00")
        assert result.balance == Decimal("935.00")
        assert result.status == Collection.Status.TO_BE_WON


@pytest.mark.django_db
class TestCollectionEditing:

    def test_edit_only_to_be_won(self, _expired_collection, _user):
        _expired_collection.originalValue = Decimal("200.00")

        with pytest.raises(CollectionTransitionError):
            CollectionService.save_instance(
                _expired_collection, user=_user, is_new=False
            )

    def test_edit_blocked_for_paid(self, _paid_collection, _user):
        _paid_collection.originalValue = Decimal("200.00")

        with pytest.raises(CollectionTransitionError):
            CollectionService.save_instance(
                _paid_collection, user=_user, is_new=False
            )

    def test_edit_blocked_for_inactive(self, _collection, _user):
        _collection.is_active = False
        _collection.save(update_fields=["is_active"])
        _collection.originalValue = Decimal("200.00")

        with pytest.raises(CollectionTransitionError):
            CollectionService.save_instance(
                _collection, user=_user, is_new=False
            )

    def test_edit_recalculates_and_preserves_audit(self, _collection, _user):
        created_by = _collection.created_by_id
        billing_date = _collection.billingDate
        _collection.originalValue = Decimal("200.00")
        _collection.discountPercent = None
        _collection.penaltyPercent = None
        _collection.feesPercent = None
        _collection.chargesPercent = None

        result = CollectionService.save_instance(
            _collection, user=_user, is_new=False
        )

        assert result.billingDate == billing_date
        assert result.created_by_id == created_by
        assert result.updated_by == _user
        assert result.totalAmount == Decimal("200.00")
        assert result.balance == Decimal("200.00")

    def test_edit_cannot_change_unit_with_linked_releases(
        self, _collection, _unit_two, _billing_release, _user
    ):
        _billing_release.collection = _collection
        _billing_release.save(update_fields=["collection"])
        _collection.condominium = _unit_two

        with pytest.raises(CollectionTransitionError):
            CollectionService.save_instance(
                _collection, user=_user, is_new=False
            )


@pytest.mark.django_db
class TestCollectionDeletion:

    def test_delete_only_to_be_won(self, _expired_collection, _user):
        with pytest.raises(CollectionTransitionError):
            CollectionService.delete_instance(
                _expired_collection, user=_user
            )

    def test_delete_to_be_won(self, _collection, _user):
        pk = _collection.pk

        CollectionService.delete_instance(_collection, user=_user)

        assert not Collection.objects.filter(pk=pk).exists()

    def test_delete_blocked_by_linked_release(
        self, _collection, _billing_release, _user
    ):
        _billing_release.collection = _collection
        _billing_release.save(update_fields=["collection"])

        with pytest.raises(CollectionTransitionError):
            CollectionService.delete_instance(_collection, user=_user)

    def test_delete_blocked_by_payment(
        self, _collection, _financial_transaction, _user
    ):
        Payment.objects.create(
            collection=_collection,
            financialTransaction=_financial_transaction,
            dateReceived=date(2026, 1, 15),
            amountReceived=Decimal("100.00"),
            created_by=_user,
            updated_by=_user,
        )

        with pytest.raises(CollectionTransitionError):
            CollectionService.delete_instance(_collection, user=_user)

    def test_delete_blocked_by_credit(self, _collection, _user):
        CollectionService.register_credit(
            _collection,
            _financial_transaction_fixture(),
            date(2026, 1, 15),
            Decimal("100.00"),
            user=_user,
        )
        _collection.refresh_from_db()
        _collection.status = Collection.Status.TO_BE_WON
        _collection.save(update_fields=["status"])

        with pytest.raises(CollectionTransitionError):
            CollectionService.delete_instance(_collection, user=_user)


def _financial_transaction_fixture():
    from domains.parameters.models import FinancialTransaction

    return FinancialTransaction.objects.get_or_create(
        description="Operação de teste"
    )[0]


@pytest.mark.django_db
class TestCollectionUpdateAction:

    def test_update_reports_partial_success(
        self, _collection, _paid_collection, _user
    ):
        results = CollectionService.update_collections(
            [_collection.pk, _paid_collection.pk],
            user=_user,
        )

        assert results[0]["success"] is True
        assert results[1]["success"] is False
        assert "paga" in results[1]["reason"]
        _paid_collection.refresh_from_db()
        assert "paga" in _paid_collection.errorStatus

    def test_update_marks_expired(self, _collection, _user):
        _collection.dueDate = timezone.localdate() - timedelta(days=1)
        _collection.save(update_fields=["dueDate"])

        results = CollectionService.update_collections(
            [_collection.pk], user=_user
        )

        assert results[0]["success"] is True
        _collection.refresh_from_db()
        assert _collection.status == Collection.Status.EXPIRED

    def test_update_rejects_inactive(self, _collection, _user):
        _collection.is_active = False
        _collection.save(update_fields=["is_active"])

        results = CollectionService.update_collections(
            [_collection.pk], user=_user
        )

        assert results[0]["success"] is False
        assert "inativa" in results[0]["reason"]

    def test_update_clears_previous_error(self, _collection, _user):
        _collection.errorStatus = "erro anterior"
        _collection.save(update_fields=["errorStatus"])

        CollectionService.update_collections([_collection.pk], user=_user)

        _collection.refresh_from_db()
        assert _collection.errorStatus == ""

    def test_missing_record_is_reported(self, _user):
        results = CollectionService.update_collections([999999], user=_user)

        assert results[0]["success"] is False
        assert "não encontrada" in results[0]["reason"]


@pytest.mark.django_db
class TestCollectionPayments:

    def test_partial_then_full_payment(
        self, _collection, _financial_transaction, _user
    ):
        CollectionService.register_payment(
            _collection,
            _financial_transaction,
            date(2026, 1, 20),
            Decimal("400.00"),
            user=_user,
        )

        _collection.refresh_from_db()
        assert _collection.balance == Decimal("535.00")
        assert _collection.status == Collection.Status.PARTIAL

        CollectionService.register_payment(
            _collection,
            _financial_transaction,
            date(2026, 1, 21),
            Decimal("535.00"),
            user=_user,
        )

        _collection.refresh_from_db()
        assert _collection.balance == Decimal("0.00")
        assert _collection.status == Collection.Status.PAID
        assert Payment.objects.filter(collection=_collection).count() == 2

    def test_payment_above_balance_is_rejected(
        self, _collection, _financial_transaction, _user
    ):
        with pytest.raises(CollectionValidationError):
            CollectionService.register_payment(
                _collection,
                _financial_transaction,
                date(2026, 1, 20),
                Decimal("935.01"),
                user=_user,
            )

        assert not Payment.objects.filter(collection=_collection).exists()

    def test_payment_on_paid_collection_is_rejected(
        self, _paid_collection, _financial_transaction, _user
    ):
        with pytest.raises(CollectionTransitionError):
            CollectionService.register_payment(
                _paid_collection,
                _financial_transaction,
                date(2026, 4, 20),
                Decimal("10.00"),
                user=_user,
            )

    def test_payment_on_inactive_collection_is_rejected(
        self, _collection, _financial_transaction, _user
    ):
        _collection.is_active = False
        _collection.save(update_fields=["is_active"])

        with pytest.raises(CollectionTransitionError):
            CollectionService.register_payment(
                _collection,
                _financial_transaction,
                date(2026, 1, 20),
                Decimal("10.00"),
                user=_user,
            )

    def test_payment_requires_active_financial_transaction(
        self, _collection, _financial_transaction, _user
    ):
        _financial_transaction.is_active = False
        _financial_transaction.save(update_fields=["is_active"])

        with pytest.raises(CollectionValidationError):
            CollectionService.register_payment(
                _collection,
                _financial_transaction,
                date(2026, 1, 20),
                Decimal("10.00"),
                user=_user,
            )

    def test_expired_collection_accepts_payment(
        self, _expired_collection, _financial_transaction, _user
    ):
        CollectionService.register_payment(
            _expired_collection,
            _financial_transaction,
            date(2026, 2, 20),
            Decimal("40.00"),
            user=_user,
        )

        _expired_collection.refresh_from_db()
        assert _expired_collection.status == Collection.Status.PARTIAL
        assert _expired_collection.balance == Decimal("60.00")


@pytest.mark.django_db
class TestCollectionCredits:

    def test_credit_reduces_balance_and_marks_partial(
        self, _collection, _financial_transaction, _user
    ):
        CollectionService.register_credit(
            _collection,
            _financial_transaction,
            date(2026, 1, 20),
            Decimal("100.00"),
            user=_user,
        )

        _collection.refresh_from_db()
        assert _collection.balance == Decimal("835.00")
        assert _collection.status == Collection.Status.PARTIAL

    def test_credit_can_mark_collection_as_paid(
        self, _collection, _financial_transaction, _user
    ):
        CollectionService.register_credit(
            _collection,
            _financial_transaction,
            date(2026, 1, 20),
            Decimal("935.00"),
            user=_user,
        )

        _collection.refresh_from_db()
        assert _collection.balance == Decimal("0.00")
        assert _collection.status == Collection.Status.PAID

    def test_credit_above_balance_is_rejected(
        self, _collection, _financial_transaction, _user
    ):
        with pytest.raises(CollectionValidationError):
            CollectionService.register_credit(
                _collection,
                _financial_transaction,
                date(2026, 1, 20),
                Decimal("935.01"),
                user=_user,
            )

    def test_recalculate_uses_payments_and_credits(
        self, _collection_credit, _user
    ):
        result = CollectionService.recalculate(
            _collection_credit.collection, user=_user
        )

        assert result.balance == Decimal("835.00")
        assert result.status == Collection.Status.PARTIAL
        assert result.errorStatus == ""

    def test_credit_and_payment_share_the_balance(
        self, _collection, _financial_transaction, _user
    ):
        CollectionService.register_credit(
            _collection,
            _financial_transaction,
            date(2026, 1, 20),
            Decimal("400.00"),
            user=_user,
        )

        with pytest.raises(CollectionValidationError):
            CollectionService.register_payment(
                _collection,
                _financial_transaction,
                date(2026, 1, 21),
                Decimal("536.00"),
                user=_user,
            )


@pytest.mark.django_db
class TestCollectionComposition:

    def test_link_release_with_same_unit(
        self, _collection, _billing_release, _user
    ):
        linked = CollectionService.link_new_releases(
            _collection, [_billing_release.pk], user=_user
        )

        assert linked == [_billing_release]
        _billing_release.refresh_from_db()
        assert _billing_release.collection_id == _collection.pk
        assert _billing_release.updated_by == _user

    def test_link_requires_cobranca_status(
        self, _collection, _new_release, _user
    ):
        with pytest.raises(CollectionTransitionError):
            CollectionService.link_new_releases(
                _collection, [_new_release.pk], user=_user
            )

    def test_link_requires_same_unit(
        self,
        _collection,
        _unit_two,
        _resident_two,
        _chart_account,
        _fund,
        _user,
    ):
        release = NewRelease.objects.create(
            condominium=_unit_two,
            paymaster=_resident_two,
            title="Outro lançamento",
            scope=date(2026, 6, 1),
            launchDate=date(2026, 6, 10),
            chartOfAccounts=_chart_account,
            fund=_fund,
            launchType=NewRelease.LaunchType.DEBITO,
            value=Decimal("10.00"),
            status=NewRelease.Status.COBRANCA,
            created_by=_user,
            updated_by=_user,
        )

        with pytest.raises(CollectionValidationError):
            CollectionService.link_new_releases(
                _collection, [release.pk], user=_user
            )

    def test_link_rejects_release_of_another_collection(
        self,
        _collection,
        _unit,
        _resident,
        _chart_account,
        _fund,
        _user,
    ):
        other = Collection.objects.create(
            condominium=_unit,
            billingDate=date(2026, 7, 5),
            scope=date(2026, 7, 1),
            discountDeadline=date(2026, 7, 10),
            dueDate=date(2099, 7, 10),
            created_by=_user,
            updated_by=_user,
        )
        release = NewRelease.objects.create(
            condominium=_unit,
            paymaster=_resident,
            title="Lançamento de outra cobrança",
            scope=date(2026, 7, 1),
            launchDate=date(2026, 7, 10),
            chartOfAccounts=_chart_account,
            fund=_fund,
            launchType=NewRelease.LaunchType.DEBITO,
            value=Decimal("10.00"),
            status=NewRelease.Status.COBRANCA,
            collection=other,
            created_by=_user,
            updated_by=_user,
        )

        with pytest.raises(CollectionTransitionError):
            CollectionService.link_new_releases(
                _collection, [release.pk], user=_user
            )
