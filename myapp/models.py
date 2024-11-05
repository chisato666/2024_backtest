from django.db import models


class BacktestResult(models.Model):
    symbol = models.CharField(max_length=10)
    score_threshold = models.FloatField()
    tp_percent = models.FloatField()
    sl_percent = models.FloatField()
    start_date = models.DateField()
    end_date = models.DateField()
    total_profit = models.FloatField()

class PriceAlert(models.Model):
    symbol = models.CharField(max_length=50)
    interval = models.CharField(max_length=10)
    percentage_decrease = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)