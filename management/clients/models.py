from django.db import models

# Create your models here.
class Client(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, blank=True)
    adress = models.CharField(max_length=200, blank=True)

def __str__(self):
    return self.name
    