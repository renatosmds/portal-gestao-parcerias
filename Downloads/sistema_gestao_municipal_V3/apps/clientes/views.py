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

from django.shortcuts import render
from .models import Clientes
from .forms import ClientesForm


class ClientesList(ListView):
    model = Clientes
    success_url = reverse_lazy('list_clientes')

#    def Clientes_list(request):
#        data = {'usuario': request.user}
#        funcionario = request.user.funcionario
#        data['result'] = funcionario.empresa.total_funcionarios
#        data['total_funcionarios'] = funcionario.empresa.total_funcionarios
#        data['result1'] = funcionario.empresa.total_funcionarios_ferias
#        data['total_funcionarios_ferias'] = funcionario.empresa.total_funcionarios_ferias
#        data['result2'] = funcionario.empresa.total_funcionarios_doc_pendente
#        data['total_funcionarios_doc_pendente'] = funcionario.empresa.total_funcionarios_doc_pendente
#        data['result3'] = funcionario.empresa.total_funcionarios_doc_ok
#        data['total_funcionarios_doc_ok'] = funcionario.empresa.total_funcionarios_doc_ok
#        data['total_funcionarios_rg'] = 10
#        data['result4'] = RegistroHoraExtra.objects.filter(
#            funcionario__empresa=funcionario.empresa, utilizada=True).aggregate(Sum('horas'))['horas__sum'] or 0
#        data['total_hora_extra_utilizadas'] = RegistroHoraExtra.objects.filter(
#            funcionario__empresa=funcionario.empresa, utilizada=True).aggregate(Sum('horas'))['horas__sum'] or 0
#        data['result5'] = RegistroHoraExtra.objects.filter(
#            funcionario__empresa=funcionario.empresa, utilizada=False).aggregate(Sum('horas'))['horas__sum'] or 0
#        data['total_hora_extra_pendente'] = RegistroHoraExtra.objects.filter(
#            funcionario__empresa=funcionario.empresa, utilizada=False).aggregate(Sum('horas'))['horas__sum'] or 0

#        return render(request, 'clientes/clientes_list.html', data)

#    def get_context_data(self, **kwargs):
#        context = super().get_context_data(**kwargs)
#        context['report_button'] = _("Employee report")
#        return context

#    def get_queryset(self):
#        empresa_logada = self.request.user.funcionario.empresa
#        return Clientes.objects.filter(empresa=empresa_logada)


class ClientesUpdate(UpdateView):
    model = Clientes
    fields = ['first_name', 'last_name', 'age', 'salary', 'bio', 'photo'
              ]


class ClientesDelete(DeleteView):
    model = Clientes
    success_url = reverse_lazy('list_clientes')


class ClientesCreate(CreateView):
    model = Clientes
    fields = ['first_name', 'last_name', 'age', 'salary', 'bio', 'photo'
              ]

#    def form_valid(self, form):
#        funcionario = form.save(commit=False)
#        username = funcionario.first_name.split(' ')[0]
#        funcionario.empresa = self.request.user.funcionario.empresa
#        funcionario.user = User.objects.create(username=username)
#        funcionario.save()
#        return super(ClientesCreate, self).form_valid(form)


def relatorio_clientes(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="mypdf.pdf"'

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)

    p.drawString(200, 810, 'Relatorio de Clientes')

#    clientes = Clientes.objects.filter(
#        empresa=request.user.funcionario.empresa)

    str_ = 'Nome: %s | Hora Extra: %.2f'

    p.drawString(0, 800, '_' * 150)

    y = 750
    for clientes in clientes:
        p.drawString(10, y, str_ % (
            clientes.first_name, clientes.total_horas_extra))
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
