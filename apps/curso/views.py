from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .models import Curso


CAMPOS_CURSO = [
    "nomeCurso", "anoCurso", "mesCurso", "cronograma", "horario",
    "carga", "docente", "ementa", "obs", "certificado", "documento",
]


class CursoList(LoginRequiredMixin, ListView):
    model = Curso
    paginate_by = 20

    def get_queryset(self):
        # O modelo legado de Curso não possui vínculo direto com empresa.
        # A listagem administrativa deve funcionar sem tentar acessar user.funcionario.
        return Curso.objects.all().order_by("-anoCurso", "-mesCurso", "nomeCurso")


class CursoUpdate(LoginRequiredMixin, UpdateView):
    model = Curso
    fields = CAMPOS_CURSO
    success_url = reverse_lazy("list_curso")


class CursoDelete(LoginRequiredMixin, DeleteView):
    model = Curso
    success_url = reverse_lazy("list_curso")


class CursoCreate(LoginRequiredMixin, CreateView):
    model = Curso
    fields = CAMPOS_CURSO
    success_url = reverse_lazy("list_curso")


def relatorio_curso(request):
    from django.http import HttpResponse
    response = HttpResponse(content_type="text/plain; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="Relatorio_de_Cursos.txt"'
    linhas = ["RELATÓRIO DE CURSOS", ""]
    for curso in Curso.objects.all().order_by("-anoCurso", "-mesCurso", "nomeCurso"):
        linhas.append(f"{curso.nomeCurso} | {curso.mesCurso}/{curso.anoCurso} | {curso.docente}")
    response.write("\n".join(linhas))
    return response
