from django import forms
from ckeditor.widgets import CKEditorWidget

from domains.administrative.models.virtual_meeting import VirtualMeeting
from domains.administrative.services.virtual_meeting_participant_service import (
    VirtualMeetingParticipantService,
)
from domains.administrative.services.virtual_meeting_service import VirtualMeetingService
from domains.administrative.validators import (
    is_html_content_empty,
    validate_rich_html_description,
)
from domains.email_service.models import ConnectionStatus, SMTPConfiguration
from domains.parameters.models import AssemblyStatus, ResidentType
from domains.residents.models import Resident


class VirtualMeetingForm(forms.ModelForm):

    REQUIRED_FIELDS = {
        'description',
        'notice_meeting_title',
        'notice_meeting_description',
        'email_smtp_configuration',
        'connection_status',
    }

    participating_groups = forms.ModelChoiceField(
        queryset=ResidentType.objects.none(),
        required=True,
        widget=forms.Select(
            attrs={
                'class': 'form-control select2-dependent-source',
                'data-participants-url': '/administrative/ajax/participants-by-group/',
                'data-placeholder': 'Selecione o grupo de participantes',
                'aria-label': 'Grupos participantes',
            },
        ),
        label='Grupos participantes',
        error_messages={
            'required': 'Selecione ao menos um grupo de participantes.',
        },
    )

    participating_resident = forms.ModelMultipleChoiceField(
        queryset=Resident.objects.none(),
        required=True,
        widget=forms.SelectMultiple(
            attrs={
                'class': 'form-control select2-dependent-target',
                'data-placeholder': 'Selecione os participantes',
                'aria-label': 'Participantes',
            },
        ),
        label='Participantes',
        help_text='Os participantes são carregados de acordo com os grupos selecionados.',
        error_messages={
            'required': 'Selecione ao menos um participante.',
        },
    )

    class Meta:
        model = VirtualMeeting
        fields = '__all__'
        widgets = {
            'condominium': forms.Select(
                attrs={'class': 'form-control'},
            ),
            'voting_type': forms.Select(
                attrs={'class': 'form-control'},
            ),
            'title': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Informe o título da assembleia',
                },
            ),
            'location': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Informe o local (opcional)',
                },
            ),
            'meeting_date_time_start': forms.DateTimeInput(
                attrs={
                    'class': 'form-control',
                    'type': 'datetime-local',
                },
                format='%Y-%m-%dT%H:%M',
            ),
            'meeting_date_time_end': forms.DateTimeInput(
                attrs={
                    'class': 'form-control',
                    'type': 'datetime-local',
                },
                format='%Y-%m-%dT%H:%M',
            ),
            'meeting_date_time_voting_begins': forms.DateTimeInput(
                attrs={
                    'class': 'form-control',
                    'type': 'datetime-local',
                },
                format='%Y-%m-%dT%H:%M',
            ),
            'meeting_date_time_voting_end': forms.DateTimeInput(
                attrs={
                    'class': 'form-control',
                    'type': 'datetime-local',
                },
                format='%Y-%m-%dT%H:%M',
            ),
            'meeting_date_time_send_mail': forms.DateTimeInput(
                attrs={
                    'class': 'form-control',
                    'type': 'datetime-local',
                },
                format='%Y-%m-%dT%H:%M',
            ),
            'president': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Informe o nome do presidente',
                },
            ),
            'secretary': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Informe o nome do secretário',
                },
            ),
            'video_conference_link': forms.URLInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'https://...',
                },
            ),
            'description': CKEditorWidget(),
            'notice_meeting_title': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Informe o título do edital de convocação',
                },
            ),
            'notice_meeting_date_time': forms.DateTimeInput(
                attrs={
                    'class': 'form-control',
                    'type': 'datetime-local',
                },
                format='%Y-%m-%dT%H:%M',
            ),
            'notice_meeting_description': CKEditorWidget(),
            'notice_meeting_send_email_participants': forms.CheckboxInput(
                attrs={'class': 'form-check-input'},
            ),
            'meeting_status': forms.Select(
                attrs={'class': 'form-control'},
            ),
            'ban_those_in_default_from_voting': forms.CheckboxInput(
                attrs={'class': 'form-check-input'},
            ),
            'hide_results_from_participants_during_voting': forms.CheckboxInput(
                attrs={'class': 'form-check-input'},
            ),
            'release_the_agenda_for_vote': forms.CheckboxInput(
                attrs={'class': 'form-check-input'},
            ),
            'allow_comments': forms.CheckboxInput(
                attrs={'class': 'form-check-input'},
            ),
            'show_comments': forms.CheckboxInput(
                attrs={'class': 'form-check-input'},
            ),
            'allow_replies_to_comments': forms.CheckboxInput(
                attrs={'class': 'form-check-input'},
            ),
            'show_replies_to_comments': forms.CheckboxInput(
                attrs={'class': 'form-check-input'},
            ),
            'participating_vote_unit': forms.CheckboxInput(
                attrs={'class': 'form-check-input'},
            ),
            'email_smtp_configuration': forms.Select(
                attrs={'class': 'form-control'},
            ),
            'connection_status': forms.Select(
                attrs={'class': 'form-control'},
            ),
            'email_log': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 4,
                    'readonly': 'readonly',
                },
            ),
        }
        labels = {
            'condominium': 'Condomínio',
            'title': 'Título',
            'voting_type': 'Tipo de Votação',
            'location': 'Local',
            'meeting_date_time_start': 'Início da assembleia',
            'meeting_date_time_end': 'Término da assembleia',
            'meeting_date_time_voting_begins': 'Início da votação',
            'meeting_date_time_voting_end': 'Término da votação',
            'meeting_date_time_send_mail': 'Data/Hora - Envio do E-mail',
            'president': 'Presidente',
            'secretary': 'Secretário',
            'video_conference_link': 'Link da videoconferência',
            'description': 'Descrição',
            'notice_meeting_title': 'Título do Edital de Convocação',
            'notice_meeting_date_time': 'Data da convocação',
            'notice_meeting_description': 'Descrição do edital',
            'notice_meeting_send_email_participants': 'Enviar e-mail aos participantes',
            'meeting_status': 'Status da assembleia',
            'ban_those_in_default_from_voting': 'Impedir inadimplentes de votar',
            'hide_results_from_participants_during_voting': 'Ocultar resultados durante a votação',
            'release_the_agenda_for_vote': 'Liberar a pauta para votação',
            'allow_comments': 'Permitir comentários',
            'show_comments': 'Exibir comentários',
            'allow_replies_to_comments': 'Permitir respostas aos comentários',
            'show_replies_to_comments': 'Exibir respostas aos comentários',
            'participating_groups': 'Grupos participantes',
            'participating_vote_unit': 'Voto principal por unidade?',
            'participating_resident': 'Participantes',
            'email_smtp_configuration': 'Configuração SMTP',
            'connection_status': 'Email Status',
            'email_log': 'Email Logs',
        }
        help_texts = {
            'video_conference_link': 'Informe apenas se a assembleia for virtual.',
            'meeting_status': 'Preenchido automaticamente na inclusão.',
        }
        error_messages = {
            'condominium': {
                'required': 'Selecione o condomínio.',
            },
            'title': {
                'required': 'Informe o título da assembleia.',
            },
            'meeting_date_time_start': {
                'required': 'Informe o início da assembleia.',
                'invalid': 'Informe uma data e hora válidas.',
            },
            'meeting_date_time_end': {
                'required': 'Informe o término da assembleia.',
                'invalid': 'Informe uma data e hora válidas.',
            },
            'meeting_date_time_voting_begins': {
                'required': 'Informe o início da votação.',
                'invalid': 'Informe uma data e hora válidas.',
            },
            'meeting_date_time_voting_end': {
                'required': 'Informe o término da votação.',
                'invalid': 'Informe uma data e hora válidas.',
            },
            'meeting_date_time_send_mail': {
                'required': 'Informe a data de envio do e-mail.',
                'invalid': 'Informe uma data válida.',
            },
            'president': {
                'required': 'Informe o presidente da assembleia.',
            },
            'secretary': {
                'required': 'Informe o secretário da assembleia.',
            },
            'description': {
                'required': 'Informe a descrição da assembleia.',
            },
            'notice_meeting_title': {
                'required': 'Informe o título do edital de convocação.',
            },
            'notice_meeting_date_time': {
                'required': 'Informe a data da convocação.',
                'invalid': 'Informe uma data e hora válidas.',
            },
            'notice_meeting_description': {
                'required': 'Informe a descrição do edital.',
            },
            'email_smtp_configuration': {
                'required': 'Selecione a configuração SMTP.',
            },
            'connection_status': {
                'required': 'Selecione o status do e-mail.',
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if 'meeting_status' in self.fields:
            self.fields['meeting_status'].queryset = AssemblyStatus.objects.all().order_by('description')
            self.fields['meeting_status'].required = False

            if not self.instance.pk:
                self.fields['meeting_status'].widget.attrs['readonly'] = True
                try:
                    self.fields['meeting_status'].initial = (
                        VirtualMeetingService.get_pending_status()
                    )
                except Exception:
                    pass

        if 'created_by_user' in self.fields:
            self.fields['created_by_user'].required = False
            self.fields['created_by_user'].widget.attrs['class'] = 'form-control'

        if 'participating_groups' in self.fields:
            self.fields['participating_groups'].queryset = (
                ResidentType.objects.filter(is_active=True).order_by('description')
            )

        if 'participating_resident' in self.fields:
            if self.is_bound:
                field_name = self.add_prefix('participating_resident')
                if hasattr(self.data, 'getlist'):
                    submitted_ids = self.data.getlist(field_name)
                else:
                    submitted_ids = self.data.get(field_name, [])
                    if submitted_ids and not isinstance(submitted_ids, (list, tuple)):
                        submitted_ids = [submitted_ids]
                self.fields['participating_resident'].queryset = (
                    Resident.objects.filter(pk__in=submitted_ids)
                )
            elif self.instance and self.instance.pk:
                self.fields['participating_resident'].queryset = (
                    self.instance.participating_resident.all()
                )

        if 'email_smtp_configuration' in self.fields:
            self.fields['email_smtp_configuration'].queryset = (
                SMTPConfiguration.objects.filter(is_active=True).order_by('description')
            )

        if 'connection_status' in self.fields:
            if not self.is_bound and not self.instance.pk:
                pendente = ConnectionStatus.objects.filter(
                    status__iexact='Pendente',
                ).first()
                if pendente:
                    self.fields['connection_status'].initial = pendente

        for field_name in self.REQUIRED_FIELDS:
            if field_name in self.fields:
                self.fields[field_name].required = True

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if not title or not title.strip():
            raise forms.ValidationError('Informe o título da assembleia.')
        return title.strip()

    def clean_president(self):
        president = self.cleaned_data.get('president')
        if not president or not president.strip():
            raise forms.ValidationError('Informe o presidente da assembleia.')
        return president.strip()

    def clean_secretary(self):
        secretary = self.cleaned_data.get('secretary')
        if not secretary or not secretary.strip():
            raise forms.ValidationError('Informe o secretário da assembleia.')
        return secretary.strip()

    def clean_description(self):
        description = self.cleaned_data.get('description')
        if description:
            validate_rich_html_description(description)
            if is_html_content_empty(description):
                raise forms.ValidationError('Informe a descrição da assembleia.')
        return description

    def clean_notice_meeting_title(self):
        title = self.cleaned_data.get('notice_meeting_title')
        if title:
            title = title.strip()
            if not title:
                raise forms.ValidationError('Informe o título do edital de convocação.')
        return title

    def clean_notice_meeting_description(self):
        description = self.cleaned_data.get('notice_meeting_description')
        if description:
            validate_rich_html_description(description)
            if is_html_content_empty(description):
                raise forms.ValidationError('Informe a descrição do edital.')
        return description

    def clean(self):
        cleaned_data = super().clean()

        start = cleaned_data.get('meeting_date_time_start')
        end = cleaned_data.get('meeting_date_time_end')
        voting_begins = cleaned_data.get('meeting_date_time_voting_begins')
        voting_end = cleaned_data.get('meeting_date_time_voting_end')
        notice = cleaned_data.get('notice_meeting_date_time')

        if start and end and end <= start:
            self.add_error(
                'meeting_date_time_end',
                'O término da assembleia deve ser maior que o início.',
            )

        if voting_begins and voting_end and voting_end <= voting_begins:
            self.add_error(
                'meeting_date_time_voting_end',
                'O término da votação deve ser maior que o início da votação.',
            )

        if start and voting_begins and voting_begins < start:
            self.add_error(
                'meeting_date_time_voting_begins',
                'O início da votação não pode ser anterior ao início da assembleia.',
            )

        if end and voting_end and voting_end > end:
            self.add_error(
                'meeting_date_time_voting_end',
                'O término da votação não pode ser posterior ao término da assembleia.',
            )

        if notice and start and notice >= start:
            self.add_error(
                'notice_meeting_date_time',
                'A data de convocação deve ser anterior ao início da assembleia.',
            )

        send_mail = cleaned_data.get('meeting_date_time_send_mail')
        voting_begins = cleaned_data.get('meeting_date_time_voting_begins')
        if send_mail and voting_begins and send_mail >= voting_begins:
            self.add_error(
                'meeting_date_time_send_mail',
                'A data/hora de envio do e-mail deve ser anterior ao início da votação.',
            )

        participating_groups = cleaned_data.get('participating_groups')
        participating_resident = cleaned_data.get('participating_resident')

        if participating_resident and not participating_groups:
            self.add_error(
                'participating_resident',
                'Selecione ao menos um grupo de participantes.',
            )
        elif participating_resident and participating_groups:
            invalid_ids = VirtualMeetingParticipantService.get_invalid_participant_ids(
                participant_ids=[r.pk for r in participating_resident],
                group_ids=[participating_groups.pk],
                condominium=cleaned_data.get('condominium'),
            )
            if invalid_ids:
                invalid_names = ', '.join(
                    Resident.objects.filter(pk__in=invalid_ids).values_list(
                        'name', flat=True,
                    )
                )
                self.add_error(
                    'participating_resident',
                    'Os seguintes participantes não pertencem aos grupos selecionados: '
                    f'{invalid_names}.',
                )

        return cleaned_data