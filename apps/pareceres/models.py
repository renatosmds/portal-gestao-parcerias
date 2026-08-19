from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class ParecerTecnico(models.Model):

    class Situacao(models.TextChoices):
        RASCUNHO = "RASCUNHO", "Rascunho"
        EM_REVISAO = "EM_REVISAO", "Em revis?o"
        FINALIZADO = "FINALIZADO", "Finalizado"
        CANCELADO = "CANCELADO", "Cancelado"
        SUBSTITUIDO = "SUBSTITUIDO", "Substitu?do"

    class TipoConclusao(models.TextChoices):
        EM_ANALISE = "EM_ANALISE", "Em an?lise"
        SEM_PENDENCIAS_RELEVANTES = (
            "SEM_PENDENCIAS_RELEVANTES",
            "Sem pend?ncias relevantes",
        )
        COM_RESSALVAS = "COM_RESSALVAS", "Com ressalvas"
        COM_PENDENCIAS_SANEAVEIS = (
            "COM_PENDENCIAS_SANEAVEIS",
            "Com pend?ncias sane?veis",
        )
        COM_IRREGULARIDADES = (
            "COM_IRREGULARIDADES",
            "Com irregularidades",
        )
        AGUARDANDO_DILIGENCIA = (
            "AGUARDANDO_DILIGENCIA",
            "Aguardando dilig?ncia",
        )
        INCONCLUSIVO = "INCONCLUSIVO", "Inconclusivo"

    prestacao = models.ForeignKey(
        "prestacao.Prestacao",
        on_delete=models.PROTECT,
        related_name="pareceres_tecnicos",
    )

    empresa = models.ForeignKey(
        "empresas.Empresa",
        on_delete=models.PROTECT,
        related_name="pareceres_tecnicos",
    )

    numero = models.CharField(
        max_length=50,
        blank=True,
        default="",
    )

    versao = models.PositiveIntegerField(
        default=1,
    )

    versao_anterior = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="versoes_posteriores",
    )

    situacao = models.CharField(
        max_length=20,
        choices=Situacao.choices,
        default=Situacao.RASCUNHO,
    )

    tipo_conclusao = models.CharField(
        max_length=40,
        choices=TipoConclusao.choices,
        default=TipoConclusao.EM_ANALISE,
    )

    resumo_executivo = models.TextField(
        blank=True,
        default="",
    )

    fundamentacao_geral = models.TextField(
        blank=True,
        default="",
    )

    conclusao = models.TextField(
        blank=True,
        default="",
    )

    ressalvas = models.TextField(
        blank=True,
        default="",
    )

    recomendacoes_gerais = models.TextField(
        blank=True,
        default="",
    )

    elaborado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="pareceres_elaborados",
    )

    revisado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="pareceres_revisados",
    )

    aprovado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="pareceres_aprovados",
    )

    elaborado_em = models.DateTimeField(
        auto_now_add=True,
    )

    revisado_em = models.DateTimeField(
        null=True,
        blank=True,
    )

    aprovado_em = models.DateTimeField(
        null=True,
        blank=True,
    )

    criado_em = models.DateTimeField(
        auto_now_add=True,
    )

    atualizado_em = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-criado_em", "-versao"]

        constraints = [
            models.UniqueConstraint(
                fields=["prestacao", "versao"],
                name="uniq_parecer_versao_prestacao",
            ),
        ]

    def __str__(self):
        referencia = self.numero or f"Parecer {self.pk or 'novo'}"
        return f"{referencia} - vers?o {self.versao}"

    def clean(self):
        erros = {}

        if (
            self.prestacao_id
            and self.empresa_id
            and self.prestacao.empresa_id
            and self.prestacao.empresa_id != self.empresa_id
        ):
            erros["empresa"] = (
                "A empresa do parecer deve ser a mesma "
                "empresa da presta??o de contas."
            )

        if self.versao_anterior_id:

            if self.versao_anterior_id == self.pk:
                erros["versao_anterior"] = (
                    "Um parecer n?o pode referenciar "
                    "a si pr?prio como vers?o anterior."
                )

            elif (
                self.prestacao_id
                and self.versao_anterior.prestacao_id
                != self.prestacao_id
            ):
                erros["versao_anterior"] = (
                    "A vers?o anterior deve pertencer "
                    "? mesma presta??o de contas."
                )

            elif self.versao_anterior.versao >= self.versao:
                erros["versao_anterior"] = (
                    "A vers?o anterior deve possuir "
                    "n?mero inferior ? vers?o atual."
                )

        if erros:
            raise ValidationError(erros)


