from django import forms
from domains.email_service.models import ConnectionStatus, TypesProvider, SMTPConfiguration, UsageProfiles, ShippingQueue, EmailHistory, TypesPriority

class ConnectionStatusForm(forms.ModelForm):
    class Meta:
        model = ConnectionStatus
        fields = '__all__'

class TypesProviderForm(forms.ModelForm):
    class Meta:
        model = TypesProvider
        fields = '__all__'

class SMTPConfigurationForm(forms.ModelForm):
    class Meta:
        model = SMTPConfiguration
        fields = '__all__'

class UsageProfilesForm(forms.ModelForm):
    class Meta:
        model = UsageProfiles
        fields = '__all__'

class ShippingQueueForm(forms.ModelForm):
    class Meta:
        model = ShippingQueue
        fields = '__all__'
