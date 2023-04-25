from django.urls import path, include
from rest_framework import routers
from .views import InvoiceViewSet, MembershipViewSet, CheckinViewSet

router = routers.DefaultRouter()
router.register(r'invoices', InvoiceViewSet)
router.register(r'memberships', MembershipViewSet)
router.register(r'checkins', CheckinViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
