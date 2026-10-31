from django.contrib import admin, messages

from domains.reservations.forms import (
    MaintenanceReservationsForm,
    MoveReservationsForm,
    RentalsForm,
)
from domains.reservations.models import (
    Rentals,
    MaintenanceReservations,
    MoveReservations,
)
from domains.reservations.services.maintenance_reservations_service import (
    MaintenanceReservationsService,
)
from domains.reservations.services.move_reservations_service import (
    MoveReservationsService,
)
from domains.reservations.services.rentals_service import RentalsService


@admin.register(Rentals)
class RentalsAdmin(admin.ModelAdmin):
    """Administração do módulo 01. Locações.

    Edição permitida somente em ``Agendamento``. ``Reservado`` e
    ``Finalizado`` ficam somente leitura, inclusive contra POST manipulado
    (``has_change_permission`` retorna ``False`` para esses registros).
    """

    form = RentalsForm
    list_display = (
        "id",
        "condominium",
        "typesOfRentals",
        "startDate",
        "endDate",
        "applicant",
        "rentalPrice",
        "charge_amount",
        "status",
        "is_active",
    )
    list_display_links = ("id", "applicant")
    list_filter = (
        "typesOfRentals",
        "status",
        "charge_amount",
        "is_active",
        "condominium__condominium",
    )
    search_fields = (
        "applicant",
        "condominium__unit_number",
        "condominium__tower",
        "condominium__condominium__name",
        "typesOfRentals__description",
    )
    list_select_related = (
        "condominium",
        "condominium__condominium",
        "typesOfRentals",
        "created_by",
        "updated_by",
    )
    autocomplete_fields = ("condominium", "typesOfRentals")
    date_hierarchy = "startDate"
    ordering = ("-startDate", "-id")
    list_per_page = 25
    empty_value_display = "-"
    jazzmin_section_order = ["Principal", "Auditoria"]

    readonly_fields = (
        "status",
        "errorStatus",
        "created_by",
        "updated_by",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Principal",
            {
                "fields": (
                    "condominium",
                    "typesOfRentals",
                    "startDate",
                    "endDate",
                    "applicant",
                    "rentalPrice",
                    "charge_amount",
                    "observations",
                ),
            },
        ),
        (
            "Auditoria",
            {
                "classes": ("collapse",),
                "fields": (
                    "is_active",
                    "status",
                    "errorStatus",
                    "created_by",
                    "updated_by",
                    "created_at",
                    "updated_at",
                ),
            },
        ),
    )

    actions = ("reservar_locacoes", "finalizar_locacoes")

    class Media:
        js = (
            "js/utils.js",
            "js/rentals_admin.js",
        )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            "condominium",
            "condominium__condominium",
            "typesOfRentals",
            "created_by",
            "updated_by",
        )

    def has_change_permission(self, request, obj=None):
        if obj is not None and obj.status != Rentals.Status.AGENDAMENTO:
            return False
        return super().has_change_permission(request, obj)

    def get_readonly_fields(self, request, obj=None):
        readonly = list(super().get_readonly_fields(request, obj))
        if obj is not None and obj.status != Rentals.Status.AGENDAMENTO:
            readonly = [field.name for field in self.model._meta.fields]
        return readonly

    def save_model(self, request, obj, form, change):
        # O formulário já validou período, preço e capacidade (com lock) dentro
        # da transação do Admin; aqui apenas auditoria e persistência.
        RentalsService.save_instance(
            obj,
            user=request.user,
            is_new=not change,
            check_capacity=False,
        )

    # ------------------------------------------------------------------
    # Ações em lote
    # ------------------------------------------------------------------
    @admin.action(
        description="Reservar locações selecionadas",
        permissions=("change",),
    )
    def reservar_locacoes(self, request, queryset):
        results = RentalsService.reserve_rentals(
            list(queryset.values_list("pk", flat=True)),
            user=request.user,
        )
        self._report_transition_results(request, results, "reservada(s)")

    @admin.action(
        description="Finalizar locações selecionadas",
        permissions=("change",),
    )
    def finalizar_locacoes(self, request, queryset):
        results = RentalsService.finalize_rentals(
            list(queryset.values_list("pk", flat=True)),
            user=request.user,
        )
        self._report_transition_results(request, results, "finalizada(s)")

    def _report_transition_results(self, request, results, success_label):
        successes = [item for item in results if item["success"]]
        failures = [item for item in results if not item["success"]]

        if successes:
            ids = ", ".join(f"#{item['pk']}" for item in successes[:20])
            if len(successes) > 20:
                ids += f" ... e mais {len(successes) - 20}"
            self.message_user(
                request,
                f"{len(successes)} locação(ões) {success_label} com sucesso: "
                f"{ids}.",
                level=messages.SUCCESS,
            )
        if failures:
            self.message_user(
                request,
                f"{len(failures)} locação(ões) rejeitada(s):",
                level=messages.WARNING,
            )
            for item in failures[:20]:
                self.message_user(
                    request,
                    f"#{item['pk']}: {item['message']}",
                    level=messages.WARNING,
                )
            if len(failures) > 20:
                self.message_user(
                    request,
                    f"... e mais {len(failures) - 20} rejeição(ões).",
                    level=messages.WARNING,
                )
        if not successes and not failures:
            self.message_user(
                request,
                "Nenhuma locação selecionada.",
                level=messages.WARNING,
            )


