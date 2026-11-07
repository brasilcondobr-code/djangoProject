import logging
from decimal import Decimal, InvalidOperation

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from domains.financial.exceptions import (
    NewReleaseError,
    NewReleaseTransitionError,
    NewReleaseValidationError,
)
from domains.financial.models import NewRelease
from domains.financial.repositories import FinancialRepository

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
        ``1.234,56`` ou ``1234,56`` e rejeita zero, negativos, mais de duas
        casas decimais e valores fora da precisão do campo.
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

        if value <= 0:
            raise NewReleaseValidationError("O valor deve ser maior que zero.")

        exponent = value.as_tuple().exponent
        if not isinstance(exponent, int) or (
            -exponent > NewReleaseService.VALUE_DECIMAL_PLACES
        ):
            raise NewReleaseValidationError(
                "O valor deve ter no máximo 2 casas decimais."
            )

        if value > NewReleaseService.VALUE_MAX:
            raise NewReleaseValidationError(
                "O valor deve ter no máximo 12 dígitos inteiros e 2 decimais."
            )

        return value

    @staticmethod
    def apply_sign(value, launch_type):
        """Aplica o sinal conforme o tipo de lançamento (D negativo, C positivo)."""
        if value is None:
            return None

        magnitude = abs(value)
        if magnitude <= 0:
            raise NewReleaseValidationError("O valor deve ser maior que zero.")
        if launch_type == NewRelease.LaunchType.DEBITO:
            return -magnitude
        if launch_type == NewRelease.LaunchType.CREDITO:
            return magnitude
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
    def generate_billing(new_release_ids, user=None):
        """Gera cobrança para cada lançamento elegível.

        Cada item é processado em seu próprio savepoint. O retorno é uma lista
        de resultados em memória, com ID e motivo das rejeições. Mensagens de
        falha não são persistidas no banco.
        """
        results = []
        actor = NewReleaseService._user_or_none(user)

        for new_release_id in new_release_ids:
            try:
                with transaction.atomic():
                    instance = FinancialRepository.get_new_release_for_update(
                        new_release_id
                    )
                    if instance.status != NewRelease.Status.LANCAMENTO:
                        raise NewReleaseTransitionError(
                            "Somente lançamentos com status 'Lançamento' "
                            "podem gerar cobrança. Status atual: "
                            f"'{instance.get_status_display()}'."
                        )

                    instance.status = NewRelease.Status.COBRANCA
                    instance.updated_by = actor
                    instance.save(
                        update_fields=["status", "updated_by", "updated_at"]
                    )

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
                    "new_release_billing_failed",
                    extra={"new_release_id": new_release_id},
                )
                results.append(
                    {
                        "id": new_release_id,
                        "success": False,
                        "reason": "Erro ao gerar cobrança.",
                    }
                )

        return results

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
