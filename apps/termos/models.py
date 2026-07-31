# coding=utf-8
from django.db import models
from django.urls import reverse


class Termos(models.Model):
    class Meta:
        ordering = ["termo", "numtermo"]
        verbose_name = "Termo"
        verbose_name_plural = "Termos"

    nomeosc = models.CharField(max_length=50, blank=True, null=True, verbose_name="Nome da OSC")
    numtermo = models.CharField(max_length=10, blank=True, null=True, verbose_name="Nº Termo")
    numpa = models.CharField(max_length=10, blank=True, null=True, verbose_name="Nº do P.A.")
    vigencia = models.CharField(max_length=25, blank=True, null=True, verbose_name="Vigência")
    assinatura = models.DateField(blank=True, null=True, verbose_name="Assinatura")
    valorglobal = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True, verbose_name="Valor Global")
    valorrepasse = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True, verbose_name="Valor Repassado")
    valorsaldo = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True, verbose_name="Valor Saldo")
    parcelasAbertas = models.CharField(max_length=10, blank=True, null=True, verbose_name="Parcelas Abertas")
    numdispensa = models.CharField(max_length=10, blank=True, null=True, verbose_name="Nº Dispensa")
    nomemunicipio = models.CharField(max_length=100, blank=True, null=True, verbose_name="Nº Beneficiários")
    nomeintermediario = models.CharField(max_length=100, blank=True, null=True, verbose_name="Nome Intermediário")
    nomesecretario = models.CharField(max_length=100, blank=True, null=True, verbose_name="Nome Secretário(a)")
    nomerepresentante = models.CharField(max_length=100, blank=True, null=True, verbose_name="Nome Representante")

    tipo = models.CharField(max_length=100, blank=True, null=True, verbose_name="Tipo")
    termo = models.CharField(max_length=100, blank=True, null=True, verbose_name="Termo")
    apelido = models.CharField(max_length=100, blank=True, null=True, verbose_name="Apelido")
    parceria = models.CharField(max_length=100, blank=True, null=True, verbose_name="Parceria")
    objeto = models.CharField(max_length=100, blank=True, null=True, verbose_name="Objeto")
    relatoriosDeSinteses = models.CharField(max_length=100, blank=True, null=True, verbose_name="Relatórios de Sínteses")
    inicioVigencia = models.CharField(max_length=100, blank=True, null=True, verbose_name="Início Vigência")
    terminoVigencia = models.CharField(max_length=100, blank=True, null=True, verbose_name="Término Vigência")
    analista = models.CharField(max_length=100, blank=True, null=True, verbose_name="Analista")
    status = models.CharField(max_length=100, blank=True, null=True, verbose_name="Status")
    saldoDashboard = models.CharField(max_length=100, blank=True, null=True, verbose_name="Saldo (Dashboard)")
    saldoContaSinteseDespesas = models.CharField(max_length=100, blank=True, null=True, verbose_name="Saldo Conta (Síntese Despesas)")
    rendimento = models.CharField(max_length=100, blank=True, null=True, verbose_name="Rendimento")
    saldoContaSinteseMovFinanceira = models.CharField(max_length=100, blank=True, null=True, verbose_name="Saldo Conta (Síntese Mov. Financeira)")
    valorDevolvido = models.CharField(max_length=100, blank=True, null=True, verbose_name="Valor Devolvido")
    saldoFinal = models.CharField(max_length=100, blank=True, null=True, verbose_name="Saldo Final")
    totalDeLacamentos = models.CharField(max_length=5, blank=True, null=True, verbose_name="Total de Lançamentos")
    lacamentosRegulares = models.CharField(max_length=5, blank=True, null=True, verbose_name="Lançamentos Regulares")
    lacamentosIrregulares = models.CharField(max_length=5, blank=True, null=True, verbose_name="Lançamentos Irregulares")
    lacamentosGlosados = models.CharField(max_length=5, blank=True, null=True, verbose_name="Lançamentos Glosados")
    lacamentosNaoEnviados = models.CharField(max_length=5, blank=True, null=True, verbose_name="Lançamentos Não Enviados")
    naoanalisados = models.CharField(max_length=5, blank=True, null=True, verbose_name="Lançamentos Não Analisados")
    total = models.CharField(max_length=5, blank=True, null=True, verbose_name="Total")
    extratosBancarios = models.CharField(max_length=3, blank=True, null=True, verbose_name="Extratos Bancários")
    pendenciasOfx = models.CharField(max_length=5, blank=True, null=True, verbose_name="Pendências OFX")
    valoresGlosados = models.CharField(max_length=10, blank=True, null=True, verbose_name="Valores Glosados")
    glosasRestituidas = models.CharField(max_length=10, blank=True, null=True, verbose_name="Glosas Restituídas")
    saldoGlosas = models.CharField(max_length=10, blank=True, null=True, verbose_name="Saldo Glosas")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")

    fileOficio = models.FileField(upload_to="prestacao_photos", blank=True, null=True, verbose_name="Ofícios")
    fileTermo = models.FileField(upload_to="prestacao_photos", blank=True, null=True, verbose_name="Termos / Aditivos")
    filePlanoTrabalho = models.FileField(upload_to="prestacao_photos", blank=True, null=True, verbose_name="Planos de Trabalho")
    fileEmpenho = models.FileField(upload_to="prestacao_photos", blank=True, null=True, verbose_name="Empenhos")
    fileNap = models.FileField(upload_to="prestacao_photos", blank=True, null=True, verbose_name="NAP's")
    fileAtesto = models.FileField(upload_to="prestacao_photos", blank=True, null=True, verbose_name="Recibos de Atesto")
    fileCertidao = models.FileField(upload_to="prestacao_photos", blank=True, null=True, verbose_name="Certidões")
    fileOficioFia = models.FileField(upload_to="prestacao_photos", blank=True, null=True, verbose_name="Ofícios FIA")

    empresa = models.ForeignKey(
        "empresas.Empresa",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="termos_vinculados",
        related_query_name="termo_vinculado",
        verbose_name="Empresa",
    )

    def get_absolute_url(self):
        return reverse("detail_termo", kwargs={"pk": self.pk})

    def __str__(self):
        return self.termo or self.numtermo or self.apelido or f"Termo #{self.pk}"
