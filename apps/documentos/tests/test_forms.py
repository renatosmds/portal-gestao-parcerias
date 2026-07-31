from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from apps.documentos.forms import ConferenciaDocumentoForm, DocumentoForm
from apps.documentos.models import Documento
from apps.empresas.models import Empresa


class DocumentoFormTests(TestCase):
    def setUp(self):
        self.empresa = Empresa.objects.create(nome="Empresa Formulário")

    def test_documento_exige_vinculo(self):
        form = DocumentoForm(
            data={
                "descricao": "Documento sem vínculo",
                "tipo": Documento.Tipo.OUTRO,
            },
            files={
                "arquivo": SimpleUploadedFile(
                    "teste.pdf",
                    b"arquivo",
                    content_type="application/pdf",
                )
            },
            empresa=self.empresa,
        )
        self.assertFalse(form.is_valid())
        self.assertIn(
            "Vincule o documento",
            str(form.non_field_errors()),
        )

    def test_pendencia_exige_observacao(self):
        form = ConferenciaDocumentoForm(
            data={
                "status": Documento.Status.COM_PENDENCIA,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("observacoes", form.errors)
