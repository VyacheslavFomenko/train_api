from django.db import transaction
from rest_framework import serializers

from trip.models import Crew, Station, TrainType, Train, Ticket, Journey, Route, Order


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name")


class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = ("id", "name", "latitude", "longitude")


class TrainTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainType
        fields = ("id", "name")


class TrainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Train
        fields = ("id", "name", "cargo_num", "places_in_cargo", "train_type")


class TrainListSerializer(serializers.ModelSerializer):
    train_type_name = serializers.CharField(source="train_type.name", read_only=True)

    class Meta:
        model = Train
        fields = ("id", "name", "cargo_num", "places_in_cargo", "train_type_name")


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


class RouteListSerializer(serializers.ModelSerializer):
    source_station_name = serializers.CharField(source="station.name", read_only=True)
    destination_station_name = serializers.CharField(source="station.name", write_only=True)

    class Meta:
        model = Route
        fields = ("id", "source_station_name", "destination_station_name", "distance")


class RouteDetailSerializer(serializers.ModelSerializer):
    source = StationSerializer(many=False, read_only=True)
    destination = StationSerializer(many=False, read_only=True)

    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


class JourneySerializer(serializers.ModelSerializer):
    class Meta:
        model = Journey
        fields = ("id", "route", "train", "departure_time", "arrival_time", "crew")


class JourneyListSerializer(serializers.ModelSerializer):
    route = RouteListSerializer(many=False, read_only=True)
    train = TrainListSerializer(many=False, read_only=True)

    class Meta:
        model = Journey
        fields = ("id", "route", "train", "departure_time", "arrival_time", "crew")


class JourneyDetailSerializer(serializers.ModelSerializer):
    route = RouteDetailSerializer(many=False, read_only=True)
    train = TrainListSerializer(many=False, read_only=True)

    class Meta:
        model = Journey
        fields = ("id", "route", "train", "departure_time", "arrival_time", "crew")


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ("id", "cargo", "seat", "journey", "order")


class TicketListSerializer(serializers.ModelSerializer):
    journey_route = serializers.CharField(source="journey.route", read_only=True)
    order_id = serializers.CharField(source="order.id", read_only=True)

    class Meta:
        model = Ticket
        fields = ("id", "cargo", "seat", "journey_route", "order_id")


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False, allow_empty=False)

    class Meta:
        model = Order
        fields = ("id", "tickets", "created_at")

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            order = Order.objects.create(**validated_data)
            for ticket in tickets_data:
                Ticket.objects.create(order=order, **ticket)
            return order


class OrderListSerializer(OrderSerializer):
    tickets = TicketListSerializer(many=True, read_only=True)
