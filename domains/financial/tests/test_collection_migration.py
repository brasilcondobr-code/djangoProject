import importlib

import pytest

migration_module = importlib.import_module(
    "domains.financial.migrations.0004_collection_fields_and_payments"
)


class _FakeManager:
    def __init__(self, has_records):
        self._has_records = has_records

    def exists(self):
        return self._has_records


class _FakeModel:
    def __init__(self, has_records):
        self.objects = _FakeManager(has_records)


class _FakeApps:
    def __init__(self, collection_records=False, payment_records=False):
        self._models = {
            "Collection": _FakeModel(collection_records),
            "Payment": _FakeModel(payment_records),
        }

    def get_model(self, app_label, model_name):
        assert app_label == "financial"
        return self._models[model_name]


class TestCollectionMigrationGuard:

    def test_aborts_when_collection_has_records(self):
        with pytest.raises(RuntimeError) as excinfo:
            migration_module.ensure_collection_tables_are_empty(
                _FakeApps(collection_records=True), None
            )

        assert "financial_collection" in str(excinfo.value)
        assert "preservar os dados" in str(excinfo.value)

    def test_aborts_when_payment_has_records(self):
        with pytest.raises(RuntimeError) as excinfo:
            migration_module.ensure_collection_tables_are_empty(
                _FakeApps(payment_records=True), None
            )

        assert "financial_payment" in str(excinfo.value)
        assert "preservar os dados" in str(excinfo.value)

    def test_proceeds_when_tables_are_empty(self):
        assert (
            migration_module.ensure_collection_tables_are_empty(
                _FakeApps(), None
            )
            is None
        )

    def test_reverse_is_noop(self):
        from django.db import migrations

        assert (
            migration_module.Migration.operations[0].reverse_code
            == migrations.RunPython.noop
        )
