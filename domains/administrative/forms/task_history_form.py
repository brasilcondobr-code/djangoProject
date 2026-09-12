from django import forms

from domains.administrative.models.task_history import TaskHistory


class TaskHistoryForm(forms.ModelForm):

    class Meta:
        model = TaskHistory
        fields = '__all__'
        widgets = {
            'task': forms.Select(
                attrs={
                    'class': 'form-control',
                },
            ),
            'history_date': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date',
                },
                format='%Y-%m-%d',
            ),
            'description_history': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 4,
                    'placeholder': 'Descreva o histórico da tarefa...',
                },
            ),
        }
        labels = {
            'task': 'Tarefa',
            'history_date': 'Data do histórico',
            'description_history': 'Descrição do histórico',
        }
        error_messages = {
            'task': {
                'required': 'Selecione a tarefa.',
                'invalid_choice': 'Selecione uma tarefa válida.',
            },
            'history_date': {
                'required': 'Selecione a data do histórico.',
                'invalid': 'Informe uma data válida.',
            },
            'description_history': {
                'required': 'A descrição do histórico deve possuir conteúdo.',
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if 'created_by_user' in self.fields:
            self.fields['created_by_user'].required = False
            self.fields['created_by_user'].widget.attrs['class'] = 'form-control'
