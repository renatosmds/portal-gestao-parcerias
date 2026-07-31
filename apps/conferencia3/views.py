import io

import xhtml2pdf.pisa as pisa
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.template.loader import get_template
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from django.views.generic import (
    ListView,
    UpdateView,
    DeleteView,
    CreateView
)
from django.views.generic.base import View, TemplateView
from reportlab.pdfgen import canvas

from .models import Conferencia3


# from conferencia3.models import Conferencia3

class Conferencia3List(ListView):
    model = Conferencia3

    # paginate_by = 10  # if pagination is desired

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['report_button'] = _("Employee report")
        return context

    # def get_queryset(self):
    #    empresa_logada = self.request.user.funcionario.empresa
    #    return Conferencia3.objects.filter(
    #        empresa=empresa_logada)

    success_url = reverse_lazy('list_conferencia3')


class Conferencia3Form:
    pass


class Conferencia3Update(UpdateView):
    model = Conferencia3
    form_class = Conferencia3Form

    # fields = ['id', 'numtermo', 'parcela', 'ordem', 'credor', 'tipo', 'CpfCnpj', 'rubricaNivel1',
    #           'rubricaNivel2', 'rubricaNivel3', 'especie', 'numero', 'data', 'comprovante', 'valor', 'fileBoleto',
    #           'fileNF', 'fileComprPag', 'fileOrcamentos', 'photo', 'conferido', 'notificado', 'aprovado', 'notificacao',
    #           'valor'
    #           ]

    def get_form_kwargs(self):
        kwargs = super(Conferencia3Update, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    # success_url = reverse_lazy('list_conferencia3')


class Conferencia3Delete(DeleteView):
    model = Conferencia3
    success_url = reverse_lazy('list_conferencia3')


class Conferencia3Create(CreateView):
    model = Conferencia3
    fields = ['id', 'numtermo', 'parcela', 'ordem', 'credor', 'tipo', 'CpfCnpj', 'rubricaNivel1',
              'rubricaNivel2', 'rubricaNivel3', 'especie', 'numero', 'data', 'comprovante', 'valor', 'fileBoleto',
              'fileNF', 'fileComprPag', 'fileOrcamentos', 'photo', 'conferido', 'notificado', 'aprovado', 'notificacao',
              'valor'
              ]
    success_url = reverse_lazy('list_conferencia3')

    def form_valid(self, form):
        funcionario = form.save(commit=False)
        username = funcionario.ordem.split(' ')[0]
        funcionario.empresa = self.request.user.funcionario.empresa
        funcionario.user = User.objects.create(username=username)
        funcionario.save()
        return super(Conferencia3Create, self).form_valid(form)


def relatorio_conferencia3(request):  # feito com reportlab
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Relatório de Prestação de Contas.pdf"'

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)

    p.drawString(200, 810, 'Relatorio de Prestação de Contas')

    # conferencia3 = Conferencia3.objects.filter(empresa=request.user.funcionario.empresa)

    str_ = 'Nome: %s | Hora Extra: %.2f'

    p.drawString(0, 800, '_' * 150)

    y = 750
    for conferencia3 in conferencia3:
        p.drawString(10, y, str_ % (
            conferencia3.credor, conferencia3.parcela))
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
    return Render.render('clientes/relatorio.html', params, 'myfile')


class Pdf(View):
    pass


class PdfDebug(TemplateView):
    template_name = 'clientes/relatorio.html'
