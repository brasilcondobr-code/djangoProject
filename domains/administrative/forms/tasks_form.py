from django import forms
from ckeditor.widgets import CKEditorWidget

from domains.administrative.models.task import Task
from domains.administrative.services.tasks_service import TaskService
from domains.administrative.validators import validate_task_title, is_html_content_empty, validate_task_description
from domains.email_service.models import ConnectionStatus


class TaskForm(forms.ModelForm):

    class Meta:
        model = Task
        fields = '__all__'
        widgets = {
            'condominium': forms.Select(
                attrs={
                    'class': 'form-control',
                },
            ),
            'responsible_user': forms.Select(
                attrs={
                    'class': 'form-control',
                },
            ),
            'title': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Informe o título da tarefa',
                },
            ),
            'release_date': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date',
                },
                format='%Y-%m-%d',
            ),
            'estimated_completion_date': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date',
                },
                format='%Y-%m-%d',
            ),
            'completion_date': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date',
                },
                format='%Y-%m-%d',
            ),
            'description': CKEditorWidget(),
            'is_active': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input',
                },
            ),
            'status': forms.Select(
                attrs={
                    'class': 'form-control',
                },
            ),
        }
        labels = {
            'condominium': 'Condomínio',
            'created_by_user': 'Criado por',
            'responsible_user': 'Responsável',
            'title': 'Título',
            'release_date': 'Data de lançamento',
            'estimated_completion_date': 'Data prevista de conclusão',
            'completion_date': 'Data de conclusão',
            'description': 'Descrição',
            'is_active': 'Ativo',
            'status': 'Status',
        }
        help_texts = {
            'completion_date': 'Deixe em branco se a tarefa ainda não foi concluída.',
            'status': 'Selecione o status da tarefa.',
        }
        error_messages = {
            'condominium': {
                'required': 'Selecione o condomínio.',
                'invalid_choice': 'Selecione um condomínio válido.',
            },
            'title': {
                'required': 'Informe o título da tarefa.',
            },
            'release_date': {
                'required': 'Selecione a data de lançamento.',
                'invalid': 'Informe uma data válida.',
            },
            'estimated_completion_date': {
                'required': 'Selecione a data prevista de conclusão.',
                'invalid': 'Informe uma data válida.',
            },
            'completion_date': {
                'invalid': 'Informe uma data válida.',
            },
            'description': {
                'required': 'A descrição da tarefa deve possuir conteúdo.',
            },
        }

    def __init__(self, *args, **kwargs):
        initial = kwargs.get('initial', {})
        super().__init__(*args, **kwargs)

        if not self.instance.pk and initial.get('created_by_user'):
            self.instance.created_by_user = initial['created_by_user']

        self.fields['status'].queryset = ConnectionStatus.objects.filter(is_active=True)
        self.fields['status'].required = False
        self.fields['status'].empty_label = '---------'

        if 'created_by_user' in self.fields:
            self.fields['created_by_user'].required = False
            self.fields['created_by_user'].widget.attrs['class'] = 'form-control'

        if not self.instance.pk:
            status_pendente = ConnectionStatus.objects.filter(status__iexact='Pendente').first()
            if status_pendente:
                self.fields['status'].initial = status_pendente

    def clean_title(self):
        return validate_task_title(self.cleaned_data.get('title'))

    def clean_description(self):
        description = self.cleaned_data.get('description')
        if is_html_content_empty(description):
            raise forms.ValidationError('A descrição da tarefa deve possuir conteúdo.')
        validate_task_description(description)
        return description

    def clean(self):
        cleaned_data = super().clean()
        release_date = cleaned_data.get('release_date')
        estimated_completion_date = cleaned_data.get('estimated_completion_date')
        completion_date = cleaned_data.get('completion_date')

        if release_date and estimated_completion_date:
            if estimated_completion_date < release_date:
                self.add_error(
                    'estimated_completion_date',
                    'A data prevista de conclusão não pode ser anterior à data de lançamento.',
                )

        if release_date and completion_date:
            if completion_date < release_date:
                self.add_error(
                    'completion_date',
                    'A data de conclusão não pode ser anterior à data de lançamento.',
                )

        title = cleaned_data.get('title')
        condominium = cleaned_data.get('condominium')
        if title and condominium:
            qs = Task.objects.filter(condominium=condominium, title=title)
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                self.add_error('title', 'Já existe uma tarefa com este título neste condomínio.')

        return cleaned_data
