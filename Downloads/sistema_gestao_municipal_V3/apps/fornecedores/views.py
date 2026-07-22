import io
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.views.generic.base import View, TemplateView
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from django.template.loader import get_template
import xhtml2pdf.pisa as pisa
from django.utils.translation import gettext as _
from .models import Fornecedores


class FornecedoresList(ListView):
    model = Fornecedores

    success_url = reverse_lazy('list_fornecedores')

    #    paginate_by = 100 # if pagination is desired

    # @property
    # def get_queryset(self):
    #    empresa_logada = self.request.user.funcionario.empresa
    #    return Fornecedores.objects.filter(empresa=empresa_logada)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['report_button'] = _("Employee report")
        return context


class FornecedorDelete(DeleteView):
    model = Fornecedores
    success_url = reverse_lazy('list_fornecedores')


class FornecedorCreate(CreateView):
    model = Fornecedores
    fields = ['credor', 'pessoa', 'razao', 'tipo', 'numero', 'fantasia', 'endereco', 'bairro', 'cep', 'cidade',
              'estado', 'email', 'telefone', 'iestadual', 'imunicipal'
              ]
    success_url = reverse_lazy('list_fornecedores')

    def form_valid(self, form):
        funcionario = form.save(commit=False)
        username = funcionario.credor.split(' ')[0]
        funcionario.empresa = self.request.user.funcionario.empresa
        funcionario.user = User.objects.create(username=username)
        funcionario.save()
        return super(FornecedorCreate, self).form_valid(form)


class FornecedorUpdate(UpdateView):
    model = Fornecedores
    fields = ['credor', 'pessoa', 'razao', 'tipo', 'numero', 'fantasia', 'endereco', 'bairro', 'cep', 'cidade',
              'estado', 'email', 'telefone', 'iestadual', 'imunicipal'
              ]
    success_url = reverse_lazy('list_fornecedores')


def relatorio_fornecedor(request):  # feito com reportlab
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Relatório de Fornecedores.pdf"'

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)

    p.drawString(200, 810, 'Relatorio de fornecedores')

    fornecedores = Fornecedores.objects.filter(
        empresa=request.user.funcionario.empresa)

    str_ = 'Nome: %s | Hora Extra: %.2f'

    p.drawString(0, 800, '_' * 150)

    y = 750
    for fornecedor in fornecedores:
        p.drawString(10, y, str_ % (
            fornecedor.nome, fornecedor.total_horas_extra))
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
    return Render.render('fornecedores/relatorio.html', params, 'Relatório de Fornecedores')


class Pdf(View):
    pass


class PdfDebug(TemplateView):
    template_name = 'fornecedores/relatorio.html'