class ItemParecer(models.Model):

    class Categoria(models.TextChoices):
        DOCUMENTAL = "DOCUMENTAL", "Documental"
        FINANCEIRA = "FINANCEIRA", "Financeira"
        PLANO_TRABALHO = "PLANO_TRABALHO", "Plano de trabalho"
        RH = "RH", "Recursos humanos"
        LGPD = "LGPD", "LGPD"
        VIGENCIA = "VIGENCIA", "Vig?ncia"
        OUTRA = "OUTRA", "Outra"

    class Severidade(models.TextChoices):
        INFORMATIVA = "INFORMATIVA", "Informativa"
        ALERTA = "ALERTA", "Alerta"
        CRITICA = "CRITICA", "Cr?tica"

    class Origem(models.TextChoices):
        MANUAL = "MANUAL", "Manual"
        PGP_RULES = "PGP_RULES", "PGP Rules"
        IA_ASSISTIDA = "IA_ASSISTIDA", "IA assistida"
        DILIGENCIA = "DILIGENCIA", "Dilig?ncia"
        OUTRA = "OUTRA", "Outra"

    class ConclusaoItem(models.TextChoices):
        NAO_ANALISADO = "NAO_ANALISADO", "N?o analisado"
        REGULAR = "REGULAR", "Regular"
        RESSALVA = "RESSALVA", "Ressalva"
        PENDENCIA_SANEAVEL = (
            "PENDENCIA_SANEAVEL",
            "Pend?ncia sane?vel",
        )
        IRREGULARIDADE = "IRREGULARIDADE", "Irregularidade"
        SANADO = "SANADO", "Sanado"
        NAO_SANADO = "NAO_SANADO", "N?o sanado"

    parecer = models.ForeignKey(
        ParecerTecnico,
        on_delete=models.CASCADE,
        related_name="itens",
    )

    codigo = models.CharField(
        max_length=100,
        blank=True,
        default="",
    )

    codigo_regra = models.CharField(
        max_length=120,
        blank=True,
        default="",
    )

    categoria = models.CharField(
        max_length=30,
        choices=Categoria.choices,
        default=Categoria.DOCUMENTAL,
    )

    severidade = models.CharField(
        max_length=20,
        choices=Severidade.choices,
        default=Severidade.ALERTA,
    )

    origem = models.CharField(
        max_length=20,
        choices=Origem.choices,
        default=Origem.MANUAL,
    )

    titulo = models.CharField(
        max_length=255,
    )

    descricao = models.TextField(
        blank=True,
        default="",
    )

    fato_verificado = models.TextField(
        blank=True,
        default="",
    )

    evidencia = models.TextField(
        blank=True,
        default="",
    )

    fundamentacao = models.TextField(
        blank=True,
        default="",
    )

    risco_glosa = models.TextField(
        blank=True,
        default="",
    )

    recomendacao = models.TextField(
        blank=True,
        default="",
    )

    manifestacao_analista = models.TextField(
        blank=True,
        default="",
    )

    conclusao_item = models.CharField(
        max_length=30,
        choices=ConclusaoItem.choices,
        default=ConclusaoItem.NAO_ANALISADO,
    )

    resultado_origem = models.CharField(
        max_length=50,
        blank=True,
        default="",
    )

    origem_normativa = models.TextField(
        blank=True,
        default="",
    )

    dados_origem = models.JSONField(
        blank=True,
        default=dict,
    )

    lancamento = models.ForeignKey(
        "lancamentos.Lancamento",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="itens_parecer",
    )

    documento = models.ForeignKey(
        "documentos.Documento",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="itens_parecer",
    )

    diligencia = models.ForeignKey(
        "diligencias.Diligencia",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="itens_parecer",
    )

    ordem = models.PositiveIntegerField(
        default=0,
    )

    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="itens_parecer_criados",
    )

    criado_em = models.DateTimeField(
        auto_now_add=True,
    )

    atualizado_em = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["ordem", "id"]

        constraints = [
            models.UniqueConstraint(
                fields=["parecer", "codigo"],
                condition=~models.Q(codigo=""),
                name="uniq_codigo_item_por_parecer",
            ),
        ]

    def __str__(self):
        return self.codigo or self.titulo or f"Item {self.pk or 'novo'}"

    def clean(self):
        erros = {}

        if not self.parecer_id:
            return

        prestacao_id = self.parecer.prestacao_id
        empresa_id = self.parecer.empresa_id

        if self.lancamento_id:

            if (
                self.lancamento.prestacao_id
                and prestacao_id
                and self.lancamento.prestacao_id != prestacao_id
            ):
                erros["lancamento"] = (
                    "O lan?amento deve pertencer ? mesma "
                    "presta??o do parecer."
                )

            if (
                self.lancamento.empresa_id
                and empresa_id
                and self.lancamento.empresa_id != empresa_id
            ):
                erros["lancamento"] = (
                    "O lan?amento deve pertencer ? mesma "
                    "empresa do parecer."
                )

        if self.documento_id:

            if (
                self.documento.prestacao_id
                and prestacao_id
                and self.documento.prestacao_id != prestacao_id
            ):
                erros["documento"] = (
                    "O documento deve pertencer ? mesma "
                    "presta??o do parecer."
                )

            if (
                self.documento.empresa_id
                and empresa_id
                and self.documento.empresa_id != empresa_id
            ):
                erros["documento"] = (
                    "O documento deve pertencer ? mesma "
                    "empresa do parecer."
                )

        if self.diligencia_id:

            if (
                self.diligencia.prestacao_id
                and prestacao_id
                and self.diligencia.prestacao_id != prestacao_id
            ):
                erros["diligencia"] = (
                    "A dilig?ncia deve pertencer ? mesma "
                    "presta??o do parecer."
                )

            if (
                self.diligencia.empresa_id
                and empresa_id
                and self.diligencia.empresa_id != empresa_id
            ):
                erros["diligencia"] = (
                    "A dilig?ncia deve pertencer ? mesma "
                    "empresa do parecer."
                )

        if erros:
            raise ValidationError(erros)


