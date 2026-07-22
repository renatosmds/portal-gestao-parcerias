import io

from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    UpdateView,
    DeleteView,
    CreateView
)
from django.views.generic.base import View, TemplateView
from reportlab.pdfgen import canvas

from django.http import HttpResponse
from django.template.loader import get_template
import xhtml2pdf.pisa as pisa

from .models import Prestacao

from django.utils.translation import gettext as _


class PrestacaoList(ListView):
    model = Prestacao

    #    paginate_by = 15 # if pagination is desired

    def get_queryset(self):
       empresa_logada = self.request.user.funcionario.empresa
       return Prestacao.objects.filter(empresa=empresa_logada)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['report_button'] = _("Employee report")
        return context


class PrestacaoEdit(UpdateView):
    model = Prestacao
    fields = ['id', 'tipoTermo', 'numtermo', 'termoAditivo', 'credor', 'numCredor', 'tipo', 'CpfCnpj', 'oficioCcoaf', 'sco',
              'agCredito', 'ccCredito', 'uo', 'funcao', 'subfuncao', 'programa', 'projeto', 'natureza', 'fonte',
              'bancoCredor', 'agCredor', 'ccCredor', 'cod_reduz', 'gestora', 'matricula', 'contato', 'valorContrato',
              'qtdParcelas', 'mesParcela1', 'anoParcela1', 'valorParcela1', 'empenhoParcela1', 'napParcela1',
              'dataNapParcela1', 'mesParcela2', 'anoParcela2', 'valorParcela2', 'empenhoParcela2', 'napParcela2',
              'dataNapParcela2', 'mesParcela3', 'anoParcela3', 'valorParcela3', 'empenhoParcela3', 'napParcela3',
              'dataNapParcela3', 'mesParcela4', 'anoParcela4', 'valorParcela4', 'empenhoParcela4', 'napParcela4',
              'dataNapParcela4', 'mesParcela5', 'anoParcela5', 'valorParcela5', 'empenhoParcela5', 'napParcela5',
              'dataNapParcela5', 'mesParcela6', 'anoParcela6', 'valorParcela6', 'empenhoParcela6', 'napParcela6',
              'dataNapParcela6', 'mesParcela7', 'anoParcela7', 'valorParcela7', 'empenhoParcela7', 'napParcela7',
              'dataNapParcela7', 'mesParcela8', 'anoParcela8', 'valorParcela8', 'empenhoParcela8', 'napParcela8',
              'dataNapParcela8', 'mesParcela9', 'anoParcela9', 'valorParcela9', 'empenhoParcela9', 'napParcela9',
              'dataNapParcela9', 'mesParcela10', 'anoParcela10', 'valorParcela10', 'empenhoParcela10', 'napParcela10',
              'dataNapParcela10', 'mesParcela11', 'anoParcela11', 'valorParcela11', 'empenhoParcela11', 'napParcela11',
              'dataNapParcela11', 'mesParcela12', 'anoParcela12', 'valorParcela12', 'empenhoParcela12', 'napParcela12',
              'dataNapParcela12', 'concluida']
    success_url = reverse_lazy('list_prestacao')


class PrestacaoDelete(DeleteView):
    model = Prestacao
    success_url = reverse_lazy('list_prestacao')


class PrestacaoCreate(CreateView):
    model = Prestacao
    fields = ['id', 'tipoTermo', 'numtermo', 'termoAditivo', 'credor', 'numCredor', 'tipo', 'CpfCnpj', 'oficioCcoaf',
              'sco', 'agCredito', 'ccCredito', 'uo', 'funcao', 'subfuncao', 'programa', 'projeto', 'natureza',
              'fonte', 'bancoCredor', 'agCredor', 'ccCredor', 'cod_reduz', 'gestora', 'matricula', 'contato',
              'valorContrato', 'qtdParcelas', 'mesParcela1', 'anoParcela1', 'valorParcela1', 'empenhoParcela1',
              'napParcela1', 'dataNapParcela1', 'mesParcela2', 'anoParcela2', 'valorParcela2', 'empenhoParcela2',
              'napParcela2', 'dataNapParcela2', 'mesParcela3', 'anoParcela3', 'valorParcela3', 'empenhoParcela3',
              'napParcela3', 'dataNapParcela3', 'mesParcela4', 'anoParcela4', 'valorParcela4', 'empenhoParcela4',
              'napParcela4', 'dataNapParcela4', 'mesParcela5', 'anoParcela5', 'valorParcela5', 'empenhoParcela5',
              'napParcela5', 'dataNapParcela5', 'mesParcela6', 'anoParcela6', 'valorParcela6', 'empenhoParcela6',
              'napParcela6', 'dataNapParcela6', 'mesParcela7', 'anoParcela7', 'valorParcela7', 'empenhoParcela7',
              'napParcela7', 'dataNapParcela7', 'mesParcela8', 'anoParcela8', 'valorParcela8', 'empenhoParcela8',
              'napParcela8', 'dataNapParcela8', 'mesParcela9', 'anoParcela9', 'valorParcela9', 'empenhoParcela9',
              'napParcela9', 'dataNapParcela9', 'mesParcela10', 'anoParcela10', 'valorParcela10', 'empenhoParcela10',
              'napParcela10', 'dataNapParcela10', 'mesParcela11', 'anoParcela11', 'valorParcela11', 'empenhoParcela11',
              'napParcela11', 'dataNapParcela11', 'mesParcela12', 'anoParcela12', 'valorParcela12', 'empenhoParcela12',
              'napParcela12', 'dataNapParcela12', 'concluida']
    success_url = reverse_lazy('list_prestacao')

    def form_valid(self, form):
        funcionario = form.save(commit=False)
        username = funcionario.numtermo.split(' ')[0]
        funcionario.empresa = self.request.user.funcionario.empresa
        funcionario.user = User.objects.create(username=username)
        funcionario.save()
        return super(PrestacaoCreate, self).form_valid(form)


def relatorio_prestacao(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="mypdf.pdf"'

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)

    p.drawString(200, 810, 'Relatorio de prestacao')

    prestacao = Prestacao.objects.filter(
        empresa=request.user.funcionario.empresa)

    str_ = 'Nome: %s | Hora Extra: %.2f'

    p.drawString(0, 800, '_' * 150)

    y = 750
    for prestacao in prestacao:
        p.drawString(10, y, str_ % (
            prestacao.nome, prestacao.total_horas_extra))
        y -= 20

    p.showPage()
    p.save()

    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)

    return response


class Render:
    @staticmethod
    def render(path: str, params: dict, filename: str):
        template = get_template(path)
        html = template.render(params)
        response = io.BytesIO()
        pdf = pisa.pisaDocument(
            io.BytesIO(html.encode("UTF-8")), response)
        if not pdf.err:
            response = HttpResponse(
                response.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = 'attachment;filename=%s.pdf' % filename
            return response
        else:
            return HttpResponse("Error Rendering PDF", status=400)


def get(request):
    params = {
        'today': 'Variavel today',
        'sales': 'Variavel sales',
        'request': request,
    }
    return Render.render('prestacao/relatorio.html', params, 'myfile')


class Pdf(View):
    pass


class PdfDebug(TemplateView):
    template_name = 'prestacao/relatorio.html'
