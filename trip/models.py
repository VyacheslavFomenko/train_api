from django.db import models
from rest_framework.exceptions import ValidationError

from train_service import settings


class TrainType(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Train(models.Model):
    name = models.CharField(max_length=255)
    cargo_num = models.IntegerField()
    places_in_cargo = models.CharField(max_length=255)
    train_type = models.ForeignKey(TrainType, on_delete=models.CASCADE, related_name="train")

    def __str__(self):
        return f"{self.name}, {self.cargo_num}, {self.places_in_cargo}, {self.train_type}"


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="order")

    def __str__(self):
        return str(self.created_at)

    class Meta:
        ordering = ["-created_at"]


class Station(models.Model):
    name = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return f"{self.name}, {self.latitude}, {self.longitude}"


class Route(models.Model):
    source = models.ForeignKey(Station, on_delete=models.CASCADE, related_name="route")
    destination = models.ForeignKey(Station, on_delete=models.CASCADE, related_name="route_destination")
    distance = models.IntegerField()

    def __str__(self):
        return f"{self.source}, {self.destination}, {self.distance}"


class Crew(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.first_name}, {self.last_name}"


class Journey(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name="journey")
    train = models.ForeignKey(Train, on_delete=models.CASCADE, related_name="journey")
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    crew = models.ManyToManyField(Crew, related_name="journey")

    def __str__(self):
        return f"{self.route}, {self.train}, {self.departure_time}, {self.arrival_time}, {self.crew}"


class Ticket(models.Model):  #
    cargo = models.IntegerField()
    seat = models.IntegerField()
    journey = models.ForeignKey(Journey, on_delete=models.CASCADE, related_name="ticket")
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="ticket")

    def __str__(self):
        return f"{self.cargo}, {self.seat}, {self.journey}, {self.order}"

    def clean(self):
        if self.cargo < 0:
            raise ValidationError("cargo must be a positive integer")
        if self.seat < 1:
            raise ValidationError("seat`s must be greater then 1")

        if Ticket.objects.filter(journey=self.journey, seat=self.seat).exists():
            raise ValidationError(f"{self.seat} is already taken please select another")

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Ticket, self).save(*args, **kwargs)
