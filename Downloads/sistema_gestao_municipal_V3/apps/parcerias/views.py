import io
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView
)
from django.views.generic.base import View, TemplateView
from reportlab.pdfgen import canvas
from django.utils.translation import gettext as _
from django.http import HttpResponse
from django.template.loader import get_template
import xhtml2pdf.pisa as pisa
from .models import Parcerias


class ParceriasList(ListView):
    model = Parcerias
    success_url = reverse_lazy('list_parcerias')

    # paginate_by = 100 # if pagination is desired

    def parcerias_list(request):
        data = {'usuario': request.user}
        funcionario = request.user.funcionario
        data['result'] = funcionario.empresa.total_funcionarios
        data['total_funcionarios'] = funcionario.empresa.total_funcionarios
        data['result1'] = funcionario.empresa.total_funcionarios_ferias
        data['total_funcionarios_ferias'] = funcionario.empresa.total_funcionarios_ferias
        data['result2'] = funcionario.empresa.total_funcionarios_doc_pendente
        data['total_funcionarios_doc_pendente'] = funcionario.empresa.total_funcionarios_doc_pendente
        data['result3'] = funcionario.empresa.total_funcionarios_doc_ok
        data['total_funcionarios_doc_ok'] = funcionario.empresa.total_funcionarios_doc_ok
        data['total_funcionarios_rg'] = 10
        data['result4'] = RegistroHoraExtra.objects.filter(
            funcionario__empresa=funcionario.empresa, utilizada=True).aggregate(Sum('horas'))['horas__sum'] or 0
        data['total_hora_extra_utilizadas'] = RegistroHoraExtra.objects.filter(
            funcionario__empresa=funcionario.empresa, utilizada=True).aggregate(Sum('horas'))['horas__sum'] or 0
        data['result5'] = RegistroHoraExtra.objects.filter(
            funcionario__empresa=funcionario.empresa, utilizada=False).aggregate(Sum('horas'))['horas__sum'] or 0
        data['total_hora_extra_pendente'] = RegistroHoraExtra.objects.filter(
            funcionario__empresa=funcionario.empresa, utilizada=False).aggregate(Sum('horas'))['horas__sum'] or 0

        return render(request, 'clientes/clientes_list.html', data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['report_button'] = _("Employee report")
        return context

    # @property
    def get_queryset(self):
       empresa_logada = self.request.user.funcionario.empresa
       return Parcerias.objects.filter(empresa=empresa_logada)


class ParceriaUpdate(UpdateView):
    model = Parcerias
    fields = ['numtermo', 'nomeOSC', 'fileTC', 'numRA', 'numOficioRA', 'fileRA', 'fileOficioRA', 'dtRaSMDS',
              'respRA', 'numRE', 'numOficioRE', 'fileRE', 'fileOficioRE', 'dtReSMDS', 'respRE', 'fileRRE',
              'prazoFinal', 'status', 'prazoDecorrido', 'prazoRestante', 'historico', 'concluido', 'photo'
              ]

    success_url = reverse_lazy('list_parcerias')


class ParceriaDelete(DeleteView):
    model = Parcerias
    success_url = reverse_lazy('list_parcerias')


class ParceriaCreate(CreateView):
    model = Parcerias
    fields = ['numtermo', 'nomeOSC', 'fileTC', 'numRA', 'numOficioRA', 'fileRA', 'fileOficioRA', 'dtRaSMDS',
              'respRA', 'numRE', 'numOficioRE', 'fileRE', 'fileOficioRE', 'dtReSMDS', 'respRE', 'fileRRE',
              'prazoFinal', 'status', 'prazoDecorrido', 'prazoRestante', 'historico', 'concluido', 'photo'
              ]

    success_url = reverse_lazy('list_parcerias')

    def form_valid(self, form):
       funcionario = form.save(commit=False)
       username = funcionario.numtermo.split(' ')[0]
       funcionario.empresa = self.request.user.funcionario.empresa
       funcionario.user = User.objects.create(username=username)
       funcionario.save()
       return super(ParceriaCreate, self).form_valid(form)


def relatorio_parcerias(request):  # feito com reportlab
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Relatório de Parcerias.pdf"'

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)

    p.drawString(200, 810, 'Relatorio de parcerias')

    parcerias = Parcerias.objects.filter(
        empresa=request.user.funcionario.empresa)

    str_ = 'Nome: %s | Hora Extra: %.2f'

    p.drawString(0, 800, '_' * 150)

    y = 750
    for parcerias in parcerias:
        p.drawString(10, y, str_ % (
            parcerias.numParceria, parcerias.total_horas_extra))
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
    return Render.render('parcerias/relatorio.html', params, 'Relatório de Parceiras')


class Pdf(View):
    pass


class PdfDebug(TemplateView):
    template_name = 'parcerias/relatorio.html'
