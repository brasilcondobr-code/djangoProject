import os

from django import forms
from django.conf import settings
from django.contrib import admin, messages
from django.contrib.staticfiles import finders
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.templatetags.static import static
from django.urls import path
from django.utils import timezone
from django.utils.formats import date_format, number_format
from django.utils.html import format_html, format_html_join

from domains.financial.exceptions import CollectionError
from domains.financial.repositories import FinancialRepository
from domains.residents.models import Resident

from .forms import (
    CollectionCreditForm,
    CollectionCreditFormSet,
    CollectionForm,
    CollectionPaymentForm,
    NewReleaseForm,
)
from .labels import paymaster_label
from .models import (
    Agreement, PaymentSlip, Cash, Collection, CollectionCredit, Shopping,
    Loan, NewRelease, Payment, Apportionment, Receipt, BankTransfer
)
from .services import CollectionService, NewReleaseService


def _static_with_mtime(path):
    """URL estática com ``?v=<mtime>`` para invalidar o cache do navegador.

    Em desenvolvimento o Django serve arquivos estáticos sem hash. O mtime
    força o navegador a buscar a versão nova sempre que o arquivo mudar. Em
    produção, ``static()`` continua aplicando o hash do ManifestStaticFilesStorage.
    """
    url = static(path)
    try:
        absolute_path = finders.find(path)
        if absolute_path:
            url = f"{url}?v={int(os.path.getmtime(absolute_path))}"
    except (OSError, ValueError):
        pass
    return url


@admin.register(Agreement)
class AgreementAdmin(admin.ModelAdmin):
    pass

@admin.register(PaymentSlip)
class PaymentSlipAdmin(admin.ModelAdmin):
    pass

@admin.register(Cash)
class CashAdmin(admin.ModelAdmin):
    pass

@admin.register(Shopping)
class ShoppingAdmin(admin.ModelAdmin):
    pass

@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    pass


class ScopeMonthFilter(admin.SimpleListFilter):
    """Filtro de Competência exibido no formato ``MM-AAAA``."""

    title = "Competência"
    parameter_name = "scope"

    def lookups(self, request, model_admin):
        scopes = (
            model_admin.get_queryset(request)
            .exclude(scope__isnull=True)
            .values_list("scope", flat=True)
            .distinct()
            .order_by("-scope")
        )
        seen = set()
        lookups = []
        for scope in scopes:
            label = scope.strftime("%m-%Y")
            if label in seen:
                continue
            seen.add(label)
            lookups.append((label, label))
        return tuple(lookups)

    def queryset(self, request, queryset):
        value = self.value()
        if not value:
            return queryset
        try:
            month, year = value.split("-")
            return queryset.filter(
                scope__year=int(year),
                scope__month=int(month),
            )
        except (AttributeError, TypeError, ValueError):
            return queryset


