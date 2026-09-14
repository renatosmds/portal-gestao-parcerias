from itertools import count


_cpf_seq = count(100000001)
_cnpj_seq = count(100000000001)


def cpf_teste():
    base = f"{next(_cpf_seq):09d}"[-9:]

    soma = sum(
        int(base[i]) * (10 - i)
        for i in range(9)
    )
    resto = (soma * 10) % 11
    primeiro = 0 if resto == 10 else resto

    parcial = base + str(primeiro)

    soma = sum(
        int(parcial[i]) * (11 - i)
        for i in range(10)
    )
    resto = (soma * 10) % 11
    segundo = 0 if resto == 10 else resto

    return parcial + str(segundo)


def cnpj_teste():
    base = f"{next(_cnpj_seq):012d}"[-12:]

    pesos_1 = [
        5, 4, 3, 2, 9, 8,
        7, 6, 5, 4, 3, 2,
    ]

    soma = sum(
        int(base[i]) * pesos_1[i]
        for i in range(12)
    )
    resto = soma % 11
    primeiro = 0 if resto < 2 else 11 - resto

    parcial = base + str(primeiro)

    pesos_2 = [
        6, 5, 4, 3, 2, 9, 8,
        7, 6, 5, 4, 3, 2,
    ]

    soma = sum(
        int(parcial[i]) * pesos_2[i]
        for i in range(13)
    )
    resto = soma % 11
    segundo = 0 if resto < 2 else 11 - resto

    return parcial + str(segundo)
