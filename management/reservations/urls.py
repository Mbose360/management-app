from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RequestedProductViewSet, ReservationViewSet

router = DefaultRouter()
router.register(r'reservation', ReservationViewSet)

rt= DefaultRouter()
rt.register(r'requested_product',RequestedProductViewSet)
urlpatterns = [
    path('', include(router.urls)),
    path('', include(rt.urls)),
]