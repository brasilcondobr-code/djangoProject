from domains.administrative.models.bank import Bank

class BankDTO:
    def __init__(self, id=None, compe=None, bank_name=None, account_type=None, initial_balance=None, initial_balance_date=None, account_name=None, iban=None, agency=None, account_number=None, account_digit=None, bank_address_id=None, is_active=False, condominium_id=None, full_name_drawn=None, cpf_drawn=None, rg_drawn=None, phone_drawn=None, email_drawn=None, addresses_drawn_id=None, full_name_manager=None, phone1_manager=None, phone2_manager=None, phone3_manager=None, email_manager=None, created_at=None, updated_at=None):
        self.id = id
        self.compe = compe
        self.bank_name = bank_name
        self.account_type = account_type
        self.initial_balance = initial_balance
        self.initial_balance_date = initial_balance_date
        self.account_name = account_name
        self.iban = iban
        self.agency = agency
        self.account_number = account_number
        self.account_digit = account_digit
        self.bank_address_id = bank_address_id
        self.is_active = is_active
        self.condominium_id = condominium_id
        self.full_name_drawn = full_name_drawn
        self.cpf_drawn = cpf_drawn
        self.rg_drawn = rg_drawn
        self.phone_drawn = phone_drawn
        self.email_drawn = email_drawn
        self.addresses_drawn_id = addresses_drawn_id
        self.full_name_manager = full_name_manager
        self.phone1_manager = phone1_manager
        self.phone2_manager = phone2_manager
        self.phone3_manager = phone3_manager
        self.email_manager = email_manager
        self.created_at = created_at
        self.updated_at = updated_at

    @classmethod
    def from_model(cls, bank):
        return cls(
            id=bank.id,
            compe=bank.compe,
            bank_name=bank.bank_name,
            account_type=bank.account_type,
            initial_balance=bank.initial_balance,
            initial_balance_date=bank.initial_balance_date,
            account_name=bank.account_name,
            iban=bank.iban,
            agency=bank.agency,
            account_number=bank.account_number,
            account_digit=bank.account_digit,
            bank_address_id=bank.bank_address.id if bank.bank_address else None,
            is_active=bank.is_active,
            condominium_id=bank.condominium.id if bank.condominium else None,
            full_name_drawn=bank.full_name_drawn,
            cpf_drawn=bank.cpf_drawn,
            rg_drawn=bank.rg_drawn,
            phone_drawn=bank.phone_drawn,
            email_drawn=bank.email_drawn,
            addresses_drawn_id=bank.addresses_drawn.id if bank.addresses_drawn else None,
            full_name_manager=bank.full_name_manager,
            phone1_manager=bank.phone1_manager,
            phone2_manager=bank.phone2_manager,
            phone3_manager=bank.phone3_manager,
            email_manager=bank.email_manager,
            created_at=bank.created_at,
            updated_at=bank.updated_at
        )
