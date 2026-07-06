from django.urls import include, path
from rest_framework.routers import SimpleRouter

from apps.favorites import views

router = SimpleRouter()
router.register(
    r"ingredients", views.FavoriteIngredientViewSet, basename="favorite-ingredient"
)
router.register(r"recipes", views.FavoriteRecipeViewSet, basename="favorite-recipe")
router.register(r"plans", views.FavoritePlanViewSet, basename="favorite-plan")

urlpatterns = [
    path("", include(router.urls)),
]
