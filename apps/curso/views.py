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
from .models import Curso


class CursoList(ListView):
    model = Curso

    success_url = reverse_lazy('list_curso')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['report_button'] = _("Employee report")
        return context

    def get_queryset(self):
        empresa_logada = self.request.user.funcionario.empresa
        return Curso.objects.filter(empresa=empresa_logada)


class CursoUpdate(UpdateView):
    model = Curso
    fields = ['nomeCurso', 'anoCurso', 'mesCurso', 'cronograma', 'horario', 'carga', 'docente', 'ementa', 'obs',
                  'certificado', 'documento']
    success_url = reverse_lazy('list_curso')


class CursoDelete(DeleteView):
    model = Curso
    success_url = reverse_lazy('list_curso')

class CursoCreate(CreateView):
    model = Curso
    fields = ['nomeCurso', 'anoCurso', 'mesCurso', 'cronograma', 'horario', 'carga', 'docente', 'ementa', 'obs',
                  'certificado', 'documento']

    success_url = reverse_lazy('list_curso')

    def form_valid(self, form):
        funcionario = form.save(commit=False)
        username = funcionario.nomeCurso.split(' ')[0]
        funcionario.empresa = self.request.user.funcionario.empresa
        funcionario.user = User.objects.create(username=username)
        funcionario.save()
        return super(CursoCreate, self).form_valid(form)


def relatorio_curso(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="mypdf.pdf"'

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)

    p.drawString(200, 810, 'Relatorio de cursos')

    curso = Curso.objects.filter(
        empresa=request.user.funcionario.empresa)

    str_ = 'Nome: %s | Hora Extra: %.2f'

    p.drawString(0, 800, '_' * 150)

    y = 750
    for curso in curso:
        p.drawString(10, y, str_ % (
            curso.nomeCurso, curso.total_horas_extra))
        y -= 20

    p.showPage()
    p.save()

    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)

    return response

#
# class Render:
#     @staticmethod
#     def render(path: str, params: dict, filename: str):
#         template = get_template(path)
#         html = template.render(params)
#         response = io.BytesIO()
#         pdf = pisa.pisaDocument(
#             io.BytesIO(html.encode("UTF-8")), response)
#         if not pdf.err:
#             response = HttpResponse(
#                 response.getvalue(), content_type='application/pdf')
#             response['Content-Disposition'] = 'attachment;filename=%s.pdf' % filename
#             return response
#         else:
#             return HttpResponse("Error Rendering PDF", status=400)
#
#
# def get(request):
#     params = {
#         'today': 'Variavel today',
#         'sales': 'Variavel sales',
#         'request': request,
#     }
#     return Render.render('curso/relatorio.html', params, 'myfile')
#
#
# class Pdf(View):
#     pass
#
#
# class PdfDebug(TemplateView):
#     template_name = 'curso/relatorio.html'
