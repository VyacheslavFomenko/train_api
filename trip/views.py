from datetime import datetime

from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAdminUser
from rest_framework.viewsets import GenericViewSet

from trip.models import Station, TrainType, Crew, Order, Train, Route, Journey
from trip.pagination import DefaultPagination
from trip.serializers import StationSerializer, TrainTypeSerializer, CrewSerializer, \
    OrderSerializer, OrderListSerializer, TrainSerializer, TrainListSerializer, RouteListSerializer, \
    RouteDetailSerializer, RouteSerializer, JourneySerializer, JourneyListSerializer, JourneyDetailSerializer
from trip.services import params_to_ints


class StationViewSet(mixins.CreateModelMixin,
                     mixins.ListModelMixin,
                     GenericViewSet, ):
    queryset = Station.objects.all()
    serializer_class = StationSerializer
    pagination_class = DefaultPagination
    permission_classes = [IsAdminUser, ]


class TrainTypeViewSet(mixins.CreateModelMixin,
                       mixins.ListModelMixin,
                       GenericViewSet, ):
    queryset = TrainType.objects.all()
    serializer_class = TrainTypeSerializer
    pagination_class = DefaultPagination
    permission_classes = [IsAdminUser, ]


class CrewViewSet(mixins.CreateModelMixin,
                  mixins.ListModelMixin,
                  GenericViewSet, ):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
    pagination_class = DefaultPagination
    permission_classes = [IsAdminUser, ]


class OrderViewSet(mixins.ListModelMixin,
                   mixins.CreateModelMixin,
                   GenericViewSet, ):
    queryset = Order.objects.prefetch_related("ticket__journey__route", "ticket__journey__train")
    serializer_class = OrderSerializer
    pagination_class = DefaultPagination

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer
        return OrderSerializer


class TrainViewSet(viewsets.ModelViewSet):
    queryset = Train.objects.select_related("train_type")
    serializer_class = TrainSerializer
    pagination_class = DefaultPagination

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return TrainListSerializer
        return TrainSerializer

    def get_queryset(self):
        name = self.request.query_params.get("name")
        cargo_num = self.request.query_params.get("cargo_num")
        places_in_cargo = self.request.query_params.get("places_in_cargo")
        train_type = self.request.query_params.get("train_type")

        queryset = self.queryset

        if name:
            queryset = queryset.filter(name__icontains=name)

        if cargo_num:
            queryset = queryset.filter(cargo_num=cargo_num)

        if places_in_cargo:
            queryset = queryset.filter(places_in_cargo=places_in_cargo)

        if train_type:
            train_type_id = params_to_ints(train_type)
            queryset = queryset.filter(train_type__id__in=train_type_id)

        return queryset.distinct()


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.select_related("source__name", "destination__name")
    serializer_class = RouteSerializer
    pagination_class = DefaultPagination

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer
        if self.action == "retrieve":
            return RouteDetailSerializer
        return RouteSerializer

    def get_queryset(self):
        source = self.request.query_params.get("source")
        destination = self.request.query_params.get("destination")

        queryset = self.queryset

        if source:
            source_id = params_to_ints(source)
            queryset = queryset.filter(source__id__in=source_id)
        if destination:
            destination_id = params_to_ints(destination)
            queryset = queryset.filter(destination__id__in=destination_id)
        return queryset.distinct()


class JourneyViewSet(viewsets.ModelViewSet):
    queryset = Journey.objects.prefetch_related("route", "train", "crew")
    serializer_class = JourneySerializer
    pagination_class = DefaultPagination

    def get_serializer_class(self):
        if self.action == "list":
            return JourneyListSerializer
        if self.action == "retrieve":
            return JourneyDetailSerializer
        return JourneySerializer

    @staticmethod
    def _extract_date(time):
        return datetime.strptime(time, "%Y-%m-%d %H:%M").date()

    def get_queryset(self):
        route = self.request.query_params.get("route")
        train = self.request.query_params.get("train")
        departure_time = self.request.query_params.get("departure_time")
        arrival_time = self.request.query_params.get("arrival_time")
        # crew = self.request.query_params.get("crew")

        queryset = self.queryset

        if route:
            route_id = params_to_ints(route)
            queryset = queryset.filter(route__id__in=route_id)
        if train:
            train_id = params_to_ints(train)
            queryset = queryset.filter(train__id__in=train_id)
        if departure_time:
            dp_time = self._extract_date(departure_time)
            queryset = queryset.filter(departure_time__date=dp_time)
        if arrival_time:
            ar_time = self._extract_date(arrival_time)
            queryset = queryset.filter(ar_time__date=ar_time)
        return queryset.distinct()
