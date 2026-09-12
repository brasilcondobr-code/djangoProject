"""
Exportadores concretos do módulo 02. Exportações.

Cada exportador define: modelo, cabeçalhos, campos (com suporte a joins via
`foo__bar`), `select_related` (anti N+1) e o filtro por condomínio quando o
dado é escopado por condomínio. A serialização usa `iterator()` (streaming) e
`get_field(...).choices` para exibir os labels das escolhas.

O registry é populado ao final do módulo — novos serviços de exportação devem
ser adicionados AQUI (registrados no código), nunca digitados pelo usuário.
"""

from abc import ABC
from dataclasses import dataclass, field as dataclass_field
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Optional, Tuple

from django.apps import apps
from django.utils import timezone

from domains.data_management.exceptions import ExportValidationException
from domains.data_management.services.export_registry import registry
from domains.data_management.services.export_writers import get_writer


@dataclass(frozen=True)
class ExportContext:
    """Contexto passado ao exportador (nunca contém código executável)."""

    export_id: int
    condominium_id: Optional[int]
    file_format: str
    destination: Path


@dataclass(frozen=True)
class ExportResult:
    """Resultado padronizado de uma geração de arquivo."""

    file_path: Path
    row_count: int
    file_size: int
    headers: Tuple[str, ...] = dataclass_field(default_factory=tuple)


class BaseExporter(ABC):
    """Contrato dos exportadores: gera o arquivo no destino do contexto."""

    service_key: str = ''
    # Modelo no formato "app_label.ModelName" (resolvido no uso, lazy).
    model: Optional[str] = None
    headers: Tuple[str, ...] = ()
    fields: Tuple[str, ...] = ()
    select_related: Tuple[str, ...] = ()
    # Quando True, o exportador filtra pelo condomínio da configuração.
    filter_by_condominium: bool = False
    condominium_lookup: str = 'condominium_id'
    # Quando True, o modelo é o próprio Condomínio (filtra pk=condominium_id).
    self_export: bool = False

    # ------------------------------------------------------------------
    # QuerySet
    # ------------------------------------------------------------------
    def build_queryset(self, condominium_id):
        model = apps.get_model(*self.model.split('.')) if self.model else None
        if model is None:
            raise ExportValidationException(
                f'O exportador {self.service_key!r} não define um modelo.'
            )
        qs = model.objects.all()
        if self.self_export and condominium_id:
            qs = qs.filter(pk=condominium_id)
        elif self.filter_by_condominium and condominium_id:
            qs = qs.filter(**{self.condominium_lookup: condominium_id})
        if self.select_related:
            qs = qs.select_related(*self.select_related)
        return qs

    # ------------------------------------------------------------------
    # Geração
    # ------------------------------------------------------------------
    def generate(self, context: ExportContext) -> ExportResult:
        queryset = self.build_queryset(context.condominium_id)
        writer = get_writer(context.file_format)
        row_count = writer.write(self.headers, self.iter_rows(queryset), context.destination)
        return ExportResult(
            file_path=Path(context.destination),
            row_count=row_count,
            file_size=Path(context.destination).stat().st_size,
            headers=self.headers,
        )

    def iter_rows(self, queryset):
        """Itera os registros em streaming, serializando cada linha."""
        for obj in queryset.iterator():
            yield [self._cell(self._value(obj, field)) for field in self.fields]

    # ------------------------------------------------------------------
    # Serialização
    # ------------------------------------------------------------------
    def _value(self, obj, field):
        if '__' in field:
            current = obj
            for part in field.split('__'):
                current = getattr(current, part, None)
                if current is None:
                    break
            return '' if current is None else str(current)

        value = getattr(obj, field)
        field_meta = None
        try:
            field_meta = obj._meta.get_field(field)
        except Exception:  # noqa: BLE001 - campos computados sem metadados
            field_meta = None
        if field_meta is not None and getattr(field_meta, 'choices', None):
            choices = dict(field_meta.choices)
            if value in choices:
                return choices[value]
        return value

    @staticmethod
    def _cell(value):
        if value is None:
            return ''
        if isinstance(value, bool):
            return 'Sim' if value else 'Não'
        if isinstance(value, datetime):
            if timezone.is_aware(value):
                value = timezone.localtime(value)
            return value.strftime('%Y-%m-%d %H:%M:%S')
        if isinstance(value, date):
            return value.isoformat()
        if isinstance(value, Decimal):
            return f'{value:f}'
        return str(value)


