from dataclasses import dataclass, field


@dataclass(frozen=True)
class InventarioDadosRH:
    dados_pessoais: tuple = field(default_factory=tuple)
    dados_financeiros: tuple = field(default_factory=tuple)
    dados_potencialmente_sensiveis: tuple = field(default_factory=tuple)

    @property
    def possui_dados_pessoais(self):
        return bool(self.dados_pessoais)

    @property
    def possui_dados_financeiros(self):
        return bool(self.dados_financeiros)

    @property
    def possui_dados_potencialmente_sensiveis(self):
        return bool(self.dados_potencialmente_sensiveis)


def inventariar_dados_funcionario(funcionario):
    """
    Inventário técnico.

    CPF, PIS/NIT, nascimento, endereço, telefone e dados
    bancários são tratados aqui como dados pessoais.

    Eles NÃO são automaticamente classificados como dados
    pessoais sensíveis nos termos do art. 5º, II, da LGPD.
    """

    pessoais = []
    financeiros = []

    campos_pessoais = (
        ("cpf", "cpf"),
        ("pis_pasep_nit", "pis_pasep_nit"),
        ("data_nascimento", "data_nascimento"),
        ("endereco", "endereco"),
        ("bairro", "bairro"),
        ("cep", "cep"),
        ("cidade", "cidade"),
        ("estado", "estado"),
        ("email", "email"),
        ("Telefone", "telefone"),
    )

    for atributo, codigo in campos_pessoais:
        valor = getattr(
            funcionario,
            atributo,
            None,
        )

        if valor:
            pessoais.append(codigo)

    campos_financeiros = (
        ("banco", "banco"),
        ("agencia", "agencia"),
        ("conta_bancaria", "conta_bancaria"),
    )

    for atributo, codigo in campos_financeiros:
        valor = getattr(
            funcionario,
            atributo,
            None,
        )

        if valor:
            financeiros.append(codigo)

    return InventarioDadosRH(
        dados_pessoais=tuple(pessoais),
        dados_financeiros=tuple(financeiros),
    )


def documento_pode_conter_dado_sensivel(documento):
    """
    Apenas identifica indício pelo metadado disponível.

    Não afirma que o arquivo efetivamente contém dado sensível.
    """

    texto = " ".join(
        [
            str(getattr(documento, "descricao", "") or ""),
            str(getattr(documento, "observacoes", "") or ""),
            str(getattr(documento, "arquivo", "") or ""),
        ]
    ).lower()

    termos = (
        "atestado",
        "atestado medico",
        "atestado médico",
        "laudo",
        "laudo medico",
        "laudo médico",
        "saude",
        "saúde",
        "doenca",
        "doença",
        "cid",
        "diagnostico",
        "diagnóstico",
        "exame medico",
        "exame médico",
        "biometr",
    )

    return any(
        termo in texto
        for termo in termos
    )