class CollectionCreditInline(admin.TabularInline):
    """Créditos da cobrança, recalculados no ``save_formset``."""

    model = CollectionCredit
    form = CollectionCreditForm
    formset = CollectionCreditFormSet
    extra = 1
    fields = ("financialTransaction", "creditDate", "amountCredit")
    verbose_name = "Crédito"
    verbose_name_plural = "Créditos"

    def has_add_permission(self, request, obj=None):
        if obj is not None and not CollectionService.can_settle(obj):
            return False
        return super().has_add_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj is not None and not CollectionService.can_settle(obj):
            return False
        return super().has_delete_permission(request, obj)

    def get_readonly_fields(self, request, obj=None):
        if obj is not None and not CollectionService.can_settle(obj):
            return [field.name for field in self.model._meta.fields]
        return super().get_readonly_fields(request, obj)


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    """Administração do módulo 04. Cobranças.

    A edição é permitida somente em ``A vencer`` e com a cobrança ativa. O
    saldo, o total, o status e a auditoria são somente leitura. As ações em
    lote revalidam cada item no servidor e reportam ID e motivo.
    """

    form = CollectionForm
    inlines = (CollectionCreditInline,)
    list_display = (
        "id",
        "condominium",
        "billingDate",
        "scope_display",
        "dueDate",
        "total_display",
        "balance_display",
        "status_display",
        "is_active",
    )
    list_display_links = ("id",)
    list_filter = (
        "status",
        ScopeMonthFilter,
        "is_active",
        "condominium__condominium",
    )
    search_fields = (
        "condominium__unit_number",
        "condominium__tower",
        "condominium__condominium__name",
    )
    autocomplete_fields = ("condominium",)
    readonly_fields = (
        "billingDate",
        "discountAmount",
        "fineAmount",
        "interestAmount",
        "chargesAmount",
        "totalAmount",
        "balance",
        "status_display",
        "errorStatus",
        "composition_table",
        "created_by",
        "updated_by",
        "created_at",
        "updated_at",
    )
    list_select_related = (
        "condominium",
        "condominium__condominium",
        "created_by",
        "updated_by",
    )
    list_per_page = 25
    ordering = ("-billingDate", "-id")
    actions = (
        "atualizar_cobranca",
        "pagamento",
        "excluir_cobrancas",
    )
    save_on_top = True

    # Jazzmin: a aba Auditoria deve ser a última, depois do inline Créditos.
    jazzmin_section_order = (
        "Principal",
        "Composição",
        "Créditos",
        "Auditoria",
    )

    fieldsets = (
        (
            "Principal",
            {
                "fields": (
                    "condominium",
                    "billingDate",
                    "scope",
                    "originalValue",
                    "discountPercent",
                    "discountAmount",
                    "penaltyPercent",
                    "fineAmount",
                    "feesPercent",
                    "interestAmount",
                    "chargesPercent",
                    "chargesAmount",
                    "discountDeadline",
                    "dueDate",
                    "totalAmount",
                    "balance",
                ),
            },
        ),
        (
            "Composição",
            {
                "fields": ("composition_table",),
            },
        ),
        (
            "Auditoria",
            {
                "fields": (
                    "is_active",
                    "status_display",
                    "errorStatus",
                    "created_by",
                    "updated_by",
                    "created_at",
                    "updated_at",
                ),
            },
        ),
    )

    @property
    def media(self):
        extra = "" if settings.DEBUG else ".min"
        return super().media + forms.Media(
            js=(
                f"admin/js/vendor/jquery/jquery{extra}.js",
                "js/jquery.mask.min.js",
                "admin/js/jquery.init.js",
                _static_with_mtime("js/collection_admin.js"),
            ),
        )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            "condominium",
            "condominium__condominium",
            "created_by",
            "updated_by",
        )

    def has_change_permission(self, request, obj=None):
        if obj is not None and not CollectionService.can_edit(obj):
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj is not None:
            if not CollectionService.can_delete(obj):
                return False
            if (
                obj.new_releases.exists()
                or obj.payments.exists()
                or obj.credits.exists()
            ):
                return False
        return super().has_delete_permission(request, obj)

    def get_actions(self, request):
        actions = super().get_actions(request)
        actions.pop("delete_selected", None)
        return actions

    def save_model(self, request, obj, form, change):
        CollectionService.save_instance(
            obj,
            user=request.user,
            is_new=not change,
        )

    def delete_model(self, request, obj):
        CollectionService.delete_instance(obj, user=request.user)

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            if not CollectionService.can_delete(obj):
                raise PermissionDenied(
                    "Não é permitido excluir cobranças que não estejam em "
                    "'A vencer'."
                )
            if (
                obj.new_releases.exists()
                or obj.payments.exists()
                or obj.credits.exists()
            ):
                raise PermissionDenied(
                    "Não é permitido excluir cobranças com lançamentos, "
                    "créditos ou pagamentos vinculados."
                )
        super().delete_queryset(request, queryset)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in formset.deleted_objects:
            instance.delete()
        for instance in instances:
            if isinstance(instance, CollectionCredit):
                if instance.pk is None:
                    instance.created_by = request.user
                instance.updated_by = request.user
            instance.save()
        formset.save_m2m()

        if form.instance.pk:
            CollectionService.recalculate(
                form.instance,
                user=request.user,
            )

    @admin.action(
        description="Atualizar Cobrança",
        permissions=("change",),
    )
    def atualizar_cobranca(self, request, queryset):
        results = CollectionService.update_collections(
            list(queryset.values_list("pk", flat=True)),
            user=request.user,
        )
        self._report_results(request, results, "atualizada(s)")

    @admin.action(
        description="Excluir cobranças selecionadas",
        permissions=("delete",),
    )
    def excluir_cobrancas(self, request, queryset):
        results = CollectionService.delete_many(
            list(queryset.values_list("pk", flat=True)),
            user=request.user,
        )
        self._report_results(request, results, "excluída(s)")

    @admin.action(
        description="Pagamento",
        permissions=("change",),
    )
    def pagamento(self, request, queryset):
        selected_ids = request.POST.getlist("_selected_action") or [
            str(pk) for pk in queryset.values_list("pk", flat=True)
        ]
        collections = Collection.objects.filter(
            pk__in=selected_ids
        ).select_related(
            "condominium",
            "condominium__condominium",
        ).order_by("id")

        if "apply" in request.POST:
            form = CollectionPaymentForm(
                request.POST,
                collections=collections,
            )
            if form.is_valid():
                data = form.cleaned_data
                try:
                    CollectionService.register_payment(
                        data["collection"],
                        data["financialTransaction"],
                        data["dateReceived"],
                        data["amountReceived"],
                        user=request.user,
                    )
                except CollectionError as exc:
                    self.message_user(
                        request,
                        str(exc),
                        messages.ERROR,
                    )
                else:
                    self.message_user(
                        request,
                        "Pagamento registrado para a cobrança "
                        f"#{data['collection'].pk}.",
                        messages.SUCCESS,
                    )
                    return redirect(
                        "admin:financial_collection_changelist"
                    )
        else:
            form = CollectionPaymentForm(
                collections=collections,
                initial={"dateReceived": timezone.localdate()},
            )

        context = {
            **self.admin_site.each_context(request),
            "title": "Registrar pagamento",
            "form": form,
            "selected_ids": selected_ids,
            "opts": self.model._meta,
            "action": "pagamento",
        }
        return TemplateResponse(
            request,
            "admin/financial/collection_payment.html",
            context,
        )

    def _report_results(self, request, results, success_label):
        successes = [
            result["id"] for result in results if result["success"]
        ]
        failures = [
            result for result in results if not result["success"]
        ]

        if successes:
            ids = ", ".join(str(pk) for pk in successes)
            self.message_user(
                request,
                f"{len(successes)} registro(s) {success_label}: "
                f"IDs {ids}.",
                messages.SUCCESS,
            )

        for failure in failures:
            self.message_user(
                request,
                f"ID {failure['id']}: {failure['reason']}",
                messages.WARNING,
            )

    @admin.display(description="Competência", ordering="scope")
    def scope_display(self, obj):
        if not obj.scope:
            return "-"
        return date_format(obj.scope, "F/Y").capitalize()

    @admin.display(description="Valor total", ordering="totalAmount")
    def total_display(self, obj):
        if obj.totalAmount is None:
            return "-"
        return number_format(obj.totalAmount, 2, force_grouping=True)

    @admin.display(description="Saldo", ordering="balance")
    def balance_display(self, obj):
        return number_format(obj.balance, 2, force_grouping=True)

    @admin.display(description="Status", ordering="status")
    def status_display(self, obj=None):
        if obj is None:
            return Collection.Status.TO_BE_WON.label
        return obj.get_status_display()

    @admin.display(description="Lançamentos vinculados")
    def composition_table(self, obj=None):
        if obj is None or not obj.pk:
            return "-"

        releases = FinancialRepository.get_collection_new_releases(obj.pk)
        if not releases:
            return format_html(
                '<p class="text-muted mb-0">{}</p>',
                "Nenhum lançamento vinculado.",
            )

        body = format_html_join(
            "",
            (
                "<tr><td>{}</td>"
                '<td><span class="text-truncate d-inline-block" '
                'style="max-width: 220px" title="{}">{}</span></td>'
                "<td>{}</td><td>{}</td>"
                '<td><span class="text-truncate d-inline-block" '
                'style="max-width: 220px" title="{}">{}</span></td>'
                "<td>{}</td><td>{}</td></tr>"
            ),
            (
                (
                    release.pk,
                    release.condominium,
                    release.condominium,
                    date_format(release.launchDate, "d/m/Y"),
                    release.scope.strftime("%m/%Y") if release.scope else "-",
                    release.title,
                    release.title,
                    release.get_launchType_display(),
                    (
                        number_format(
                            release.value, 2, force_grouping=True
                        )
                        if release.value is not None
                        else "-"
                    ),
                )
                for release in releases
            ),
        )

        return format_html(
            '<div class="table-responsive"><table class="table table-sm '
            'table-striped align-middle mb-0"><thead><tr>'
            "<th>ID</th><th>Condomínio/Unidade</th><th>Data</th>"
            "<th>Competência</th><th>Título</th><th>Tipo</th><th>Valor</th>"
            "</tr></thead><tbody>{}</tbody></table></div>",
            body,
        )


