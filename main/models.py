from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Portfolio(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="portfolio", null=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    assets = models.DecimalField(max_digits=10, decimal_places=2)

    # def __str__(self):
    #     return self.user

class Stock(models.Model):
    name = models.CharField(max_length=5)
    open_price = models.DecimalField(max_digits=10, decimal_places=2)
    current_price = models.DecimalField(max_digits=10, decimal_places=2)

class StockItem(models.Model):
    stock = models.ForeignKey(Stock, related_name="item", on_delete=models.CASCADE)
    portfolio = models.ForeignKey(Portfolio, related_name="stocks", on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=5)
    value = models.DecimalField(max_digits=10, decimal_places=2)

    # def __str__(self):
    #     return self.name