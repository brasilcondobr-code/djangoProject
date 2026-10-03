from datetime import date

import pytest

from domains.gatehouse.exceptions import UsefulPhoneNumberError
from domains.gatehouse.models import UsefulPhoneNumber
from domains.parameters.models import CategoryPhone
from domains.gatehouse.services import UsefulPhoneNumberService

pytestmark = pytest.mark.django_db


class TestUsefulPhoneNumberServiceCreate:

    @pytest.fixture
    def category_phone(self):
        return CategoryPhone.objects.create(name="Emergencia")

    def _data(self, condominium, category_phone, **overrides):
        data = {
            "condominium": condominium,
            "categoryPhone": category_phone,
            "releaseDate": date(2026, 10, 2),
            "name": "  Portao Geral  ",
            "phone1": "(11) 3333-4444",
            "phone2": "(11) 99999-8888",
            "observations": "Uteis da portaria",
        }
        data.update(overrides)
        return data

    def test_create(self, admin_user, condominium, category_phone):
        phone = UsefulPhoneNumberService.create_useful_phone_number(
            self._data(condominium, category_phone),
            user=admin_user,
        )
        assert phone.pk is not None
        assert phone.name == "Portao Geral"
        assert phone.phone1 == "(11) 3333-4444"
        assert phone.phone2 == "(11) 99999-8888"
        assert phone.is_active is True
        assert phone.created_by == admin_user

    def test_create_without_user(self, condominium, category_phone):
        phone = UsefulPhoneNumberService.create_useful_phone_number(
            self._data(condominium, category_phone)
        )
        assert phone.pk is not None
        assert phone.created_by is None

    def test_create_with_pks(self, condominium, category_phone):
        phone = UsefulPhoneNumberService.create_useful_phone_number(
            self._data(condominium.pk, category_phone.pk, name="Chaveiro")
        )
        assert phone.condominium == condominium
        assert phone.categoryPhone == category_phone

    def test_create_minimal_required(self, condominium, category_phone):
        phone = UsefulPhoneNumberService.create_useful_phone_number(
            {
                "condominium": condominium,
                "categoryPhone": category_phone,
                "releaseDate": date(2026, 10, 2),
                "name": "Minimo",
                "phone1": "11999998888",
            }
        )
        assert phone.pk is not None
        assert phone.phone2 == ""
        assert phone.observations is None

    @pytest.mark.parametrize(
        "missing",
        ["condominium", "categoryPhone", "releaseDate", "name", "phone1"],
    )
    def test_missing_required_field(self, missing, condominium, category_phone):
        data = self._data(condominium, category_phone)
        data[missing] = None
        with pytest.raises(UsefulPhoneNumberError) as exc:
            UsefulPhoneNumberService.create_useful_phone_number(data)
        assert missing in str(exc.value)
        assert UsefulPhoneNumber.objects.count() == 0

    def test_invalid_phone_rejected(self, condominium, category_phone):
        with pytest.raises(UsefulPhoneNumberError) as exc:
            UsefulPhoneNumberService.create_useful_phone_number(
                self._data(condominium, category_phone, phone1="123")
            )
        assert "Telefone inválido" in str(exc.value)
        assert UsefulPhoneNumber.objects.count() == 0

    def test_invalid_optional_phone_rejected(self, condominium, category_phone):
        with pytest.raises(UsefulPhoneNumberError):
            UsefulPhoneNumberService.create_useful_phone_number(
                self._data(condominium, category_phone, phone2="abc")
            )
        assert UsefulPhoneNumber.objects.count() == 0

    def test_invalid_release_date_rejected(self, condominium, category_phone):
        with pytest.raises(UsefulPhoneNumberError) as exc:
            UsefulPhoneNumberService.create_useful_phone_number(
                self._data(condominium, category_phone, releaseDate="31/13/2026")
            )
        assert "Data de lançamento" in str(exc.value)
        assert UsefulPhoneNumber.objects.count() == 0

    def test_duplicate_rejected(self, condominium, category_phone):
        UsefulPhoneNumberService.create_useful_phone_number(
            self._data(condominium, category_phone)
        )
        with pytest.raises(UsefulPhoneNumberError) as exc:
            UsefulPhoneNumberService.create_useful_phone_number(
                self._data(condominium, category_phone, phone1="11999997777")
            )
        assert "Já existe" in str(exc.value)
        assert UsefulPhoneNumber.objects.count() == 1

    def test_duplicate_different_name_allowed(self, condominium, category_phone):
        UsefulPhoneNumberService.create_useful_phone_number(
            self._data(condominium, category_phone)
        )
        phone = UsefulPhoneNumberService.create_useful_phone_number(
            self._data(condominium, category_phone, name="Portao Socorro")
        )
        assert phone.pk is not None
        assert UsefulPhoneNumber.objects.count() == 2

    def test_nonexistent_condominium_pk(self, category_phone):
        with pytest.raises(UsefulPhoneNumberError) as exc:
            UsefulPhoneNumberService.create_useful_phone_number(
                self._data(999999, category_phone)
            )
        assert "Condomínio não encontrado" in str(exc.value)

    def test_nonexistent_category_pk(self, condominium):
        with pytest.raises(UsefulPhoneNumberError) as exc:
            UsefulPhoneNumberService.create_useful_phone_number(
                self._data(condominium, 999999)
            )
        assert "Categoria de telefone não encontrada" in str(exc.value)


class TestUsefulPhoneNumberServiceDelete:

    @pytest.fixture
    def phone_record(self, condominium):
        return UsefulPhoneNumber.objects.create(
            condominium=condominium,
            name="Portao",
            phone1="11999998888",
            releaseDate=date(2026, 10, 2),
        )

    def test_delete(self, phone_record):
        pk = phone_record.pk
        UsefulPhoneNumberService.delete_useful_phone_number(phone_record)
        assert not UsefulPhoneNumber.objects.filter(pk=pk).exists()

    def test_delete_none_raises(self):
        with pytest.raises(UsefulPhoneNumberError):
            UsefulPhoneNumberService.delete_useful_phone_number(None)


class TestUsefulPhoneNumberServiceGet:

    @pytest.fixture
    def category_phone(self):
        return CategoryPhone.objects.create(name="Emergencia")

    def test_get_all_ordered(self, condominium, category_phone):
        for name in ("Zebra", "Alfa"):
            UsefulPhoneNumber.objects.create(
                condominium=condominium,
                name=name,
                phone1="11999998888",
                categoryPhone=category_phone,
            )
        rows = UsefulPhoneNumberService.get_all_useful_phone_numbers()
        assert [r.name for r in rows] == ["Alfa", "Zebra"]
        assert all(r.condominium_id for r in rows)
