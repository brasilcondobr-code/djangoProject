from datetime import date
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from domains.financial.models import Collection, NewRelease


@pytest.mark.django_db
class TestCollectionModel:

    def test_defaults(self):
        collection = Collection()

        assert collection.status == Collection.Status.TO_BE_WON
        assert collection.is_active is True
        assert collection.balance == Decimal("0.00")
        assert collection.errorStatus == ""

    def test_status_labels(self):
        assert Collection.Status.TO_BE_WON.label == "A vencer"
        assert Collection.Status.EXPIRED.label == "Vencido"
        assert Collection.Status.PAID.label == "Pago"
        assert Collection.Status.PARTIAL.label == "Parcial"

    def test_str(self, _collection):
        text = str(_collection)

        assert f"#{_collection.pk}" in text
        assert "01/2026" in text

    def test_unique_constraint(self, _collection, _unit, _user):
        with pytest.raises(IntegrityError), transaction.atomic():
            Collection.objects.create(
                condominium=_unit,
                billingDate=_collection.billingDate,
                scope=_collection.scope,
                discountDeadline=date(2026, 1, 10),
                dueDate=_collection.dueDate,
                created_by=_user,
                updated_by=_user,
            )

    def test_percent_validators_reject_out_of_range(self, _collection):
        _collection.discountPercent = Decimal("101.00")

        with pytest.raises(ValidationError):
            _collection.full_clean()

    def test_new_release_can_be_linked(self, _collection, _billing_release):
        _billing_release.collection = _collection
        _billing_release.save(update_fields=["collection"])

        assert list(_collection.new_releases.all()) == [_billing_release]
        assert _billing_release.collection_id == _collection.pk

    def test_new_release_relation_is_optional(self, _new_release):
        assert _new_release.collection_id is None
        assert NewRelease.objects.filter(collection__isnull=True).exists()
