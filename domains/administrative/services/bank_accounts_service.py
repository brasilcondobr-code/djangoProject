import logging
from django.db import transaction
from django.db import IntegrityError
from domains.administrative.repositories.bank_accounts_repository import BankAccountRepository
from domains.administrative.selectors.bank_accounts_selector import BankAccountSelector

logger = logging.getLogger(__name__)


class BankAccountService:
    @staticmethod
    def create_bank_account(data):
        try:
            with transaction.atomic():
                account = BankAccountRepository.create(data)
                logger.info(
                    'Bank account created: bank=%s, condominium=%s, account_ending=****-%s',
                    data.get('bank'),
                    data.get('condominium'),
                    str(data.get('account_number', ''))[-4:] if data.get('account_number') else '0000',
                )
                return account
        except IntegrityError as e:
            logger.warning('IntegrityError creating bank account: %s', str(e))
            raise

    @staticmethod
    def update_bank_account(account_id, data):
        account = BankAccountRepository.get_by_id(account_id)
        if not account:
            return None
        try:
            with transaction.atomic():
                account = BankAccountRepository.update(account, data)
                logger.info(
                    'Bank account updated: id=%s, account_ending=****-%s',
                    account_id,
                    str(data.get('account_number', ''))[-4:] if data.get('account_number') else '0000',
                )
                return account
        except IntegrityError as e:
            logger.warning('IntegrityError updating bank account %s: %s', account_id, str(e))
            raise

    @staticmethod
    def delete_bank_account(account_id):
        account = BankAccountRepository.get_by_id(account_id)
        if not account:
            return False
        logger.info(
            'Bank account deleted: id=%s, account_ending=****-%s',
            account_id,
            str(account.account_number)[-4:] if account.account_number else '0000',
        )
        BankAccountRepository.delete(account)
        return True

    @staticmethod
    def get_all_bank_accounts():
        return BankAccountSelector.get_all()

    @staticmethod
    def get_bank_account_by_id(id):
        return BankAccountSelector.get_by_id(id)
