import logging
from datetime import date, datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone

from domains.financial.exceptions import (
    CollectionError,
    CollectionTransitionError,
    CollectionValidationError,
)
from domains.financial.models import (
    Collection,
    CollectionCredit,
    NewRelease,
    Payment,
)
from domains.financial.repositories import FinancialRepository
from domains.parameters.models import FinancialTransaction

logger = logging.getLogger(__name__)


class CollectionService:
    """Regras de domínio do módulo 04. Cobranças."""

    VALUE_MAX = Decimal("999999999999.99")
    MONEY_DECIMAL_PLACES = 2
    PERCENT_MAX = Decimal("100.00")
    ZERO = Decimal("0.00")
    ONE_HUNDRED = Decimal("100")
    QUANT = Decimal("0.01")

    EDITABLE_STATUSES = {Collection.Status.TO_BE_WON}
    SETTLEMENT_STATUSES = {
        Collection.Status.TO_BE_WON,
        Collection.Status.EXPIRED,
        Collection.Status.PARTIAL,
    }

    PERCENT_FIELDS = {
        "discountPercent": "% desconto",
        "penaltyPercent": "% multa",
        "feesPercent": "% juros",
        "chargesPercent": "% encargos",
    }

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
    def _parse_decimal(raw, label):
        if isinstance(raw, Decimal):
            return raw

        text = str(raw).strip()
        if not text:
            raise CollectionValidationError(f"Informe um {label} válido.")
        if "," in text:
            text = text.replace(".", "").replace(",", ".")
        try:
            return Decimal(text)
        except (InvalidOperation, ValueError):
            raise CollectionValidationError(f"Informe um {label} válido.")

    @staticmethod
    def normalize_scope(value):
        """Normaliza a competência para o primeiro dia do mês."""
        if value in (None, ""):
            return None
        try:
            return value.replace(day=1)
        except (AttributeError, TypeError):
            raise CollectionValidationError(
                "Informe uma competência válida no formato AAAA-MM."
            )

    @staticmethod
    def parse_money(raw, *, label="valor", required=False):
        """Converte valor monetário pt-BR em ``Decimal`` com duas casas."""
        if raw in (None, "") or (
            isinstance(raw, str) and not raw.strip()
        ):
            if required:
                raise CollectionValidationError(f"Informe o {label}.")
            return None

        value = CollectionService._parse_decimal(raw, label)

        if value <= 0:
            raise CollectionValidationError(
                f"O {label} deve ser maior que zero."
            )

        exponent = value.as_tuple().exponent
        if not isinstance(exponent, int) or (
            -exponent > CollectionService.MONEY_DECIMAL_PLACES
        ):
            raise CollectionValidationError(
                f"O {label} deve ter no máximo 2 casas decimais."
            )

        if value > CollectionService.VALUE_MAX:
            raise CollectionValidationError(
                f"O {label} deve ter no máximo 12 dígitos inteiros e 2 "
                "decimais."
            )

        return value.quantize(CollectionService.QUANT)

    @staticmethod
    def parse_percent(raw, *, label="percentual"):
        """Converte percentual entre 0,00 e 100,00."""
        if raw in (None, "") or (
            isinstance(raw, str) and not raw.strip()
        ):
            return None

        value = CollectionService._parse_decimal(raw, label)

        if value < 0 or value > CollectionService.PERCENT_MAX:
            raise CollectionValidationError(
                f"O {label} deve estar entre 0 e 100."
            )

        exponent = value.as_tuple().exponent
        if not isinstance(exponent, int) or (
            -exponent > CollectionService.MONEY_DECIMAL_PLACES
        ):
            raise CollectionValidationError(
                f"O {label} deve ter no máximo 2 casas decimais."
            )

        return value.quantize(CollectionService.QUANT)

    @staticmethod
    def _coerce_date(value, label):
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
            return value
        try:
            return date.fromisoformat(str(value))
        except (TypeError, ValueError):
            raise CollectionValidationError(f"Informe uma {label} válida.")

    @staticmethod
    def calculate_amounts(
        original_value,
        discount_percent=None,
        penalty_percent=None,
        fees_percent=None,
        charges_percent=None,
    ):
        """Calcula os valores derivados e o total da cobrança.

        ``totalAmount = originalValue - discountAmount + fineAmount +
        interestAmount + chargesAmount``, com arredondamento
        ``ROUND_HALF_UP`` em duas casas.
        """
        if original_value is None:
            return {
                "originalValue": None,
                "discountAmount": None,
                "fineAmount": None,
                "interestAmount": None,
                "chargesAmount": None,
                "totalAmount": None,
            }

        original = Decimal(original_value).quantize(
            CollectionService.QUANT,
            rounding=ROUND_HALF_UP,
        )

        def amount(percent):
            if percent is None:
                return None
            return (
                original
                * Decimal(percent)
                / CollectionService.ONE_HUNDRED
            ).quantize(CollectionService.QUANT, rounding=ROUND_HALF_UP)

        discount = amount(discount_percent)
        fine = amount(penalty_percent)
        interest = amount(fees_percent)
        charges = amount(charges_percent)

        total = (
            original
            - (discount or CollectionService.ZERO)
            + (fine or CollectionService.ZERO)
            + (interest or CollectionService.ZERO)
            + (charges or CollectionService.ZERO)
        ).quantize(CollectionService.QUANT, rounding=ROUND_HALF_UP)

        return {
            "originalValue": original,
            "discountAmount": discount,
            "fineAmount": fine,
            "interestAmount": interest,
            "chargesAmount": charges,
            "totalAmount": total,
        }

    @staticmethod
    def calculate_balance(total_amount, received_amount):
        """Saldo nunca negativo."""
        if total_amount is None:
            return CollectionService.ZERO
        balance = (
            Decimal(total_amount) - Decimal(received_amount or 0)
        ).quantize(CollectionService.QUANT, rounding=ROUND_HALF_UP)
        return max(balance, CollectionService.ZERO)

    @staticmethod
    def compute_status(total_amount, received_amount, due_date, today=None):
        """Pagamentos têm precedência sobre a data de vencimento."""
        today = today or timezone.localdate()
        received = Decimal(received_amount or 0)

        if (
            total_amount is not None
            and Decimal(total_amount) > 0
            and received >= Decimal(total_amount)
        ):
            return Collection.Status.PAID
        if received > 0:
            return Collection.Status.PARTIAL
        if due_date and due_date < today:
            return Collection.Status.EXPIRED
        return Collection.Status.TO_BE_WON

    @staticmethod
    def received_total(collection_id):
        payments = FinancialRepository.get_collection_payments_total(
            collection_id
        )
        credits = FinancialRepository.get_collection_credits_total(
            collection_id
        )
        return Decimal(payments or 0) + Decimal(credits or 0)

    @staticmethod
    def available_balance(collection):
        if collection is None or collection.totalAmount is None:
            return CollectionService.ZERO
        if not collection.pk:
            return CollectionService.calculate_balance(
                collection.totalAmount, 0
            )
        return CollectionService.calculate_balance(
            collection.totalAmount,
            CollectionService.received_total(collection.pk),
        )

    @staticmethod
    def can_edit(collection):
        return bool(
            collection
            and collection.is_active
            and collection.status in CollectionService.EDITABLE_STATUSES
        )

    @staticmethod
    def can_delete(collection):
        return bool(
            collection
            and collection.status in CollectionService.EDITABLE_STATUSES
        )

    @staticmethod
    def can_settle(collection):
        return bool(
            collection
            and collection.is_active
            and collection.status in CollectionService.SETTLEMENT_STATUSES
        )

    @staticmethod
    def _apply_values(instance):
        instance.scope = CollectionService.normalize_scope(instance.scope)
        original = CollectionService.parse_money(
            instance.originalValue,
            label="valor original",
        )

        percents = {}
        for field, label in CollectionService.PERCENT_FIELDS.items():
            percents[field] = CollectionService.parse_percent(
                getattr(instance, field),
                label=label,
            )

        amounts = CollectionService.calculate_amounts(
            original,
            discount_percent=percents["discountPercent"],
            penalty_percent=percents["penaltyPercent"],
            fees_percent=percents["feesPercent"],
            charges_percent=percents["chargesPercent"],
        )

        instance.originalValue = amounts["originalValue"]
        for field in CollectionService.PERCENT_FIELDS:
            setattr(instance, field, percents[field])
        instance.discountAmount = amounts["discountAmount"]
        instance.fineAmount = amounts["fineAmount"]
        instance.interestAmount = amounts["interestAmount"]
        instance.chargesAmount = amounts["chargesAmount"]
        instance.totalAmount = amounts["totalAmount"]

    @staticmethod
    def _sync_locked(instance, actor):
        """Recalcula saldo e status da linha já bloqueada e persiste."""
        received = CollectionService.received_total(instance.pk)
        instance.balance = CollectionService.calculate_balance(
            instance.totalAmount, received
        )
        instance.status = CollectionService.compute_status(
            instance.totalAmount,
            received,
            instance.dueDate,
        )
        instance.errorStatus = ""
        instance.updated_by = actor
        instance.save(
            update_fields=[
                "balance",
                "status",
                "errorStatus",
                "updated_by",
                "updated_at",
            ]
        )
        return instance

    @staticmethod
    @transaction.atomic
    def save_instance(instance, user=None, is_new=False):
        """Cria ou edita uma cobrança aplicando as regras de domínio."""
        if instance is None:
            raise CollectionValidationError("Cobrança não encontrada.")

        actor = CollectionService._user_or_none(user)

        if is_new:
            instance.pk = None
            instance.billingDate = timezone.localdate()
            instance.created_by = actor
            instance.updated_by = actor
        else:
            try:
                locked = FinancialRepository.get_collection_for_update(
                    instance.pk
                )
            except Collection.DoesNotExist:
                raise CollectionValidationError("Cobrança não encontrada.")

            if not CollectionService.can_edit(locked):
                reason = (
                    "inativa" if not locked.is_active else "bloqueada pelo "
                    f"status '{locked.get_status_display()}'"
                )
                raise CollectionTransitionError(
                    "Somente cobranças ativas em 'A vencer' podem ser "
                    f"editadas. Cobrança {reason}."
                )

            if (
                instance.condominium_id != locked.condominium_id
                and locked.new_releases.exists()
            ):
                raise CollectionTransitionError(
                    "Não é possível alterar a unidade de uma cobrança que "
                    "possui lançamentos vinculados."
                )

            instance.billingDate = locked.billingDate
            instance.created_by_id = locked.created_by_id
            instance.status = locked.status
            instance.balance = locked.balance
            instance.updated_by = actor

        CollectionService._apply_values(instance)

        received = (
            CollectionService.received_total(instance.pk)
            if instance.pk
            else CollectionService.ZERO
        )
        if (
            received > 0
            and instance.totalAmount is not None
            and received > instance.totalAmount
        ):
            raise CollectionValidationError(
                "O valor total não pode ser menor que o total já recebido "
                f"de R$ {received:.2f}."
            )
        if received > 0 and instance.totalAmount is None:
            raise CollectionValidationError(
                "A cobrança possui recebimentos e exige um valor total."
            )
        instance.balance = CollectionService.calculate_balance(
            instance.totalAmount, received
        )
        instance.status = CollectionService.compute_status(
            instance.totalAmount,
            received,
            instance.dueDate,
        )
        instance.errorStatus = ""

        try:
            instance.full_clean()
            instance.save()
        except ValidationError as exc:
            raise CollectionValidationError(
                CollectionService._format_validation_error(exc)
            ) from exc
        except IntegrityError as exc:
            raise CollectionValidationError(
                "Não foi possível salvar a cobrança. Verifique a unicidade "
                "de unidade, data de cobrança, competência e vencimento."
            ) from exc

        logger.info(
            "collection_saved",
            extra={
                "collection_id": instance.pk,
                "unit_id": instance.condominium_id,
                "status": instance.status,
                "operation": "create" if is_new else "update",
                "user_id": getattr(actor, "pk", None),
            },
        )
        return instance

    @staticmethod
    def _assert_deletable(locked):
        if not CollectionService.can_delete(locked):
            raise CollectionTransitionError(
                "Somente cobranças com status 'A vencer' podem ser "
                f"excluídas. Status atual: '{locked.get_status_display()}'."
            )
        if locked.new_releases.exists():
            raise CollectionTransitionError(
                "A cobrança possui lançamentos vinculados e não pode ser "
                "excluída."
            )
        if locked.payments.exists():
            raise CollectionTransitionError(
                "A cobrança possui pagamentos registrados e não pode ser "
                "excluída."
            )
        if locked.credits.exists():
            raise CollectionTransitionError(
                "A cobrança possui créditos registrados e não pode ser "
                "excluída."
            )

    @staticmethod
    @transaction.atomic
    def delete_instance(instance, user=None):
        if instance is None:
            raise CollectionValidationError("Cobrança não encontrada.")

        try:
            locked = FinancialRepository.get_collection_for_update(
                instance.pk
            )
        except Collection.DoesNotExist:
            raise CollectionValidationError("Cobrança não encontrada.")

        CollectionService._assert_deletable(locked)

        collection_id = locked.pk
        locked.delete()

        logger.info(
            "collection_deleted",
            extra={
                "collection_id": collection_id,
                "user_id": getattr(
                    CollectionService._user_or_none(user), "pk", None
                ),
            },
        )

    @staticmethod
    @transaction.atomic
    def link_new_releases(collection, new_release_ids, user=None):
        """Vincula lançamentos em status ``Cobrança`` à cobrança.

        A operação é atômica: qualquer lançamento inválido cancela o lote.
        """
        collection_id = getattr(collection, "pk", collection)
        ids = []
        for value in new_release_ids or []:
            try:
                value = int(value)
            except (TypeError, ValueError):
                raise CollectionValidationError(
                    "Informe lançamentos válidos para vinculação."
                )
            if value not in ids:
                ids.append(value)

        try:
            locked = FinancialRepository.get_collection_for_update(
                collection_id
            )
        except Collection.DoesNotExist:
            raise CollectionValidationError("Cobrança não encontrada.")

        if not CollectionService.can_edit(locked):
            raise CollectionTransitionError(
                "Somente cobranças ativas em 'A vencer' podem receber "
                "lançamentos."
            )

        if not ids:
            return []

        actor = CollectionService._user_or_none(user)
        releases = {
            release.pk: release
            for release in NewRelease.objects.select_for_update().filter(
                pk__in=ids
            )
        }

        missing = [pk for pk in ids if pk not in releases]
        if missing:
            raise CollectionValidationError(
                "Lançamento(s) não encontrado(s): "
                + ", ".join(str(pk) for pk in missing)
                + "."
            )

        for release in releases.values():
            if release.status != NewRelease.Status.COBRANCA:
                raise CollectionTransitionError(
                    f"O lançamento {release.pk} não está com status "
                    "'Cobrança'."
                )
            if release.condominium_id != locked.condominium_id:
                raise CollectionValidationError(
                    f"O lançamento {release.pk} pertence a outra unidade."
                )
            if (
                release.collection_id
                and release.collection_id != locked.pk
            ):
                raise CollectionTransitionError(
                    f"O lançamento {release.pk} já está vinculado a outra "
                    "cobrança."
                )

        for release in releases.values():
            release.collection = locked
            release.updated_by = actor
            release.save(
                update_fields=["collection", "updated_by", "updated_at"]
            )

        logger.info(
            "collection_new_releases_linked",
            extra={
                "collection_id": locked.pk,
                "new_release_ids": ids,
                "user_id": getattr(actor, "pk", None),
            },
        )
        return list(releases.values())

    @staticmethod
    @transaction.atomic
    def recalculate(collection, user=None):
        """Recalcula saldo e status após alterações de créditos."""
        collection_id = getattr(collection, "pk", collection)
        try:
            locked = FinancialRepository.get_collection_for_update(
                collection_id
            )
        except Collection.DoesNotExist:
            raise CollectionValidationError("Cobrança não encontrada.")

        actor = CollectionService._user_or_none(user)
        return CollectionService._sync_locked(locked, actor)

    @staticmethod
    def _resolve_collection(collection):
        collection_id = getattr(collection, "pk", collection)
        try:
            return FinancialRepository.get_collection_for_update(
                collection_id
            )
        except Collection.DoesNotExist:
            raise CollectionValidationError("Cobrança não encontrada.")

    @staticmethod
    def _resolve_financial_transaction(financial_transaction):
        transaction_id = getattr(
            financial_transaction, "pk", financial_transaction
        )
        instance = FinancialTransaction.objects.filter(
            pk=transaction_id,
            is_active=True,
        ).first()
        if instance is None:
            raise CollectionValidationError(
                "Selecione uma operação financeira ativa."
            )
        return instance

    @staticmethod
    def _assert_settleable(locked):
        if not locked.is_active:
            raise CollectionTransitionError(
                "A cobrança está inativa e não aceita movimentações."
            )
        if locked.status == Collection.Status.PAID:
            raise CollectionTransitionError(
                "A cobrança já está paga e não aceita movimentações."
            )
        if locked.status not in CollectionService.SETTLEMENT_STATUSES:
            raise CollectionTransitionError(
                "A cobrança não está elegível para movimentação. Status "
                f"atual: '{locked.get_status_display()}'."
            )

    @staticmethod
    @transaction.atomic
    def register_payment(
        collection,
        financial_transaction,
        date_received,
        amount_received,
        user=None,
    ):
        """Registra um pagamento e atualiza saldo/status da cobrança."""
        locked = CollectionService._resolve_collection(collection)
        CollectionService._assert_settleable(locked)

        amount = CollectionService.parse_money(
            amount_received,
            label="valor recebido",
            required=True,
        )
        received_date = CollectionService._coerce_date(
            date_received, "data de recebimento"
        )
        operation = CollectionService._resolve_financial_transaction(
            financial_transaction
        )

        if locked.totalAmount is None:
            raise CollectionValidationError(
                "A cobrança não possui valor total para receber pagamentos."
            )

        available = CollectionService.available_balance(locked)
        if amount > available:
            raise CollectionValidationError(
                "O valor recebido excede o saldo disponível de "
                f"R$ {available:.2f}."
            )

        actor = CollectionService._user_or_none(user)
        payment = Payment.objects.create(
            collection=locked,
            financialTransaction=operation,
            dateReceived=received_date,
            amountReceived=amount,
            created_by=actor,
            updated_by=actor,
        )

        CollectionService._sync_locked(locked, actor)

        logger.info(
            "collection_payment_registered",
            extra={
                "collection_id": locked.pk,
                "payment_id": payment.pk,
                "amount": str(amount),
                "user_id": getattr(actor, "pk", None),
            },
        )
        return payment

    @staticmethod
    @transaction.atomic
    def register_credit(
        collection,
        financial_transaction,
        credit_date,
        amount_credit,
        user=None,
    ):
        """Registra um crédito e atualiza saldo/status da cobrança."""
        locked = CollectionService._resolve_collection(collection)
        CollectionService._assert_settleable(locked)

        amount = CollectionService.parse_money(
            amount_credit,
            label="valor do crédito",
            required=True,
        )
        credit_day = CollectionService._coerce_date(
            credit_date, "data do crédito"
        )
        operation = CollectionService._resolve_financial_transaction(
            financial_transaction
        )

        if locked.totalAmount is None:
            raise CollectionValidationError(
                "A cobrança não possui valor total para receber créditos."
            )

        available = CollectionService.available_balance(locked)
        if amount > available:
            raise CollectionValidationError(
                "O valor do crédito excede o saldo disponível de "
                f"R$ {available:.2f}."
            )

        actor = CollectionService._user_or_none(user)
        credit = CollectionCredit.objects.create(
            collection=locked,
            financialTransaction=operation,
            creditDate=credit_day,
            amountCredit=amount,
            created_by=actor,
            updated_by=actor,
        )

        CollectionService._sync_locked(locked, actor)

        logger.info(
            "collection_credit_registered",
            extra={
                "collection_id": locked.pk,
                "credit_id": credit.pk,
                "amount": str(amount),
                "user_id": getattr(actor, "pk", None),
            },
        )
        return credit

    @staticmethod
    def update_collections(collection_ids, user=None):
        """Ação 'Atualizar Cobrança' com savepoint e sucesso parcial."""
        results = []
        actor = CollectionService._user_or_none(user)

        for collection_id in collection_ids:
            try:
                with transaction.atomic():
                    locked = FinancialRepository.get_collection_for_update(
                        collection_id
                    )
                    CollectionService._assert_settleable(locked)
                    CollectionService._sync_locked(locked, actor)

                results.append(
                    {"id": collection_id, "success": True, "reason": ""}
                )
            except Collection.DoesNotExist:
                results.append(
                    {
                        "id": collection_id,
                        "success": False,
                        "reason": "Cobrança não encontrada.",
                    }
                )
            except CollectionError as exc:
                reason = str(exc)
                FinancialRepository.set_collection_error_status(
                    collection_id, reason
                )
                results.append(
                    {
                        "id": collection_id,
                        "success": False,
                        "reason": reason,
                    }
                )
            except Exception:
                reason = "Erro ao atualizar a cobrança."
                FinancialRepository.set_collection_error_status(
                    collection_id, reason
                )
                logger.exception(
                    "collection_update_failed",
                    extra={"collection_id": collection_id},
                )
                results.append(
                    {
                        "id": collection_id,
                        "success": False,
                        "reason": reason,
                    }
                )

        return results

    @staticmethod
    def delete_many(collection_ids, user=None):
        """Exclui cobranças em lote com savepoint e relatório por item."""
        results = []

        for collection_id in collection_ids:
            try:
                with transaction.atomic():
                    locked = FinancialRepository.get_collection_for_update(
                        collection_id
                    )
                    CollectionService._assert_deletable(locked)
                    locked.delete()

                results.append(
                    {"id": collection_id, "success": True, "reason": ""}
                )
            except Collection.DoesNotExist:
                results.append(
                    {
                        "id": collection_id,
                        "success": False,
                        "reason": "Cobrança não encontrada.",
                    }
                )
            except CollectionError as exc:
                reason = str(exc)
                FinancialRepository.set_collection_error_status(
                    collection_id, reason
                )
                results.append(
                    {
                        "id": collection_id,
                        "success": False,
                        "reason": reason,
                    }
                )
            except Exception:
                reason = "Erro ao excluir a cobrança."
                FinancialRepository.set_collection_error_status(
                    collection_id, reason
                )
                logger.exception(
                    "collection_delete_failed",
                    extra={"collection_id": collection_id},
                )
                results.append(
                    {
                        "id": collection_id,
                        "success": False,
                        "reason": reason,
                    }
                )

        return results
