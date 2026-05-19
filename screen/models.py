from django.db import models

# Create your models here.
class Hplc(models.Model):
    name = models.CharField(max_length=36)
    benz = models.DecimalField(default=0,max_digits=10,decimal_places=2)
    caf = models.DecimalField(default=0,max_digits=10,decimal_places=2)
    sorb = models.DecimalField(default=0,max_digits=10,decimal_places=2)
    ace = models.DecimalField(default=0,max_digits=10,decimal_places=2)
    
    def __str__(self):
        return self.name.title()