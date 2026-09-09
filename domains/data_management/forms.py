from django import forms
from django.core.exceptions import ValidationError

from core.services.validators import validate_date
from .models import BackupModule


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