@admin.register(MaintenanceReservations)
class MaintenanceReservationsAdmin(admin.ModelAdmin):
    """Administração do módulo 02. Manutenções.

    Edição permitida somente em ``Agendamento``. ``Execução`` e
    ``Finalizado`` ficam somente leitura, inclusive contra POST manipulado.
    As ações Executar/Finalizar revalidam o status no servidor e reportam o
    resultado individualmente.
    """

    form = MaintenanceReservationsForm
    list_display = (
        "id",
        "condominium",
        "typesOfMaintenance",
        "startDate",
        "endDate",
        "applicant",
        "status",
        "is_active",
    )
    list_display_links = ("id", "applicant")
    list_filter = (
        "typesOfMaintenance",
        "status",
        "is_active",
        "condominium__condominium",
    )
    search_fields = (
        "applicant",
        "condominium__unit_number",
        "condominium__tower",
        "condominium__condominium__name",
        "typesOfMaintenance__description",
    )
    list_select_related = (
        "condominium",
        "condominium__condominium",
        "typesOfMaintenance",
        "created_by",
        "updated_by",
    )
    autocomplete_fields = ("condominium", "typesOfMaintenance")
    date_hierarchy = "startDate"
    ordering = ("-startDate", "-id")
    list_per_page = 25
    empty_value_display = "-"
    jazzmin_section_order = ["Principal", "Auditoria"]

    readonly_fields = (
        "status",
        "created_by",
        "updated_by",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Principal",
            {
                "fields": (
                    "condominium",
                    "typesOfMaintenance",
                    "startDate",
                    "endDate",
                    "applicant",
                    "observations",
                ),
            },
        ),
        (
            "Auditoria",
            {
                "classes": ("collapse",),
                "fields": (
                    "is_active",
                    "status",
                    "created_by",
                    "updated_by",
                    "created_at",
                    "updated_at",
                ),
            },
        ),
    )

    actions = ("executar_manutencoes", "finalizar_manutencoes")

    class Media:
        js = ("js/maintenance_reservations_admin.js",)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            "condominium",
            "condominium__condominium",
            "typesOfMaintenance",
            "created_by",
            "updated_by",
        )

    def has_change_permission(self, request, obj=None):
        if (
            obj is not None
            and obj.status != MaintenanceReservations.Status.AGENDAMENTO
        ):
            return False
        return super().has_change_permission(request, obj)

    def get_readonly_fields(self, request, obj=None):
        readonly = list(super().get_readonly_fields(request, obj))
        if (
            obj is not None
            and obj.status != MaintenanceReservations.Status.AGENDAMENTO
        ):
            readonly = [field.name for field in self.model._meta.fields]
        return readonly

    def save_model(self, request, obj, form, change):
        MaintenanceReservationsService.save_instance(
            obj,
            user=request.user,
            is_new=not change,
        )

    # ------------------------------------------------------------------
    # Ações em lote
    # ------------------------------------------------------------------
    @admin.action(
        description="Executar manutenções selecionadas",
        permissions=("change",),
    )
    def executar_manutencoes(self, request, queryset):
        results = MaintenanceReservationsService.execute_maintenances(
            list(queryset.values_list("pk", flat=True)),
            user=request.user,
        )
        self._report_transition_results(request, results, "executada(s)")

    @admin.action(
        description="Finalizar manutenções selecionadas",
        permissions=("change",),
    )
    def finalizar_manutencoes(self, request, queryset):
        results = MaintenanceReservationsService.finalize_maintenances(
            list(queryset.values_list("pk", flat=True)),
            user=request.user,
        )
        self._report_transition_results(request, results, "finalizada(s)")

    def _report_transition_results(self, request, results, success_label):
        successes = [item for item in results if item["success"]]
        failures = [item for item in results if not item["success"]]

        if successes:
            ids = ", ".join(f"#{item['pk']}" for item in successes[:20])
            if len(successes) > 20:
                ids += f" ... e mais {len(successes) - 20}"
            self.message_user(
                request,
                f"{len(successes)} manutenção(ões) {success_label} com "
                f"sucesso: {ids}.",
                level=messages.SUCCESS,
            )
        if failures:
            self.message_user(
                request,
                f"{len(failures)} manutenção(ões) rejeitada(s):",
                level=messages.WARNING,
            )
            for item in failures[:20]:
                self.message_user(
                    request,
                    f"#{item['pk']}: {item['message']}",
                    level=messages.WARNING,
                )
            if len(failures) > 20:
                self.message_user(
                    request,
                    f"... e mais {len(failures) - 20} rejeição(ões).",
                    level=messages.WARNING,
                )
        if not successes and not failures:
            self.message_user(
                request,
                "Nenhuma manutenção selecionada.",
                level=messages.WARNING,
            )