# ---------------------------------------------------------------------------
# Serviços registrados (chaves usadas no ExportModule.export_service)
# ---------------------------------------------------------------------------

class CondominiumTypesExporter(BaseExporter):
    service_key = 'parameters.condominium_types'
    model = 'parameters.TypesCondominium'
    headers = ('Tipo de Condomínio', 'Ativo', 'Criado em', 'Atualizado em')
    fields = ('name', 'is_active', 'created_at', 'updated_at')


class CondominiumStructuresExporter(BaseExporter):
    service_key = 'parameters.condominium_structures'
    model = 'parameters.StructionCondominium'
    headers = ('Estrutura do Condomínio', 'Ativo', 'Criado em', 'Atualizado em')
    fields = ('name', 'is_active', 'created_at', 'updated_at')


class StatesExporter(BaseExporter):
    service_key = 'parameters.states'
    model = 'parameters.States'
    headers = ('Estado', 'UF', 'Capital', 'Região', 'Criado em', 'Atualizado em')
    fields = ('name', 'abbreviation', 'capital', 'region', 'created_at', 'updated_at')


class CondominiumsExporter(BaseExporter):
    service_key = 'condominium.condominiums'
    model = 'condominium.Condominium'
    headers = (
        'Código', 'Nome', 'CNPJ', 'Ativo', 'Inscrição Estadual',
        'Inscrição Municipal', 'Tipo de Condomínio', 'Estrutura do Condomínio',
        'Endereço', 'Criado em', 'Atualizado em',
    )
    fields = (
        'code', 'name', 'cnpj', 'is_active', 'state_registration',
        'municipal_registration', 'type_condominium__name',
        'struction_condominium__name', 'address', 'created_at', 'updated_at',
    )
    select_related = ('type_condominium', 'struction_condominium', 'address')
    self_export = True


class CollaboratorsExporter(BaseExporter):
    service_key = 'condominium.collaborators'
    model = 'condominium.Collaborator'
    headers = (
        'Condomínio', 'Nome', 'CPF', 'RG', 'E-mail', 'Telefone',
        'Tipo de Colaborador', 'Ativo', 'Criado em', 'Atualizado em',
    )
    fields = (
        'condominium__name', 'name', 'cpf', 'rg', 'email', 'phone_number',
        'type_collaborator__name', 'is_active', 'created_at', 'updated_at',
    )
    select_related = ('condominium', 'type_collaborator')
    filter_by_condominium = True


class UnitsExporter(BaseExporter):
    service_key = 'residents.units'
    model = 'residents.CondominiumUnit'
    headers = (
        'Condomínio', 'Bloco / Torre', 'Número', 'Pavimento', 'Identificação',
        'Tipo', 'Quartos', 'Banheiros', 'Suítes', 'Vagas de garagem',
        'Área total', 'Status', 'Para venda', 'Para aluguel',
        'Preço de venda', 'Preço de aluguel', 'Criado em', 'Atualizado em',
    )
    fields = (
        'condominium__name', 'tower', 'unit_number', 'floor', 'identification',
        'unit_type', 'bedrooms', 'bathrooms', 'suites', 'garage_spaces',
        'area_total', 'status', 'for_sale', 'for_rent', 'sale_price',
        'rent_price', 'created_at', 'updated_at',
    )
    select_related = ('condominium',)
    filter_by_condominium = True


