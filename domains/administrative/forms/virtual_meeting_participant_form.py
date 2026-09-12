from django import forms

from domains.administrative.models.virtual_meeting_participant import VirtualMeetingParticipant


class VirtualMeetingParticipantForm(forms.ModelForm):

    class Meta:
        model = VirtualMeetingParticipant
        fields = ('virtual_meeting', 'resident_type', 'resident')
        widgets = {
            'virtual_meeting': forms.Select(
                attrs={'class': 'form-control'},
            ),
            'resident_type': forms.Select(
                attrs={
                    'class': 'form-control resident-type-select',
                    'data-residents-url': '/administrative/ajax/residents-by-type/',
                },
            ),
            'resident': forms.Select(
                attrs={'class': 'form-control resident-select'},
            ),
        }
        labels = {
            'virtual_meeting': 'Assembleia',
            'resident_type': 'Tipo de Residente',
            'resident': 'Morador',
        }
        error_messages = {
            'virtual_meeting': {
                'required': 'Selecione a assembleia.',
            },
            'resident_type': {
                'required': 'Selecione o tipo de residente.',
            },
            'resident': {
                'required': 'Selecione o morador.',
            },
        }

    def clean(self):
        cleaned_data = super().clean()
        resident = cleaned_data.get('resident')
        resident_type = cleaned_data.get('resident_type')

        if resident and resident_type and resident.type_of_resident_id != resident_type.pk:
            self.add_error(
                'resident',
                f'O morador selecionado não pertence ao tipo "{resident_type}".',
            )

        return cleaned_data