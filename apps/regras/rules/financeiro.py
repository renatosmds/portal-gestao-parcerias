from decimal import Decimal

from apps.documentos.models import Documento
from apps.lancamentos.models import Lancamento
from apps.regras.resultado import ResultadoRegra


def avaliar_financeiro_lancamento(lancamento, contexto=None):
    achados = []

    documentos = Documento.objects.filter(
        lancamento=lancamento
    )

    documentos_pagamento = documentos.filter(
        tipo=Documento.Tipo.COMPROVANTE
    )

    pagamento_confirmado_no_checklist = documentos.filter(
        pagamento_comprovado=True
    ).exists()

    if (
        not lancamento.comprovante_pagamento
        and not documentos_pagamento.exists()
        and not pagamento_confirmado_no_checklist
    ):
        achados.append(
            ResultadoRegra(
                codigo="FIN_SEM_COMPROVANTE_PAGAMENTO",
                severidade="critico",
                titulo="Comprovante de pagamento não localizado",
                descricao=(
                    "Não foi localizado comprovante de pagamento no lançamento "
                    "nem documento específico de pagamento vinculado."
                ),
                regra="FIN_SEM_COMPROVANTE_PAGAMENTO",
                categoria="financeiro",
                resultado="achado",
                fato_verificado=(
                    "Ausência de evidência documental específica do pagamento."
                ),
                evidencia=(
                    f"Lançamento {lancamento.numero_lancamento}: "
                    "campo comprovante_pagamento vazio e nenhum Documento "
                    "do tipo comprovante vinculado."
                ),
                risco_glosa=(
                    "Elevado caso o efetivo desembolso da despesa não possa "
                    "ser comprovado."
                ),
                recomendacao=(
                    "Solicitar e conferir comprovante de pagamento compatível "
                    "com favorecido, valor, data e despesa analisada."
                ),
            )
        )

    documentos_fiscais = documentos.filter(
        tipo=Documento.Tipo.NOTA_FISCAL
    )

    for documento in documentos_fiscais:
        valor_documento = getattr(
            documento,
            "valor_documento",
            None,
        )

        if valor_documento is None:
            continue

        valor_documento = Decimal(str(valor_documento))
        valor_lancamento = Decimal(str(lancamento.valor_documento))

        if valor_documento != valor_lancamento:
            achados.append(
                ResultadoRegra(
                    codigo="FIN_VALOR_DIVERGENTE",
                    severidade="critico",
                    titulo="Valor divergente entre lançamento e documento",
                    descricao=(
                        "O valor registrado no lançamento difere do valor "
                        "informado no documento comprobatório."
                    ),
                    regra="FIN_VALOR_DIVERGENTE",
                    categoria="financeiro",
                    resultado="achado",
                    fato_verificado=(
                        "Divergência objetiva entre os valores cadastrados."
                    ),
                    evidencia=(
                        f"Lançamento=R$ {valor_lancamento}; "
                        f"documento=R$ {valor_documento}."
                    ),
                    risco_glosa=(
                        "Elevado até que a divergência seja justificada e "
                        "documentalmente comprovada."
                    ),
                    recomendacao=(
                        "Conferir documento fiscal, lançamento, pagamento e "
                        "eventuais rateios antes da conclusão."
                    ),
                )
            )

    duplicados = Lancamento.objects.filter(
        empresa=lancamento.empresa,
        numero_documento__iexact=lancamento.numero_documento.strip(),
        valor_documento=lancamento.valor_documento,
    ).exclude(
        pk=lancamento.pk
    )

    if lancamento.data_documento:
        duplicados = duplicados.filter(
            data_documento=lancamento.data_documento
        )

    if lancamento.numero_documento and duplicados.exists():
        achados.append(
            ResultadoRegra(
                codigo="FIN_POSSIVEL_DUPLICIDADE",
                severidade="critico",
                titulo="Possível duplicidade financeira",
                descricao=(
                    "Foi localizado outro lançamento da mesma empresa/OSC "
                    "com número de documento, valor e data coincidentes."
                ),
                regra="FIN_POSSIVEL_DUPLICIDADE",
                categoria="financeiro",
                resultado="achado",
                fato_verificado=(
                    "Existe outro lançamento com combinação coincidente "
                    "de documento, valor e data."
                ),
                evidencia=(
                    f"Quantidade adicional localizada: {duplicados.count()}."
                ),
                risco_glosa=(
                    "Elevado caso seja confirmada duplicidade de despesa "
                    "ou pagamento."
                ),
                recomendacao=(
                    "Comparar os lançamentos, documentos fiscais e "
                    "comprovantes de pagamento antes da aprovação."
                ),
            )
        )

    return achados

