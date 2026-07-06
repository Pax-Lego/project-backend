from django.urls import include, path
from rest_framework.routers import SimpleRouter

from apps.plans import views

router = SimpleRouter()
router.register(r"", views.DailyPlanViewSet, basename="daily-plan")

urlpatterns = [
    path("", include(router.urls)),
]
