from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import decimal
class Migration(migrations.Migration):
 dependencies=[migrations.swappable_dependency(settings.AUTH_USER_MODEL),("lancamentos","0001_initial")]
 operations=[
  migrations.AddField(model_name="lancamento",name="tipo_glosa",field=models.CharField(choices=[("nenhuma","Sem glosa"),("parcial","Glosa parcial"),("global","Glosa global")],default="nenhuma",max_length=12,verbose_name="Tipo de glosa")),
  migrations.AddField(model_name="lancamento",name="motivo_glosa",field=models.CharField(blank=True,choices=[("sem_comprovacao","Despesa sem comprovação"),("documento_irregular","Documento fiscal irregular"),("fora_vigencia","Despesa fora da vigência"),("nao_prevista","Despesa não prevista no plano de trabalho"),("duplicidade","Pagamento em duplicidade"),("sem_pagamento","Ausência de comprovante de pagamento"),("incompativel","Despesa incompatível com o objeto"),("outro","Outro motivo")],max_length=30,verbose_name="Motivo da glosa")),
  migrations.AddField(model_name="lancamento",name="fundamentacao_glosa",field=models.TextField(blank=True,verbose_name="Fundamentação da glosa")),
  migrations.AddField(model_name="lancamento",name="glosa_registrada_em",field=models.DateTimeField(blank=True,null=True)),
  migrations.AddField(model_name="lancamento",name="glosa_registrada_por",field=models.ForeignKey(blank=True,null=True,on_delete=django.db.models.deletion.SET_NULL,related_name="glosas_registradas",to=settings.AUTH_USER_MODEL)),
  migrations.CreateModel(name="HistoricoGlosa",fields=[("id",models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name="ID")),("tipo_anterior",models.CharField(blank=True,max_length=12)),("tipo_novo",models.CharField(choices=[("nenhuma","Sem glosa"),("parcial","Glosa parcial"),("global","Glosa global")],max_length=12)),("valor_anterior",models.DecimalField(decimal_places=2,default=decimal.Decimal("0.00"),max_digits=15)),("valor_novo",models.DecimalField(decimal_places=2,default=decimal.Decimal("0.00"),max_digits=15)),("motivo",models.CharField(blank=True,max_length=30)),("fundamentacao",models.TextField(blank=True)),("criado_em",models.DateTimeField(auto_now_add=True)),("lancamento",models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name="historico_glosas",to="lancamentos.lancamento")),("usuario",models.ForeignKey(blank=True,null=True,on_delete=django.db.models.deletion.SET_NULL,to=settings.AUTH_USER_MODEL))],options={"ordering":["-criado_em"]}),
 ]
