from django import forms
from django.core.exceptions import ValidationError

from core.services.validators import validate_date
from .exceptions import ExportValidationException
from .models import BackupModule, ExportModule
from .services.export_validation_service import ExportValidationService


class BackupModuleForm(forms.ModelForm):
    """Formulário administrativo do módulo 01. Backups."""

    class Meta:
        model = BackupModule
        # Campos técnicos (file_url, status, created_at, updated_at) ficam FORA
        # do form: tentativas de envio manipuladas no POST são simplesmente
        # ignoradas pelo Django (a segurança não depende de readonly no HTML).
        fields = ['title', 'dateTime', 'description', 'is_active']
        widgets = {
            'title': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'maxlength': 250,
                    'placeholder': 'Informe o título do backup',
                }
            ),
            'dateTime': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date',
                    'placeholder': 'Selecione a data do backup',
                },
                format='%Y-%m-%d',
            ),
            'description': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 4,
                    'placeholder': 'Informe uma descrição opcional',
                }
            ),
            'is_active': forms.CheckboxInput(
                attrs={'class': 'form-check-input'}
            ),
        }
        help_texts = {
            'title': 'Título do backup (máximo de 250 caracteres).',
            'dateTime': 'Data do backup. Utilize o calendário para selecionar.',
            'description': 'Descrição detalhada e opcional do backup.',
            'is_active': 'Indica se o registro está ativo.',
        }
        error_messages = {
            'title': {
                'required': 'O título é obrigatório.',
                'max_length': 'O título deve ter no máximo 250 caracteres.',
            },
            'dateTime': {
                'required': 'A data do backup é obrigatória.',
                'invalid': 'Informe uma data válida.',
            },
        }

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if title:
            title = ' '.join(title.split())
            if not title:
                raise ValidationError('O título não pode conter apenas espaços.')
        return title

    def clean_dateTime(self):
        date_value = self.cleaned_data.get('dateTime')
        if date_value is not None and not validate_date(date_value):
            # Validação de backend da data (não depende de JavaScript).
            raise ValidationError('Data inválida. Informe uma data válida.')
        return date_value

    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data.get('title')
        date_value = cleaned_data.get('dateTime')
        if title and date_value:
            queryset = BackupModule.objects.filter(
                title=title, dateTime=date_value
            )
            if self.instance and self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise ValidationError(
                    'Já existe um backup com este título para a data informada.'
                )
        return cleaned_data


class ExportModuleForm(forms.ModelForm):
    """Formulário administrativo do módulo 02. Exportações."""

    class Meta:
        model = ExportModule
        # Campos técnicos (generate_datetime, file_generate, file_status,
        # created_at, updated_at) ficam FORA do form: submissões manipuladas
        # no POST são ignoradas pelo Django (segurança não depende de HTML).
        fields = [
            'condominium', 'group', 'module', 'file_format',
            'export_service', 'description', 'is_active',
        ]
        widgets = {
            'condominium': forms.Select(
                attrs={'class': 'form-control'}
            ),
            'group': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'maxlength': 250,
                    'placeholder': 'parameters',
                }
            ),
            'module': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'maxlength': 250,
                    'placeholder': 'condominium_types',
                }
            ),
            'file_format': forms.Select(
                attrs={'class': 'form-control'}
            ),
            'export_service': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'maxlength': 255,
                    'placeholder': 'parameters.condominium_types',
                }
            ),
            'description': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'Informe uma descrição opcional',
                }
            ),
            'is_active': forms.CheckboxInput(
                attrs={'class': 'form-check-input'}
            ),
        }
        help_texts = {
            'condominium': 'Condomínio dono desta configuração.',
            'group': 'Grupo do módulo (ex.: parameters, condominium, residents).',
            'module': 'Módulo a exportar (ex.: condominium_types, states).',
            'file_format': 'Formato do arquivo gerado: CSV ou XLSX.',
            'export_service': 'Chave do serviço de exportação registrado no código '
                              '(ex.: parameters.condominium_types).',
            'description': 'Descrição opcional da exportação.',
            'is_active': 'Indica se o registro está ativo.',
        }
        error_messages = {
            'condominium': {'required': 'O condomínio é obrigatório.'},
            'group': {
                'required': 'O grupo é obrigatório.',
                'max_length': 'O grupo deve ter no máximo 250 caracteres.',
            },
            'module': {
                'required': 'O módulo é obrigatório.',
                'max_length': 'O módulo deve ter no máximo 250 caracteres.',
            },
            'export_service': {
                'required': 'O serviço de exportação é obrigatório.',
                'max_length': 'O serviço deve ter no máximo 255 caracteres.',
            },
        }

    def _validate_or_raise(self, validator, value, *args, **kwargs):
        try:
            return validator(value, *args, **kwargs)
        except ExportValidationException as exc:
            # Domínio -> formulário: erros de validação viram ValidationError.
            raise ValidationError(str(exc)) from exc

    def clean_group(self):
        value = self.cleaned_data.get('group')
        if value:
            value = self._validate_or_raise(
                ExportValidationService.validate_group_module,
                value, field_label='Grupo',
            )
        return value

    def clean_module(self):
        value = self.cleaned_data.get('module')
        if value:
            value = self._validate_or_raise(
                ExportValidationService.validate_group_module,
                value, field_label='Módulo',
            )
        return value

    def clean_export_service(self):
        value = self.cleaned_data.get('export_service')
        if value:
            value = self._validate_or_raise(
                ExportValidationService.validate_service_key, value
            )
        return value

    def clean(self):
        cleaned_data = super().clean()
        condominium = cleaned_data.get('condominium')
        group = cleaned_data.get('group')
        module = cleaned_data.get('module')
        file_format = cleaned_data.get('file_format')
        if condominium and group and module and file_format:
            queryset = ExportModule.objects.filter(
                condominium=condominium,
                group=group,
                module=module,
                file_format=file_format,
            )
            if self.instance and self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise ValidationError(
                    'Já existe uma configuração de exportação com este '
                    'condomínio, grupo, módulo e formato.'
                )
        return cleaned_data