class HistoricoParecer(models.Model):

    parecer = models.ForeignKey(
        ParecerTecnico,
        on_delete=models.CASCADE,
        related_name="historico",
    )

    acao = models.CharField(
        max_length=100,
    )

    situacao_anterior = models.CharField(
        max_length=20,
        blank=True,
        default="",
    )

    nova_situacao = models.CharField(
        max_length=20,
        blank=True,
        default="",
    )

    conclusao_anterior = models.CharField(
        max_length=40,
        blank=True,
        default="",
    )

    nova_conclusao = models.CharField(
        max_length=40,
        blank=True,
        default="",
    )

    observacao = models.TextField(
        blank=True,
        default="",
    )

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="historicos_parecer",
    )

    criado_em = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-criado_em", "-id"]

    def __str__(self):
        return f"{self.parecer} - {self.acao}"



class EvidenciaParecer(models.Model):

    class Tipo(models.TextChoices):
        DOCUMENTO = "DOCUMENTO", "Documento"
        LANCAMENTO = "LANCAMENTO", "Lan?amento"
        DILIGENCIA = "DILIGENCIA", "Dilig?ncia"
        REGISTRO_SISTEMA = "REGISTRO_SISTEMA", "Registro do sistema"
        DECLARACAO = "DECLARACAO", "Declara??o"
        OUTRA = "OUTRA", "Outra"

    item = models.ForeignKey(
        ItemParecer,
        on_delete=models.CASCADE,
        related_name="evidencias_estruturadas",
    )

    tipo = models.CharField(
        max_length=30,
        choices=Tipo.choices,
        default=Tipo.OUTRA,
    )

    descricao = models.TextField()

    documento = models.ForeignKey(
        "documentos.Documento",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="evidencias_parecer",
    )

    lancamento = models.ForeignKey(
        "lancamentos.Lancamento",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="evidencias_parecer",
    )

    diligencia = models.ForeignKey(
        "diligencias.Diligencia",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="evidencias_parecer",
    )

    referencia_externa = models.CharField(
        max_length=500,
        blank=True,
        default="",
    )

    dados_snapshot = models.JSONField(
        blank=True,
        default=dict,
    )

    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="evidencias_parecer_criadas",
    )

    criado_em = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.item} - {self.get_tipo_display()}"

    def clean(self):
        erros = {}

        parecer = self.item.parecer

        if self.documento_id:
            if (
                self.documento.prestacao_id
                and parecer.prestacao_id
                and self.documento.prestacao_id
                != parecer.prestacao_id
            ):
                erros["documento"] = (
                    "O documento deve pertencer ? mesma presta??o do parecer."
                )

            if (
                self.documento.empresa_id
                and parecer.empresa_id
                and self.documento.empresa_id
                != parecer.empresa_id
            ):
                erros["documento"] = (
                    "O documento deve pertencer ? mesma empresa do parecer."
                )

        if self.lancamento_id:
            if (
                self.lancamento.prestacao_id
                and parecer.prestacao_id
                and self.lancamento.prestacao_id
                != parecer.prestacao_id
            ):
                erros["lancamento"] = (
                    "O lan?amento deve pertencer ? mesma presta??o do parecer."
                )

            if (
                self.lancamento.empresa_id
                and parecer.empresa_id
                and self.lancamento.empresa_id
                != parecer.empresa_id
            ):
                erros["lancamento"] = (
                    "O lan?amento deve pertencer ? mesma empresa do parecer."
                )

        if self.diligencia_id:
            if (
                self.diligencia.prestacao_id
                and parecer.prestacao_id
                and self.diligencia.prestacao_id
                != parecer.prestacao_id
            ):
                erros["diligencia"] = (
                    "A dilig?ncia deve pertencer ? mesma presta??o do parecer."
                )

            if (
                self.diligencia.empresa_id
                and parecer.empresa_id
                and self.diligencia.empresa_id
                != parecer.empresa_id
            ):
                erros["diligencia"] = (
                    "A dilig?ncia deve pertencer ? mesma empresa do parecer."
                )

        if erros:
            raise ValidationError(erros)


