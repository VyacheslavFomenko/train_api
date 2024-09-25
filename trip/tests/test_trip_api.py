from datetime import datetime, timedelta, date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from trip.models import TrainType, Station, Crew, Train, Route, Journey
from trip.serializers import RouteSerializer, RouteListSerializer, TrainListSerializer, JourneyListSerializer

TRIP_URL = reverse("trip:journey-list")
ROUTES_URL = reverse("trip:routes-list")
TRAIN_URL = reverse("trip:trains-list")


def sample_user(**params):
    return get_user_model().objects.create_user(**params)


def sample_train_type(**params):
    defaults = {
        "name": "Test Train Type"
    }
    defaults.update(params)

    return TrainType.objects.create(**defaults)


def sample_station(**params):
    defaults = {
        "name": "Test Station",
        "latitude": "14",
        "longitude": "13"
    }
    defaults.update(params)
    return Station.objects.create(**defaults)


def sample_crew(**params):
    defaults = {
        "first_name": "Test first name",
        "last_name": "Test last name"
    }
    defaults.update(params)
    return Crew.objects.create(**defaults)


def sample_train(**params):
    train_type = sample_train_type(name="Test Train Type")
    defaults = {
        "name": "Test Train",
        "cargo_num": 14,
        "places_in_cargo": 13,
        "train_type": train_type
    }
    defaults.update(params)
    return Train.objects.create(**defaults)


def sample_route(**params):
    source = sample_station(name="Test Station 1", latitude="14", longitude="13")
    destination = sample_station(name="Test Station 2", latitude="14", longitude="13")
    defaults = {
        "source": source,
        "destination": destination,
        "distance": 100
    }
    defaults.update(params)
    return Route.objects.create(**defaults)


def sample_journey(**params):
    defaults = {
        "departure_time": datetime.now(),
        "arrival_time": datetime.now() + timedelta(hours=2)
    }
    defaults.update(params)
    return Journey.objects.create(**defaults)


class UnauthenticatedTripApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(TRIP_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedTripApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = sample_user(username="test1", email="test1@gmail.com", password="12345678")
        self.client.force_authenticate(self.user)

    def test_list_routes(self):
        sample_route()
        sample_route(distance=101)

        res = self.client.get(ROUTES_URL)

        routes = Route.objects.order_by("id")
        serializer = RouteListSerializer(routes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_route_filter_by_source_and_destination(self):
        source = sample_station()
        destination = sample_station(name="Test destination", latitude=1, longitude=2)

        route1 = sample_route(source=source, destination=destination)
        route2 = sample_route(distance=101)

        res = self.client.get(ROUTES_URL, {"source": f"{source.id}", "destination": f"{destination.id}"})

        serializer_route_1 = RouteListSerializer(route1)
        serializer_route_2 = RouteListSerializer(route2)

        self.assertIn(serializer_route_1.data, res.data["results"])
        self.assertNotIn(serializer_route_2.data, res.data["results"])

    def test_list_trains(self):
        sample_train()
        sample_train(name="Tomas")

        res = self.client.get(TRAIN_URL)

        trains = Train.objects.order_by("id")
        serializer = TrainListSerializer(trains, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_filter_train_by_name(self):
        train1 = sample_train(name="Tomas")
        train2 = sample_train()

        res = self.client.get(TRAIN_URL, {"name": "Tomas"})

        serializer_train_1 = TrainListSerializer(train1)
        serializer_train_2 = TrainListSerializer(train2)

        self.assertIn(serializer_train_1.data, res.data["results"])
        self.assertNotIn(serializer_train_2.data, res.data["results"])

    def test_filter_train_by_cargo_num(self):
        train1 = sample_train(name="Tomas")
        train2 = sample_train(cargo_num=100)

        res = self.client.get(TRAIN_URL, {"cargo_num": 14})

        serializer_train_1 = TrainListSerializer(train1)
        serializer_train_2 = TrainListSerializer(train2)

        self.assertIn(serializer_train_1.data, res.data["results"])
        self.assertNotIn(serializer_train_2.data, res.data["results"])

    def test_filter_train_by_places_in_cargo(self):
        train1 = sample_train(name="Tomas", places_in_cargo=100)
        train2 = sample_train()

        res = self.client.get(TRAIN_URL, {"places_in_cargo": 100})

        serializer_train_1 = TrainListSerializer(train1)
        serializer_train_2 = TrainListSerializer(train2)

        self.assertIn(serializer_train_1.data, res.data["results"])
        self.assertNotIn(serializer_train_2.data, res.data["results"])

    def test_filter_train_by_train_type(self):
        train_type = sample_train_type(name="Express")

        train1 = sample_train(name="Tomas", train_type=train_type)
        train2 = sample_train()

        res = self.client.get(TRAIN_URL, {"train_type": f"{train_type.id}"})

        serializer_train_1 = TrainListSerializer(train1)
        serializer_train_2 = TrainListSerializer(train2)

        self.assertIn(serializer_train_1.data, res.data["results"])
        self.assertNotIn(serializer_train_2.data, res.data["results"])

    def test_list_journeys(self):
        train1 = sample_train()
        train2 = sample_train(name="Tomas")

        route1 = sample_route()
        route2 = sample_route(distance=101)

        crew = sample_crew()

        journey1 = sample_journey(route=route1, train=train1)
        journey2 = sample_journey(route=route2, train=train2)

        journey1.crew.add(crew)
        journey2.crew.add(crew)

        res = self.client.get(TRIP_URL)

        trains = Journey.objects.order_by("id")
        serializer = JourneyListSerializer(trains, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_filter_journey_by_route(self):
        train1 = sample_train()
        train2 = sample_train(name="Tomas")

        route1 = sample_route(distance=101)
        route2 = sample_route()

        crew = sample_crew()

        journey1 = sample_journey(route=route1, train=train1)
        journey2 = sample_journey(route=route2, train=train2)

        journey1.crew.add(crew)
        journey2.crew.add(crew)

        res = self.client.get(TRIP_URL, {"route": f"{route1.id}"})

        serializer_journey_1 = JourneyListSerializer(journey1)
        serializer_journey_2 = JourneyListSerializer(journey2)

        self.assertIn(serializer_journey_1.data, res.data["results"])
        self.assertNotIn(serializer_journey_2.data, res.data["results"])

    def test_filter_journey_by_train(self):
        train1 = sample_train(name="Tomas")
        train2 = sample_train()

        route1 = sample_route()
        route2 = sample_route(distance=101)

        crew = sample_crew()

        journey1 = sample_journey(route=route1, train=train1)
        journey2 = sample_journey(route=route2, train=train2)

        journey1.crew.add(crew)
        journey2.crew.add(crew)

        print(journey1.departure_time)
        print(journey2.arrival_time)
        res = self.client.get(TRIP_URL, {"train": f"{train1.id}"})

        serializer_journey_1 = JourneyListSerializer(journey1)
        serializer_journey_2 = JourneyListSerializer(journey2)

        self.assertIn(serializer_journey_1.data, res.data["results"])
        self.assertNotIn(serializer_journey_2.data, res.data["results"])

    def test_filter_journey_by_departure_time(self):
        train1 = sample_train(name="Tomas")
        train2 = sample_train()

        route1 = sample_route()
        route2 = sample_route(distance=101)

        crew = sample_crew()

        journey1 = Journey.objects.create(
            train=train1,
            route=route1,
            departure_time=datetime.now() + timedelta(days=1),
            arrival_time=datetime.now() + timedelta(days=1, hours=2)
        )
        journey2 = sample_journey(route=route2, train=train2)

        journey1.crew.add(crew)
        journey2.crew.add(crew)

        departure_time = journey1.departure_time.strftime("%Y-%m-%d %H:%M")

        res = self.client.get(TRIP_URL, {"departure_time": departure_time})

        serializer_journey_1 = JourneyListSerializer(journey1)
        serializer_journey_2 = JourneyListSerializer(journey2)

        print(serializer_journey_1.data)
        print(res.data["results"])

        self.assertIn(serializer_journey_1.data, res.data["results"])
        self.assertNotIn(serializer_journey_2.data, res.data["results"])

    def test_filter_journey_by_arrival_time(self):
        train1 = sample_train(name="Tomas")
        train2 = sample_train()

        route1 = sample_route()
        route2 = sample_route(distance=101)

        crew = sample_crew()

        journey1 = Journey.objects.create(
            train=train1,
            route=route1,
            departure_time=datetime.now() + timedelta(days=1),
            arrival_time=datetime.now() + timedelta(days=1, hours=2)
        )
        journey2 = sample_journey(route=route2, train=train2)

        journey1.crew.add(crew)
        journey2.crew.add(crew)

        arrival_time = journey1.arrival_time.strftime("%Y-%m-%d %H:%M")

        res = self.client.get(TRIP_URL, {"arrival_time": arrival_time})

        serializer_journey_1 = JourneyListSerializer(journey1)
        serializer_journey_2 = JourneyListSerializer(journey2)

        print(serializer_journey_1.data)
        print(res.data["results"])

        self.assertIn(serializer_journey_1.data, res.data["results"])
        self.assertNotIn(serializer_journey_2.data, res.data["results"])

    def test_create_journey_forbidden(self):
        payload = {
            "route": sample_route().id,
            "train": sample_train().id,
            "departure_time": datetime.now() + timedelta(days=1),
            "arrival_timedate": datetime.now() + timedelta(days=1, hours=2),
            "crew": [sample_crew().id, ]
        }
        res = self.client.post(TRIP_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminTripApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = sample_user(username="test1", email="test1@gmail.com", password="12345678", is_staff=True)
        self.client.force_authenticate(self.user)

    def test_create_journey(self):
        payload = {
            "route": sample_route().id,
            "train": sample_train().id,
            "departure_time": datetime.now() + timedelta(days=1),
            "arrival_time": datetime.now() + timedelta(days=1, hours=2),
            "crew": [sample_crew().id, ]
        }
        res = self.client.post(TRIP_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED, res.data)
        journey = Journey.objects.get(id=res.data["id"])
        for key in ["departure_time", "arrival_time"]:
            self.assertEqual(payload[key].strftime("%Y-%m-%d %H:%M"), getattr(journey, key).strftime("%Y-%m-%d %H:%M"))

        for key in ["route", "train"]:
            self.assertEqual(payload[key], getattr(journey, key).id)

        self.assertEqual(payload["crew"], list(journey.crew.values_list("id", flat=True)))

    def test_create_route(self):
        payload = {
            "source": sample_station().id,
            "destination": sample_station(name="Test 2 Station", latitude="13", longitude=17).id,
            "distance": 1000
        }

        res = self.client.post(ROUTES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED, res.data)
        route = Route.objects.get(id=res.data["id"])
        print(route)
        for key in ["source", "destination"]:
            self.assertEqual(payload[key], getattr(route, key).id)

        self.assertEqual(payload["distance"], route.distance)

    def test_create_train(self):

        payload = {
            "name": "Test Train Name",
            "cargo_num": 100,
            "places_in_cargo": 114,
            "train_type": sample_train().id
        }

        res = self.client.post(TRAIN_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED, res.data)
        train = Train.objects.get(id=res.data["id"])
        for key in ["cargo_num", "places_in_cargo"]:
            self.assertEqual(payload[key], int(getattr(train, key)))

        self.assertEqual(payload["name"], train.name)

        self.assertEqual(payload["train_type"], train.train_type.id)
