import csv
import json

import xlwt
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .forms import RegistroHoraExtraForm
from .models import RegistroHoraExtra


class HoraExtraEscopoMixin(LoginRequiredMixin):
    def get_queryset(self):
        queryset = RegistroHoraExtra.objects.select_related("funcionario", "empresa")
        if self.request.user.is_superuser:
            return queryset
        funcionario = getattr(self.request.user, "funcionario", None)
        empresa = getattr(funcionario, "empresa", None) if funcionario else None
        if not empresa:
            raise PermissionDenied("O usuário não possui OSC/empresa vinculada.")
        return queryset.filter(empresa=empresa)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        registro = form.save(commit=False)
        registro.user = self.request.user
        registro.empresa = registro.funcionario.empresa
        registro.save()
        self.object = registro
        return super().form_valid(form)


class HoraExtraList(HoraExtraEscopoMixin, ListView):
    model = RegistroHoraExtra
    paginate_by = 20


class HoraExtraEdit(HoraExtraEscopoMixin, UpdateView):
    model = RegistroHoraExtra
    form_class = RegistroHoraExtraForm
    success_url = reverse_lazy("list_hora_extra")


class HoraExtraEditBase(HoraExtraEdit):
    pass


class HoraExtraDelete(HoraExtraEscopoMixin, DeleteView):
    model = RegistroHoraExtra
    success_url = reverse_lazy("list_hora_extra")


class HoraExtraCreate(HoraExtraEscopoMixin, CreateView):
    model = RegistroHoraExtra
    form_class = RegistroHoraExtraForm
    success_url = reverse_lazy("list_hora_extra")


class UtilizouHoraExtra(HoraExtraEscopoMixin, View):
    def post(self, request, *args, **kwargs):
        registro = self.get_queryset().get(pk=kwargs["pk"])
        registro.utilizada = True
        registro.save(update_fields=["utilizada"])
        return HttpResponse(json.dumps({"mensagem": "Requisição executada"}), content_type="application/json")


class NaoUtilizouHE(HoraExtraEscopoMixin, View):
    def post(self, request, *args, **kwargs):
        registro = self.get_queryset().get(pk=kwargs["pk"])
        registro.utilizada = False
        registro.save(update_fields=["utilizada"])
        return HttpResponse(json.dumps({"mensagem": "Requisição executada"}), content_type="application/json")


class ExportarParaCSV(HoraExtraEscopoMixin, View):
    def get(self, request):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="Banco de Horas.csv"'
        writer = csv.writer(response)
        writer.writerow(["Id", "Motivo", "Funcionário", "Horas", "Utilizada"])
        for registro in self.get_queryset():
            writer.writerow([registro.id, registro.motivo, registro.funcionario, registro.horas, registro.utilizada])
        return response


class ExportarExcel(HoraExtraEscopoMixin, View):
    def get(self, request):
        response = HttpResponse(content_type="application/ms-excel")
        response["Content-Disposition"] = 'attachment; filename="Banco de Horas.xls"'
        wb = xlwt.Workbook(encoding="utf-8")
        ws = wb.add_sheet("Banco de Horas")
        for col, titulo in enumerate(["Id", "Motivo", "Funcionário", "Horas", "Utilizada"]):
            ws.write(0, col, titulo)
        for row, registro in enumerate(self.get_queryset(), start=1):
            ws.write(row, 0, registro.id)
            ws.write(row, 1, registro.motivo or "")
            ws.write(row, 2, str(registro.funcionario))
            ws.write(row, 3, float(registro.horas or 0))
            ws.write(row, 4, "Sim" if registro.utilizada else "Não")
        wb.save(response)
        return response
