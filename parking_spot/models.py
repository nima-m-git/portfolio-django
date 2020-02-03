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
    
    def update_entries():
        spots = Entries.objects.distinct('spot')
        hours = [str(i).zfill(2) for i in range(24)]
        for spot in spots:
            for hour in hours:
            # empty count ="SELECT COUNT(*) FROM parking_spot_entries WHERE 
            # SPOT = (%s) AND TIME = (%s) AND EMPTY = true",
                            #(spot, hour))
                empty_count = Entries.objects.filter(spot=spot, time=hour, empty=True).count()
            # total count = "SELECT COUNT(*) FROM parking_spot_entries WHERE 
            # SPOT = (%s) AND TIME = (%s)", (spot, hour))
                total_count = Entries.objects.filter(spot=spot, time=hour).count()
                if total_count >= 3:
                    probability = empty_count/total_count
                    std = (probability*(1-probability)/total_count)**0.5
                # entry_query = '''INSERT INTO "parking_spot_stats" (SPOT, TIME, PROBABILITY, ENTRIES, STD) 
                        #VALUES (%s, %s, %s, %s, %s)'''
                Statistics(spot=spot, time=time, probability=probability, entries=total_count, std=std).save()
            

