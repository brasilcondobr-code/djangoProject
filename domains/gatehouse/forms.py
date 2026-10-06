from django import forms
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils import timezone
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.db.models import Q

from core.services.validators import validate_date, validate_phone
from domains.condominium.models import Collaborator, Condominium
from domains.gatehouse.exceptions import OrderError
from domains.gatehouse.models import (
    Order, OrderPhoto, ServiceTransition, ServiceTransitionObject, Shift,
    ShiftScale, UsefulPhoneNumber,
)
from domains.gatehouse.services import OrderService
from domains.gatehouse.validators import IMAGE_EXTENSIONS, validate_order_file
from domains.parameters.models import CategoryPhone, ConciergeServiceCategory
from domains.residents.models import CondominiumUnit

SELECT_ATTRS = {
    "class": "servicetransition-select",
    "style": (
        "color: #212529 !important; background-color: #ffffff !important; "
        "border: 1px solid #ced4da !important;"
    ),
}


class ISODateInput(forms.DateInput):
    """DateInput HTML5 (type=date) que emite o value em ISO (YYYY-MM-DD).

    O DateInput padrao localiza a data (pt-BR: dd/mm/yyyy); o navegador ignora
    esse valor em <input type="date">, que exige ISO — resultando em campo
    vazio na tela e envio vazio no POST.
    """

    def format_value(self, value):
        if value in (None, ""):
            return None
        if isinstance(value, str):
            return value
        isoformat = getattr(value, "isoformat", None)
        if callable(isoformat):
            return isoformat()
        return super().format_value(value)


def active_queryset(model, instance, field_name, order_by="name"):
    """Queryset ordenado, sem inativos, preservando o registro selecionado na edição."""
    qs = model._default_manager.all()
    selected_pk = getattr(instance, "%s_id" % field_name, None)
    if selected_pk:
        qs = qs.filter(Q(is_active=True) | Q(pk=selected_pk))
    else:
        qs = qs.filter(is_active=True)
    return qs.order_by(order_by)