class ResidentsExporter(BaseExporter):
    service_key = 'residents.residents'
    model = 'residents.Resident'
    headers = (
        'Condomínio', 'Unidade', 'Tipo de morador', 'Nome', 'E-mail',
        'Telefone', 'CPF', 'RG', 'Sexo', 'Data de nascimento', 'Profissão',
        'Principal', 'É residente', 'Ativo', 'Criado em', 'Atualizado em',
    )
    fields = (
        'unit__condominium__name', 'unit__unit_number', 'type_of_resident__name',
        'name', 'email', 'phone', 'cpf', 'rg', 'sex', 'date_of_birth',
        'profession', 'is_primary', 'is_resident', 'is_active',
        'created_at', 'updated_at',
    )
    select_related = ('unit__condominium', 'type_of_resident')
    filter_by_condominium = True
    condominium_lookup = 'unit__condominium_id'


class VehiclesExporter(BaseExporter):
    service_key = 'residents.vehicles'
    model = 'residents.Vehicle'
    headers = (
        'Condomínio', 'Unidade', 'Tipo', 'Placa', 'Marca', 'Modelo', 'Cor',
        'Ano', 'Vaga de garagem', 'Ativo', 'Criado em', 'Atualizado em',
    )
    fields = (
        'condo_unit__condominium__name', 'condo_unit__unit_number',
        'vehicle_type', 'license_plate', 'brand', 'model', 'color', 'year',
        'garage_space', 'is_active', 'created_at', 'updated_at',
    )
    select_related = ('condo_unit__condominium',)
    filter_by_condominium = True
    condominium_lookup = 'condo_unit__condominium_id'


class TypesCondominiumExporter(BaseExporter):
    service_key = 'parameters.typescondominium'
    model = 'parameters.TypesCondominium'
    headers = ('Tipo de Condomínio', 'Ativo', 'Criado em', 'Atualizado em')
    fields = ('name', 'is_active', 'created_at', 'updated_at')


class StructionCondominiumExporter(BaseExporter):
    service_key = 'parameters.structioncondominium'
    model = 'parameters.StructionCondominium'
    headers = ('Estrutura do Condomínio', 'Ativo', 'Criado em', 'Atualizado em')
    fields = ('name', 'is_active', 'created_at', 'updated_at')


# ---------------------------------------------------------------------------
# Novos exportadores para parâmetros adicionais
# ---------------------------------------------------------------------------

class StatesExporter2(BaseExporter):
    service_key = 'parameters.states'
    model = 'parameters.States'
    headers = ('Estado', 'UF', 'Capital', 'Região', 'Criado em', 'Atualizado em')
    fields = ('name', 'abbreviation', 'capital', 'region', 'created_at', 'updated_at')


class AddressesExporter(BaseExporter):
    service_key = 'parameters.addresses'
    model = 'parameters.Addresses'
    headers = ('Logradouro', 'Número', 'Bairro', 'Cep', 'Cidade', 'Estado', 'Ativo', 'Criado em', 'Atualizado em')
    fields = ('street', 'number', 'neighborhood', 'zip_code', 'city', 'state__name', 'is_active', 'created_at', 'updated_at')
    select_related = ('state',)


class TypesVisitorRestrictionsExporter(BaseExporter):
    service_key = 'parameters.typesvisitorrestrictions'
    model = 'parameters.TypesVisitorRestrictions'
    headers = ('Tipo de Restrição de Visitante', 'Descrição', 'Ativo', 'Criado em', 'Atualizado em')
    fields = ('description', 'is_active', 'created_at', 'updated_at')


class ResidentTypeExporter(BaseExporter):
    service_key = 'parameters.residenttype'
    model = 'parameters.ResidentType'
    headers = ('Tipo de Residente', 'Descrição', 'Ativo', 'Criado em', 'Atualizado em')
    fields = ('description', 'is_active', 'created_at', 'updated_at')


