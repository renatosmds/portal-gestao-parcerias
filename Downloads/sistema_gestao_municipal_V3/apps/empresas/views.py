from django.http import HttpResponse
from django.views.generic.edit import CreateView, UpdateView  # ok
from .models import Empresa  # ok


class EmpresaCreate(CreateView):
    model = Empresa  # ok
    fields = ['nome']  # ok

    def form_valid(self, form):
        obj = form.save()
        funcionario = self.request.user.funcionario.empresa
        funcionario.empresa = obj
        funcionario.save()
        return HttpResponse('Ok')


class EmpresaEdit(UpdateView):
    model = Empresa
    fields = ['nome']
