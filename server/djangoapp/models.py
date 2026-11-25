"""Relational car catalogue, separate from MongoDB dealer/review records."""
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

class CarMake(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

class CarModel(models.Model):
    BODY_TYPES = [(value, value) for value in (
        "Sedan", "SUV", "Wagon", "Hatchback", "Coupe", "Convertible", "Minivan", "Pickup",
    )]
    car_make = models.ForeignKey(CarMake, on_delete=models.PROTECT, related_name="models")
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=BODY_TYPES)
    year = models.PositiveIntegerField(validators=[
        MinValueValidator(2015), MaxValueValidator(2023),
    ])
    dealer_id = models.PositiveIntegerField(default=1)
    mileage = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["car_make__name", "name", "year"]
        constraints = [models.UniqueConstraint(
            fields=["car_make", "name", "year", "dealer_id"], name="unique_dealer_car_model"
        )]

    def __str__(self):
        return f"{self.car_make.name} {self.name} ({self.year})"
