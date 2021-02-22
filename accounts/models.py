from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator

# Create your models here.

class Customer(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, null=True)
    phone = models.CharField(max_length=200, null=True)
    email = models.CharField(max_length=200, null=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.name

class Transportation(models.Model):
    CATEGORY = (
            ('Carbon Neutral', 'Carbon Neutral'),
            ('Low Carbon Emission', 'Low Carbon Emission'),
            ('High Carbon Emission', 'High Carbon Emission'),
            )

    name = models.CharField(max_length=200, null=True)
    carbon_price = models.FloatField(null=True)
    category = models.CharField(max_length=200, null=True, choices=CATEGORY)
    date_created = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.name

class Journey(models.Model):
    STATUS = (
            ('Not Offset', 'Not Offset'),
            ('Offset', 'Offset'),
            )  
    customer = models.ForeignKey(Customer, null=True, on_delete=models.SET_NULL)
    transportation = models.ForeignKey(Transportation, null=True, on_delete=models.SET_NULL)
    duration_hours = models.PositiveIntegerField(null=True, validators=[MinValueValidator(0), MaxValueValidator(23)], default=0)
    duration_minutes = models.PositiveIntegerField(null=True, validators=[MinValueValidator(0), MaxValueValidator(59)], default=0)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    status = models.CharField(max_length=200, null=True, choices=STATUS, default="Not Offset")