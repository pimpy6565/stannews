from django.db import models

# Create your models here.
class Hplc(models.Model):
    name = models.CharField(max_length=36)
    benz = models.DecimalField(default=0,max_digits=10,decimal_places=2)
    benz_low = models.DecimalField(default=0,max_digits=10,decimal_places=2)
    benz_high = models.DecimalField(default=0,max_digits=10,decimal_places=2)
    
    caf = models.DecimalField(default=0,max_digits=10,decimal_places=2)
    caf_low = models.DecimalField(default=0,max_digits=10,decimal_places=2)
    caf_high = models.DecimalField(default=0,max_digits=10,decimal_places=2)
    
    sorb = models.DecimalField(default=0,max_digits=10,decimal_places=2)
    sorb_low = models.DecimalField(default=0,max_digits=10,decimal_places=2)
    sorb_high = models.DecimalField(default=0,max_digits=10,decimal_places=2)
    
    ace = models.DecimalField(default=0,max_digits=10,decimal_places=2)
    ace_low = models.DecimalField(default=0,max_digits=10,decimal_places=2)
    ace_high = models.DecimalField(default=0,max_digits=10,decimal_places=2)
    
    asp = models.DecimalField(default=0,max_digits=10,decimal_places=2)
    asp_low = models.DecimalField(default=0,max_digits=10,decimal_places=2)
    asp_high = models.DecimalField(default=0,max_digits=10,decimal_places=2)
    
    def __str__(self):
        return self.name.title()