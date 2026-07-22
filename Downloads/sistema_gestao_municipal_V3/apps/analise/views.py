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
from django.utils.translation import gettext as _
from django.http import HttpResponse
from django.template.loader import get_template
import xhtml2pdf.pisa as pisa
from .models import Analise


class AnaliseList(ListView):
    model = Analise

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['report_button'] = _("Employee report")
        return context

    def get_queryset(self):
        empresa_logada = self.request.user.funcionario.empresa
        return Analise.objects.filter(empresa=empresa_logada)


class AnaliseUpdate(UpdateView):
    model = Analise
    fields = ['numtermo', 'nomeOSC', 'numRA', 'item', 'inconformidade', 'recomendacoes', 'posicaoSecretaria',
              'status'
              ]


class AnaliseDelete(DeleteView):
    model = Analise
    success_url = reverse_lazy('list_analise')


class AnaliseCreate(CreateView):
    model = Analise
    fields = ['numtermo', 'nomeOSC', 'numRA', 'item', 'inconformidade', 'recomendacoes', 'posicaoSecretaria',
              'status'
              ]

    def form_valid(self, form):
        funcionario = form.save(commit=False)
        username = funcionario.numParceria.split(' ')[0]
        funcionario.empresa = self.request.user.funcionario.empresa
        funcionario.user = User.objects.create(username=username)
        funcionario.save()
        return super(AnaliseCreate, self).form_valid(form)


def relatorio_analise(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="mypdf.pdf"'

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)

    p.drawString(200, 810, 'Relatorio de analise')

    analise = Analise.objects.filter(
        empresa=request.user.funcionario.empresa)

    str_ = 'Nome: %s | Hora Extra: %.2f'

    p.drawString(0, 800, '_' * 150)

    y = 750
    for analise in analise:
        p.drawString(10, y, str_ % (
            analise.nome, analise.total_horas_extra))
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
    return Render.render('analise/relatorio.html', params, 'myfile')


class Pdf(View):
    pass


class PdfDebug(TemplateView):
    template_name = 'analise/relatorio.html'
