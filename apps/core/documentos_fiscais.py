import re


def somente_digitos(valor):
    return re.sub(r"\D", "", valor or "")


def validar_cpf(valor):
    cpf = somente_digitos(valor)

    if len(cpf) != 11:
        return False

    if cpf == cpf[0] * 11:
        return False

    soma = sum(
        int(cpf[i]) * (10 - i)
        for i in range(9)
    )
    resto = (soma * 10) % 11
    primeiro = 0 if resto == 10 else resto

    if primeiro != int(cpf[9]):
        return False

    soma = sum(
        int(cpf[i]) * (11 - i)
        for i in range(10)
    )
    resto = (soma * 10) % 11
    segundo = 0 if resto == 10 else resto

    return segundo == int(cpf[10])


def validar_cnpj(valor):
    cnpj = somente_digitos(valor)

    if len(cnpj) != 14:
        return False

    if cnpj == cnpj[0] * 14:
        return False

    pesos_1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma = sum(
        int(cnpj[i]) * pesos_1[i]
        for i in range(12)
    )

    resto = soma % 11
    primeiro = 0 if resto < 2 else 11 - resto

    if primeiro != int(cnpj[12]):
        return False

    pesos_2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma = sum(
        int(cnpj[i]) * pesos_2[i]
        for i in range(13)
    )

    resto = soma % 11
    segundo = 0 if resto < 2 else 11 - resto

    return segundo == int(cnpj[13])


def documento_cpf_normalizado(valor):
    cpf = somente_digitos(valor)

    if not validar_cpf(cpf):
        raise ValueError("CPF invalido.")

    return cpf


def documento_cnpj_normalizado(valor):
    cnpj = somente_digitos(valor)

    if not validar_cnpj(cnpj):
        raise ValueError("CNPJ invalido.")

    return cnpj