class ServiceTransitionForm(forms.ModelForm):
    """Formulário principal da passagem de serviço (02)."""

    class Meta:
        model = ServiceTransition
        fields = ("condominium", "collaboratorEnd", "collaboratorStart", "releaseDate", "observations")
        widgets = {
            "condominium": forms.Select(attrs=SELECT_ATTRS),
            "collaboratorEnd": forms.Select(attrs=SELECT_ATTRS),
            "collaboratorStart": forms.Select(attrs=SELECT_ATTRS),
            "releaseDate": ISODateInput(attrs={"type": "date"}),
            "observations": forms.Textarea(
                attrs={"rows": 3, "placeholder": "Observações da passagem de serviço"},
            ),
        }
        help_texts = {
            "condominium": "Condomínio da passagem de serviço",
            "collaboratorEnd": "Colaborador que está saindo do turno",
            "collaboratorStart": "Colaborador que está entrando no turno",
            "releaseDate": "Data de lançamento da passagem",
            "observations": "Observações adicionais (opcional)",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["condominium"].queryset = active_queryset(
            Condominium, self.instance, "condominium"
        )
        self.fields["collaboratorEnd"].queryset = active_queryset(
            Collaborator, self.instance, "collaboratorEnd"
        )
        self.fields["collaboratorStart"].queryset = active_queryset(
            Collaborator, self.instance, "collaboratorStart"
        )


class ServiceTransitionObjectForm(forms.ModelForm):
    """Formulário de cada objeto vinculado à passagem de serviço."""

    amountObj = forms.IntegerField(
        label="Quantidade",
        min_value=1,
        initial=1,
        help_text="Quantidade do item (mínimo 1)",
        widget=forms.NumberInput(attrs={"min": 1, "step": 1, "placeholder": "1"}),
    )

    class Meta:
        model = ServiceTransitionObject
        fields = ("categoryObj", "itemObj", "amountObj", "shiftDate")
        widgets = {
            "categoryObj": forms.Select(attrs=SELECT_ATTRS),
            "itemObj": forms.TextInput(attrs={"placeholder": "Nome do item"}),
            "shiftDate": ISODateInput(attrs={"type": "date"}),
        }
        help_texts = {
            "categoryObj": "Categoria do objeto",
            "itemObj": "Nome do item",
            "shiftDate": "Data do turno (padrão: data atual)",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["categoryObj"].queryset = active_queryset(
            ConciergeServiceCategory, self.instance, "categoryObj", order_by="description"
        )


class ShiftScaleForm(forms.Form):
    """Formulário para uma escala individual."""

    description = forms.CharField(
        label="Descrição",
        max_length=255,
        required=False,
        help_text="Descrição da escala",
    )
    shiftDate = forms.DateField(
        label="Data do Plantão",
        help_text="Data da escala",
        widget=ISODateInput(attrs={"type": "date"}),
    )
    startTime = forms.TimeField(
        label="Hora Inicial",
        help_text="Hora inicial da escala",
        widget=forms.TimeInput(attrs={"type": "time"}),
    )
    endTime = forms.TimeField(
        label="Hora Final",
        help_text="Hora final da escala",
        widget=forms.TimeInput(attrs={"type": "time"}),
    )
    is_active = forms.BooleanField(
        label="Ativo",
        initial=True,
        required=False,
    )


class ShiftForm(forms.ModelForm):
    """Formulário principal para o plantão."""

    class Meta:
        model = Shift
        fields = (
            "condominium",
            "collaborator",
            "startDate",
            "endDate",
            "title",
            "status",
            "is_active",
        )
        widgets = {
            "startDate": ISODateInput(attrs={"type": "date"}),
            "endDate": ISODateInput(attrs={"type": "date"}),
            "title": forms.TextInput(attrs={"placeholder": "Título do plantão"}),
        }
        help_texts = {
            "condominium": "Condomínio associado ao plantão",
            "collaborator": "Colaborador do plantão",
            "startDate": "Data inicial do plantão",
            "endDate": "Data final do plantão",
            "title": "Título do plantão (opcional)",
            "status": "Status do plantão",
            "is_active": "Indica se o plantão está ativo",
        }

    def clean(self):
        """Validações cruzadas no formulário."""
        cleaned_data = super().clean()
        startDate = cleaned_data.get("startDate")
        endDate = cleaned_data.get("endDate")

        if startDate and endDate and startDate > endDate:
            raise forms.ValidationError(
                "A data final deve ser maior ou igual à data inicial."
            )

        return cleaned_data


class UsefulPhoneNumberForm(forms.ModelForm):
    """Formulário do módulo 03. Telefones Úteis."""

    class Meta:
        model = UsefulPhoneNumber
        fields = (
            "condominium",
            "categoryPhone",
            "releaseDate",
            "name",
            "phone1",
            "phone2",
            "phone3",
            "phone4",
            "phone5",
            "observations",
            "is_active",
        )
        widgets = {
            "condominium": forms.Select(attrs=SELECT_ATTRS),
            "categoryPhone": forms.Select(attrs=SELECT_ATTRS),
            "releaseDate": ISODateInput(attrs={"type": "date"}),
            "name": forms.TextInput(attrs={"placeholder": "Nome do telefone útil"}),
            "phone1": forms.TextInput(attrs={"class": "mask-phone", "placeholder": "(99) 99999-9999"}),
            "phone2": forms.TextInput(attrs={"class": "mask-phone", "placeholder": "(99) 99999-9999"}),
            "phone3": forms.TextInput(attrs={"class": "mask-phone", "placeholder": "(99) 99999-9999"}),
            "phone4": forms.TextInput(attrs={"class": "mask-phone", "placeholder": "(99) 99999-9999"}),
            "phone5": forms.TextInput(attrs={"class": "mask-phone", "placeholder": "(99) 99999-9999"}),
            "observations": forms.Textarea(
                attrs={"rows": 3, "placeholder": "Observações (opcional)"},
            ),
        }
        help_texts = {
            "condominium": "Condomínio do telefone útil",
            "categoryPhone": "Categoria do telefone",
            "releaseDate": "Data de lançamento do registro",
            "name": "Nome de até 255 caracteres",
            "phone1": "Digite no seguinte formato: (99) 99999-9999",
            "phone2": "Digite no seguinte formato: (99) 99999-9999",
            "phone3": "Digite no seguinte formato: (99) 99999-9999",
            "phone4": "Digite no seguinte formato: (99) 99999-9999",
            "phone5": "Digite no seguinte formato: (99) 99999-9999",
            "observations": "Observações adicionais (opcional)",
            "is_active": "Indica se o telefone está ativo",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Em paginas de visualizacao (sem permissao de edicao) o Django monta o
        # form com todos os campos excluidos — entao nao ha o que configurar.
        if "condominium" in self.fields:
            self.fields["condominium"].queryset = active_queryset(
                Condominium, self.instance, "condominium"
            )
        if "categoryPhone" in self.fields:
            self.fields["categoryPhone"].queryset = active_queryset(
                CategoryPhone, self.instance, "categoryPhone", order_by="name"
            )
        # categoryPhone e releaseDate sao obrigatorios no form embora sejam
        # nullable no banco (ver divergencia de requisitos do modulo 03).
        if "categoryPhone" in self.fields:
            self.fields["categoryPhone"].required = True
        if "releaseDate" in self.fields:
            self.fields["releaseDate"].required = True

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get("name")
        if isinstance(name, str):
            cleaned_data["name"] = name.strip()

        release_date = cleaned_data.get("releaseDate")
        if release_date and not validate_date(release_date):
            raise forms.ValidationError("Informe uma data de lançamento válida.")

        for field in ("phone1", "phone2", "phone3", "phone4", "phone5"):
            phone = cleaned_data.get(field)
            if phone and not validate_phone(phone):
                raise forms.ValidationError(
                    "Telefone inválido no campo %s. Use o formato: (99) 99999-9999."
                    % self.fields[field].label
                )

        condominium = cleaned_data.get("condominium")
        category = cleaned_data.get("categoryPhone")
        if condominium and category and cleaned_data.get("name") and release_date:
            duplicated = UsefulPhoneNumber.objects.filter(
                condominium=condominium,
                categoryPhone=category,
                name=cleaned_data.get("name"),
                releaseDate=release_date,
            ).exclude(pk=self.instance.pk if self.instance.pk else None)
            if duplicated.exists():
                raise forms.ValidationError(
                    "Já existe um telefone útil com os mesmos condomínio, "
                    "categoria, nome e data de lançamento."
                )
        return cleaned_data


class OrderFileInput(forms.ClearableFileInput):
    """Arquivo da encomenda com botão 'Foto' (câmera) ao lado.

    O input de fotos (name=photos, múltiplo) vive neste template; as fotos
    chegam por request.FILES.getlist("photos") e são validadas/persistidas
    pelo OrderForm — não existe campo de formulário 'photos'.
    """

    template_name = "gatehouse/order_file_input.html"


class OrderForm(forms.ModelForm):
    """Formulário do módulo 04. Encomendas."""

    class Meta:
        model = Order
        fields = (
            "unit",
            "releaseDate",
            "documentNumber",
            "fileImage",
            "observations",
            "is_active",
        )
        widgets = {
            "unit": forms.Select(attrs=SELECT_ATTRS),
            "releaseDate": ISODateInput(attrs={"type": "date"}),
            "documentNumber": forms.TextInput(
                attrs={"placeholder": "Ex.: 12345 ou NF-2026/001"},
            ),
            "fileImage": OrderFileInput(),
            "observations": forms.Textarea(
                attrs={"rows": 3, "placeholder": "Observações (opcional)"},
            ),
        }
        labels = {
            "unit": "Unidade",
            "releaseDate": "Data de lançamento",
            "documentNumber": "Número do documento",
            "fileImage": "Arquivo",
            "observations": "Observações",
            "is_active": "Ativo",
        }
        help_texts = {
            "unit": "Unidade de destino da encomenda",
            "releaseDate": "Data de chegada da encomenda (preenchida pelo servidor na criação)",
            "documentNumber": "Conteúdo numérico ou alfanumérico, sem máscara (opcional)",
            "fileImage": "Formatos aceitos: .jpg, .jpeg, .png, .pdf. Máx: 10 MB",
            "observations": "Observações adicionais (opcional)",
            "is_active": "Indica se a encomenda está ativa",
        }
        error_messages = {
            "unit": {
                "required": "A unidade é obrigatória.",
                "invalid_choice": "Selecione uma unidade válida.",
            },
            "fileImage": {
                "required": "O arquivo é obrigatório.",
            },
            "releaseDate": {
                "invalid": "Informe uma data de lançamento válida.",
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["unit"].queryset = (
            CondominiumUnit.objects.select_related("condominium").order_by(
                "tower", "unit_number"
            )
        )
        if not self.instance.pk:
            # Criacao: data somente leitura no navegador e preenchida pelo
            # servidor quando o valor nao e enviado.
            self.fields["releaseDate"].widget.attrs["readonly"] = "readonly"
            self.fields["releaseDate"].initial = timezone.localdate()
            self.fields["releaseDate"].required = False
        else:
            self.fields["releaseDate"].required = True
            self.fields["fileImage"].help_text = self._build_file_help_text()

    def _build_file_help_text(self):
        """Help do campo Arquivo + lista de fotos já anexadas (edição)."""
        base = "Formatos aceitos: .jpg, .jpeg, .png, .pdf. Máx: 10 MB"
        photos = list(self.instance.photos.all())
        if not photos:
            return base
        items = mark_safe(
            "".join(
                format_html(
                    '<span class="order-photo-item" style="display:inline-block;'
                    ' margin:4px; text-align:center;">'
                    '<a href="{0}" target="_blank" rel="noopener">'
                    '<img src="{0}" alt="Foto da encomenda" style="max-width:80px;'
                    ' max-height:80px;"></a><br>'
                    '<label><input type="checkbox" name="photo_delete"'
                    ' value="{1}"> Remover</label></span>',
                    photo.file.url,
                    photo.pk,
                )
                for photo in photos
            )
        )
        return format_html(
            '{}<div class="order-photo-list" style="margin-top:4px;">'
            "<strong>Fotos anexadas:</strong>{}</div>",
            base,
            items,
        )

    @staticmethod
    def _uploaded_photos(form_files):
        """Lista dos arquivos enviados no input 'photos' (aceita dict simples)."""
        files = form_files or {}
        if hasattr(files, "getlist"):
            return files.getlist("photos")
        value = files.get("photos") or []
        return value if isinstance(value, list) else [value]

    @staticmethod
    def _deleted_photo_ids(form_data):
        """Ids marcados para remoção no checkbox 'photo_delete'."""
        data = form_data or {}
        if hasattr(data, "getlist"):
            return data.getlist("photo_delete")
        value = data.get("photo_delete") or []
        return value if isinstance(value, list) else [value]

    def clean_releaseDate(self):
        release_date = self.cleaned_data.get("releaseDate")
        if not release_date:
            if self.instance.pk:
                raise forms.ValidationError(
                    "A data de lançamento é obrigatória."
                )
            release_date = timezone.localdate()
        if not validate_date(release_date):
            raise forms.ValidationError("Informe uma data de lançamento válida.")
        return release_date

    def clean_documentNumber(self):
        document_number = self.cleaned_data.get("documentNumber")
        if document_number is None:
            return None
        document_number = document_number.strip()
        if not document_number:
            return None
        return document_number

    def clean_fileImage(self):
        file = self.cleaned_data.get("fileImage")
        if not file:
            # Arquivo opcional: a exigencia (arquivo OU ao menos uma foto)
            # e conferida em clean().
            return None
        from django.core.files.uploadedfile import UploadedFile
        if isinstance(file, UploadedFile):
            validate_order_file(file)
        return file

    def clean(self):
        cleaned_data = super().clean()
        new_photos = self._uploaded_photos(getattr(self, "files", None))
        for photo in new_photos:
            try:
                validate_order_file(photo, extensions=IMAGE_EXTENSIONS)
            except DjangoValidationError as exc:
                self.add_error("fileImage", "; ".join(exc.messages))
                break
        has_file = bool(cleaned_data.get("fileImage"))
        has_existing_evidence = bool(
            self.instance.pk
            and (
                self.instance.fileImage
                or self.instance.photos.exists()
            )
        )
        if not (has_file or new_photos or has_existing_evidence):
            self.add_error(
                "fileImage", "Anexe o arquivo ou tire ao menos uma foto."
            )
        if cleaned_data.get("unit") and cleaned_data.get("releaseDate"):
            try:
                OrderService.check_duplicate(
                    cleaned_data,
                    instance=self.instance if self.instance.pk else None,
                )
            except OrderError as exc:
                raise forms.ValidationError(str(exc))
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=commit)
        if commit:
            self.persist_photos(instance)
        return instance

    def persist_photos(self, order, user=None):
        """Cria as fotos enviadas e remove as marcadas (após o pedido salvo).

        No admin o form é salvo com commit=False; a chamada acontece em
        ``OrderAdmin.save_related`` com o usuário da requisição.
        """
        for photo_id in self._deleted_photo_ids(self.data):
            OrderPhoto.objects.filter(order=order, pk=photo_id).delete()
        for photo in self._uploaded_photos(getattr(self, "files", None)):
            OrderPhoto.objects.create(order=order, file=photo, created_by=user)