@admin.register(MoveReservations)
class MoveReservationsAdmin(admin.ModelAdmin):
    """Administração do módulo 03. Mudanças.

    Edição permitida somente em ``Agendamento``. ``Execução`` e
    ``Finalizado`` ficam somente leitura, inclusive contra POST manipulado.
    As ações Executar/Finalizar revalidam o status no servidor e reportam o
    resultado individualmente.
    """

    form = MoveReservationsForm
    list_display = (
        "id",
        "condominium",
        "typeOfChange",
        "startDate",
        "endDate",
        "applicant",
        "status",
        "is_active",
    )
    list_display_links = ("id", "applicant")
    list_filter = (
        "typeOfChange",
        "status",
        "is_active",
        "condominium__condominium",
    )
    search_fields = (
        "applicant",
        "condominium__unit_number",
        "condominium__tower",
        "condominium__condominium__name",
    )
    list_select_related = (
        "condominium",
        "condominium__condominium",
        "created_by",
        "updated_by",
    )
    autocomplete_fields = ("condominium",)
    date_hierarchy = "startDate"
    ordering = ("-startDate", "-id")
    list_per_page = 25
    empty_value_display = "-"
    jazzmin_section_order = ["Principal", "Auditoria"]

    readonly_fields = (
        "status",
        "created_by",
        "updated_by",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Principal",
            {
                "fields": (
                    "condominium",
                    "typeOfChange",
                    "startDate",
                    "endDate",
                    "applicant",
                    "observations",
                ),
            },
        ),
        (
            "Auditoria",
            {
                "classes": ("collapse",),
                "fields": (
                    "is_active",
                    "status",
                    "created_by",
                    "updated_by",
                    "created_at",
                    "updated_at",
                ),
            },
        ),
    )

    actions = ("executar_mudancas", "finalizar_mudancas")

    class Media:
        js = ("js/move_reservations_admin.js",)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            "condominium",
            "condominium__condominium",
            "created_by",
            "updated_by",
        )

    def has_change_permission(self, request, obj=None):
        if (
            obj is not None
            and obj.status != MoveReservations.Status.AGENDAMENTO
        ):
            return False
        return super().has_change_permission(request, obj)

    def get_readonly_fields(self, request, obj=None):
        readonly = list(super().get_readonly_fields(request, obj))
        if (
            obj is not None
            and obj.status != MoveReservations.Status.AGENDAMENTO
        ):
            readonly = [field.name for field in self.model._meta.fields]
        return readonly

    def save_model(self, request, obj, form, change):
        MoveReservationsService.save_instance(
            obj,
            user=request.user,
            is_new=not change,
        )

    # ------------------------------------------------------------------
    # Ações em lote
    # ------------------------------------------------------------------
    @admin.action(
        description="Executar mudanças selecionadas",
        permissions=("change",),
    )
    def executar_mudancas(self, request, queryset):
        results = MoveReservationsService.execute_moves(
            list(queryset.values_list("pk", flat=True)),
            user=request.user,
        )
        self._report_transition_results(request, results, "executada(s)")

    @admin.action(
        description="Finalizar mudanças selecionadas",
        permissions=("change",),
    )
    def finalizar_mudancas(self, request, queryset):
        results = MoveReservationsService.finalize_moves(
            list(queryset.values_list("pk", flat=True)),
            user=request.user,
        )
        self._report_transition_results(request, results, "finalizada(s)")

    def _report_transition_results(self, request, results, success_label):
        successes = [item for item in results if item["success"]]
        failures = [item for item in results if not item["success"]]

        if successes:
            ids = ", ".join(f"#{item['pk']}" for item in successes[:20])
            if len(successes) > 20:
                ids += f" ... e mais {len(successes) - 20}"
            self.message_user(
                request,
                f"{len(successes)} mudança(s) {success_label} com sucesso: "
                f"{ids}.",
                level=messages.SUCCESS,
            )
        if failures:
            self.message_user(
                request,
                f"{len(failures)} mudança(s) rejeitada(s):",
                level=messages.WARNING,
            )
            for item in failures[:20]:
                self.message_user(
                    request,
                    f"#{item['pk']}: {item['message']}",
                    level=messages.WARNING,
                )
            if len(failures) > 20:
                self.message_user(
                    request,
                    f"... e mais {len(failures) - 20} rejeição(ões).",
                    level=messages.WARNING,
                )
        if not successes and not failures:
            self.message_user(
                request,
                "Nenhuma mudança selecionada.",
                level=messages.WARNING,
            )
