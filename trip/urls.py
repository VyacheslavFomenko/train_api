from django.urls import path, include
from rest_framework import routers

from trip.views import StationViewSet, TrainTypeViewSet, CrewViewSet, OrderViewSet, TrainViewSet, RouteViewSet, \
    JourneyViewSet

router = routers.DefaultRouter()
router.register("station", StationViewSet)
router.register("train_type", TrainTypeViewSet)
router.register("crew", CrewViewSet)
router.register("order", OrderViewSet)
router.register("train", TrainViewSet, basename="trains")
router.register("route", RouteViewSet, basename="routes")
router.register("journey", JourneyViewSet, basename="journey")

urlpatterns = [
    path("", include(router.urls))
]

app_name = 'trip'