class DocumentTypeExporter(BaseExporter):
    service_key = 'parameters.documenttype'
    model = 'parameters.DocumentType'
    headers = ('Tipo de Documento', 'Descrição', 'Ativo', 'Criado em', 'Atualizado em')
    fields = ('description', 'is_active', 'created_at', 'updated_at')


class InfractionsTypeExporter(BaseExporter):
    service_key = 'parameters.infractionstype'
    model = 'parameters.InfractionsType'
    headers = ('Tipo de Infração', 'Descrição', 'Ativo', 'Criado em', 'Atualizado em')
    fields = ('description', 'infraction_type', 'is_active', 'created_at', 'updated_at')


class MeterTypeExporter(BaseExporter):
    service_key = 'parameters.metertype'
    model = 'parameters.MeterType'
    headers = ('Tipo de Medidor', 'Descrição', 'Ativo', 'Criado em', 'Atualizado em')
    fields = ('description', 'is_active', 'created_at', 'updated_at')


class AssetCategoryExporter(BaseExporter):
    service_key = 'parameters.assetcategory'
    model = 'parameters.AssetCategory'
    headers = ('Categoria de Ativo', 'Descrição', 'Ativo', 'Criado em', 'Atualizado em')
    fields = ('description', 'is_active', 'created_at', 'updated_at')


class AssetStateConditionExporter(BaseExporter):
    service_key = 'parameters.assetstatecondition'
    model = 'parameters.AssetStateCondition'
    headers = ('Estado de Condição do Ativo', 'Descrição', 'Ativo', 'Criado em', 'Atualizado em')
    fields = ('description', 'is_active', 'created_at', 'updated_at')


class AssetMaintenanceFrequencyExporter(BaseExporter):
    service_key = 'parameters.assetmaintenancefrequency'
    model = 'parameters.AssetMaintenanceFrequency'
    headers = ('Frequência de Manutenção', 'Descrição', 'Ativo', 'Criado em', 'Atualizado em')
    fields = ('description', 'is_active', 'created_at', 'updated_at')


class AssetBrandExporter(BaseExporter):
    service_key = 'parameters.assetbrand'
    model = 'parameters.AssetBrand'
    headers = ('Marca do Ativo', 'Descrição', 'Ativo', 'Criado em', 'Atualizado em')
    fields = ('description', 'is_active', 'created_at', 'updated_at')


class AssetStatusExporter(BaseExporter):
    service_key = 'parameters.assetstatus'
    model = 'parameters.AssetStatus'
    headers = ('Status do Ativo', 'Descrição', 'Ativo', 'Criado em', 'Atualizado em')
    fields = ('description', 'is_active', 'created_at', 'updated_at')


class AssetTypeExporter(BaseExporter):
    service_key = 'parameters.assettype'
    model = 'parameters.AssetType'
    headers = ('Tipo de Ativo', 'Descrição', 'Ativo', 'Criado em', 'Atualizado em')
    fields = ('description', 'is_active', 'created_at', 'updated_at')


class BankAccountTypeExporter(BaseExporter):
    service_key = 'parameters.bankaccounttype'
    model = 'parameters.BankAccountType'
    headers = ('Tipo de Conta Bancária', 'Descrição', 'Ativo', 'Criado em', 'Atualizado em')
    fields = ('description', 'is_active', 'created_at', 'updated_at')


class ChartOfAccountTypeExporter(BaseExporter):
    service_key = 'parameters.chartofaccountstype'
    model = 'parameters.Chartofaccountstype'
    headers = ('Tipo de Conta Contábil', 'Descrição', 'Ativo', 'Criado em', 'Atualizado em')
    fields = ('code', 'description', 'nature', 'is_active', 'created_at', 'updated_at')


