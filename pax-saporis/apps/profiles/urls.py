from django.urls import include, path
from rest_framework.routers import SimpleRouter

from apps.profiles import views

router = SimpleRouter()
router.register(r"weight", views.WeightEntryViewSet, basename="weight")
router.register(r"", views.ProfileView, basename="profile")

urlpatterns = [
    path("", include(router.urls)),
]
