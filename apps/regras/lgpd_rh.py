from dataclasses import dataclass, field

from apps.documentos.models import Documento
from apps.regras.context import ContextoRegras
from apps.regras.resultado import ResultadoRegra
from apps.regras.rules.lgpd_rh import (
    documento_pode_conter_dado_sensivel,
    inventariar_dados_funcionario,
)


@dataclass
class ResultadoLGPDRH:
    funcionario_id: int
    inventario: object
    achados: list = field(default_factory=list)

    @property
    def total_achados(self):
        return len(self.achados)

    @property
    def criticos(self):
        return [
            item
            for item in self.achados
            if item.severidade == "critico"
        ]

    @property
    def alertas(self):
        return [
            item
            for item in self.achados
            if item.severidade == "alerta"
        ]

    @property
    def resultado_preliminar(self):
        if self.criticos:
            return "risco_elevado_privacidade"

        if self.alertas:
            return "requer_controle_privacidade"

        return "sem_risco_adicional_detectado"


def analisar_lgpd_rh(
    funcionario,
    contexto=None,
    *,
    uso_ia=False,
    dados_minimizados=False,
):
    contexto = contexto or ContextoRegras()

    achados = []

    inventario = inventariar_dados_funcionario(
        funcionario
    )

    # ---------------------------------------------------------
    # Dados pessoais identificáveis
    # ---------------------------------------------------------
    if inventario.possui_dados_pessoais:
        achados.append(
            ResultadoRegra(
                codigo="LGPD_RH_DADOS_PESSOAIS",
                severidade="info",
                titulo="Dados pessoais presentes no cadastro de RH",
                descricao=(
                    "O cadastro contém dados pessoais identificáveis "
                    "necessários a controles de acesso, finalidade "
                    "e minimização."
                ),
                regra="LGPD_RH_DADOS_PESSOAIS",
                categoria="lgpd_rh",
                resultado="informativo",
                fato_verificado=(
                    "Foram identificadas categorias de dados pessoais "
                    "no cadastro do trabalhador."
                ),
                evidencia=(
                    "categorias="
                    + ",".join(inventario.dados_pessoais)
                ),
                fundamentacao=(
                    "LGPD - princípios da finalidade, adequação, "
                    "necessidade, segurança e prevenção."
                ),
                risco_glosa="",
                recomendacao=(
                    "Manter acesso restrito e utilizar somente os dados "
                    "necessários à finalidade da prestação de contas."
                ),
                origem_normativa="Lei Federal nº 13.709/2018 - LGPD",
            )
        )

    # ---------------------------------------------------------
    # Dados bancários
    # ---------------------------------------------------------
    if inventario.possui_dados_financeiros:
        achados.append(
            ResultadoRegra(
                codigo="LGPD_RH_DADOS_FINANCEIROS",
                severidade="alerta",
                titulo="Dados bancários presentes no cadastro",
                descricao=(
                    "Existem dados bancários associados ao trabalhador."
                ),
                regra="LGPD_RH_DADOS_FINANCEIROS",
                categoria="lgpd_rh",
                resultado="nao_verificado",
                fato_verificado=(
                    "O cadastro contém categorias de informações bancárias."
                ),
                evidencia=(
                    "categorias="
                    + ",".join(inventario.dados_financeiros)
                ),
                fundamentacao=(
                    "LGPD - necessidade de proteção contra acesso "
                    "não autorizado e tratamento excessivo."
                ),
                risco_glosa="",
                recomendacao=(
                    "Não expor banco, agência ou conta em pareceres, "
                    "logs ou telas quando não forem necessários à finalidade."
                ),
                origem_normativa="Lei Federal nº 13.709/2018 - LGPD",
            )
        )

    # ---------------------------------------------------------
    # Documentos potencialmente sensíveis
    # ---------------------------------------------------------
    documentos = Documento.objects.filter(
        pertence=funcionario
    )

    documentos_potencialmente_sensiveis = [
        documento
        for documento in documentos
        if documento_pode_conter_dado_sensivel(documento)
    ]

    if documentos_potencialmente_sensiveis:
        achados.append(
            ResultadoRegra(
                codigo="LGPD_RH_DOC_POTENCIALMENTE_SENSIVEL",
                severidade="critico",
                titulo="Documento pode conter dado pessoal sensível",
                descricao=(
                    "Foram localizados documentos cujos metadados indicam "
                    "possível conteúdo relacionado à saúde, biometria "
                    "ou outra categoria que exige tratamento reforçado."
                ),
                regra="LGPD_RH_DOC_POTENCIALMENTE_SENSIVEL",
                categoria="lgpd_rh",
                resultado="achado",
                fato_verificado=(
                    "Metadados documentais apresentam indícios de "
                    "conteúdo potencialmente sensível."
                ),
                evidencia=(
                    f"quantidade="
                    f"{len(documentos_potencialmente_sensiveis)}."
                ),
                fundamentacao=(
                    "A classificação é preventiva e não substitui "
                    "a leitura do documento. Dados de saúde e outras "
                    "categorias previstas na LGPD possuem proteção reforçada."
                ),
                risco_glosa="",
                recomendacao=(
                    "Restringir acesso, evitar reprodução desnecessária "
                    "e aplicar minimização ou anonimização quando possível."
                ),
                origem_normativa="Lei Federal nº 13.709/2018 - LGPD",
            )
        )

    # ---------------------------------------------------------
    # Uso de IA sem minimização
    # ---------------------------------------------------------
    if (
        uso_ia
        and not dados_minimizados
        and (
            inventario.possui_dados_pessoais
            or inventario.possui_dados_financeiros
            or documentos_potencialmente_sensiveis
        )
    ):
        achados.append(
            ResultadoRegra(
                codigo="LGPD_RH_IA_SEM_MINIMIZACAO",
                severidade="critico",
                titulo="Uso de IA sem minimização registrada",
                descricao=(
                    "O processamento assistido por IA foi indicado, "
                    "mas não há confirmação de minimização dos dados "
                    "antes do tratamento."
                ),
                regra="LGPD_RH_IA_SEM_MINIMIZACAO",
                categoria="lgpd_rh",
                resultado="achado",
                fato_verificado=(
                    "Uso de IA informado sem indicação de minimização."
                ),
                evidencia=(
                    "uso_ia=True; dados_minimizados=False."
                ),
                fundamentacao=(
                    "A LGPD estabelece o princípio da necessidade e "
                    "deveres de segurança e prevenção."
                ),
                risco_glosa="",
                recomendacao=(
                    "Antes do processamento assistido, remover ou mascarar "
                    "dados desnecessários e limitar o conteúdo ao mínimo "
                    "necessário à conferência."
                ),
                origem_normativa="Lei Federal nº 13.709/2018 - LGPD",
            )
        )

    # ---------------------------------------------------------
    # Uso de IA com minimização
    # ---------------------------------------------------------
    if uso_ia and dados_minimizados:
        achados.append(
            ResultadoRegra(
                codigo="LGPD_RH_IA_MINIMIZADA",
                severidade="info",
                titulo="Processamento assistido com minimização indicada",
                descricao=(
                    "O processamento assistido por IA foi informado "
                    "com indicação de minimização prévia dos dados."
                ),
                regra="LGPD_RH_IA_MINIMIZADA",
                categoria="lgpd_rh",
                resultado="informativo",
                fato_verificado=(
                    "Uso de IA com minimização declarada."
                ),
                evidencia=(
                    "uso_ia=True; dados_minimizados=True."
                ),
                fundamentacao=(
                    "Aplicação preventiva do princípio da necessidade."
                ),
                risco_glosa="",
                recomendacao=(
                    "Manter registro da finalidade, dados enviados, "
                    "responsável e salvaguardas adotadas."
                ),
                origem_normativa="Lei Federal nº 13.709/2018 - LGPD",
            )
        )

    return ResultadoLGPDRH(
        funcionario_id=funcionario.pk,
        inventario=inventario,
        achados=achados,
    )
