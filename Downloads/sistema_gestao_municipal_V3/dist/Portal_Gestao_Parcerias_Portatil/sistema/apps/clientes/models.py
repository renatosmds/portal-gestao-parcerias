from django.db import models


class Clientes(models.Model):
    first_name = models.CharField(max_length=30, null=True, blank=True)
    last_name = models.CharField(max_length=30, null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    salary = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    photo = models.ImageField(upload_to='clients_photos', null=True, blank=True)

#    user = models.OneToOneField(User, on_delete=models.PROTECT)
#    departamento = models.ManyToManyField(Departamento)
#    empresa = models.ForeignKey(Empresa, on_delete=models.PROTECT, null=True, blank=True)

#    def __init__(self, *args, **kwargs):
#        super().__init__(*args, **kwargs)
#        self.clientes_set = None

#    @property
#    def clientes(self):
#        total = self.clientes_set.filter().aggregate(
#            Sum('salary'))['salary__sum']
#        return total or 0


    def __str__(self):
        return self.first_name + ' ' + self.last_name
