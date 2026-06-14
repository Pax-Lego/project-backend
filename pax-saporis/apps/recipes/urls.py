from django.urls import path, include
from rest_framework.routers import SimpleRouter
from apps.recipes import views

router = SimpleRouter()
router.register(r'', views.RecipeViewSet, basename='recipe')

urlpatterns = [
    path('', include(router.urls)),
]