class FundamentacaoParecer(models.Model):

    class Esfera(models.TextChoices):
        FEDERAL = "FEDERAL", "Federal"
        ESTADUAL = "ESTADUAL", "Estadual"
        MUNICIPAL = "MUNICIPAL", "Municipal"
        INTERNA = "INTERNA", "Norma interna"
        OUTRA = "OUTRA", "Outra"

    item = models.ForeignKey(
        ItemParecer,
        on_delete=models.CASCADE,
        related_name="fundamentacoes_estruturadas",
    )

    esfera = models.CharField(
        max_length=20,
        choices=Esfera.choices,
        default=Esfera.OUTRA,
    )

    ente = models.CharField(
        max_length=255,
        blank=True,
        default="",
    )

    norma = models.CharField(
        max_length=255,
    )

    dispositivo = models.CharField(
        max_length=255,
        blank=True,
        default="",
    )

    descricao = models.TextField(
        blank=True,
        default="",
    )

    inicio_vigencia = models.DateField(
        null=True,
        blank=True,
    )

    fim_vigencia = models.DateField(
        null=True,
        blank=True,
    )

    origem = models.CharField(
        max_length=500,
        blank=True,
        default="",
    )

    dados_snapshot = models.JSONField(
        blank=True,
        default=dict,
    )

    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="fundamentacoes_parecer_criadas",
    )

    criado_em = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["esfera", "norma", "dispositivo", "id"]

    def __str__(self):
        referencia = self.norma
        if self.dispositivo:
            referencia += f" - {self.dispositivo}"
        return referencia

    def clean(self):
        erros = {}

        if (
            self.inicio_vigencia
            and self.fim_vigencia
            and self.fim_vigencia < self.inicio_vigencia
        ):
            erros["fim_vigencia"] = (
                "O fim da vig?ncia n?o pode ser anterior ao in?cio."
            )

        if erros:
            raise ValidationError(erros)
