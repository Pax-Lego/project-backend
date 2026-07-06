from django.urls import include, path
from rest_framework.routers import SimpleRouter

from apps.recipes import views

router = SimpleRouter()
router.register(r"", views.RecipeViewSet, basename="recipe")

urlpatterns = [
    path("", include(router.urls)),
]