@admin.register(NewRelease)
class NewReleaseAdmin(admin.ModelAdmin):
    """Administração do módulo 07. Lançamentos.

    Edição e exclusão são permitidas somente em ``Lançamento``. ``Cobrança``
    fica bloqueada inclusive contra POST manipulado e ações em lote. A ação
    ``Gerar cobrança`` seleciona a competência atual, cria a cobrança por
    unidade, vincula os lançamentos e só então muda o status para ``Cobrança``,
    reportando cada item.
    """

    form = NewReleaseForm
    list_display = (
        "id",
        "condominium",
        "paymaster",
        "title",
        "scope_display",
        "launchDate",
        "chartOfAccounts",
        "fund",
        "launch_type_display",
        "value_display",
        "status_display",
        "is_active",
    )
    list_display_links = ("id", "title")
    list_filter = (
        "status",
        ScopeMonthFilter,
        "launchType",
        "is_active",
        "condominium__condominium",
        "fund",
        "chartOfAccounts",
    )
    search_fields = (
        "title",
        "paymaster__name",
        "condominium__unit_number",
        "condominium__tower",
        "condominium__condominium__name",
        "chartOfAccounts__account_code",
        "chartOfAccounts__account_name",
        "fund__description",
    )
    autocomplete_fields = ("condominium", "chartOfAccounts", "fund")
    readonly_fields = (
        "status_display",
        "created_by",
        "updated_by",
        "created_at",
        "updated_at",
    )
    list_select_related = (
        "condominium",
        "condominium__condominium",
        "paymaster",
        "chartOfAccounts",
        "fund",
        "created_by",
        "updated_by",
    )
    list_per_page = 25
    ordering = ("-launchDate", "-id")
    actions = ("gerar_cobranca", "excluir_lancamentos")
    save_on_top = True

    fieldsets = (
        (
            "Principal",
            {
                "fields": (
                    "condominium",
                    "paymaster",
                    "launchDate",
                    "scope",
                    "title",
                    "chartOfAccounts",
                    "fund",
                    "launchType",
                    "value",
                    "notes",
                ),
            },
        ),
        (
            "Auditoria",
            {
                "fields": (
                    "is_active",
                    "status_display",
                    "created_by",
                    "updated_by",
                    "created_at",
                    "updated_at",
                ),
            },
        ),
    )

    @property
    def media(self):
        # A versão é calculada a cada requisição para invalidar o cache do
        # navegador assim que o arquivo JS mudar, sem exigir reinício do servidor.
        extra = "" if settings.DEBUG else ".min"
        return super().media + forms.Media(
            css={"all": ("css/newrelease_admin.css",)},
            js=(
                f"admin/js/vendor/jquery/jquery{extra}.js",
                f"admin/js/vendor/select2/select2.full{extra}.js",
                "js/jquery.mask.min.js",
                "admin/js/jquery.init.js",
                _static_with_mtime("js/newrelease_admin.js"),
            ),
        )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            "condominium",
            "condominium__condominium",
            "paymaster",
            "chartOfAccounts",
            "fund",
            "created_by",
            "updated_by",
        )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "residents-by-unit/",
                self.admin_site.admin_view(self.residents_by_unit),
                name="financial_newrelease_residents_by_unit",
            ),
        ]
        return custom_urls + urls

    def residents_by_unit(self, request):
        """Endpoint AJAX usado pelo select dependente de pagador."""
        allowed = (
            self.has_view_permission(request)
            or self.has_add_permission(request)
            or self.has_change_permission(request)
        )
        if not allowed:
            raise PermissionDenied

        unit_id = request.GET.get("unit_id")
        if not unit_id:
            return JsonResponse(
                {
                    "results": [],
                    "message": "Unidade não informada.",
                },
                status=400,
            )

        try:
            unit_id = int(unit_id)
        except (TypeError, ValueError):
            return JsonResponse(
                {
                    "results": [],
                    "message": "Unidade inválida.",
                },
                status=400,
            )

        residents = (
            Resident.objects.filter(unit_id=unit_id, is_active=True)
            .select_related("unit", "unit__condominium", "type_of_resident")
            .order_by("name")
        )
        results = [
            {"id": resident.pk, "text": paymaster_label(resident)}
            for resident in residents
        ]
        return JsonResponse({"results": results})

    def has_change_permission(self, request, obj=None):
        if (
            obj is not None
            and obj.status != NewRelease.Status.LANCAMENTO
        ):
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if (
            obj is not None
            and obj.status != NewRelease.Status.LANCAMENTO
        ):
            return False
        return super().has_delete_permission(request, obj)

    def get_readonly_fields(self, request, obj=None):
        readonly = list(super().get_readonly_fields(request, obj))
        if (
            obj is not None
            and obj.status != NewRelease.Status.LANCAMENTO
        ):
            readonly = ["status_display"] + [
                field.name for field in self.model._meta.fields
            ]
        return readonly

    def get_actions(self, request):
        actions = super().get_actions(request)
        # O delete_selected padrão não revalida has_delete_permission por
        # objeto. A exclusão em lote é feita pela ação abaixo, com savepoint
        # por item e relatório individual.
        actions.pop("delete_selected", None)
        return actions

    def save_model(self, request, obj, form, change):
        NewReleaseService.save_instance(
            obj,
            user=request.user,
            is_new=not change,
        )

    def delete_model(self, request, obj):
        NewReleaseService.delete_instance(obj, user=request.user)

    def delete_queryset(self, request, queryset):
        blocked = list(
            queryset.exclude(status=NewRelease.Status.LANCAMENTO)
            .values_list("pk", flat=True)
        )
        if blocked:
            raise PermissionDenied(
                "Não é permitido excluir lançamentos em Cobrança: "
                + ", ".join(str(pk) for pk in blocked)
            )
        super().delete_queryset(request, queryset)

    @admin.action(
        description="Gerar cobrança",
        permissions=("change",),
    )
    def gerar_cobranca(self, request, queryset):
        results = NewReleaseService.generate_billing(
            list(queryset.values_list("pk", flat=True)),
            user=request.user,
        )
        self._report_results(request, results, "cobrança gerada")

    @admin.action(
        description="Excluir lançamentos selecionados",
        permissions=("delete",),
    )
    def excluir_lancamentos(self, request, queryset):
        results = NewReleaseService.delete_many(
            list(queryset.values_list("pk", flat=True)),
            user=request.user,
        )
        self._report_results(request, results, "excluído(s)")

    def _report_results(self, request, results, success_label):
        successes = [
            result["id"] for result in results if result["success"]
        ]
        failures = [
            result for result in results if not result["success"]
        ]

        if successes:
            ids = ", ".join(str(pk) for pk in successes)
            self.message_user(
                request,
                f"{len(successes)} registro(s) {success_label}: "
                f"IDs {ids}.",
                messages.SUCCESS,
            )

        for failure in failures:
            self.message_user(
                request,
                f"ID {failure['id']}: {failure['reason']}",
                messages.WARNING,
            )

    @admin.display(description="Competência", ordering="scope")
    def scope_display(self, obj):
        if not obj.scope:
            return "-"
        return date_format(obj.scope, "F/Y").capitalize()

    @admin.display(description="Tipo", ordering="launchType")
    def launch_type_display(self, obj):
        return obj.get_launchType_display()

    @admin.display(description="Valor", ordering="value")
    def value_display(self, obj):
        if obj.value is None:
            return "-"
        return number_format(obj.value, 2, force_grouping=True)

    @admin.display(description="Status", ordering="status")
    def status_display(self, obj=None):
        if obj is None:
            return NewRelease.Status.LANCAMENTO.label
        return obj.get_status_display()

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Pagamentos são criados somente pela ação 'Pagamento' da cobrança."""

    list_display = (
        "id",
        "collection",
        "financialTransaction",
        "dateReceived",
        "amountReceived",
    )
    list_select_related = ("collection", "financialTransaction")
    readonly_fields = (
        "collection",
        "financialTransaction",
        "dateReceived",
        "amountReceived",
        "created_by",
        "updated_by",
        "created_at",
        "updated_at",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(Apportionment)
class ApportionmentAdmin(admin.ModelAdmin):
    pass

@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    pass

@admin.register(BankTransfer)
class BankTransferAdmin(admin.ModelAdmin):
    pass
