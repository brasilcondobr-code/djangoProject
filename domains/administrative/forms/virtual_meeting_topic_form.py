from django import forms
from django.forms.models import BaseInlineFormSet

from domains.administrative.models.virtual_meeting_topic import VirtualMeetingTopic
from domains.administrative.services.virtual_meeting_topic_service import VirtualMeetingTopicService


class VirtualMeetingTopicForm(forms.ModelForm):

    class Meta:
        model = VirtualMeetingTopic
        fields = ('virtual_meeting', 'title', 'description', 'topic_options')
        widgets = {
            'virtual_meeting': forms.Select(
                attrs={'class': 'form-control'},
            ),
            'title': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Informe o título da pauta',
                },
            ),
            'description': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 4,
                    'placeholder': 'Descreva a pauta (opcional)',
                },
            ),
            'topic_options': forms.SelectMultiple(
                attrs={'class': 'form-control'},
            ),
        }
        labels = {
            'virtual_meeting': 'Assembleia',
            'title': 'Título',
            'description': 'Descrição',
            'topic_options': 'Opções de votação',
        }
        error_messages = {
            'virtual_meeting': {
                'required': 'Selecione a assembleia.',
            },
            'title': {
                'required': 'Informe o título da pauta.',
            },
        }

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if not title or not title.strip():
            raise forms.ValidationError('Informe o título da pauta.')
        return title.strip()

    def clean(self):
        cleaned_data = super().clean()
        virtual_meeting = cleaned_data.get('virtual_meeting')
        title = cleaned_data.get('title')

        if virtual_meeting and title:
            if VirtualMeetingTopicService.topic_title_exists(
                virtual_meeting, title, exclude_pk=self.instance.pk if self.instance else None
            ):
                self.add_error(
                    'title',
                    'Já existe uma pauta com este título nesta assembleia.',
                )

        return cleaned_data


class VirtualMeetingTopicFormSet(BaseInlineFormSet):

    def clean(self):
        super().clean()
        seen = {}
        for form in self.forms:
            if not form.is_valid() or not form.cleaned_data:
                continue
            if self._should_delete_form(form):
                continue
            title = form.cleaned_data.get('title')
            if not title:
                continue
            key = title.casefold()
            if key in seen:
                raise forms.ValidationError(
                    'Já existe uma pauta com este título nesta assembleia.'
                )
            seen[key] = True