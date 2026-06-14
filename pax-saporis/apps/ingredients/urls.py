from django.urls import path, include
from rest_framework.routers import SimpleRouter
from apps.ingredients import views

router = SimpleRouter()
router.register(r'', views.IngredientViewSet, basename='ingredient')

urlpatterns = [
    path('', include(router.urls)),
]
