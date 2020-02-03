from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils import timezone


class Entries(models.Model):
    spot = models.CharField(max_length=5, null=False)
    empty = models.BooleanField(null=False)
    time = models.IntegerField(validators=[
                    MaxValueValidator(23),
                    MinValueValidator(0)
                ])
    date_added = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.spot
    

class Statistics(models.Model):
    spot = models.CharField(max_length=5, null=False)
    time = models.IntegerField(validators=[
                    MaxValueValidator(23),
                    MinValueValidator(0)
                ]
            )
    probability = models.DecimalField(max_digits=3, decimal_places=2)
    entries = models.IntegerField()
    std = models.DecimalField(max_digits=4, decimal_places=3)
    
    def __str__(self):
        return self.spot
    
    
            