class AccountingClassTypesExporter(BaseExporter):
    service_key = 'parameters.accountingclasstypes'
    model = 'parameters.Accountingclasstypes'
    headers = ('Tipo de Classe Contábil', 'Descrição', 'Ativo', 'Criado em', 'Atualizado em')
    fields = ('code', 'description', 'account_type', 'is_active', 'created_at', 'updated_at')


class ChartOfAccountsMainGroupExporter(BaseExporter):
    service_key = 'parameters.chartofaccountsmaingroup'
    model = 'parameters.ChartofaccountsMaingroup'
    headers = ('Grupo Principal da Conta', 'Descrição', 'Ativo', 'Criado em', 'Atualizado em')
    fields = ('code', 'account_class', 'description', 'is_active', 'created_at', 'updated_at')


class ChartOfAccountsSubgroupExporter(BaseExporter):
    service_key = 'parameters.chartofaccountssubgroup'
    model = 'parameters.ChartofaccountsSubgroup'
    headers = ('Subgrupo da Conta', 'Descrição', 'Ativo', 'Criado em', 'Atualizado em')
    fields = ('code', 'main_group', 'description', 'is_active', 'created_at', 'updated_at')


class ChartOfAccountsStatusExporter(BaseExporter):
    service_key = 'parameters.chartofaccountsstatus'
    model = 'parameters.ChartofaccountsStatus'
    headers = ('Status da Conta', 'Descrição', 'Ativo', 'Criado em', 'Atualizado em')
    fields = ('description', 'is_active', 'created_at', 'updated_at')


class VotingTypeExporter(BaseExporter):
    service_key = 'parameters.votingtype'
    model = 'parameters.VotingType'
    headers = ('Tipo de Votacao', 'Descrição', 'Ativo', 'Criado em', 'Atualizado em')
    fields = ('description', 'is_active', 'created_at', 'updated_at')


class AssemblyStatusExporter(BaseExporter):
    service_key = 'parameters.assemblystatus'
    model = 'parameters.AssemblyStatus'
    headers = ('Status da Assembleia', 'Descrição', 'Ativo', 'Criado em', 'Atualizado em')
    fields = ('description', 'is_pending', 'is_running', 'is_complete', 'is_active', 'created_at', 'updated_at')


class TopicOptionExporter(BaseExporter):
    service_key = 'parameters.topicoption'
    model = 'parameters.TopicOption'
    headers = ('Opção de Pauta', 'Descrição', 'Ativo', 'Criado em', 'Atualizado em')
    fields = ('description', 'is_active', 'created_at', 'updated_at')


# ---------------------------------------------------------------------------
# Registro no registry global (importação deste módulo registra os serviços)
# ---------------------------------------------------------------------------
_DEFAULT_EXPORTERS = (
    CondominiumTypesExporter,
    CondominiumStructuresExporter,
    StatesExporter,
    AddressesExporter,
    TypesVisitorRestrictionsExporter,
    ResidentTypeExporter,
    DocumentTypeExporter,
    InfractionsTypeExporter,
    MeterTypeExporter,
    AssetCategoryExporter,
    AssetStateConditionExporter,
    AssetMaintenanceFrequencyExporter,
    AssetBrandExporter,
    AssetStatusExporter,
    AssetTypeExporter,
    BankAccountTypeExporter,
    ChartOfAccountTypeExporter,
    AccountingClassTypesExporter,
    ChartOfAccountsMainGroupExporter,
    ChartOfAccountsSubgroupExporter,
    ChartOfAccountsStatusExporter,
    VotingTypeExporter,
    AssemblyStatusExporter,
    TopicOptionExporter,
    CondominiumsExporter,
    CollaboratorsExporter,
    UnitsExporter,
    ResidentsExporter,
    VehiclesExporter,
    StructionCondominiumExporter,
)

for _exporter_cls in _DEFAULT_EXPORTERS:
    registry.register(_exporter_cls.service_key, _exporter_cls())