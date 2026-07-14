from django.urls import include, path
from rest_framework.routers import SimpleRouter

from apps.lists import views

router = SimpleRouter()
router.register(r"ingredients", views.IngredientListViewSet, basename="ingredient-list")
router.register(r"recipes", views.RecipeListViewSet, basename="recipe-list")

urlpatterns = [
    path("", include(router.urls)),
]
