from django import forms
from core.services.validators import validate_date
from domains.administrative.models.circular import Circular
from ckeditor.widgets import CKEditorWidget

class CircularForm(forms.ModelForm):
    class Meta:
        model = Circular
        fields = '__all__'
        widgets = {
            'circular_content': CKEditorWidget(),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'release_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
        labels = {
            'condominium': 'Condomínio',
            'release_date': 'Data de Lançamento',
            'title': 'Título',
            'circular_content': 'Conteúdo da Circular',
            'is_active': 'Ativo',
            'types_residents': 'Tipo de Residente',
            'residents': 'Residentes',
            'email_smtp_configuration': 'Configuração SMTP',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['condominium'].required = True
        self.fields['release_date'].required = True
        self.fields['title'].required = True
        self.fields['circular_content'].required = True

    def clean_release_date(self):
        release_date = self.cleaned_data.get('release_date')
        if release_date and not validate_date(release_date):
            raise forms.ValidationError('A data de lançamento informada é inválida.')
        return release_date
