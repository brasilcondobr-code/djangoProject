import pytest
from django.db import IntegrityError, models

from domains.condominium.models import Condominium
from domains.parameters.models import FundFinancial


def make_fund(condominium, **overrides):
    data = {
        'condominium': condominium,
        'description': 'Fundo de Reserva',
    }
    data.update(overrides)
    return FundFinancial.objects.create(**data)


@pytest.mark.django_db
class TestFundFinancialModel:

    def test_create_valid(self, fund_condominium):
        fund = make_fund(fund_condominium)

        assert fund.pk is not None
        assert fund.condominium == fund_condominium
        assert fund.description == 'Fundo de Reserva'

    def test_default_is_active_true(self, fund_condominium):
        fund = make_fund(fund_condominium)

        assert fund.is_active is True

    def test_created_at_auto_set(self, fund_condominium):
        fund = make_fund(fund_condominium)

        assert fund.created_at is not None
        assert fund.updated_at is not None

    def test_updated_at_changes_on_update(self, fund_condominium):
        fund = make_fund(fund_condominium)
        original_updated = fund.updated_at

        fund.description = 'Fundo de Reserva Atualizado'
        fund.save()
        fund.refresh_from_db()

        assert fund.updated_at >= original_updated

    def test_str_returns_description(self, fund_condominium):
        fund = make_fund(fund_condominium, description='Fundo de Obras')

        assert str(fund) == 'Fundo de Obras'

    def test_description_required(self, fund_condominium):
        with pytest.raises(IntegrityError):
            make_fund(fund_condominium, description=None)

    def test_condominium_required(self):
        with pytest.raises(IntegrityError):
            FundFinancial.objects.create(
                condominium=None,
                description='Fundo de Reserva',
            )

    def test_description_max_length(self):
        field = FundFinancial._meta.get_field('description')

        assert field.max_length == 255
        assert field.null is False
        assert field.blank is False
        assert field.unique is False

    def test_duplicate_description_same_condominium_raises(
        self, fund_condominium
    ):
        make_fund(fund_condominium, description='Fundo de Reserva')

        with pytest.raises(IntegrityError):
            make_fund(fund_condominium, description='Fundo de Reserva')

    def test_same_description_different_condominium_allowed(
        self, fund_condominium, other_condominium
    ):
        first = make_fund(fund_condominium, description='Fundo de Reserva')
        second = make_fund(other_condominium, description='Fundo de Reserva')

        assert first.pk != second.pk
        assert FundFinancial.objects.count() == 2

    def test_different_description_same_condominium_allowed(
        self, fund_condominium
    ):
        first = make_fund(fund_condominium, description='Fundo de Reserva')
        second = make_fund(fund_condominium, description='Fundo de Obras')

        assert first.pk != second.pk
        assert FundFinancial.objects.count() == 2

    def test_related_name_on_condominium(self, fund_condominium):
        fund = make_fund(fund_condominium)

        assert list(fund_condominium.fund_financials.all()) == [fund]

    def test_condominium_fk_target(self):
        field = FundFinancial._meta.get_field('condominium')

        assert field.remote_field.model is Condominium
        assert field.remote_field.on_delete is models.CASCADE
        assert field.related_model is Condominium

    def test_deleting_condominium_cascades_fund(self, fund_condominium):
        fund = make_fund(fund_condominium)

        fund_condominium.delete()

        assert not FundFinancial.objects.filter(pk=fund.pk).exists()

    def test_single_composite_constraint(self):
        constraints = FundFinancial._meta.constraints

        assert len(constraints) == 1
        assert constraints[0].name == (
            'uq_fundfinancial_condominium_description'
        )
        assert list(constraints[0].fields) == [
            'condominium',
            'description',
        ]

    def test_no_redundant_unique_together(self):
        assert FundFinancial._meta.unique_together == ()

    def test_verbose_names(self):
        assert FundFinancial._meta.verbose_name == '29. Fundo'
        assert FundFinancial._meta.verbose_name_plural == '29. Fundos'

    def test_app_label(self):
        assert FundFinancial._meta.app_label == 'parameters'

    def test_db_table(self):
        assert FundFinancial._meta.db_table == 'parameters_fundfinancial'

    def test_ordering(self, fund_condominium):
        make_fund(fund_condominium, description='Bbb')
        make_fund(fund_condominium, description='Aaa')

        assert list(FundFinancial.objects.values_list('description', flat=True)) == [
            'Aaa',
            'Bbb',
        ]
