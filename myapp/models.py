from django.db import models

class PriceAlert(models.Model):
    symbol = models.CharField(max_length=50)
    interval = models.CharField(max_length=10)
    percentage_decrease = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)