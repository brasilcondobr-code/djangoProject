from django import forms
from django.urls import reverse
from domains.administrative.models.chart_of_account import ChartOfAccount
from domains.condominium.models import Condominium
from domains.parameters.models import (
    Chartofaccountstype, Accountingclasstypes,
    ChartofaccountsMaingroup, ChartofaccountsSubgroup,
    ChartofaccountsStatus,
)
from domains.administrative.validators import (
    validate_chart_account_code,
    validate_external_reference,
    validate_archive_reason,
)


class ChartOfAccountForm(forms.ModelForm):

    class Meta:
        model = ChartOfAccount
        fields = '__all__'
        widgets = {
            'account_code': forms.TextInput(attrs={
                'class': 'mask-chart-account-code',
                'placeholder': 'Ex.: 004.001.002.005',
            }),
            'account_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex.: Manutenção preventiva de elevadores',
            }),
            'account_level': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '1 a 4',
            }),
            'account_description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Informe a finalidade e a utilização da conta',
                'rows': 4,
            }),
            'external_reference': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex.: DESP-MAN-ELEV-001',
            }),
            'effective_start_date': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control',
                },
                format='%Y-%m-%d',
            ),
            'effective_end_date': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control',
                },
                format='%Y-%m-%d',
            ),
            'archive_reason': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Informe o motivo do arquivamento',
                'rows': 3,
            }),
            'version': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex.: 1.0',
            }),
            'change_reason': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Informe o motivo da alteração',
                'rows': 3,
            }),
        }
        labels = {
            'condominium': 'Condomínio',
            'account_code': 'Código da conta',
            'account_name': 'Nome da conta',
            'account_type': 'Tipo da conta',
            'account_level': 'Nível hierárquico',
            'account_class': 'Classe contábil',
            'account_group': 'Grupo principal',
            'account_subgroup': 'Subgrupo',
            'parent_account': 'Conta-pai',
            'account_description': 'Descrição detalhada da conta',
            'external_reference': 'Referência externa',
            'status': 'Situação da conta',
            'effective_start_date': 'Data inicial de vigência',
            'effective_end_date': 'Data final de vigência',
            'is_default': 'Conta padrão',
            'is_system_account': 'Conta do sistema',
            'can_be_archived': 'Permite arquivamento',
            'archive_reason': 'Motivo do arquivamento',
            'replacement_account': 'Conta substituta',
            'version': 'Versão do cadastro',
            'change_reason': 'Motivo da alteração',
        }
        help_texts = {
            'account_code': 'Código único dentro do condomínio.',
            'account_level': 'Informe um valor entre 1 e 4.',
            'account_type': 'Selecione o tipo da conta para filtrar a classe contábil.',
            'account_class': 'Selecione primeiro o tipo da conta.',
            'account_group': 'Selecione primeiro a classe contábil.',
            'account_subgroup': 'Selecione primeiro o grupo principal.',
            'parent_account': 'A conta-pai deve pertencer ao mesmo condomínio.',
            'effective_end_date': 'Deixe em branco enquanto a conta estiver vigente.',
            'replacement_account': 'Informe a conta que substituirá esta conta, quando aplicável.',
            'archive_reason': 'Obrigatório quando a conta estiver arquivada.',
        }
        error_messages = {
            'condominium': {
                'required': 'Informe o condomínio.',
                'invalid_choice': 'Selecione um condomínio válido.',
            },
            'account_code': {
                'required': 'Informe o código da conta.',
            },
            'account_name': {
                'required': 'Informe o nome da conta.',
            },
            'account_type': {
                'required': 'Selecione o tipo da conta.',
                'invalid_choice': 'Selecione um tipo de conta válido.',
            },
            'account_level': {
                'required': 'Informe o nível hierárquico.',
                'invalid': 'Informe um número inteiro válido para o nível.',
            },
            'account_class': {
                'required': 'Selecione a classe contábil.',
                'invalid_choice': 'Selecione uma classe contábil válida.',
            },
            'status': {
                'required': 'Selecione a situação da conta.',
                'invalid_choice': 'Selecione uma situação válida.',
            },
            'effective_start_date': {
                'required': 'Informe a data inicial de vigência.',
                'invalid': 'Informe uma data válida.',
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        is_bound = bool(self.data)
        instance = self.instance

        self.fields['account_code'].widget.attrs['class'] = 'mask-chart-account-code form-control'
        self.fields['condominium'].widget.attrs['class'] = 'form-control'

        self.fields['account_type'].queryset = Chartofaccountstype.objects.filter(is_active=True)
        self.fields['account_type'].widget.attrs['class'] = 'form-control'
        self.fields['account_type'].widget.attrs['data-classes-url'] = reverse('filter_classes_by_type')
        self.fields['account_type'].required = True
        self.fields['account_type'].empty_label = '---------'

        all_classes = Accountingclasstypes.objects.filter(is_active=True)
        all_groups = ChartofaccountsMaingroup.objects.filter(is_active=True)
        all_subgroups = ChartofaccountsSubgroup.objects.filter(is_active=True)

        if is_bound:
            type_id = self.data.get('account_type')
            if type_id:
                self.fields['account_class'].queryset = all_classes.filter(account_type_id=type_id)
            else:
                self.fields['account_class'].queryset = all_classes
            class_id = self.data.get('account_class')
            if class_id:
                self.fields['account_group'].queryset = all_groups.filter(account_class_id=class_id)
            else:
                self.fields['account_group'].queryset = all_groups
            group_id = self.data.get('account_group')
            if group_id:
                self.fields['account_subgroup'].queryset = all_subgroups.filter(main_group_id=group_id)
            else:
                self.fields['account_subgroup'].queryset = all_subgroups
        elif instance.pk:
            if instance.account_type_id:
                self.fields['account_class'].queryset = all_classes.filter(account_type=instance.account_type)
            else:
                self.fields['account_class'].queryset = all_classes
            if instance.account_class_id:
                self.fields['account_group'].queryset = all_groups.filter(account_class=instance.account_class)
            else:
                self.fields['account_group'].queryset = all_groups
            if instance.account_group_id:
                self.fields['account_subgroup'].queryset = all_subgroups.filter(main_group=instance.account_group)
            else:
                self.fields['account_subgroup'].queryset = all_subgroups
        else:
            self.fields['account_class'].queryset = all_classes
            self.fields['account_group'].queryset = all_groups
            self.fields['account_subgroup'].queryset = all_subgroups

        self.fields['account_class'].widget.attrs['class'] = 'form-control'
        self.fields['account_class'].widget.attrs['data-groups-url'] = reverse('filter_groups_by_class')
        self.fields['account_class'].required = False
        self.fields['account_class'].empty_label = '---------'
        self.fields['account_group'].widget.attrs['class'] = 'form-control'
        self.fields['account_group'].widget.attrs['data-subgroups-url'] = reverse('filter_subgroups_by_group')
        self.fields['account_group'].required = False
        self.fields['account_group'].empty_label = '---------'
        self.fields['account_subgroup'].widget.attrs['class'] = 'form-control'
        self.fields['account_subgroup'].required = False
        self.fields['account_subgroup'].empty_label = '---------'

        self.fields['status'].queryset = ChartofaccountsStatus.objects.filter(is_active=True)
        self.fields['status'].widget.attrs['class'] = 'form-control'

        condominium_id = None
        if self.instance and self.instance.pk:
            condominium_id = self.instance.condominium_id
        elif self.data.get('condominium'):
            try:
                condominium_id = int(self.data.get('condominium'))
            except (ValueError, TypeError):
                pass

        self._filter_parent_account(condominium_id)
        self._filter_replacement_account(condominium_id)

    def _filter_parent_account(self, condominium_id):
        qs = ChartOfAccount.objects.all()
        if condominium_id:
            qs = qs.filter(condominium_id=condominium_id)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk).exclude(
                parent_account=self.instance,
            )
        self.fields['parent_account'].queryset = qs
        self.fields['parent_account'].widget.attrs['class'] = 'form-control'

    def _filter_replacement_account(self, condominium_id):
        qs = ChartOfAccount.objects.all()
        if condominium_id:
            qs = qs.filter(condominium_id=condominium_id)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        self.fields['replacement_account'].queryset = qs
        self.fields['replacement_account'].widget.attrs['class'] = 'form-control'

    def clean_account_code(self):
        value = self.cleaned_data.get('account_code')
        if not value:
            raise forms.ValidationError('Informe o código da conta.')
        value = value.strip()
        validate_chart_account_code(value)
        return value

    def clean_account_name(self):
        value = self.cleaned_data.get('account_name')
        if not value:
            raise forms.ValidationError('Informe o nome da conta.')
        value = value.strip()
        if not value:
            raise forms.ValidationError('O nome da conta não pode conter apenas espaços.')
        return value

    def clean_account_level(self):
        value = self.cleaned_data.get('account_level')
        if value is None:
            raise forms.ValidationError('Informe o nível hierárquico.')
        if value < 1 or value > 4:
            raise forms.ValidationError('O nível da conta deve estar entre 1 e 4.')
        return value

    def clean_external_reference(self):
        value = self.cleaned_data.get('external_reference', '')
        if value:
            validate_external_reference(value)
        return value

    def clean_archive_reason(self):
        value = self.cleaned_data.get('archive_reason', '')
        if value:
            validate_archive_reason(value)
        return value

    def clean_effective_start_date(self):
        start = self.cleaned_data.get('effective_start_date')
        if not start:
            raise forms.ValidationError('Informe a data inicial de vigência.')
        return start

    def clean_effective_end_date(self):
        start = self.cleaned_data.get('effective_start_date')
        end = self.cleaned_data.get('effective_end_date')
        if start and end and end < start:
            raise forms.ValidationError('A data final não pode ser anterior à data inicial.')
        return end

    def clean_account_type(self):
        value = self.cleaned_data.get('account_type')
        if not value:
            raise forms.ValidationError('Selecione o tipo da conta.')
        return value

    def clean_account_class(self):
        value = self.cleaned_data.get('account_class')
        if not value:
            raise forms.ValidationError('Selecione a classe contábil.')
        return value

    def clean(self):
        cleaned_data = super().clean()
        condominium = cleaned_data.get('condominium')
        account_code = cleaned_data.get('account_code')
        account_level = cleaned_data.get('account_level')
        parent_account = cleaned_data.get('parent_account')
        replacement_account = cleaned_data.get('replacement_account')
        status = cleaned_data.get('status')
        archive_reason = cleaned_data.get('archive_reason')

        if condominium and account_code:
            qs = ChartOfAccount.objects.filter(
                condominium=condominium,
                account_code=account_code,
            )
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                self.add_error('account_code', 'O código da conta já está cadastrado para este condomínio.')

        if account_level is not None:
            if account_level == 1 and parent_account:
                self.add_error('parent_account', 'Uma conta de nível 1 não deve possuir conta-pai.')
            elif account_level > 1:
                if not parent_account:
                    self.add_error('parent_account', 'Contas de nível superior devem possuir uma conta-pai.')
                elif parent_account and parent_account.condominium != condominium:
                    self.add_error('parent_account', 'A conta-pai deve pertencer ao mesmo condomínio.')
                elif parent_account and int(parent_account.account_level) + 1 != int(account_level):
                    self.add_error(
                        'parent_account',
                        f'O nível da conta-pai deve ser {int(account_level) - 1}.',
                    )

        if parent_account and parent_account.pk == self.instance.pk:
            self.add_error('parent_account', 'A conta não pode ser pai dela mesma.')

        if replacement_account:
            if replacement_account.condominium != condominium:
                self.add_error('replacement_account', 'A conta substituta deve pertencer ao mesmo condomínio.')
            if replacement_account.pk == self.instance.pk:
                self.add_error('replacement_account', 'A conta substituta não pode ser a própria conta.')

        if status and status.description and 'arquivada' in status.description.lower():
            if not archive_reason:
                self.add_error('archive_reason', 'Informe o motivo do arquivamento.')
            if self.instance and self.instance.pk and not self.instance.can_be_archived:
                self.add_error('archive_reason', 'Esta conta não permite arquivamento.')

        account_type = cleaned_data.get('account_type')
        account_class = cleaned_data.get('account_class')
        account_group = cleaned_data.get('account_group')
        account_subgroup = cleaned_data.get('account_subgroup')

        if account_type and account_class and account_class.account_type_id != account_type.pk:
            self.add_error(
                'account_class',
                'A classe contábil selecionada não pertence ao tipo da conta informado.',
            )

        if account_class and account_group and account_group.account_class_id != account_class.pk:
            self.add_error(
                'account_group',
                'O grupo principal selecionado não pertence à classe contábil informada.',
            )

        if account_group and account_subgroup and account_subgroup.main_group_id != account_group.pk:
            self.add_error(
                'account_subgroup',
                'O subgrupo selecionado não pertence ao grupo principal informado.',
            )

        return cleaned_data
