"""Rótulos de apresentação usados pelo módulo 07. Lançamentos."""


def paymaster_label(resident):
    """Rótulo do Pagador no formato ``Nome | Tipo | Unidade``.

    O ``__str__`` de ``Resident`` é compartilhado com outros apps e por isso
    não é alterado aqui. Este rótulo é aplicado somente no formulário e no
    endpoint AJAX do módulo de lançamentos.
    """
    resident_type = getattr(resident, "type_of_resident", None)
    type_label = str(resident_type) if resident_type else "Não informado"

    unit = getattr(resident, "unit", None)
    unit_label = str(unit) if unit else "Sem Unidade"

    return f"{resident.name} | {type_label} | {unit_label}"
