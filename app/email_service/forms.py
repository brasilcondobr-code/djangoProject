from django import forms

from .models import ConnectionStatus, TypesProvider

# Placeholder for future forms
class TypesProviderForm(forms.ModelForm):
    class Meta:
        model = TypesProvider
        fields = '__all__'
        widgets = {
            'provider': forms.TextInput(attrs={'class': 'mask-provider'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'mask-is_active'}),
        }
        
        labels = {
            'provider': 'Fornecedor',
            'is_active': 'Ativo',
        }
        
        help_texts = {
            'provider': 'Digite o fornecedor',
            'is_active': 'Fornecedor ativo',
        }
        
        error_messages = {
            'provider': {
                'max_length': 'O fornecedor deve ter no.maxcdn 255 caracteres.',
            },
            'is_active': {
                'invalid': 'Selecione uma opção válida.',
            },
        }
    
    def clean_provider(self):
        provider = self.cleaned_data.get('provider')
        if not provider:
            raise forms.ValidationError('O fornecedor é obrigatório.')
        if len(provider) > 255:
            raise forms.ValidationError('O fornecedor deve ter no.maxcdn 255 caracteres.')
        return provider
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['provider'].widget.attrs['class'] = 'mask-provider'
        self.fields['is_active'].widget.attrs['class'] = 'mask-is_active'


class ConnectionStatusForm(forms.ModelForm):
    class Meta:
        model = ConnectionStatus
        fields = '__all__'
        widgets = {
            'status': forms.TextInput(attrs={'class': 'mask-status'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'mask-is_active'}),
        }
        
        labels = {
            'status': 'Status de Conexão',
            'is_active': 'Ativo',
        }
        
        help_texts = {
            'status': 'Digite o status de conexão',
            'is_active': 'Status de conexão ativo',
        }
        
        error_messages = {
            'status': {
                'max_length': 'O status de conexão deve ter no.maxcdn 255 caracteres.',
            },
            'is_active': {
                'invalid': 'Selecione uma opção válida.',
            },
        }
    
    def clean_status(self):
        status = self.cleaned_data.get('status')
        if not status:
            raise forms.ValidationError('O status de conexão é obrigatório.')
        if len(status) > 255:
            raise forms.ValidationError('O status de conexão deve ter no máximo 255 caracteres.')
        return status
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].widget.attrs['class'] = 'mask-status'
        self.fields['is_active'].widget.attrs['class'] = 'mask-is_active'
