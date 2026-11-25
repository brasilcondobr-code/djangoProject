import logging
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone

from domains.financial.exceptions import (
    CollectionError,
    NewReleaseError,
    NewReleaseTransitionError,
    NewReleaseValidationError,
)
from domains.financial.models import Collection, NewRelease
from domains.financial.repositories import FinancialRepository
from domains.financial.services.collection_service import CollectionService

logger = logging.getLogger(__name__)


class NewReleaseService:
    """Regras de domínio do módulo 07. Lançamentos."""

    VALUE_MAX = Decimal("999999999999.99")
    VALUE_DECIMAL_PLACES = 2

    @staticmethod
    def normalize_scope(value):
        """Normaliza a competência para o primeiro dia do mês."""
        if value in (None, ""):
            return None
        try:
            return value.replace(day=1)
        except (AttributeError, TypeError):
            raise NewReleaseValidationError(
                "Informe uma competência válida no formato AAAA-MM."
            )

    @staticmethod
    def parse_value(raw):
        """Converte a magnitude monetária pt-BR em ``Decimal``.

        A máscara do navegador é apenas visual. O backend aceita valores como
        ``1.234,56``, ``1234,56`` ou ``-1.234,56`` e devolve sempre a
        magnitude positiva; o sinal é aplicado por ``apply_sign`` conforme o
        tipo de lançamento. Zero, mais de duas casas decimais e valores fora
        da precisão do campo são rejeitados.
        """
        if raw in (None, ""):
            return None

        if isinstance(raw, Decimal):
            value = raw
        else:
            text = str(raw).strip()
            if not text:
                return None
            if "," in text:
                text = text.replace(".", "").replace(",", ".")
            try:
                value = Decimal(text)
            except (InvalidOperation, ValueError):
                raise NewReleaseValidationError(
                    "Informe um valor monetário válido."
                )

        magnitude = abs(value)
        if magnitude <= 0:
            raise NewReleaseValidationError("O valor deve ser maior que zero.")

        exponent = magnitude.as_tuple().exponent
        if not isinstance(exponent, int) or (
            -exponent > NewReleaseService.VALUE_DECIMAL_PLACES
        ):
            raise NewReleaseValidationError(
                "O valor deve ter no máximo 2 casas decimais."
            )

        if magnitude > NewReleaseService.VALUE_MAX:
            raise NewReleaseValidationError(
                "O valor deve ter no máximo 12 dígitos inteiros e 2 decimais."
            )

        return magnitude

    @staticmethod
    def apply_sign(value, launch_type):
        """Aplica o sinal conforme o tipo (D positivo, C negativo)."""
        if value is None:
            return None

        magnitude = abs(value)
        if magnitude <= 0:
            raise NewReleaseValidationError("O valor deve ser maior que zero.")
        if launch_type == NewRelease.LaunchType.DEBITO:
            return magnitude
        if launch_type == NewRelease.LaunchType.CREDITO:
            return -magnitude
        raise NewReleaseValidationError("Tipo de lançamento inválido.")

    @staticmethod
    def _user_or_none(user):
        return user if getattr(user, "is_authenticated", False) else None

    @staticmethod
    def _format_validation_error(exc):
        if hasattr(exc, "message_dict"):
            parts = []
            for field, messages in exc.message_dict.items():
                parts.append(f"{field}: {'; '.join(messages)}")
            return " | ".join(parts)
        return "; ".join(exc.messages)

    @staticmethod
    def _validate_relations(instance):
        """Valida o vínculo entre unidade, pagador, plano de contas e fundo.

        A validação também existe no formulário, mas precisa ser repetida no
        service para cobrir uso programático e POST manipulado.
        """
        unit = instance.condominium
        if unit is None:
            return

        paymaster = instance.paymaster
        if paymaster is not None and paymaster.unit_id != unit.pk:
            raise NewReleaseValidationError(
                "O pagador deve pertencer à unidade selecionada."
            )

        chart_of_accounts = instance.chartOfAccounts
        if (
            chart_of_accounts is not None
            and chart_of_accounts.condominium_id != unit.condominium_id
        ):
            raise NewReleaseValidationError(
                "O plano de contas deve pertencer ao condomínio da unidade "
                "selecionada."
            )

        fund = instance.fund
        if fund is not None and fund.condominium_id != unit.condominium_id:
            raise NewReleaseValidationError(
                "O fundo deve pertencer ao condomínio da unidade selecionada."
            )

    @staticmethod
    @transaction.atomic
    def save_instance(instance, user=None, is_new=False):
        """Persiste uma instância já preenchida (Admin ou uso programático).

        Em edição, bloqueia a linha original e garante que somente lançamentos
        em ``Lançamento`` sejam alterados. ``created_by`` nunca é sobrescrito.
        """
        if instance is None:
            raise NewReleaseValidationError("Lançamento não encontrado.")

        actor = NewReleaseService._user_or_none(user)

        if is_new:
            instance.pk = None
            instance.status = NewRelease.Status.LANCAMENTO
            instance.created_by = actor
            instance.updated_by = actor
        else:
            try:
                locked = FinancialRepository.get_new_release_for_update(
                    instance.pk
                )
            except NewRelease.DoesNotExist:
                raise NewReleaseValidationError("Lançamento não encontrado.")

            if locked.status != NewRelease.Status.LANCAMENTO:
                raise NewReleaseTransitionError(
                    "Somente lançamentos com status 'Lançamento' podem ser "
                    f"editados. Status atual: '{locked.get_status_display()}'."
                )

            instance.status = locked.status
            instance.created_by_id = locked.created_by_id
            instance.updated_by = actor

        instance.scope = NewReleaseService.normalize_scope(instance.scope)
        instance.value = NewReleaseService.apply_sign(
            instance.value,
            instance.launchType,
        )
        instance.title = (instance.title or "").strip()

        NewReleaseService._validate_relations(instance)

        try:
            instance.full_clean()
            instance.save()
        except ValidationError as exc:
            raise NewReleaseValidationError(
                NewReleaseService._format_validation_error(exc)
            ) from exc
        except IntegrityError as exc:
            raise NewReleaseValidationError(
                "Não foi possível salvar o lançamento. Verifique a unicidade "
                "de título, competência e data para a unidade."
            ) from exc

        logger.info(
            "new_release_saved",
            extra={
                "new_release_id": instance.pk,
                "unit_id": instance.condominium_id,
                "status": instance.status,
                "operation": "create" if is_new else "update",
                "user_id": getattr(actor, "pk", None),
            },
        )
        return instance

    @staticmethod
    @transaction.atomic
    def delete_instance(instance, user=None):
        """Exclui um lançamento somente enquanto estiver em ``Lançamento``."""
        if instance is None:
            raise NewReleaseValidationError("Lançamento não encontrado.")

        try:
            locked = FinancialRepository.get_new_release_for_update(
                instance.pk
            )
        except NewRelease.DoesNotExist:
            raise NewReleaseValidationError("Lançamento não encontrado.")

        if locked.status != NewRelease.Status.LANCAMENTO:
            raise NewReleaseTransitionError(
                "Somente lançamentos com status 'Lançamento' podem ser "
                f"excluídos. Status atual: '{locked.get_status_display()}'."
            )

        new_release_id = locked.pk
        locked.delete()

        logger.info(
            "new_release_deleted",
            extra={
                "new_release_id": new_release_id,
                "user_id": getattr(
                    NewReleaseService._user_or_none(user),
                    "pk",
                    None,
                ),
            },
        )

    @staticmethod
    def _dedupe_ids(new_release_ids):
        """Mantém a ordem da seleção e remove IDs repetidos."""
        ordered = []
        for raw in new_release_ids or []:
            try:
                value = int(raw)
            except (TypeError, ValueError):
                value = raw
            if value not in ordered:
                ordered.append(value)
        return ordered

    @staticmethod
    def generate_billing(new_release_ids, user=None):
        """Gera cobranças para os lançamentos selecionados.

        Regras aprovadas:

        * processa somente os IDs selecionados, revalidados no servidor;
        * considera apenas status ``Lançamento`` e competência do mês atual;
        * agrupa por unidade + competência;
        * cria uma cobrança por grupo, com a soma líquida dos lançamentos
          (débito positivo, crédito negativo);
        * usa savepoint por grupo, permitindo sucesso parcial e relatório
          individual;
        * só altera o status para ``Cobrança`` depois de criar e vincular a
          cobrança do grupo.

        Os erros são devolvidos em memória; nada é persistido em
        ``Collection.errorStatus``.
        """
        actor = NewReleaseService._user_or_none(user)
        tmp_scope = timezone.localdate().replace(day=1)
        ordered_ids = NewReleaseService._dedupe_ids(new_release_ids)
        results = {}

        def add_failure(release_id, reason):
            results[release_id] = {
                "id": release_id,
                "success": False,
                "reason": reason,
            }

        with transaction.atomic():
            releases = {
                release.pk: release
                for release in NewRelease.objects.select_for_update()
                .filter(
                    pk__in=[
                        release_id
                        for release_id in ordered_ids
                        if isinstance(release_id, int)
                    ]
                )
                .order_by(
                    "condominium_id",
                    "scope",
                    "launchType",
                    "launchDate",
                    "pk",
                )
            }

            groups = {}
            for release_id in ordered_ids:
                if not isinstance(release_id, int):
                    add_failure(release_id, "Lançamento inválido.")
                    continue

                release = releases.get(release_id)
                if release is None:
                    add_failure(release_id, "Lançamento não encontrado.")
                    continue
                if release.status != NewRelease.Status.LANCAMENTO:
                    add_failure(
                        release_id,
                        "Somente lançamentos com status 'Lançamento' podem "
                        "gerar cobrança. Status atual: "
                        f"'{release.get_status_display()}'.",
                    )
                    continue
                if release.scope != tmp_scope:
                    add_failure(
                        release_id,
                        "O lançamento pertence à competência "
                        f"{release.scope:%m/%Y}; a ação processa somente "
                        f"{tmp_scope:%m/%Y}.",
                    )
                    continue
                if release.value is None:
                    add_failure(
                        release_id,
                        "O lançamento não possui valor para gerar cobrança.",
                    )
                    continue
                if release.collection_id is not None:
                    add_failure(
                        release_id,
                        "O lançamento já está vinculado a uma cobrança.",
                    )
                    continue

                groups.setdefault(
                    release.condominium_id, []
                ).append(release)

            for unit_id in sorted(groups):
                NewReleaseService._generate_group(
                    groups[unit_id],
                    actor=actor,
                    tmp_scope=tmp_scope,
                    results=results,
                )

        return [results[release_id] for release_id in ordered_ids]

    @staticmethod
    def _generate_group(releases, *, actor, tmp_scope, results):
        """Cria a cobrança de um grupo em um savepoint próprio."""
        release_ids = [release.pk for release in releases]
        try:
            with transaction.atomic():
                due_date = max(
                    release.launchDate for release in releases
                )
                total = sum(
                    (Decimal(release.value) for release in releases),
                    Decimal("0.00"),
                ).quantize(
                    CollectionService.QUANT,
                    rounding=ROUND_HALF_UP,
                )

                if total <= 0:
                    raise NewReleaseValidationError(
                        "O total líquido dos lançamentos do grupo deve ser "
                        "maior que zero."
                    )

                collection = Collection(
                    condominium_id=releases[0].condominium_id,
                    scope=tmp_scope,
                    originalValue=total,
                    discountPercent=Decimal("0.00"),
                    penaltyPercent=Decimal("0.00"),
                    feesPercent=Decimal("0.00"),
                    chargesPercent=Decimal("0.00"),
                    discountDeadline=due_date,
                    dueDate=due_date,
                    is_active=True,
                    errorStatus="",
                )
                CollectionService.save_instance(
                    collection,
                    user=actor,
                    is_new=True,
                )

                for release in releases:
                    release.collection = collection
                    release.status = NewRelease.Status.COBRANCA
                    release.updated_by = actor
                    release.save(
                        update_fields=[
                            "collection",
                            "status",
                            "updated_by",
                            "updated_at",
                        ]
                    )
        except (NewReleaseError, CollectionError) as exc:
            reason = str(exc)
            logger.warning(
                "new_release_billing_rejected",
                extra={
                    "new_release_ids": release_ids,
                    "unit_id": releases[0].condominium_id,
                    "reason": reason,
                },
            )
            for release_id in release_ids:
                results[release_id] = {
                    "id": release_id,
                    "success": False,
                    "reason": reason,
                }
        except Exception:
            logger.exception(
                "new_release_billing_failed",
                extra={"new_release_ids": release_ids},
            )
            for release_id in release_ids:
                results[release_id] = {
                    "id": release_id,
                    "success": False,
                    "reason": "Erro ao gerar cobrança.",
                }
        else:
            logger.info(
                "new_release_billing_generated",
                extra={
                    "collection_id": collection.pk,
                    "new_release_ids": release_ids,
                    "unit_id": collection.condominium_id,
                    "scope": str(collection.scope),
                    "total": str(collection.totalAmount),
                    "user_id": getattr(actor, "pk", None),
                },
            )
            for release_id in release_ids:
                results[release_id] = {
                    "id": release_id,
                    "success": True,
                    "reason": "",
                }

    @staticmethod
    def delete_many(new_release_ids, user=None):
        """Exclui lançamentos em lote com sucesso parcial e savepoint por item."""
        results = []

        for new_release_id in new_release_ids:
            try:
                with transaction.atomic():
                    instance = FinancialRepository.get_new_release_for_update(
                        new_release_id
                    )
                    if instance.status != NewRelease.Status.LANCAMENTO:
                        raise NewReleaseTransitionError(
                            "Somente lançamentos com status 'Lançamento' "
                            "podem ser excluídos. Status atual: "
                            f"'{instance.get_status_display()}'."
                        )
                    instance.delete()

                results.append(
                    {"id": new_release_id, "success": True, "reason": ""}
                )
            except NewRelease.DoesNotExist:
                results.append(
                    {
                        "id": new_release_id,
                        "success": False,
                        "reason": "Lançamento não encontrado.",
                    }
                )
            except NewReleaseError as exc:
                results.append(
                    {
                        "id": new_release_id,
                        "success": False,
                        "reason": str(exc),
                    }
                )
            except Exception:
                logger.exception(
                    "new_release_delete_failed",
                    extra={"new_release_id": new_release_id},
                )
                results.append(
                    {
                        "id": new_release_id,
                        "success": False,
                        "reason": "Erro ao excluir lançamento.",
                    }
                )

        return results
