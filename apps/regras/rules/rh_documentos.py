from django.db.models import Q

from apps.documentos.models import Documento
from apps.regras.resultado import ResultadoRegra


def avaliar_documentacao_rh(folha, contexto=None):
    achados = []

    funcionario = folha.funcionario
    empresa = getattr(funcionario, "empresa", None)
    termo = getattr(funcionario, "termo", None)

    # ---------------------------------------------------------
    # Documentos diretamente associados ao trabalhador.
    #
    # O campo pertence é legado, portanto serve como evidência
    # disponível no modelo atual, mas não deve ser considerado
    # arquitetura definitiva.
    # ---------------------------------------------------------
    documentos_funcionario = Documento.objects.filter(
        pertence=funcionario
    )

    folhas = documentos_funcionario.filter(
        tipo=Documento.Tipo.FOLHA
    )

    comprovantes = documentos_funcionario.filter(
        tipo=Documento.Tipo.COMPROVANTE
    )

    guias_individuais = documentos_funcionario.filter(
        tipo=Documento.Tipo.GUIA
    )

    # ---------------------------------------------------------
    # Folha de pagamento documental
    # ---------------------------------------------------------
    if not folhas.exists():
        achados.append(
            ResultadoRegra(
                codigo="RH_DOC_FOLHA_NAO_LOCALIZADA",
                severidade="alerta",
                titulo="Documento da folha de pagamento não localizado",
                descricao=(
                    "Não foi localizado, entre os documentos diretamente "
                    "associados ao trabalhador, documento classificado como "
                    "folha de pagamento."
                ),
                regra="RH_DOC_FOLHA_NAO_LOCALIZADA",
                categoria="documentacao_rh",
                resultado="nao_verificado",
                fato_verificado=(
                    "Documento do tipo folha não identificado no vínculo "
                    "documental disponível para o trabalhador."
                ),
                evidencia=(
                    f"funcionario={funcionario.pk}; "
                    f"competencia={folha.competencia:%m/%Y}."
                ),
                risco_glosa=(
                    "Indeterminado. A ausência do documento no cadastro "
                    "não comprova, isoladamente, inexistência da folha."
                ),
                recomendacao=(
                    "Localizar e vincular a folha de pagamento da competência "
                    "antes da conclusão da análise."
                ),
            )
        )

    # ---------------------------------------------------------
    # Comprovante de pagamento do trabalhador
    # ---------------------------------------------------------
    if not comprovantes.exists():
        achados.append(
            ResultadoRegra(
                codigo="RH_DOC_PAGAMENTO_NAO_LOCALIZADO",
                severidade="alerta",
                titulo="Comprovante de pagamento não localizado",
                descricao=(
                    "Não foi localizado comprovante de pagamento diretamente "
                    "associado ao trabalhador."
                ),
                regra="RH_DOC_PAGAMENTO_NAO_LOCALIZADO",
                categoria="documentacao_rh",
                resultado="nao_verificado",
                fato_verificado=(
                    "Comprovante individual não identificado no vínculo "
                    "documental disponível."
                ),
                evidencia=(
                    f"funcionario={funcionario.pk}; "
                    f"competencia={folha.competencia:%m/%Y}."
                ),
                risco_glosa=(
                    "Indeterminado até a comprovação do efetivo pagamento."
                ),
                recomendacao=(
                    "Localizar e conferir comprovante contendo favorecido, "
                    "valor, data e origem do pagamento."
                ),
            )
        )

    # ---------------------------------------------------------
    # Necessidade de evidência de encargos
    # ---------------------------------------------------------
    inss = folha.inss or 0
    fgts = getattr(funcionario, "fgts", None) or 0

    possui_encargos = (
        inss > 0
        or fgts > 0
    )

    guias_escopo = Documento.objects.none()

    if possui_encargos and empresa:
        filtro = Q(
            empresa=empresa,
            tipo=Documento.Tipo.GUIA,
        )

        if termo:
            filtro &= Q(termo=termo)

        guias_escopo = Documento.objects.filter(
            filtro
        )

    if possui_encargos:
        if guias_individuais.exists():
            pass

        elif guias_escopo.exists():
            achados.append(
                ResultadoRegra(
                    codigo="RH_GUIA_COLETIVA_CANDIDATA",
                    severidade="info",
                    titulo="Guia coletiva de encargos localizada",
                    descricao=(
                        "Foi localizada guia de encargos vinculada à OSC/Termo, "
                        "mas sem vínculo individual direto com o trabalhador."
                    ),
                    regra="RH_GUIA_COLETIVA_CANDIDATA",
                    categoria="documentacao_rh",
                    resultado="informativo",
                    fato_verificado=(
                        "Existe documento do tipo guia no escopo institucional "
                        "da parceria."
                    ),
                    evidencia=(
                        f"guias_localizadas={guias_escopo.count()}; "
                        f"empresa={empresa.pk}; "
                        f"termo={getattr(termo, 'pk', None)}."
                    ),
                    risco_glosa="",
                    recomendacao=(
                        "Conferir se a guia coletiva abrange o trabalhador, "
                        "a competência e os encargos analisados."
                    ),
                )
            )

        else:
            achados.append(
                ResultadoRegra(
                    codigo="RH_DOC_GUIA_NAO_LOCALIZADA",
                    severidade="alerta",
                    titulo="Guia de encargos não localizada",
                    descricao=(
                        "Existem valores de encargos informados, mas não foi "
                        "localizada guia de recolhimento individual ou coletiva "
                        "no escopo documental disponível."
                    ),
                    regra="RH_DOC_GUIA_NAO_LOCALIZADA",
                    categoria="documentacao_rh",
                    resultado="nao_verificado",
                    fato_verificado=(
                        "Não foi identificado documento do tipo guia "
                        "associável aos encargos registrados."
                    ),
                    evidencia=(
                        f"inss={inss}; "
                        f"fgts={fgts}; "
                        f"funcionario={funcionario.pk}."
                    ),
                    risco_glosa=(
                        "Indeterminado. A ausência da guia no cadastro "
                        "não significa, isoladamente, ausência de recolhimento."
                    ),
                    recomendacao=(
                        "Localizar guia, memória de cálculo e comprovante "
                        "de recolhimento correspondentes."
                    ),
                )
            )

    # ---------------------------------------------------------
    # Divergência institucional dos documentos vinculados
    # ---------------------------------------------------------
    if empresa:
        divergentes_empresa = documentos_funcionario.exclude(
            empresa__isnull=True
        ).exclude(
            empresa=empresa
        )

        if divergentes_empresa.exists():
            achados.append(
                ResultadoRegra(
                    codigo="RH_DOC_EMPRESA_DIVERGENTE",
                    severidade="critico",
                    titulo="Documento vinculado a outra empresa/OSC",
                    descricao=(
                        "Foi localizado documento associado ao trabalhador "
                        "que pertence a empresa/OSC diferente daquela "
                        "registrada no cadastro do trabalhador."
                    ),
                    regra="RH_DOC_EMPRESA_DIVERGENTE",
                    categoria="documentacao_rh",
                    resultado="achado",
                    fato_verificado=(
                        "Divergência institucional no vínculo documental."
                    ),
                    evidencia=(
                        f"empresa_funcionario={empresa.pk}; "
                        f"documentos_divergentes={divergentes_empresa.count()}."
                    ),
                    risco_glosa=(
                        "Elevado até que seja esclarecido a qual OSC/parceria "
                        "o documento efetivamente pertence."
                    ),
                    recomendacao=(
                        "Conferir trabalhador, OSC, Termo e documento antes "
                        "de utilizar a evidência na prestação de contas."
                    ),
                )
            )

    if termo:
        divergentes_termo = documentos_funcionario.exclude(
            termo__isnull=True
        ).exclude(
            termo=termo
        )

        if divergentes_termo.exists():
            achados.append(
                ResultadoRegra(
                    codigo="RH_DOC_TERMO_DIVERGENTE",
                    severidade="critico",
                    titulo="Documento vinculado a outro Termo",
                    descricao=(
                        "Foi localizado documento associado ao trabalhador "
                        "que está vinculado a Termo diferente daquele "
                        "registrado para o vínculo de RH."
                    ),
                    regra="RH_DOC_TERMO_DIVERGENTE",
                    categoria="documentacao_rh",
                    resultado="achado",
                    fato_verificado=(
                        "Divergência entre Termo do trabalhador "
                        "e Termo do documento."
                    ),
                    evidencia=(
                        f"termo_funcionario={termo.pk}; "
                        f"documentos_divergentes={divergentes_termo.count()}."
                    ),
                    risco_glosa=(
                        "Elevado até que seja confirmada a correta imputação "
                        "da despesa à parceria."
                    ),
                    recomendacao=(
                        "Conferir o Termo e corrigir o vínculo documental "
                        "antes da conclusão da análise."
                    ),
                )
            )

    # ---------------------------------------------------------
    # Status dos documentos diretamente associados
    # ---------------------------------------------------------
    documentos_reprovados = documentos_funcionario.filter(
        status=Documento.Status.REPROVADO
    )

    if documentos_reprovados.exists():
        achados.append(
            ResultadoRegra(
                codigo="RH_DOC_REPROVADO",
                severidade="critico",
                titulo="Documento de RH anteriormente reprovado",
                descricao=(
                    "Existe documento associado ao trabalhador com status "
                    "de conferência igual a reprovado."
                ),
                regra="RH_DOC_REPROVADO",
                categoria="documentacao_rh",
                resultado="achado",
                fato_verificado=(
                    "Documento relacionado ao trabalhador possui "
                    "status de reprovação."
                ),
                evidencia=(
                    f"documentos_reprovados={documentos_reprovados.count()}."
                ),
                risco_glosa=(
                    "Elevado enquanto a pendência documental que motivou "
                    "a reprovação permanecer sem solução."
                ),
                recomendacao=(
                    "Examinar a causa da reprovação documental e eventual "
                    "documentação substitutiva ou saneadora."
                ),
            )
        )

    documentos_pendentes = documentos_funcionario.filter(
        status=Documento.Status.COM_PENDENCIA
    )

    if documentos_pendentes.exists():
        achados.append(
            ResultadoRegra(
                codigo="RH_DOC_COM_PENDENCIA",
                severidade="alerta",
                titulo="Documento de RH com pendência",
                descricao=(
                    "Existe documento associado ao trabalhador marcado "
                    "como contendo pendência."
                ),
                regra="RH_DOC_COM_PENDENCIA",
                categoria="documentacao_rh",
                resultado="nao_verificado",
                fato_verificado=(
                    "Documento relacionado ao trabalhador possui "
                    "pendência registrada."
                ),
                evidencia=(
                    f"documentos_com_pendencia={documentos_pendentes.count()}."
                ),
                risco_glosa=(
                    "Indeterminado até o saneamento ou avaliação da pendência."
                ),
                recomendacao=(
                    "Examinar a pendência registrada antes da conclusão "
                    "da análise de RH."
                ),
            )
        )

    return achados
