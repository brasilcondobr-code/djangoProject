from django.core.exceptions import ValidationError

import pytest

from domains.gatehouse.models import UsefulPhoneNumber
from domains.parameters.models import CategoryPhone

pytestmark = pytest.mark.django_db


class TestUsefulPhoneNumber:

    @pytest.fixture
    def category_phone(self):
        return CategoryPhone.objects.create(name="Emergencia")

    @pytest.fixture
    def phone(self, condominium, category_phone):
        return UsefulPhoneNumber.objects.create(
            condominium=condominium,
            categoryPhone=category_phone,
            releaseDate="2026-10-01",
            name="Portao Geral",
            phone1="(11) 3333-4444",
            phone2="(11) 99999-8888",
        )

    def test_create_and_str(self, phone):
        assert phone.pk is not None
        assert "Portao Geral" in str(phone)
        assert "3333-4444" in str(phone)

    def test_str_without_name(self):
        assert str(UsefulPhoneNumber()) == "03. Telefone Útil"

    def test_meta_verbose(self):
        assert str(UsefulPhoneNumber._meta.verbose_name) == "03. Telefone Útil"
        assert str(UsefulPhoneNumber._meta.verbose_name_plural) == "03. Telefones Úteis"
        assert UsefulPhoneNumber._meta.app_label == "gatehouse"

    def test_ordering(self):
        assert UsefulPhoneNumber._meta.ordering == ["name", "id"]

    def test_default_is_active(self, phone):
        phone2 = UsefulPhoneNumber.objects.create(
            condominium=phone.condominium,
            name="Outro",
            phone1="11999998888",
        )
        assert phone2.is_active is True

    def test_field_null_blank_rules(self):
        get = UsefulPhoneNumber._meta.get_field
        assert get("condominium").null is False
        assert get("condominium").blank is False
        assert get("categoryPhone").null is True
        assert get("categoryPhone").blank is True
        assert get("releaseDate").null is True
        assert get("releaseDate").blank is True
        assert get("name").null is False
        assert get("name").blank is False
        assert get("phone1").null is False
        assert get("phone1").blank is False
        for phone_field in ("phone2", "phone3", "phone4", "phone5"):
            assert get(phone_field).blank is True
        assert get("observations").blank is True
        assert get("observations").null is True

    def test_phone_max_length_25(self):
        field = UsefulPhoneNumber._meta.get_field("phone1")
        assert field.max_length == 25

    def test_audit_fields(self):
        assert UsefulPhoneNumber._meta.get_field("created_by").editable is False
        assert UsefulPhoneNumber._meta.get_field("created_at").auto_now_add is True
        assert UsefulPhoneNumber._meta.get_field("updated_at").auto_now is True

    def test_foreign_keys(self):
        assert UsefulPhoneNumber._meta.get_field("condominium").related_model.__name__ == "Condominium"
        assert UsefulPhoneNumber._meta.get_field("categoryPhone").related_model is CategoryPhone

    def test_unique_constraint(self, condominium, category_phone):
        constraint = next(
            c for c in UsefulPhoneNumber._meta.constraints if "uniq_uphone" in c.name
        )
        assert constraint.name == "uniq_uphone_cond_cat_name_date"
        assert tuple(constraint.fields) == (
            "condominium",
            "categoryPhone",
            "name",
            "releaseDate",
        )
        UsefulPhoneNumber.objects.create(
            condominium=condominium,
            categoryPhone=category_phone,
            releaseDate="2026-10-01",
            name="Duplicado",
            phone1="11999998888",
        )
        with pytest.raises(ValidationError):
            duplicate = UsefulPhoneNumber(
                condominium=condominium,
                categoryPhone=category_phone,
                releaseDate="2026-10-01",
                name="Duplicado",
                phone1="11999997777",
            )
            duplicate.full_clean()
