from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies=[migrations.swappable_dependency(settings.AUTH_USER_MODEL),("prestacao","0009_prestacao_empresa")]
    operations=[
      migrations.AddField(model_name="prestacao",name="situacao_workflow",field=models.CharField(choices=[("elaboracao","Em elaboração"),("enviada","Enviada pela OSC"),("recebida","Recebida pelo órgão"),("em_analise","Em análise"),("diligencia","Em diligência"),("corrigida","Corrigida pela OSC"),("aprovada","Aprovada"),("aprovada_ressalvas","Aprovada com ressalvas"),("reprovada","Reprovada"),("encerrada","Encerrada")],default="elaboracao",max_length=24,verbose_name="Situação do fluxo")),
      migrations.AddField(model_name="prestacao",name="analista_responsavel",field=models.ForeignKey(blank=True,null=True,on_delete=django.db.models.deletion.SET_NULL,related_name="prestacoes_atribuidas",to=settings.AUTH_USER_MODEL,verbose_name="Analista responsável")),
      migrations.AddField(model_name="prestacao",name="enviada_em",field=models.DateTimeField(blank=True,null=True)),
      migrations.AddField(model_name="prestacao",name="recebida_em",field=models.DateTimeField(blank=True,null=True)),
      migrations.CreateModel(name="HistoricoPrestacao",fields=[("id",models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name="ID")),("situacao_anterior",models.CharField(blank=True,max_length=24)),("nova_situacao",models.CharField(choices=[("elaboracao","Em elaboração"),("enviada","Enviada pela OSC"),("recebida","Recebida pelo órgão"),("em_analise","Em análise"),("diligencia","Em diligência"),("corrigida","Corrigida pela OSC"),("aprovada","Aprovada"),("aprovada_ressalvas","Aprovada com ressalvas"),("reprovada","Reprovada"),("encerrada","Encerrada")],max_length=24)),("observacao",models.TextField(blank=True)),("criado_em",models.DateTimeField(auto_now_add=True)),("prestacao",models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name="historico_workflow",to="prestacao.prestacao")),("usuario",models.ForeignKey(blank=True,null=True,on_delete=django.db.models.deletion.SET_NULL,to=settings.AUTH_USER_MODEL))],options={"ordering":["-criado_em"]}),
    ]
