from django.db import models

class Earthquake(models.Model):
    place = models.CharField(max_length=255)
    magnitude = models.FloatField()
    time = models.DateTimeField()
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return f'{self.place} - {self.magnitude}'
