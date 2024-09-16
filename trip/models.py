from django.db import models

from train_service import settings


class TrainType(models.Model):
    name = models.CharField(max_length=255)


class Train(models.Model):
    name = models.CharField(max_length=255)
    cargo_num = models.IntegerField()
    places_in_cargo = models.CharField(max_length=255)
    train_type = models.ForeignKey(TrainType, on_delete=models.CASCADE, related_name="train")


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="order")


class Station(models.Model):
    name = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()


class Route(models.Model):
    source = models.ForeignKey(Station, on_delete=models.CASCADE, related_name="route")
    destination = models.ForeignKey(Station, on_delete=models.CASCADE, related_name="route_destination")
    distance = models.IntegerField()


class Crew(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)


class Journey(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name="journey")
    train = models.ForeignKey(Train, on_delete=models.CASCADE, related_name="journey")
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    crew = models.ManyToManyField(Crew, related_name="journey")


class Ticket(models.Model):
    cargo = models.IntegerField()
    seat = models.IntegerField()
    journey = models.ForeignKey(Journey, on_delete=models.CASCADE, related_name="ticket")
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="ticket")
