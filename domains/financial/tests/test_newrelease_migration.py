import importlib

import pytest

migration_module = importlib.import_module(
    "domains.financial.migrations.0003_newrelease_fields"
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
    def __init__(self, has_records):
        self._model = _FakeModel(has_records)

    def get_model(self, app_label, model_name):
        assert app_label == "financial"
        assert model_name == "NewRelease"
        return self._model


class TestNewReleaseMigrationGuard:

    def test_aborts_when_table_has_records(self):
        with pytest.raises(RuntimeError) as excinfo:
            migration_module.ensure_newrelease_table_is_empty(
                _FakeApps(has_records=True), None
            )

        assert "financial_newrelease" in str(excinfo.value)
        assert "preservar os dados" in str(excinfo.value)

    def test_proceeds_when_table_is_empty(self):
        assert (
            migration_module.ensure_newrelease_table_is_empty(
                _FakeApps(has_records=False), None
            )
            is None
        )

    def test_reverse_is_noop(self):
        from django.db import migrations

        operations = migration_module.Migration.operations
        assert operations[0].reverse_code == migrations.RunPython.noop
